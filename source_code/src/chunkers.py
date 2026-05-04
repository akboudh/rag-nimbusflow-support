from __future__ import annotations

import re
from typing import Any


CLAIM_TOPIC_KEYWORDS = {
    "scim_sync_delay": {"scim", "deprovision", "deprovisioning", "identity", "okta", "retry", "sync"},
    "saml_supported": {"saml", "single", "sign", "identity"},
    "group_mapping_limit": {"group", "groups", "mapping", "role", "roles", "idp"},
    "api_rate_limit": {"api", "rate", "limit", "retry", "429"},
    "restore_rpo": {"restore", "recovery", "backup", "backups", "snapshot", "preview"},
    "restore_retention": {"restore", "retention", "backup", "backups", "days", "snapshot"},
    "agent_cert_store": {"agent", "certificate", "certificates", "proxy", "trust", "store", "bundle", "keychain"},
    "personal_token_expiry": {"token", "tokens", "personal", "expire", "expiration", "rotation"},
    "service_token_expiry": {"token", "tokens", "service", "account", "rotation", "long"},
    "audit_export_format": {"audit", "export", "exports", "ndjson", "csv", "siem"},
}


def _clean(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text.strip())


def _relevant_claims(entry: dict[str, Any], text: str) -> list[dict[str, Any]]:
    token_set = set(re.findall(r"[a-z0-9_]+", text.lower()))
    relevant: list[dict[str, Any]] = []
    for claim in entry.get("claims", []):
        keywords = CLAIM_TOPIC_KEYWORDS.get(claim["topic"], set())
        if token_set.intersection(keywords):
            relevant.append(claim)
    return relevant


def chunk_documentation(entry: dict[str, Any], content: str) -> list[dict[str, Any]]:
    title = content.splitlines()[0].lstrip("# ").strip()
    sections = re.split(r"(?m)^##\s+", content)
    chunks: list[dict[str, Any]] = []

    for raw_section in sections:
        raw_section = raw_section.strip()
        if not raw_section:
            continue

        if raw_section.startswith("# "):
            continue

        lines = raw_section.splitlines()
        section_title = lines[0].strip()
        body = "\n".join(lines[1:]).strip()

        subsections = re.split(r"(?m)^###\s+", body) if body else []
        if len(subsections) <= 1:
            text = _clean(f"{title}\n{section_title}\n{body}")
            chunks.append(
                {
                    "chunk_id": f"{entry['id']}::{len(chunks)+1}",
                    "source_id": entry["id"],
                    "source_type": entry["source_type"],
                    "title": entry["title"],
                    "section_title": section_title,
                    "text": text,
                    "claims": _relevant_claims(entry, text),
                    "authority": entry["authority"],
                    "updated_at": entry["updated_at"],
                    "tags": entry.get("tags", []),
                }
            )
            continue

        prefix = subsections[0].strip()
        if prefix:
            text = _clean(f"{title}\n{section_title}\n{prefix}")
            chunks.append(
                {
                    "chunk_id": f"{entry['id']}::{len(chunks)+1}",
                    "source_id": entry["id"],
                    "source_type": entry["source_type"],
                    "title": entry["title"],
                    "section_title": section_title,
                    "text": text,
                    "claims": _relevant_claims(entry, text),
                    "authority": entry["authority"],
                    "updated_at": entry["updated_at"],
                    "tags": entry.get("tags", []),
                }
            )

        for subsection in subsections[1:]:
            sub_lines = subsection.splitlines()
            sub_title = sub_lines[0].strip()
            sub_body = "\n".join(sub_lines[1:]).strip()
            text = _clean(f"{title}\n{section_title}\n{sub_title}\n{sub_body}")
            chunks.append(
                {
                    "chunk_id": f"{entry['id']}::{len(chunks)+1}",
                    "source_id": entry["id"],
                    "source_type": entry["source_type"],
                    "title": entry["title"],
                    "section_title": f"{section_title} / {sub_title}",
                    "text": text,
                    "claims": _relevant_claims(entry, text),
                    "authority": entry["authority"],
                    "updated_at": entry["updated_at"],
                    "tags": entry.get("tags", []),
                }
            )
    return chunks


def chunk_forum(entry: dict[str, Any], content: dict[str, Any]) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    accepted_id = content.get("accepted_post_id")

    question = next((post for post in content["posts"] if post["role"] == "customer"), content["posts"][0])

    for post in content["posts"]:
        boost_text = "Accepted answer." if post["id"] == accepted_id else ""
        combined = _clean(
            f"Thread: {content['title']}\n"
            f"Question: {question['body']}\n"
            f"Post by {post['author']} ({post['role']}): {post['body']}\n"
            f"{boost_text}"
        )
        chunks.append(
            {
                "chunk_id": f"{entry['id']}::{post['id']}",
                "source_id": entry["id"],
                "source_type": entry["source_type"],
                "title": entry["title"],
                "section_title": f"Forum post {post['id']}",
                "text": combined,
                "claims": _relevant_claims(entry, combined),
                "authority": entry["authority"] + (0.08 if post["role"] == "support-engineer" else 0.0),
                "updated_at": post["created_at"],
                "tags": entry.get("tags", []),
                "accepted": post["id"] == accepted_id,
                "role": post["role"],
            }
        )

    return chunks


def chunk_blog(entry: dict[str, Any], content: str) -> list[dict[str, Any]]:
    lines = [line.rstrip() for line in content.strip().splitlines()]
    title = lines[0].lstrip("# ").strip()
    chunks: list[dict[str, Any]] = []
    current_heading = title
    paragraph_buffer: list[str] = []

    def flush_with_windows() -> None:
        nonlocal paragraph_buffer
        if not paragraph_buffer:
            return
        window_size = 2
        overlap = 1
        step = max(1, window_size - overlap)
        for index in range(0, len(paragraph_buffer), step):
            window = paragraph_buffer[index:index + window_size]
            if not window:
                continue
            text = _clean(f"{title}\n{current_heading}\n" + "\n\n".join(window))
            chunks.append(
                {
                    "chunk_id": f"{entry['id']}::{len(chunks)+1}",
                    "source_id": entry["id"],
                    "source_type": entry["source_type"],
                    "title": entry["title"],
                    "section_title": current_heading,
                    "text": text,
                    "claims": _relevant_claims(entry, text),
                    "authority": entry["authority"],
                    "updated_at": entry["updated_at"],
                    "tags": entry.get("tags", []),
                }
            )
            if index + window_size >= len(paragraph_buffer):
                break
        paragraph_buffer = []

    for line in lines[1:]:
        if line.startswith("## "):
            flush_with_windows()
            current_heading = line[3:].strip()
            continue
        if not line:
            continue
        paragraph_buffer.append(line)

    flush_with_windows()
    return chunks


def chunk_source(entry: dict[str, Any], content: Any) -> list[dict[str, Any]]:
    if entry["source_type"] == "documentation":
        return chunk_documentation(entry, content)
    if entry["source_type"] == "forum":
        return chunk_forum(entry, content)
    if entry["source_type"] == "blog":
        return chunk_blog(entry, content)
    raise ValueError(f"Unsupported source type: {entry['source_type']}")
