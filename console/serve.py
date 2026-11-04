"""Bring-Up Bot console: a local live view of agent runs.
    python console/serve.py      then open http://localhost:8765
"""
import json
import re
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
RUNS = ROOT / "runs"


class Handler(BaseHTTPRequestHandler):
    def send(self, body: bytes, ctype: str, code: int = 200) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path in ("/", "/index.html"):
            return self.send((HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
        if self.path == "/api/runs":
            names = sorted((p.name for p in RUNS.glob("run-*.json")), reverse=True)
            return self.send(json.dumps(names).encode(), "application/json")
        m = re.fullmatch(r"/api/runs/(run-[\d-]+\.json)", self.path)
        if m and (RUNS / m.group(1)).exists():
            return self.send((RUNS / m.group(1)).read_bytes(), "application/json")
        self.send(b"not found", "text/plain", 404)

    def do_POST(self) -> None:
        if self.path != "/api/run":
            return self.send(b"not found", "text/plain", 404)
        try:
            length = int(self.headers.get("Content-Length", 0) or 0)
            body = json.loads(self.rfile.read(length) or b"{}")
        except ValueError:
            return self.send(b"bad request", "text/plain", 400)
        task = body.get("task", "")
        try:
            max_turns = int(body.get("max_turns", 20))
        except (TypeError, ValueError):
            max_turns = 0
        if not isinstance(task, str) or not task.strip() or max_turns < 1:
            return self.send(b"task and positive max_turns required", "text/plain", 400)
        subprocess.Popen([sys.executable, str(ROOT / "bringup_agent" / "agent.py"),
                          "--max-turns", str(max_turns), task.strip()],
                         cwd=ROOT, start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.send(b'{"started": true}', "application/json")

    def log_message(self, *args) -> None:
        pass


if __name__ == "__main__":
    print("Bring-Up Bot console: http://localhost:8765")
    ThreadingHTTPServer(("127.0.0.1", 8765), Handler).serve_forever()
