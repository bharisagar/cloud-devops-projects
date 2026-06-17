from __future__ import annotations

import json
import logging
import os
import re
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import boto3
from botocore.exceptions import ClientError
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
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
GOVERNANCE_POLICY_VERSION = os.getenv("GOVERNANCE_POLICY_VERSION", "2026-06-16-production-baseline")
GOVERNANCE_RULES_S3_URI = os.getenv("GOVERNANCE_RULES_S3_URI", "")
STATIC_DIR = Path(__file__).resolve().parent / "static"
POLICY_RULES_FILE = Path(
    os.getenv("GOVERNANCE_RULES_FILE", str(Path(__file__).resolve().parent / "policies" / "governance-rules.json"))
)

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

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

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
    policy_rule: str
    policy_action: str
    policy_stage: str
    policy_version: str
    rule_category: str
    rule_severity: str
    responsible_ai_dimensions: list[str]
    guardrail_policy_types: list[str]
    human_review_required: bool
    reviewer_route: str
    redaction_applied: bool
    audit_status: str
    monitoring_stream: str
    evidence_lookup: str
    answer: str
    stop_reason: str
    latency_ms: int


DEFAULT_POLICY_RULES = [
    {
        "name": "credential_exfiltration",
        "description": "Blocks attempts to retrieve cloud credentials, passwords, tokens, API keys, or private keys.",
        "action": "block",
        "category": "secrets",
        "severity": "critical",
        "responsible_ai_dimensions": ["privacy_and_security", "safety", "governance"],
        "guardrail_policy_types": ["sensitive_information_filters", "word_filters"],
        "human_review_required": True,
        "reviewer_route": "security-incident",
        "pattern": (
            r"(give|show|share|print|reveal|send|provide|extract|dump|fetch|get|retrieve|return|display|list).*(aws|iam|access key|secret key|"
            r"credential|password|token|api key|private key|ssh key|session token)|"
            r"(aws_access_key_id|aws_secret_access_key|aws_session_token|secret_access_key)"
        ),
    },
    {
        "name": "prompt_injection",
        "description": "Detects attempts to bypass instructions, jailbreak the assistant, or reveal hidden prompts.",
        "action": "policy_mode",
        "category": "model_safety",
        "severity": "high",
        "responsible_ai_dimensions": ["safety", "controllability", "veracity_and_robustness"],
        "guardrail_policy_types": ["content_filters", "prompt_attack_filters"],
        "human_review_required": False,
        "reviewer_route": "ai-platform-security",
        "pattern": r"(ignore|bypass).*(previous|system|developer|instruction)|jailbreak|reveal.*prompt",
    },
    {
        "name": "restricted_professional_advice",
        "description": "Detects risky legal, medical, or financial instructions that require professional review.",
        "action": "policy_mode",
        "category": "regulated_advice",
        "severity": "medium",
        "responsible_ai_dimensions": ["safety", "transparency", "governance"],
        "guardrail_policy_types": ["denied_topics"],
        "human_review_required": True,
        "reviewer_route": "risk-and-compliance",
        "pattern": r"(guaranteed|exactly).*(legal|medical|financial)|avoid all taxes|prescribe medicine",
    },
    {
        "name": "sensitive_identifier",
        "description": "Detects common sensitive identifiers such as SSNs and payment card-like numbers.",
        "action": "block",
        "category": "data_protection",
        "severity": "critical",
        "responsible_ai_dimensions": ["privacy_and_security", "governance", "transparency"],
        "guardrail_policy_types": ["sensitive_information_filters"],
        "human_review_required": True,
        "reviewer_route": "privacy-review",
        "pattern": r"\b\d{3}-\d{2}-\d{4}\b|\b(?:\d[ -]*?){13,16}\b",
    },
    {
        "name": "cyber_abuse",
        "description": "Blocks requests for malware, credential theft, phishing, ransomware, or unauthorized exploitation.",
        "action": "block",
        "category": "misconduct",
        "severity": "critical",
        "responsible_ai_dimensions": ["safety", "privacy_and_security", "governance"],
        "guardrail_policy_types": ["content_filters", "denied_topics"],
        "human_review_required": True,
        "reviewer_route": "security-incident",
        "pattern": r"(write|create|build|generate|help).*(malware|ransomware|phishing|credential theft|keylogger|steal credentials|exploit a server)",
    },
]


REDACTION_PATTERNS = [
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("ssn", re.compile(r"\b\d{3}-\d{2}-\d{4}\b")),
    ("payment_card", re.compile(r"\b(?:\d[ -]*?){13,16}\b")),
    ("email", re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)),
    (
        "secret_assignment",
        re.compile(
            r"(?i)\b(aws_secret_access_key|aws_session_token|secret_access_key|password|api[_ -]?key|token)\s*[:=]\s*['\"]?[^'\"\s]+"
        ),
    ),
]


def read_s3_json(uri: str) -> Any:
    parsed = urlparse(uri)
    if parsed.scheme != "s3" or not parsed.netloc or not parsed.path.strip("/"):
        raise RuntimeError("GOVERNANCE_RULES_S3_URI must be an s3://bucket/key URI.")

    s3 = boto3.client("s3", region_name=AWS_REGION)
    result = s3.get_object(Bucket=parsed.netloc, Key=parsed.path.lstrip("/"))
    return json.loads(result["Body"].read().decode("utf-8"))


def load_policy_rules() -> list[dict[str, Any]]:
    if GOVERNANCE_RULES_S3_URI:
        loaded = read_s3_json(GOVERNANCE_RULES_S3_URI)
    elif POLICY_RULES_FILE.exists():
        with POLICY_RULES_FILE.open("r", encoding="utf-8") as rules_file:
            loaded = json.load(rules_file)
    else:
        loaded = DEFAULT_POLICY_RULES

    if isinstance(loaded, dict):
        rules = loaded.get("rules", [])
    else:
        rules = loaded

    if not isinstance(rules, list):
        raise RuntimeError("Governance rules must be a JSON array or an object with a rules array.")

    for rule in rules:
        if not {"name", "pattern", "action"}.issubset(rule):
            raise RuntimeError("Each governance rule must include name, pattern, and action.")

    return rules


POLICY_RULES = load_policy_rules()
COMPILED_POLICY_RULES = [
    {
        **rule,
        "compiled_pattern": re.compile(rule["pattern"], re.I),
    }
    for rule in POLICY_RULES
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ttl_epoch() -> int:
    return int((datetime.now(timezone.utc) + timedelta(days=AUDIT_TTL_DAYS)).timestamp())


def redact_sensitive(value: str) -> tuple[str, bool]:
    redacted = value
    changed = False
    for label, pattern in REDACTION_PATTERNS:
        updated = pattern.sub(f"[REDACTED_{label.upper()}]", redacted)
        if updated != redacted:
            changed = True
        redacted = updated
    return redacted, changed


def preview(value: str, limit: int = 240) -> tuple[str, bool]:
    redacted, changed = redact_sensitive(value)
    cleaned = " ".join(redacted.split())
    return cleaned[:limit], changed


def log_event(event_type: str, **fields: Any) -> None:
    payload = {"event_type": event_type, "service": SERVICE_NAME, "time": utc_now(), **fields}
    logger.info(json.dumps(payload, default=str))


def monitoring_stream() -> str:
    return f"/aws/ecs/{SERVICE_NAME}"


def evidence_lookup(request_id: str) -> str:
    if AUDIT_TABLE_NAME:
        return f"DynamoDB table {AUDIT_TABLE_NAME}, key request_id={request_id}"
    return f"CloudWatch structured logs, event request_id={request_id}"


def resolve_rule_action(rule: dict[str, Any]) -> str:
    configured_action = str(rule.get("action", "policy_mode")).lower()
    if configured_action in {"block", "blocked"}:
        return "blocked"
    if configured_action in {"monitor", "monitored"}:
        return "monitored"
    if configured_action == "policy_mode":
        return "blocked" if APP_POLICY_MODE == "enforce" else "monitored"
    raise RuntimeError(f"Unsupported governance rule action: {configured_action}")


def evaluate_local_policy(value: str, stage: str = "input") -> dict[str, Any]:
    for rule in COMPILED_POLICY_RULES:
        if rule["compiled_pattern"].search(value):
            return {
                "rule": rule["name"],
                "action": resolve_rule_action(rule),
                "stage": stage,
                "category": rule.get("category", "general"),
                "severity": rule.get("severity", "medium"),
                "description": rule.get("description", ""),
                "responsible_ai_dimensions": rule.get("responsible_ai_dimensions", []),
                "guardrail_policy_types": rule.get("guardrail_policy_types", []),
                "human_review_required": bool(rule.get("human_review_required", False)),
                "reviewer_route": rule.get("reviewer_route", "none"),
            }
    return {
        "rule": "none",
        "action": "allowed",
        "stage": stage,
        "category": "none",
        "severity": "none",
        "description": "No local governance rule matched.",
        "responsible_ai_dimensions": [],
        "guardrail_policy_types": [],
        "human_review_required": False,
        "reviewer_route": "none",
    }


def write_audit(item: dict[str, Any]) -> None:
    if not audit_table:
        log_event("audit_skipped", reason="AUDIT_TABLE_NAME not configured", request_id=item.get("request_id"))
        return

    audit_table.put_item(Item=item)


def call_bedrock(prompt: str, request_metadata: dict[str, str] | None = None) -> dict[str, str]:
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
    if request_metadata:
        request["requestMetadata"] = request_metadata
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


def invoke_provider(prompt: str, policy: dict[str, Any], request_metadata: dict[str, str]) -> dict[str, str]:
    if policy["action"] == "blocked":
        return call_demo_provider(prompt, policy)

    if AI_PROVIDER == "bedrock":
        return call_bedrock(prompt, request_metadata)
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
        "policy_version": GOVERNANCE_POLICY_VERSION,
        "rules_source": GOVERNANCE_RULES_S3_URI or str(POLICY_RULES_FILE),
        "rules_file": str(POLICY_RULES_FILE),
    }


@app.get("/governance/rules")
def governance_rules() -> dict[str, Any]:
    return {
        "rules_source": GOVERNANCE_RULES_S3_URI or str(POLICY_RULES_FILE),
        "rules_file": str(POLICY_RULES_FILE),
        "policy_mode": APP_POLICY_MODE,
        "policy_version": GOVERNANCE_POLICY_VERSION,
        "rules": [
            {
                "name": rule["name"],
                "description": rule.get("description", ""),
                "action": rule.get("action", "policy_mode"),
                "category": rule.get("category", "general"),
                "severity": rule.get("severity", "medium"),
                "responsible_ai_dimensions": rule.get("responsible_ai_dimensions", []),
                "guardrail_policy_types": rule.get("guardrail_policy_types", []),
                "human_review_required": bool(rule.get("human_review_required", False)),
                "reviewer_route": rule.get("reviewer_route", "none"),
            }
            for rule in POLICY_RULES
        ],
    }


@app.get("/", response_class=HTMLResponse)
@app.get("/chat", response_class=HTMLResponse)
def chat_console() -> Any:
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)

    return HTMLResponse(
        "<h1>Enterprise AI Governance Gateway</h1>"
        "<p>Static chat console is not packaged. Use <a href='/docs'>/docs</a>.</p>",
        status_code=200,
    )


@app.post("/prompt", response_model=PromptResponse)
def prompt(request: PromptRequest) -> PromptResponse:
    started = time.time()
    request_id = str(uuid.uuid4())
    policy = evaluate_local_policy(request.prompt, "input")
    prompt_preview, prompt_redacted = preview(request.prompt)
    request_metadata = {
        "request_id": request_id,
        "tenant_id": request.tenant_id,
        "use_case": request.use_case,
        "policy_version": GOVERNANCE_POLICY_VERSION,
    }

    audit_item: dict[str, Any] = {
        "request_id": request_id,
        "created_at": utc_now(),
        "expires_at": ttl_epoch(),
        "tenant_id": request.tenant_id,
        "user_id": request.user_id or "unknown",
        "use_case": request.use_case,
        "sensitivity": request.sensitivity,
        "provider": AI_PROVIDER,
        "policy_version": GOVERNANCE_POLICY_VERSION,
        "prompt_preview": prompt_preview,
        "redaction_applied": prompt_redacted,
        "policy_rule": policy["rule"],
        "policy_action": policy["action"],
        "policy_stage": policy["stage"],
        "rule_category": policy["category"],
        "rule_severity": policy["severity"],
        "responsible_ai_dimensions": policy["responsible_ai_dimensions"],
        "guardrail_policy_types": policy["guardrail_policy_types"],
        "human_review_required": policy["human_review_required"],
        "reviewer_route": policy["reviewer_route"],
        "status": "STARTED",
    }

    try:
        result = invoke_provider(request.prompt, policy, request_metadata)
        final_policy = policy
        if result["governance_action"] != "blocked":
            output_policy = evaluate_local_policy(result["answer"], "output")
            if output_policy["action"] == "blocked":
                final_policy = output_policy
                result = {
                    **result,
                    "answer": "The model response was stopped by the enterprise AI governance policy.",
                    "stop_reason": output_policy["rule"],
                    "governance_action": output_policy["action"],
                }
            elif output_policy["action"] == "monitored":
                final_policy = output_policy
                result = {**result, "governance_action": "monitored"}

        latency_ms = int((time.time() - started) * 1000)

        answer_preview, answer_redacted = preview(result["answer"])
        audit_item.update(
            {
                "status": "COMPLETED",
                "model_id": result["model_id"],
                "governance_action": result["governance_action"],
                "stop_reason": result["stop_reason"],
                "policy_rule": final_policy["rule"],
                "policy_action": final_policy["action"],
                "policy_stage": final_policy["stage"],
                "rule_category": final_policy["category"],
                "rule_severity": final_policy["severity"],
                "responsible_ai_dimensions": final_policy["responsible_ai_dimensions"],
                "guardrail_policy_types": final_policy["guardrail_policy_types"],
                "human_review_required": final_policy["human_review_required"],
                "reviewer_route": final_policy["reviewer_route"],
                "answer_preview": answer_preview,
                "answer_redaction_applied": answer_redacted,
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
            policy_rule=final_policy["rule"],
            policy_stage=final_policy["stage"],
            rule_category=final_policy["category"],
            rule_severity=final_policy["severity"],
            policy_version=GOVERNANCE_POLICY_VERSION,
            human_review_required=final_policy["human_review_required"],
            reviewer_route=final_policy["reviewer_route"],
            latency_ms=latency_ms,
        )

        return PromptResponse(
            request_id=request_id,
            provider=AI_PROVIDER,
            model_id=result["model_id"],
            governance_action=result["governance_action"],
            policy_rule=final_policy["rule"],
            policy_action=final_policy["action"],
            policy_stage=final_policy["stage"],
            policy_version=GOVERNANCE_POLICY_VERSION,
            rule_category=final_policy["category"],
            rule_severity=final_policy["severity"],
            responsible_ai_dimensions=final_policy["responsible_ai_dimensions"],
            guardrail_policy_types=final_policy["guardrail_policy_types"],
            human_review_required=final_policy["human_review_required"],
            reviewer_route=final_policy["reviewer_route"],
            redaction_applied=prompt_redacted or answer_redacted,
            audit_status="stored" if audit_table else "cloudwatch_only",
            monitoring_stream=monitoring_stream(),
            evidence_lookup=evidence_lookup(request_id),
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
                "error_preview": preview(str(exc), 500)[0],
                "latency_ms": latency_ms,
            }
        )
        write_audit(audit_item)
        log_event(
            "prompt_failed",
            request_id=request_id,
            error_code=error_code,
            policy_rule=policy["rule"],
            rule_category=policy["category"],
            policy_version=GOVERNANCE_POLICY_VERSION,
            latency_ms=latency_ms,
        )

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
                "error_preview": preview(str(exc), 500)[0],
                "latency_ms": latency_ms,
            }
        )
        write_audit(audit_item)
        log_event(
            "prompt_failed",
            request_id=request_id,
            error_code="ApplicationError",
            policy_rule=policy["rule"],
            rule_category=policy["category"],
            policy_version=GOVERNANCE_POLICY_VERSION,
            latency_ms=latency_ms,
        )

        raise HTTPException(
            status_code=500,
            detail={"request_id": request_id, "error": "Application error in AI governance gateway."},
        ) from exc
