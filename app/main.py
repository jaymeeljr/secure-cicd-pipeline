"""Minimal task API used as the target of the secure CI/CD pipeline.

The application is intentionally small: the point of this repository is the
pipeline around it, not the app itself.
"""

import os
from flask import Flask, jsonify, request, abort

app = Flask(__name__)

# In-memory store keeps the demo dependency-free (no database to secure).
TASKS: dict[int, dict] = {}
_next_id = 1

MAX_TITLE_LENGTH = 200


@app.get("/health")
def health():
    """Liveness/readiness probe target for Kubernetes."""
    return jsonify(status="ok")


@app.get("/tasks")
def list_tasks():
    return jsonify(list(TASKS.values()))


@app.post("/tasks")
def create_task():
    global _next_id
    payload = request.get_json(silent=True) or {}
    title = payload.get("title")

    # Input validation: reject missing, non-string or oversized input.
    if not isinstance(title, str) or not title.strip():
        abort(400, description="'title' must be a non-empty string")
    if len(title) > MAX_TITLE_LENGTH:
        abort(400, description=f"'title' must be at most {MAX_TITLE_LENGTH} characters")

    task = {"id": _next_id, "title": title.strip(), "done": False}
    TASKS[_next_id] = task
    _next_id += 1
    return jsonify(task), 201


@app.patch("/tasks/<int:task_id>")
def complete_task(task_id: int):
    task = TASKS.get(task_id)
    if task is None:
        abort(404, description="task not found")
    task["done"] = True
    return jsonify(task)


@app.after_request
def security_headers(response):
    """Basic security headers on every response."""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = "default-src 'none'"
    response.headers["Referrer-Policy"] = "no-referrer"
    return response


if __name__ == "__main__":
    # Local development only: bind to loopback. In the container, gunicorn serves the app.
    # Debug mode stays off unless explicitly enabled; never in production.
    debug = os.environ.get("APP_DEBUG", "false").lower() == "true"
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", "8080")), debug=debug)
