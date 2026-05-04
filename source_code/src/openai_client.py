from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any
from urllib import error, request


class OpenAIAPIError(RuntimeError):
    """Raised when the OpenAI API returns an error or malformed payload."""


@dataclass
class EmbeddingResponse:
    vectors: list[list[float]]
    usage: dict[str, Any]


@dataclass
class TextResponse:
    text: str
    usage: dict[str, Any]
    response_id: str | None


class OpenAIClient:
    def __init__(
        self,
        api_key: str,
        embedding_model: str = "text-embedding-3-small",
        response_model: str = "gpt-5-mini",
        base_url: str = "https://api.openai.com/v1",
    ) -> None:
        self.api_key = api_key
        self.embedding_model = embedding_model
        self.response_model = response_model
        self.base_url = base_url.rstrip("/")

    @classmethod
    def from_env(cls) -> "OpenAIClient | None":
        api_key = os.getenv("OPENAI_API_KEY", "").strip()
        if not api_key:
            return None
        embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small").strip()
        response_model = os.getenv("OPENAI_RESPONSE_MODEL", "gpt-5-mini").strip()
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1").strip()
        return cls(
            api_key=api_key,
            embedding_model=embedding_model,
            response_model=response_model,
            base_url=base_url,
        )

    def _request(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            f"{self.base_url}{path}",
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=120) as response:
                raw = response.read().decode("utf-8")
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise OpenAIAPIError(self._extract_error_message(detail, exc.reason)) from exc
        except error.URLError as exc:
            raise OpenAIAPIError(f"Network error: {exc.reason}") from exc

        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise OpenAIAPIError("OpenAI API returned invalid JSON.") from exc

    def embed_texts(self, texts: list[str]) -> EmbeddingResponse:
        payload = {
            "model": self.embedding_model,
            "input": texts,
        }
        data = self._request("/embeddings", payload)
        rows = data.get("data", [])
        vectors = [row.get("embedding", []) for row in rows]
        if len(vectors) != len(texts):
            raise OpenAIAPIError("Embedding response length did not match input length.")
        return EmbeddingResponse(vectors=vectors, usage=data.get("usage", {}))

    def generate_answer(self, instructions: str, prompt: str) -> TextResponse:
        payload = {
            "model": self.response_model,
            "instructions": instructions,
            "input": prompt,
        }
        data = self._request("/responses", payload)
        text = self._extract_output_text(data)
        if not text:
            raise OpenAIAPIError("Responses API returned no text output.")
        return TextResponse(
            text=text.strip(),
            usage=data.get("usage", {}),
            response_id=data.get("id"),
        )

    def _extract_error_message(self, raw: str, fallback: str) -> str:
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return f"OpenAI API request failed: {fallback}"

        error_payload = payload.get("error", {})
        if isinstance(error_payload, dict):
            message = error_payload.get("message")
            if message:
                return f"OpenAI API request failed: {message}"
        return f"OpenAI API request failed: {fallback}"

    def _extract_output_text(self, payload: dict[str, Any]) -> str:
        top_level = payload.get("output_text")
        if isinstance(top_level, str) and top_level.strip():
            return top_level

        parts: list[str] = []
        for item in payload.get("output", []):
            if item.get("type") == "message":
                for content in item.get("content", []):
                    if content.get("type") == "output_text" and content.get("text"):
                        parts.append(content["text"])
            if item.get("type") == "output_text" and item.get("text"):
                parts.append(item["text"])
        return "\n".join(part for part in parts if part).strip()
