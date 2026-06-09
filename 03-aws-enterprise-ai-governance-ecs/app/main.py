from __future__ import annotations

import json
import logging
import os
import re
import time
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import boto3
from botocore.exceptions import ClientError
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


SERVICE_NAME = os.getenv("SERVICE_NAME", "enterprise-ai-governance-gateway")
AWS_REGION = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION", "ap-south-1")
AI_PROVIDER = os.getenv("AI_PROVIDER", "demo").lower()
APP_POLICY_MODE = os.getenv("APP_POLICY_MODE", "monitor").lower()

AUDIT_TABLE_NAME = os.getenv("AUDIT_TABLE_NAME", "")
AUDIT_TTL_DAYS = int(os.getenv("AUDIT_TTL_DAYS", "30"))

BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "apac.amazon.nova-pro-v1:0")
BEDROCK_GUARDRAIL_ID = os.getenv("BEDROCK_GUARDRAIL_ID", "")
BEDROCK_GUARDRAIL_VERSION = os.getenv("BEDROCK_GUARDRAIL_VERSION", "DRAFT")

SAGEMAKER_ENDPOINT_NAME = os.getenv("SAGEMAKER_ENDPOINT_NAME", "")

logger = logging.getLogger(SERVICE_NAME)
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(message)s",
)

app = FastAPI(
    title="Enterprise AI Governance Gateway",
    description="Governed AI API for Bedrock or SageMaker backends.",
    version="1.0.0",
)

bedrock_runtime = boto3.client("bedrock-runtime", region_name=AWS_REGION)
sagemaker_runtime = boto3.client("sagemaker-runtime", region_name=AWS_REGION)
dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION) if AUDIT_TABLE_NAME else None
audit_table = dynamodb.Table(AUDIT_TABLE_NAME) if dynamodb else None


class PromptRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=8000)
    tenant_id: str = Field("sandbox", min_length=1, max_length=80)
    use_case: str = Field("architecture-review", min_length=1, max_length=120)
    user_id: str | None = Field(default=None, max_length=120)
    sensitivity: str = Field("internal", max_length=40)


class PromptResponse(BaseModel):
    request_id: str
    provider: str
    model_id: str
    governance_action: str
    answer: str
    stop_reason: str
    latency_ms: int


POLICY_RULES = [
    (
        "prompt_injection",
        re.compile(r"(ignore|bypass).*(previous|system|developer|instruction)|jailbreak|reveal.*prompt", re.I),
    ),
    (
        "restricted_professional_advice",
        re.compile(r"(guaranteed|exactly).*(legal|medical|financial)|avoid all taxes|prescribe medicine", re.I),
    ),
    (
        "sensitive_identifier",
        re.compile(r"\b\d{3}-\d{2}-\d{4}\b|\b(?:\d[ -]*?){13,16}\b", re.I),
    ),
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ttl_epoch() -> int:
    return int((datetime.now(timezone.utc) + timedelta(days=AUDIT_TTL_DAYS)).timestamp())


def preview(value: str, limit: int = 240) -> str:
    cleaned = " ".join(value.split())
    return cleaned[:limit]


def log_event(event_type: str, **fields: Any) -> None:
    payload = {"event_type": event_type, "service": SERVICE_NAME, "time": utc_now(), **fields}
    logger.info(json.dumps(payload, default=str))


def evaluate_local_policy(prompt: str) -> dict[str, str]:
    for rule_name, pattern in POLICY_RULES:
        if pattern.search(prompt):
            action = "blocked" if APP_POLICY_MODE == "enforce" else "monitored"
            return {"rule": rule_name, "action": action}
    return {"rule": "none", "action": "allowed"}


def write_audit(item: dict[str, Any]) -> None:
    if not audit_table:
        log_event("audit_skipped", reason="AUDIT_TABLE_NAME not configured", request_id=item.get("request_id"))
        return

    audit_table.put_item(Item=item)


def call_bedrock(prompt: str) -> dict[str, str]:
    guardrail_config = None
    if BEDROCK_GUARDRAIL_ID:
        guardrail_config = {
            "guardrailIdentifier": BEDROCK_GUARDRAIL_ID,
            "guardrailVersion": BEDROCK_GUARDRAIL_VERSION,
            "trace": "enabled",
        }

    request: dict[str, Any] = {
        "modelId": BEDROCK_MODEL_ID,
        "messages": [{"role": "user", "content": [{"text": prompt}]}],
        "inferenceConfig": {"maxTokens": 600, "temperature": 0.2},
    }
    if guardrail_config:
        request["guardrailConfig"] = guardrail_config

    result = bedrock_runtime.converse(**request)
    blocks = result.get("output", {}).get("message", {}).get("content", [])
    answer = "".join(block.get("text", "") for block in blocks)
    stop_reason = result.get("stopReason", "unknown")
    action = "blocked" if stop_reason == "guardrail_intervened" else "allowed"

    return {
        "answer": answer or "No model text was returned.",
        "stop_reason": stop_reason,
        "governance_action": action,
        "model_id": BEDROCK_MODEL_ID,
    }


def call_sagemaker(prompt: str) -> dict[str, str]:
    if not SAGEMAKER_ENDPOINT_NAME:
        raise RuntimeError("SAGEMAKER_ENDPOINT_NAME is required when AI_PROVIDER=sagemaker")

    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 300, "temperature": 0.2}}
    result = sagemaker_runtime.invoke_endpoint(
        EndpointName=SAGEMAKER_ENDPOINT_NAME,
        ContentType="application/json",
        Body=json.dumps(payload).encode("utf-8"),
    )

    raw_body = result["Body"].read().decode("utf-8")
    parsed = json.loads(raw_body)

    if isinstance(parsed, list) and parsed:
        first = parsed[0]
        answer = first.get("generated_text") or first.get("answer") or json.dumps(first)
    elif isinstance(parsed, dict):
        answer = parsed.get("generated_text") or parsed.get("answer") or json.dumps(parsed)
    else:
        answer = raw_body

    return {
        "answer": answer,
        "stop_reason": "sagemaker_endpoint_completed",
        "governance_action": "allowed",
        "model_id": SAGEMAKER_ENDPOINT_NAME,
    }


def call_demo_provider(prompt: str, policy: dict[str, str]) -> dict[str, str]:
    if policy["action"] == "blocked":
        return {
            "answer": "This request was blocked by the enterprise AI governance policy.",
            "stop_reason": policy["rule"],
            "governance_action": "blocked",
            "model_id": "demo-governed-model",
        }

    if policy["action"] == "monitored":
        answer = (
            "This prompt matched a monitored governance rule. In production, the request "
            "would be reviewed with Bedrock Guardrails, audit logging, and policy evidence."
        )
    else:
        answer = (
            "Approved response from the demo AI gateway. The request was accepted, "
            "audited, and routed through the governed enterprise API path."
        )

    return {
        "answer": answer,
        "stop_reason": "demo_completed",
        "governance_action": policy["action"],
        "model_id": "demo-governed-model",
    }


def invoke_provider(prompt: str, policy: dict[str, str]) -> dict[str, str]:
    if policy["action"] == "blocked":
        return call_demo_provider(prompt, policy)

    if AI_PROVIDER == "bedrock":
        return call_bedrock(prompt)
    if AI_PROVIDER == "sagemaker":
        return call_sagemaker(prompt)
    if AI_PROVIDER == "demo":
        return call_demo_provider(prompt, policy)

    raise RuntimeError(f"Unsupported AI_PROVIDER value: {AI_PROVIDER}")


@app.get("/health")
def health() -> dict[str, Any]:
    return {
        "service": SERVICE_NAME,
        "status": "healthy",
        "region": AWS_REGION,
        "provider": AI_PROVIDER,
        "audit_enabled": bool(AUDIT_TABLE_NAME),
        "policy_mode": APP_POLICY_MODE,
    }


@app.post("/prompt", response_model=PromptResponse)
def prompt(request: PromptRequest) -> PromptResponse:
    started = time.time()
    request_id = str(uuid.uuid4())
    policy = evaluate_local_policy(request.prompt)

    audit_item: dict[str, Any] = {
        "request_id": request_id,
        "created_at": utc_now(),
        "expires_at": ttl_epoch(),
        "tenant_id": request.tenant_id,
        "user_id": request.user_id or "unknown",
        "use_case": request.use_case,
        "sensitivity": request.sensitivity,
        "provider": AI_PROVIDER,
        "prompt_preview": preview(request.prompt),
        "policy_rule": policy["rule"],
        "policy_action": policy["action"],
        "status": "STARTED",
    }

    try:
        result = invoke_provider(request.prompt, policy)
        latency_ms = int((time.time() - started) * 1000)

        audit_item.update(
            {
                "status": "COMPLETED",
                "model_id": result["model_id"],
                "governance_action": result["governance_action"],
                "stop_reason": result["stop_reason"],
                "answer_preview": preview(result["answer"]),
                "latency_ms": latency_ms,
            }
        )
        write_audit(audit_item)
        log_event(
            "prompt_completed",
            request_id=request_id,
            tenant_id=request.tenant_id,
            provider=AI_PROVIDER,
            action=result["governance_action"],
            latency_ms=latency_ms,
        )

        return PromptResponse(
            request_id=request_id,
            provider=AI_PROVIDER,
            model_id=result["model_id"],
            governance_action=result["governance_action"],
            answer=result["answer"],
            stop_reason=result["stop_reason"],
            latency_ms=latency_ms,
        )

    except ClientError as exc:
        latency_ms = int((time.time() - started) * 1000)
        error_code = exc.response.get("Error", {}).get("Code", "ClientError")
        audit_item.update(
            {
                "status": "FAILED",
                "error_code": error_code,
                "error_preview": preview(str(exc), 500),
                "latency_ms": latency_ms,
            }
        )
        write_audit(audit_item)
        log_event("prompt_failed", request_id=request_id, error_code=error_code, latency_ms=latency_ms)

        if error_code in {"ThrottlingException", "TooManyRequestsException"}:
            raise HTTPException(
                status_code=429,
                detail={
                    "request_id": request_id,
                    "error": "AI backend throttled the request. Check model quota and retry policy.",
                    "error_code": error_code,
                },
            ) from exc

        raise HTTPException(
            status_code=500,
            detail={
                "request_id": request_id,
                "error": "AI backend request failed.",
                "error_code": error_code,
            },
        ) from exc

    except Exception as exc:
        latency_ms = int((time.time() - started) * 1000)
        audit_item.update(
            {
                "status": "FAILED",
                "error_code": "ApplicationError",
                "error_preview": preview(str(exc), 500),
                "latency_ms": latency_ms,
            }
        )
        write_audit(audit_item)
        log_event("prompt_failed", request_id=request_id, error_code="ApplicationError", latency_ms=latency_ms)

        raise HTTPException(
            status_code=500,
            detail={"request_id": request_id, "error": "Application error in AI governance gateway."},
        ) from exc
