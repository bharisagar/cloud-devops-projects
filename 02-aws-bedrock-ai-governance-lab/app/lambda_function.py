import json
import os
import time
import uuid
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError

bedrock = boto3.client("bedrock-runtime")
dynamodb = boto3.resource("dynamodb")

audit_table = dynamodb.Table(os.environ["AUDIT_TABLE_NAME"])
model_id = os.environ["BEDROCK_MODEL_ID"]
guardrail_id = os.environ["BEDROCK_GUARDRAIL_ID"]
guardrail_version = os.environ.get("BEDROCK_GUARDRAIL_VERSION", "DRAFT")


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(body),
    }


def lambda_handler(event, context):
    started = time.time()
    request_id = str(uuid.uuid4())

    try:
        payload = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return _response(400, {"error": "Invalid JSON body"})

    prompt = payload.get("prompt", "").strip()
    if not prompt:
        return _response(400, {"error": "prompt is required"})

    audit_item = {
        "request_id": request_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "prompt_preview": prompt[:180],
        "status": "STARTED",
        "model_id": model_id,
        "guardrail_id": guardrail_id,
    }

    try:
        result = bedrock.converse(
            modelId=model_id,
            guardrailConfig={
                "guardrailIdentifier": guardrail_id,
                "guardrailVersion": guardrail_version,
                "trace": "enabled",
            },
            messages=[{"role": "user", "content": [{"text": prompt}]}],
            inferenceConfig={"maxTokens": 600, "temperature": 0.2},
        )

        output_blocks = result.get("output", {}).get("message", {}).get("content", [])
        answer = "".join(block.get("text", "") for block in output_blocks)
        stop_reason = result.get("stopReason", "unknown")
        latency_ms = int((time.time() - started) * 1000)

        audit_item.update({
            "status": "COMPLETED",
            "stop_reason": stop_reason,
            "latency_ms": latency_ms,
            "answer_preview": answer[:180],
        })
        audit_table.put_item(Item=audit_item)

        return _response(200, {
            "request_id": request_id,
            "answer": answer,
            "stop_reason": stop_reason,
            "latency_ms": latency_ms,
        })

    except ClientError as exc:
        error_code = exc.response.get("Error", {}).get("Code", "ClientError")
        http_status = 429 if error_code == "ThrottlingException" else 500
        latency_ms = int((time.time() - started) * 1000)
        audit_item.update({
            "status": "FAILED_OR_BLOCKED",
            "latency_ms": latency_ms,
            "error": str(exc)[:500],
        })
        audit_table.put_item(Item=audit_item)
        return _response(500, {
            "request_id": request_id,
            "error": "The request failed or was blocked by governance controls.",
            "error_code": error_code,
            "detail": str(exc)[:300],
        }) if http_status == 500 else _response(429, {
            "request_id": request_id,
            "error": "Bedrock model generation is currently throttled by the account quota.",
            "error_code": error_code,
            "detail": str(exc)[:300],
        })

    except Exception as exc:
        latency_ms = int((time.time() - started) * 1000)
        audit_item.update({
            "status": "FAILED_OR_BLOCKED",
            "latency_ms": latency_ms,
            "error": str(exc)[:500],
        })
        audit_table.put_item(Item=audit_item)
        return _response(500, {
            "request_id": request_id,
            "error": "The request failed because of an application error.",
            "detail": str(exc)[:300],
        })
