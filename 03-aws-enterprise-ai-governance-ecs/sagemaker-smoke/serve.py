from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    server_version = "SageMakerSmoke/1.0"

    def do_GET(self) -> None:
        if self.path == "/ping":
            self._send_json(200, {"status": "healthy"})
            return
        self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        if self.path != "/invocations":
            self._send_json(404, {"error": "not found"})
            return

        length = int(self.headers.get("content-length", "0"))
        body = self.rfile.read(length).decode("utf-8") if length else "{}"

        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            self._send_json(400, {"error": "invalid json"})
            return

        prompt = payload.get("inputs") or payload.get("prompt") or ""
        prompt = " ".join(str(prompt).split())

        response = {
            "generated_text": (
                "SageMaker Runtime smoke test succeeded. "
                "The governed AI gateway can route a request to a SageMaker endpoint. "
                f"Prompt preview: {prompt[:160]}"
            ),
            "model": "sagemaker-smoke-custom-endpoint",
            "purpose": "low-cost endpoint integration evidence",
        }
        self._send_json(200, response)

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send_json(self, status: int, payload: dict[str, object]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
