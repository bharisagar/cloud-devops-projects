import argparse
import json
import urllib.error
import urllib.request
from pathlib import Path


def post_json(url, payload):
    data = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw_body = exc.read().decode("utf-8")
        try:
            return exc.code, json.loads(raw_body)
        except json.JSONDecodeError:
            return exc.code, {"error": raw_body}
    except Exception as exc:
        return 0, {"error": str(exc)}


def main():
    parser = argparse.ArgumentParser(description="Run Bedrock AI governance test prompts")
    parser.add_argument("--endpoint", required=True, help="API Gateway endpoint URL")
    parser.add_argument("--prompts", default="test_prompts.json", help="Path to prompt test file")
    args = parser.parse_args()

    prompts = json.loads(Path(args.prompts).read_text(encoding="utf-8-sig"))
    for item in prompts:
        status, body = post_json(args.endpoint, {"prompt": item["prompt"]})
        print(f"\n=== {item['name']} ({item['category']}) ===")
        print(f"HTTP: {status}")
        print(json.dumps(body, indent=2)[:1200])


if __name__ == "__main__":
    main()
