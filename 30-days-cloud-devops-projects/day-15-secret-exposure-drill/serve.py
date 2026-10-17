"""Serve the Day 15 dashboard and local scan API on loopback only."""

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from scan import scan_text


ROOT = Path(__file__).resolve().parent
MAX_BODY = 100_000


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == "/api/sample":
            self.send_json(200, {"text": (ROOT / "sample.env.txt").read_text(encoding="utf-8")})
            return
        if self.path == "/":
            self.send_response(302)
            self.send_header("Location", "/app/")
            self.end_headers()
            return
        if self.path not in ("/app/", "/app/index.html", "/app/styles.css", "/app/app.js"):
            self.send_error(404)
            return
        super().do_GET()

    def do_POST(self):
        if self.path != "/api/scan":
            self.send_error(404)
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if size <= 0 or size > MAX_BODY:
                self.send_json(413, {"error": "Input must be between 1 and 100000 bytes."})
                return
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict) or not isinstance(payload.get("text"), str):
                raise ValueError("Expected JSON object with text string")
            if len(payload["text"].encode("utf-8")) > MAX_BODY:
                self.send_json(413, {"error": "Text is too large."})
                return
            self.send_json(200, scan_text(payload["text"]))
        except (ValueError, UnicodeDecodeError):
            self.send_json(400, {"error": "Invalid scan request."})


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8150), Handler)
    print("Day 15 dashboard: http://127.0.0.1:8150/app/", flush=True)
    server.serve_forever()
