from __future__ import annotations

import hashlib
import json
import math
import os
import re
import threading
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from src.chunkers import chunk_source
from src.env_loader import load_env_file
from src.logging_utils import append_jsonl
from src.openai_client import OpenAIAPIError, OpenAIClient
from src.source_loader import load_manifest, load_source_content


STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "does", "for", "from",
    "how", "i", "if", "in", "is", "it", "me", "my", "of", "on", "or", "our", "so",
    "the", "to", "up", "we", "what", "when", "why", "with", "you", "your"
}

SOURCE_PRIORS = {
    "documentation": 1.0,
    "forum": 0.82,
    "blog": 0.78,
}

QUERY_HINTS = {
    "documentation": {
        "official", "policy", "limit", "supported", "steps", "configure", "settings",
        "expire", "expiry", "changed", "retention", "deprovision", "roles", "groups", "audit"
    },
    "forum": {"error", "stuck", "issue", "fails", "community", "anyone", "problem"},
    "blog": {"why", "lessons", "deep", "background", "tuning", "migration", "explain"},
}

TOPIC_QUERY_HINTS = {
    "scim_sync_delay": {"scim", "deprovision", "deprovisioning", "okta", "contractor", "identity"},
    "group_mapping_limit": {"group", "groups", "mapping", "role", "roles", "idp"},
    "api_rate_limit": {"api", "rate", "limit", "429", "retry"},
    "restore_rpo": {"restore", "restoring", "backup", "backups", "snapshot", "snapshots", "workspace"},
    "restore_retention": {"restore", "backup", "backups", "retention", "days", "older"},
    "agent_cert_store": {"agent", "certificate", "certificates", "proxy", "trust", "bundle", "ca", "keychain"},
    "personal_token_expiry": {"token", "tokens", "personal", "expire", "expiry", "rotation"},
    "service_token_expiry": {"service", "account", "accounts", "automation", "jobs", "unattended"},
    "audit_export_format": {"audit", "export", "exports", "ndjson", "csv"},
}

AUTHORITY_QUERY_HINTS = {
    "check", "changed", "configure", "settings", "should", "trust", "use", "version", "what"
}

RELEASE_NOTE_QUERY_HINTS = {"changed", "changes", "new", "version", "4", "2"}

ANSWER_INSTRUCTIONS = """
You are a technical support assistant for the fictional product NimbusFlow.
Answer only from the supplied evidence.
Prefer sources in this order when claims conflict: documentation, forum, blog.
If there is a contradiction, mention it briefly and explain which source you trust more.
Do not invent product behavior.
Keep the answer concise but actionable.
Include short inline citations using the exact source labels provided in the evidence block.
If the evidence is incomplete, say so directly.
""".strip()


def tokenize(text: str) -> list[str]:
    raw = re.findall(r"[a-z0-9_]+", text.lower())
    return [token for token in raw if token not in STOPWORDS and len(token) > 1]


def parse_iso_date(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def slugify_model_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


def normalize_vector(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(component * component for component in vector))
    if not norm:
        return vector
    return [component / norm for component in vector]


def vector_dot(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    return sum(a * b for a, b in zip(left, right))


@dataclass
class QueryResult:
    answer: str
    top_chunks: list[dict[str, Any]]
    contradictions: list[dict[str, Any]]
    source_usage: dict[str, int]
    logs: dict[str, Any]
    runtime: dict[str, Any]


class MultiSourceRAG:
    def __init__(self, root: Path) -> None:
        self.root = root
        load_env_file(root / ".env")
        self.log_path = root / "logs" / "query_logs.jsonl"
        self.sources = load_manifest(root)
        self.chunks = self._build_chunks()
        self.idf = self._build_idf()
        self.chunk_vectors = [self._vectorize_chunk(chunk["text"]) for chunk in self.chunks]
        self.openai_client = OpenAIClient.from_env()
        self.embedding_cache_path = root / "cache" / f"embeddings-{self.embedding_model_slug}.json"
        self.embedding_cache = self._load_embedding_cache()
        self.chunk_embeddings: list[list[float] | None] = [None] * len(self.chunks)
        self.last_runtime_warning: str | None = None
        self.last_embedding_usage: dict[str, Any] = {}
        self._embedding_lock = threading.RLock()
        self._hydrate_chunk_embeddings_from_cache()

    @property
    def embedding_model(self) -> str:
        if self.openai_client:
            return self.openai_client.embedding_model
        return "text-embedding-3-small"

    @property
    def response_model(self) -> str:
        if self.openai_client:
            return self.openai_client.response_model
        return "gpt-5-mini"

    @property
    def embedding_model_slug(self) -> str:
        return slugify_model_name(self.embedding_model)

    def _build_chunks(self) -> list[dict[str, Any]]:
        chunks: list[dict[str, Any]] = []
        for entry in self.sources:
            content = load_source_content(self.root, entry)
            chunks.extend(chunk_source(entry, content))
        return chunks

    def _build_idf(self) -> dict[str, float]:
        doc_freq: Counter[str] = Counter()
        for chunk in self.chunks:
            doc_freq.update(set(tokenize(chunk["text"])))
        total_docs = len(self.chunks)
        idf: dict[str, float] = {}
        for term, freq in doc_freq.items():
            idf[term] = math.log((1 + total_docs) / (1 + freq)) + 1.0
        return idf

    def _vectorize_chunk(self, text: str) -> dict[str, float]:
        tokens = tokenize(text)
        counts = Counter(tokens)
        if not counts:
            return {}
        norm_base = sum(counts.values())
        return {term: (count / norm_base) * self.idf.get(term, 0.0) for term, count in counts.items()}

    def _vectorize_query(self, text: str) -> dict[str, float]:
        counts = Counter(tokenize(text))
        total = sum(counts.values()) or 1
        return {term: (count / total) * self.idf.get(term, 1.0) for term, count in counts.items()}

    def _cosine(self, left: dict[str, float], right: dict[str, float]) -> float:
        if not left or not right:
            return 0.0
        dot = sum(weight * right.get(term, 0.0) for term, weight in left.items())
        left_norm = math.sqrt(sum(weight * weight for weight in left.values()))
        right_norm = math.sqrt(sum(weight * weight for weight in right.values()))
        if not left_norm or not right_norm:
            return 0.0
        return dot / (left_norm * right_norm)

    def _query_source_multiplier(self, query_tokens: set[str], source_type: str) -> float:
        hints = QUERY_HINTS[source_type]
        overlap = len(query_tokens.intersection(hints))
        return 1.0 + (0.08 * overlap)

    def _recency_score(self, updated_at: str) -> float:
        newest = parse_iso_date("2026-04-30")
        current = parse_iso_date(updated_at)
        days_old = max(0, (newest - current).days)
        return max(0.72, 1.0 - (days_old / 1200))

    def _lexical_overlap_bonus(self, query_tokens: set[str], chunk_tokens: set[str]) -> float:
        if not query_tokens:
            return 0.0
        overlap = len(query_tokens.intersection(chunk_tokens))
        return overlap / len(query_tokens)

    def _chunk_signature(self, chunk: dict[str, Any]) -> str:
        payload = {
            "chunk_id": chunk["chunk_id"],
            "text": chunk["text"],
            "title": chunk["title"],
            "section_title": chunk["section_title"],
            "updated_at": chunk["updated_at"],
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()

    def _load_embedding_cache(self) -> dict[str, Any]:
        if not self.embedding_cache_path.exists():
            return {"model": self.embedding_model, "entries": {}}
        try:
            payload = json.loads(self.embedding_cache_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {"model": self.embedding_model, "entries": {}}
        if payload.get("model") != self.embedding_model:
            return {"model": self.embedding_model, "entries": {}}
        payload.setdefault("entries", {})
        return payload

    def _save_embedding_cache(self) -> None:
        self.embedding_cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.embedding_cache["model"] = self.embedding_model
        temp_path = self.embedding_cache_path.with_name(f".{self.embedding_cache_path.name}.tmp")
        temp_path.write_text(json.dumps(self.embedding_cache, indent=2), encoding="utf-8")
        os.replace(temp_path, self.embedding_cache_path)

    def _hydrate_chunk_embeddings_from_cache(self) -> None:
        entries = self.embedding_cache.get("entries", {})
        for index, chunk in enumerate(self.chunks):
            cached = entries.get(chunk["chunk_id"])
            if not cached:
                continue
            if cached.get("signature") != self._chunk_signature(chunk):
                continue
            vector = cached.get("vector")
            if isinstance(vector, list):
                self.chunk_embeddings[index] = vector

    def _ensure_chunk_embeddings(self) -> tuple[bool, str | None]:
        if not self.openai_client:
            return False, "OPENAI_API_KEY is not configured."

        with self._embedding_lock:
            missing_indexes = [index for index, vector in enumerate(self.chunk_embeddings) if vector is None]
            if not missing_indexes:
                return True, None

            pending_texts = [self.chunks[index]["text"] for index in missing_indexes]
            try:
                for batch_start in range(0, len(pending_texts), 24):
                    batch_indexes = missing_indexes[batch_start:batch_start + 24]
                    batch_texts = [self.chunks[index]["text"] for index in batch_indexes]
                    response = self.openai_client.embed_texts(batch_texts)
                    self.last_embedding_usage = response.usage
                    for chunk_index, vector in zip(batch_indexes, response.vectors):
                        normalized = normalize_vector(vector)
                        chunk = self.chunks[chunk_index]
                        self.chunk_embeddings[chunk_index] = normalized
                        self.embedding_cache["entries"][chunk["chunk_id"]] = {
                            "signature": self._chunk_signature(chunk),
                            "vector": normalized,
                        }
                self._save_embedding_cache()
            except OpenAIAPIError as exc:
                warning = f"OpenAI embedding setup failed: {exc}"
                self.last_runtime_warning = warning
                return False, warning

        return True, None

    def _select_diverse_results(self, scored: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
        per_source_cap = {"documentation": 3, "forum": 3, "blog": 3}
        selected: list[dict[str, Any]] = []
        selected_count: defaultdict[str, int] = defaultdict(int)

        for item in scored:
            source_type = item["source_type"]
            if selected_count[source_type] >= per_source_cap.get(source_type, 2):
                continue
            selected.append(item)
            selected_count[source_type] += 1
            if len(selected) >= limit:
                break

        if len(selected) < min(limit, len(scored)):
            for item in scored:
                if item in selected:
                    continue
                selected.append(item)
                if len(selected) >= limit:
                    break
        return selected

    def _retrieve_hybrid(self, query: str, limit: int) -> tuple[list[dict[str, Any]], str, str | None]:
        ready, warning = self._ensure_chunk_embeddings()
        if not ready:
            return self._retrieve_lexical(query, limit, warning)

        assert self.openai_client is not None
        try:
            query_embedding = normalize_vector(self.openai_client.embed_texts([query]).vectors[0])
        except OpenAIAPIError as exc:
            warning = f"OpenAI query embedding failed: {exc}"
            self.last_runtime_warning = warning
            return self._retrieve_lexical(query, limit, warning)

        query_vector = self._vectorize_query(query)
        query_tokens = set(tokenize(query))
        scored: list[dict[str, Any]] = []

        for chunk, lexical_vector, semantic_vector in zip(self.chunks, self.chunk_vectors, self.chunk_embeddings):
            if semantic_vector is None:
                continue
            semantic_score = max(0.0, vector_dot(query_embedding, semantic_vector))
            lexical_score = self._cosine(query_vector, lexical_vector)
            base = (semantic_score * 0.72) + (lexical_score * 0.28)
            if base <= 0:
                continue
            multiplier = SOURCE_PRIORS[chunk["source_type"]] * self._query_source_multiplier(query_tokens, chunk["source_type"])
            score = base * multiplier
            scored.append(
                {
                    **chunk,
                    "semantic_score": round(semantic_score, 6),
                    "lexical_score": round(lexical_score, 6),
                    "retrieval_score": round(score, 6),
                }
            )

        scored.sort(key=lambda item: item["retrieval_score"], reverse=True)
        return self._select_diverse_results(scored, limit), "hybrid-openai", warning

    def _retrieve_lexical(self, query: str, limit: int, warning: str | None = None) -> tuple[list[dict[str, Any]], str, str | None]:
        query_vector = self._vectorize_query(query)
        query_tokens = set(tokenize(query))
        scored: list[dict[str, Any]] = []

        for chunk, vector in zip(self.chunks, self.chunk_vectors):
            lexical_score = self._cosine(query_vector, vector)
            if lexical_score <= 0:
                continue
            multiplier = SOURCE_PRIORS[chunk["source_type"]] * self._query_source_multiplier(query_tokens, chunk["source_type"])
            score = lexical_score * multiplier
            scored.append(
                {
                    **chunk,
                    "semantic_score": 0.0,
                    "lexical_score": round(lexical_score, 6),
                    "retrieval_score": round(score, 6),
                }
            )

        scored.sort(key=lambda item: item["retrieval_score"], reverse=True)
        return self._select_diverse_results(scored, limit), "lexical-fallback", warning

    def retrieve(self, query: str, limit: int = 8) -> list[dict[str, Any]]:
        chunks, _, _ = self._retrieve_hybrid(query, limit)
        return chunks

    def rerank(self, query: str, retrieved: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
        query_tokens = set(tokenize(query))
        reranked: list[dict[str, Any]] = []

        for chunk in retrieved:
            chunk_tokens = set(tokenize(chunk["text"]))
            lexical_bonus = self._lexical_overlap_bonus(query_tokens, chunk_tokens)
            authority_bonus = chunk["authority"]
            recency_bonus = self._recency_score(chunk["updated_at"])
            semantic_bonus = chunk.get("semantic_score", 0.0)
            lexical_score = chunk.get("lexical_score", 0.0)
            accepted_bonus = 0.03 if chunk.get("accepted") else 0.0
            support_bonus = 0.02 if chunk.get("role") == "support-engineer" else 0.0
            policy_bonus = 0.08 if (
                chunk["source_type"] == "documentation"
                and query_tokens.intersection(QUERY_HINTS["documentation"])
            ) else 0.0
            authority_intent_bonus = 0.08 if (
                chunk["source_type"] == "documentation"
                and query_tokens.intersection(AUTHORITY_QUERY_HINTS)
            ) else 0.0
            release_note_bonus = 0.09 if (
                "release notes" in chunk["title"].lower()
                and query_tokens.intersection(RELEASE_NOTE_QUERY_HINTS)
            ) else 0.0
            final_score = (
                (chunk["retrieval_score"] * 0.34)
                + (semantic_bonus * 0.22)
                + (lexical_score * 0.08)
                + (lexical_bonus * 0.10)
                + (authority_bonus * 0.16)
                + (recency_bonus * 0.08)
                + accepted_bonus
                + support_bonus
                + policy_bonus
                + authority_intent_bonus
                + release_note_bonus
            )
            reranked.append({**chunk, "rerank_score": round(final_score, 6)})

        reranked.sort(key=lambda item: item["rerank_score"], reverse=True)
        return reranked[:limit]

    def _topic_relevant_to_query(self, topic: str, query_tokens: set[str]) -> bool:
        keywords = TOPIC_QUERY_HINTS.get(topic, set())
        if not keywords:
            return True
        return bool(query_tokens.intersection(keywords))

    def detect_contradictions(self, chunks: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
        query_tokens = set(tokenize(query))
        by_topic: defaultdict[str, list[dict[str, Any]]] = defaultdict(list)
        for chunk in chunks:
            for claim in chunk.get("claims", []):
                if not self._topic_relevant_to_query(claim["topic"], query_tokens):
                    continue
                by_topic[claim["topic"]].append(
                    {
                        "topic": claim["topic"],
                        "value": claim["value"],
                        "confidence": claim["confidence"],
                        "source_type": chunk["source_type"],
                        "source_title": chunk["title"],
                        "updated_at": chunk["updated_at"],
                    }
                )

        contradictions: list[dict[str, Any]] = []
        for topic, claims in by_topic.items():
            unique_values = {claim["value"] for claim in claims}
            if len(unique_values) <= 1:
                continue

            ordered = sorted(
                claims,
                key=lambda item: (
                    SOURCE_PRIORS[item["source_type"]],
                    self._recency_score(item["updated_at"]),
                    item["confidence"],
                ),
                reverse=True,
            )
            contradictions.append(
                {
                    "topic": topic,
                    "preferred": ordered[0],
                    "alternatives": ordered[1:],
                }
            )
        return contradictions

    def _source_usage(self, chunks: list[dict[str, Any]]) -> dict[str, int]:
        usage = {"documentation": 0, "forum": 0, "blog": 0}
        for chunk in chunks:
            usage[chunk["source_type"]] += 1
        return usage

    def _build_evidence_prompt(
        self,
        query: str,
        top_chunks: list[dict[str, Any]],
        contradictions: list[dict[str, Any]],
        source_usage: dict[str, int],
    ) -> str:
        evidence_lines = []
        for index, chunk in enumerate(top_chunks, start=1):
            evidence_lines.append(
                "\n".join(
                    [
                        f"[Chunk {index}]",
                        f"Source label: [{chunk['source_type']}: {chunk['title']} | {chunk['section_title']}]",
                        f"Source type: {chunk['source_type']}",
                        f"Updated at: {chunk['updated_at']}",
                        f"Retrieval score: {chunk.get('retrieval_score')}",
                        f"Rerank score: {chunk.get('rerank_score')}",
                        "Text:",
                        chunk["text"],
                    ]
                )
            )

        contradiction_lines = []
        for item in contradictions:
            alternatives = ", ".join(
                f"{alt['source_type']}={alt['value']}" for alt in item["alternatives"]
            )
            contradiction_lines.append(
                f"- {item['topic']}: prefer {item['preferred']['source_type']}={item['preferred']['value']}; alternatives: {alternatives}"
            )

        return "\n\n".join(
            [
                f"User question:\n{query}",
                (
                    "Source usage in top results:\n"
                    f"- documentation: {source_usage['documentation']}\n"
                    f"- forum: {source_usage['forum']}\n"
                    f"- blog: {source_usage['blog']}"
                ),
                "Detected contradictions:\n" + ("\n".join(contradiction_lines) if contradiction_lines else "none"),
                "Evidence:\n" + "\n\n".join(evidence_lines),
            ]
        )

    def _compose_answer(self, top_chunks: list[dict[str, Any]], contradictions: list[dict[str, Any]]) -> str:
        intro = "OpenAI generation is unavailable, so this answer uses the deterministic fallback synthesizer."
        evidence_chunks = list(top_chunks)
        if contradictions:
            evidence_chunks = sorted(
                top_chunks,
                key=lambda chunk: (SOURCE_PRIORS[chunk["source_type"]], chunk.get("rerank_score", 0)),
                reverse=True,
            )

        bullets: list[str] = []
        for chunk in evidence_chunks[:3]:
            snippet = chunk["text"].split("\n", 2)[-1].strip().replace("\n", " ")
            snippet = re.sub(r"\s+", " ", snippet)
            snippet = snippet[:220].rstrip()
            bullets.append(f"- {chunk['source_type'].title()}: {snippet}")

        contradiction_text = ""
        if contradictions:
            lines = []
            for contradiction in contradictions[:2]:
                preferred = contradiction["preferred"]
                alt_values = ", ".join(
                    f"{alt['source_type']} says {alt['value']}" for alt in contradiction["alternatives"][:2]
                )
                lines.append(
                    f"- On `{contradiction['topic']}`, prefer {preferred['source_type']} ({preferred['value']}); conflicting evidence: {alt_values}."
                )
            contradiction_text = "\n\nContradictions detected:\n" + "\n".join(lines)

        citations = "\n".join(
            f"- [{chunk['source_type']}] {chunk['title']} -> {chunk['section_title']}"
            for chunk in evidence_chunks[:4]
        )
        return (
            f"{intro}\n\n"
            f"Evidence summary:\n"
            f"{chr(10).join(bullets)}"
            f"{contradiction_text}\n\n"
            f"Top citations:\n{citations}"
        )

    def _generate_answer_with_llm(
        self,
        query: str,
        top_chunks: list[dict[str, Any]],
        contradictions: list[dict[str, Any]],
        source_usage: dict[str, int],
    ) -> tuple[str, str, dict[str, Any], str | None]:
        if not self.openai_client:
            return self._compose_answer(top_chunks, contradictions), "deterministic-fallback", {}, None

        prompt = self._build_evidence_prompt(query, top_chunks, contradictions, source_usage)
        try:
            response = self.openai_client.generate_answer(ANSWER_INSTRUCTIONS, prompt)
        except OpenAIAPIError as exc:
            warning = f"OpenAI answer generation failed: {exc}"
            self.last_runtime_warning = warning
            return self._compose_answer(top_chunks, contradictions), "deterministic-fallback", {}, warning

        return response.text, "openai-responses", response.usage, None

    def runtime_status(self) -> dict[str, Any]:
        with self._embedding_lock:
            cached_embeddings = sum(1 for item in self.chunk_embeddings if item is not None)
        if self.openai_client and cached_embeddings == len(self.chunks):
            embedding_status = "ready"
        elif self.openai_client:
            embedding_status = "pending"
        else:
            embedding_status = "not_configured"

        return {
            "openai_configured": bool(self.openai_client),
            "embedding_model": self.embedding_model,
            "response_model": self.response_model,
            "embedding_status": embedding_status,
            "cached_embeddings": cached_embeddings,
            "total_chunks": len(self.chunks),
            "warning": self.last_runtime_warning,
        }

    def answer(self, query: str) -> QueryResult:
        self.last_runtime_warning = None
        retrieved, retrieval_provider, retrieval_warning = self._retrieve_hybrid(query, limit=8)
        reranked = self.rerank(query, retrieved)
        contradictions = self.detect_contradictions(reranked, query)
        source_usage = self._source_usage(reranked)
        answer, answer_provider, response_usage, answer_warning = self._generate_answer_with_llm(
            query,
            reranked,
            contradictions,
            source_usage,
        )

        runtime_warning = answer_warning or retrieval_warning or self.last_runtime_warning
        status = self.runtime_status()
        runtime = {
            "retrieval_provider": retrieval_provider,
            "answer_provider": answer_provider,
            "embedding_model": status["embedding_model"],
            "response_model": status["response_model"],
            "openai_configured": status["openai_configured"],
            "embedding_status": status["embedding_status"],
            "cached_embeddings": status["cached_embeddings"],
            "total_chunks": status["total_chunks"],
            "warning": runtime_warning,
            "embedding_usage": self.last_embedding_usage,
            "response_usage": response_usage,
        }

        log_record = {
            "query": query,
            "runtime": runtime,
            "source_usage": source_usage,
            "retrieved_chunks": [
                {
                    "chunk_id": chunk["chunk_id"],
                    "source_type": chunk["source_type"],
                    "title": chunk["title"],
                    "section_title": chunk["section_title"],
                    "retrieval_score": chunk.get("retrieval_score"),
                    "rerank_score": chunk.get("rerank_score"),
                    "semantic_score": chunk.get("semantic_score"),
                    "lexical_score": chunk.get("lexical_score"),
                }
                for chunk in reranked
            ],
            "contradictions": contradictions,
        }
        append_jsonl(self.log_path, log_record)

        return QueryResult(
            answer=answer,
            top_chunks=reranked,
            contradictions=contradictions,
            source_usage=source_usage,
            logs=log_record,
            runtime=runtime,
        )

    def recent_logs(self, limit: int = 12) -> list[dict[str, Any]]:
        if not self.log_path.exists():
            return []
        parsed: deque[dict[str, Any]] = deque(maxlen=limit)
        with self.log_path.open("r", encoding="utf-8") as handle:
            for row in handle:
                try:
                    payload = json.loads(row)
                except json.JSONDecodeError:
                    continue
                if isinstance(payload, dict):
                    parsed.append(payload)
        return list(parsed)
