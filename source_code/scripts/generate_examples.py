from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.rag_engine import MultiSourceRAG


def main() -> None:
    engine = MultiSourceRAG(ROOT)
    examples = json.loads((ROOT / "outputs" / "example_queries.json").read_text(encoding="utf-8"))
    runtime = engine.runtime_status()

    md_lines = [
        "# Example Queries and Responses",
        "",
        "## Runtime",
        "",
        f"- openai_configured: {runtime['openai_configured']}",
        f"- embedding_model: {runtime['embedding_model']}",
        f"- response_model: {runtime['response_model']}",
        f"- embedding_status: {runtime['embedding_status']}",
        "",
    ]
    structured: list[dict[str, object]] = []

    for index, item in enumerate(examples, start=1):
        result = engine.answer(item["query"])
        md_lines.extend(
            [
                f"## {index}. {item['query']}",
                "",
                "### Response",
                "",
                result.answer,
                "",
                "### Source Usage",
                "",
                json.dumps(result.source_usage, indent=2),
                "",
                "### Runtime",
                "",
                json.dumps(result.runtime, indent=2),
                "",
                "### Top Chunks",
                "",
            ]
        )

        for chunk in result.top_chunks:
            md_lines.append(
                f"- `{chunk['source_type']}` {chunk['title']} -> {chunk['section_title']} "
                f"(retrieval={chunk.get('retrieval_score')}, rerank={chunk.get('rerank_score')})"
            )
        md_lines.append("")

        structured.append(
            {
                "query": item["query"],
                "answer": result.answer,
                "runtime": result.runtime,
                "source_usage": result.source_usage,
                "top_chunks": [
                    {
                        "source_type": chunk["source_type"],
                        "source_id": chunk["source_id"],
                        "title": chunk["title"],
                        "section_title": chunk["section_title"],
                        "retrieval_score": chunk.get("retrieval_score"),
                        "rerank_score": chunk.get("rerank_score"),
                    }
                    for chunk in result.top_chunks
                ],
                "contradictions": result.contradictions,
            }
        )

    (ROOT / "outputs" / "example_queries.md").write_text("\n".join(md_lines), encoding="utf-8")
    (ROOT / "outputs" / "example_queries_results.json").write_text(json.dumps(structured, indent=2), encoding="utf-8")
    print("Wrote outputs/example_queries.md and outputs/example_queries_results.json")


if __name__ == "__main__":
    main()
