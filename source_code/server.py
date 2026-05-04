from __future__ import annotations

import json
import mimetypes
import os
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from src.env_loader import load_env_file
from src.rag_engine import MultiSourceRAG


ROOT = Path(__file__).resolve().parent
STATIC_ROOT = ROOT / "static"
STATIC_ROOT_RESOLVED = STATIC_ROOT.resolve()
load_env_file(ROOT / ".env")
ENGINE = MultiSourceRAG(ROOT)
ENGINE_LOCK = threading.RLock()
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))
MAX_REQUEST_BODY_BYTES = int(os.getenv("MAX_REQUEST_BODY_BYTES", str(64 * 1024)))
MAX_QUERY_CHARS = int(os.getenv("MAX_QUERY_CHARS", "1200"))


class AppHandler(BaseHTTPRequestHandler):
    def _write_json(self, payload: dict, status: int = HTTPStatus.OK) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _resolve_static_path(self, route: str) -> Path | None:
        relative_route = "index.html" if route == "/" else unquote(route).lstrip("/")
        path = (STATIC_ROOT_RESOLVED / relative_route).resolve()
        if path != STATIC_ROOT_RESOLVED and STATIC_ROOT_RESOLVED not in path.parents:
            return None
        return path

    def _serve_file(self, path: Path) -> None:
        if not path.exists() or not path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        content = path.read_bytes()
        content_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
        self.send_response(HTTPStatus.OK)
        if content_type.startswith("text/") or content_type in {"application/javascript", "image/svg+xml"}:
            self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        else:
            self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        cache_control = "no-cache" if path.name == "index.html" else "public, max-age=3600"
        self.send_header("Cache-Control", cache_control)
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        route = parsed.path

        if route == "/api/health":
            with ENGINE_LOCK:
                runtime = ENGINE.runtime_status()
            self._write_json({"status": "ok", **runtime})
            return
        if route == "/api/logs":
            with ENGINE_LOCK:
                logs = ENGINE.recent_logs()
            self._write_json({"logs": logs})
            return
        if route == "/api/example-queries":
            examples_path = ROOT / "outputs" / "example_queries.json"
            examples = json.loads(examples_path.read_text(encoding="utf-8")) if examples_path.exists() else []
            self._write_json({"examples": examples})
            return

        file_path = self._resolve_static_path(route)
        if file_path is None:
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        self._serve_file(file_path)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        if parsed.path != "/api/query":
            self.send_error(HTTPStatus.NOT_FOUND)
            return

        content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        if content_type != "application/json":
            self._write_json(
                {"error": "Content-Type must be application/json."},
                status=HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
            )
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._write_json({"error": "Content-Length must be an integer."}, status=HTTPStatus.BAD_REQUEST)
            return
        if length > MAX_REQUEST_BODY_BYTES:
            self._write_json({"error": "Request body is too large."}, status=HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
            return

        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw.decode("utf-8") or "{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._write_json({"error": "Request body must be valid JSON."}, status=HTTPStatus.BAD_REQUEST)
            return

        if not isinstance(payload, dict):
            self._write_json({"error": "Request body must be a JSON object."}, status=HTTPStatus.BAD_REQUEST)
            return

        query_value = payload.get("query", "")
        query = query_value.strip() if isinstance(query_value, str) else ""

        if not query:
            self._write_json({"error": "Query is required."}, status=HTTPStatus.BAD_REQUEST)
            return
        if len(query) > MAX_QUERY_CHARS:
            self._write_json(
                {"error": f"Query must be {MAX_QUERY_CHARS} characters or fewer."},
                status=HTTPStatus.BAD_REQUEST,
            )
            return

        try:
            # MultiSourceRAG.answer still owns request-scoped runtime fields on the
            # shared engine, so serialize full answers until that state is local.
            with ENGINE_LOCK:
                result = ENGINE.answer(query)
        except Exception:
            self._write_json({"error": "Internal server error."}, status=HTTPStatus.INTERNAL_SERVER_ERROR)
            return

        self._write_json(
            {
                "answer": result.answer,
                "top_chunks": result.top_chunks,
                "contradictions": result.contradictions,
                "source_usage": result.source_usage,
                "logs": result.logs,
                "runtime": result.runtime,
            }
        )


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), AppHandler)
    print(f"NimbusFlow RAG app running at http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
