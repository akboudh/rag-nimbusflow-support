from __future__ import annotations

import json
import tempfile
import unittest
from email.message import Message
from http import HTTPStatus
from io import BytesIO
from pathlib import Path

import server
from src.rag_engine import MultiSourceRAG


class FakeEngine:
    def runtime_status(self) -> dict[str, object]:
        return {"openai_configured": False, "embedding_status": "not_configured"}

    def recent_logs(self) -> list[dict[str, object]]:
        return []

    def answer(self, query: str) -> object:
        raise RuntimeError("secret backend detail")


class TrackingLock:
    def __init__(self) -> None:
        self.locked = False

    def __enter__(self) -> None:
        self.locked = True

    def __exit__(self, *_args: object) -> None:
        self.locked = False


class LockAssertingEngine:
    def __init__(self, lock: TrackingLock) -> None:
        self.lock = lock

    def answer(self, query: str) -> object:
        if not self.lock.locked:
            raise AssertionError("answer called without ENGINE_LOCK")
        return type(
            "Result",
            (),
            {
                "answer": "ok",
                "top_chunks": [],
                "contradictions": [],
                "source_usage": {},
                "logs": {},
                "runtime": {},
            },
        )()


class ServerValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_engine = server.ENGINE
        self.original_engine_lock = server.ENGINE_LOCK
        server.ENGINE = FakeEngine()

    def tearDown(self) -> None:
        server.ENGINE = self.original_engine
        server.ENGINE_LOCK = self.original_engine_lock

    def _handler(self, method: str, path: str, body: bytes = b"", content_type: str = "application/json") -> server.AppHandler:
        handler = server.AppHandler.__new__(server.AppHandler)
        handler.command = method
        handler.path = path
        handler.request_version = "HTTP/1.1"
        handler.requestline = f"{method} {path} HTTP/1.1"
        handler.client_address = ("127.0.0.1", 12345)
        handler.server = object()
        handler.log_message = lambda *_args: None
        handler.rfile = BytesIO(body)
        handler.wfile = BytesIO()
        headers = Message()
        headers["Content-Length"] = str(len(body))
        headers["Content-Type"] = content_type
        handler.headers = headers
        return handler

    def _response(self, handler: server.AppHandler) -> tuple[int, dict[str, str], bytes]:
        raw = handler.wfile.getvalue()
        head, _, body = raw.partition(b"\r\n\r\n")
        header_lines = head.decode("iso-8859-1").split("\r\n")
        status = int(header_lines[0].split()[1])
        headers: dict[str, str] = {}
        for line in header_lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                headers[key] = value.strip()
        return status, headers, body

    def _post(self, body: bytes, content_type: str = "application/json") -> tuple[int, dict[str, object]]:
        handler = self._handler("POST", "/api/query", body, content_type)
        handler.do_POST()
        status, _, response_body = self._response(handler)
        return status, json.loads(response_body.decode("utf-8"))

    def test_post_requires_json_content_type(self) -> None:
        status, payload = self._post(b'{"query": "hello"}', "text/plain")

        self.assertEqual(status, HTTPStatus.UNSUPPORTED_MEDIA_TYPE)
        self.assertEqual(payload["error"], "Content-Type must be application/json.")

    def test_post_rejects_oversized_body(self) -> None:
        status, payload = self._post(b"x" * (server.MAX_REQUEST_BODY_BYTES + 1))

        self.assertEqual(status, HTTPStatus.REQUEST_ENTITY_TOO_LARGE)
        self.assertEqual(payload["error"], "Request body is too large.")

    def test_post_rejects_long_query(self) -> None:
        status, payload = self._post(json.dumps({"query": "x" * (server.MAX_QUERY_CHARS + 1)}).encode("utf-8"))

        self.assertEqual(status, HTTPStatus.BAD_REQUEST)
        self.assertEqual(payload["error"], f"Query must be {server.MAX_QUERY_CHARS} characters or fewer.")

    def test_internal_errors_do_not_leak_exception_detail(self) -> None:
        status, payload = self._post(b'{"query": "valid question"}')

        self.assertEqual(status, HTTPStatus.INTERNAL_SERVER_ERROR)
        self.assertEqual(payload["error"], "Internal server error.")

    def test_query_answer_runs_under_engine_lock(self) -> None:
        lock = TrackingLock()
        server.ENGINE_LOCK = lock
        server.ENGINE = LockAssertingEngine(lock)

        status, payload = self._post(b'{"query": "valid question"}')

        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(payload["answer"], "ok")

    def test_static_traversal_is_not_served(self) -> None:
        handler = self._handler("GET", "/../server.py")
        handler.do_GET()
        status, _, _ = self._response(handler)

        self.assertEqual(status, HTTPStatus.NOT_FOUND)

    def test_static_response_has_cache_and_security_headers(self) -> None:
        handler = self._handler("GET", "/")
        handler.do_GET()
        status, headers, _ = self._response(handler)

        self.assertEqual(status, HTTPStatus.OK)
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertIn("Cache-Control", headers)


class LogParsingTests(unittest.TestCase):
    def test_recent_logs_skips_malformed_lines_and_caps_tail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "data").mkdir()
            (root / "data" / "manifest.json").write_text("[]", encoding="utf-8")
            engine = MultiSourceRAG(root)
            engine.log_path.parent.mkdir()
            rows = [json.dumps({"query": f"q{index}"}) for index in range(20)]
            engine.log_path.write_text("\n".join(rows[:8] + ["not-json"] + rows[8:]), encoding="utf-8")

            logs = engine.recent_logs(limit=5)

            self.assertEqual([item["query"] for item in logs], ["q15", "q16", "q17", "q18", "q19"])


if __name__ == "__main__":
    unittest.main()
