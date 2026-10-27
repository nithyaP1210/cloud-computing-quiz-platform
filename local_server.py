"""Run the quiz on your own computer. No installs needed (Python 3 only).

    python local_server.py        then open http://localhost:8000

Same routes as the AWS Lambda version (src/app.py), but scores are saved
in scores.json instead of DynamoDB.
"""
import json
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
SCORES_FILE = os.path.join(HERE, "scores.json")
PORT = 8000


def load_scores():
    try:
        with open(SCORES_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return []


class Handler(BaseHTTPRequestHandler):
    def send(self, status, content_type, body):
        data = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/scores":
            items = sorted(load_scores(), key=lambda x: (-x["score"], x["timestamp"]))
            top = [{"name": i["name"], "score": i["score"]} for i in items[:10]]
            self.send(200, "application/json", json.dumps(top))
        else:
            with open(os.path.join(HERE, "src", "index.html"), encoding="utf-8") as f:
                self.send(200, "text/html; charset=utf-8", f.read())

    def do_POST(self):
        if self.path != "/scores":
            return self.send(404, "application/json", '{"error": "Not found"}')
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length) or b"{}")
            name = str(data.get("name", "")).strip()[:30]
            score = int(data.get("score", -1))
        except (ValueError, TypeError):
            return self.send(400, "application/json", '{"error": "Invalid request"}')
        if not name or not 0 <= score <= 5:
            return self.send(400, "application/json", '{"error": "Name and a score from 0 to 5 are required"}')
        scores = load_scores()
        scores.append({"name": name, "score": score, "timestamp": int(time.time())})
        with open(SCORES_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f)
        self.send(201, "application/json", '{"message": "Score saved"}')


if __name__ == "__main__":
    print(f"Quiz running at http://localhost:{PORT}  (Ctrl+C to stop)")
    HTTPServer(("", PORT), Handler).serve_forever()
