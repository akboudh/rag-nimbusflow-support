from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.rag_engine import MultiSourceRAG

THRESHOLDS = {
    "retrieval_hit_rate_at_5": 0.85,
    "rerank_hit_rate_at_5": 0.85,
    "rerank_mrr_at_5": 0.75,
    "contradiction_accuracy": 0.85,
    "preferred_source_top_rate": 0.9,
    "avg_source_diversity_top5": 2.0,
}


def reciprocal_rank(items: list[dict[str, object]], expected_source_ids: set[str]) -> float:
    for index, item in enumerate(items, start=1):
        if item["source_id"] in expected_source_ids:
            return 1.0 / index
    return 0.0


def contains_expected(items: list[dict[str, object]], expected_source_ids: set[str]) -> bool:
    return any(item["source_id"] in expected_source_ids for item in items)


def contradiction_hit(result_topics: set[str], expected_topics: set[str], expect_contradiction: bool) -> bool:
    if not expect_contradiction:
        return not result_topics
    return result_topics == expected_topics


def evaluate_row(
    row: dict[str, object],
    retrieved: list[dict[str, object]],
    reranked: list[dict[str, object]],
    contradictions: list[dict[str, object]],
) -> dict[str, object]:
    expected_source_ids = set(row["expected_source_ids"])
    expected_topics = set(row["expected_topics"])
    expected_preferred_source_id = row.get("expected_preferred_source_id")
    contradiction_topics = {item["topic"] for item in contradictions}

    retrieval_hit = contains_expected(retrieved[:5], expected_source_ids)
    rerank_hit = contains_expected(reranked[:5], expected_source_ids)
    retrieval_rr = reciprocal_rank(retrieved[:5], expected_source_ids)
    rerank_rr = reciprocal_rank(reranked[:5], expected_source_ids)
    contradiction_ok = contradiction_hit(contradiction_topics, expected_topics, bool(row["expect_contradiction"]))
    source_diversity = len({chunk["source_type"] for chunk in reranked[:5]})
    source_id_diversity = len({chunk["source_id"] for chunk in reranked[:5]})
    preferred_source_top = bool(reranked) and reranked[0]["source_id"] == expected_preferred_source_id

    return {
        "query": row["query"],
        "retrieval_hit@5": retrieval_hit,
        "rerank_hit@5": rerank_hit,
        "retrieval_rr": round(retrieval_rr, 4),
        "rerank_rr": round(rerank_rr, 4),
        "contradiction_ok": contradiction_ok,
        "preferred_source_top": preferred_source_top,
        "source_diversity": source_diversity,
        "source_id_diversity": source_id_diversity,
        "top_retrieved_sources": [chunk["source_id"] for chunk in retrieved[:5]],
        "top_reranked_sources": [chunk["source_id"] for chunk in reranked[:5]],
        "contradiction_topics": sorted(contradiction_topics),
    }


def summarize_results(details: list[dict[str, object]]) -> dict[str, object]:
    count = len(details)
    if not count:
        return {
            "query_count": 0,
            "retrieval_hit_rate_at_5": 0.0,
            "rerank_hit_rate_at_5": 0.0,
            "retrieval_mrr_at_5": 0.0,
            "rerank_mrr_at_5": 0.0,
            "contradiction_accuracy": 0.0,
            "preferred_source_top_rate": 0.0,
            "avg_source_diversity_top5": 0.0,
            "avg_source_id_diversity_top5": 0.0,
        }

    return {
        "query_count": count,
        "retrieval_hit_rate_at_5": round(sum(int(item["retrieval_hit@5"]) for item in details) / count, 3),
        "rerank_hit_rate_at_5": round(sum(int(item["rerank_hit@5"]) for item in details) / count, 3),
        "retrieval_mrr_at_5": round(sum(float(item["retrieval_rr"]) for item in details) / count, 3),
        "rerank_mrr_at_5": round(sum(float(item["rerank_rr"]) for item in details) / count, 3),
        "contradiction_accuracy": round(sum(int(item["contradiction_ok"]) for item in details) / count, 3),
        "preferred_source_top_rate": round(sum(int(item["preferred_source_top"]) for item in details) / count, 3),
        "avg_source_diversity_top5": round(sum(int(item["source_diversity"]) for item in details) / count, 3),
        "avg_source_id_diversity_top5": round(sum(int(item["source_id_diversity"]) for item in details) / count, 3),
    }


def meets_thresholds(summary: dict[str, object]) -> bool:
    return all(float(summary.get(metric, 0.0)) >= minimum for metric, minimum in THRESHOLDS.items())


def evaluate(engine: MultiSourceRAG, eval_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    details: list[dict[str, object]] = []

    for row in eval_rows:
        query = row["query"]

        retrieved = engine.retrieve(query)
        reranked = engine.rerank(query, retrieved)
        contradictions = engine.detect_contradictions(reranked, query)
        details.append(evaluate_row(row, retrieved, reranked, contradictions))
    return details


def write_reports(runtime: dict[str, object], summary: dict[str, object], details: list[dict[str, object]]) -> None:

    markdown = [
        "# Performance Analysis",
        "",
        "## Runtime",
        "",
        f"- openai_configured: {runtime['openai_configured']}",
        f"- embedding_model: {runtime['embedding_model']}",
        f"- response_model: {runtime['response_model']}",
        f"- embedding_status: {runtime['embedding_status']}",
        "",
        "## Summary",
        "",
        *(f"- {key}: {value}" for key, value in summary.items()),
        "",
        "## Interpretation",
        "",
        "- Retrieval hit rate shows whether the weighted retrieval stage surfaced at least one expected source in the top 5.",
        "- Rerank hit rate and MRR show whether the weighted reranking stage improved the final ordering.",
        "- Contradiction accuracy checks whether the system surfaced disagreements when expected and stayed quiet otherwise.",
        "- Source diversity measures whether the final answer is informed by multiple source types instead of collapsing onto a single corpus.",
        "- Preferred source top rate checks whether the most authoritative expected source wins the top reranked slot.",
        "- This is a small seeded benchmark, not a statistically broad production evaluation.",
        "",
        "## Query-level Results",
        "",
    ]

    for item in details:
        markdown.extend(
            [
                f"### {item['query']}",
                "",
                f"- retrieval hit@5: {item['retrieval_hit@5']}",
                f"- rerank hit@5: {item['rerank_hit@5']}",
                f"- retrieval RR: {item['retrieval_rr']}",
                f"- rerank RR: {item['rerank_rr']}",
                f"- contradiction ok: {item['contradiction_ok']}",
                f"- preferred source top: {item['preferred_source_top']}",
                f"- source diversity: {item['source_diversity']}",
                f"- source-id diversity: {item['source_id_diversity']}",
                f"- top retrieved: {', '.join(item['top_retrieved_sources'])}",
                f"- top reranked: {', '.join(item['top_reranked_sources'])}",
                f"- contradiction topics: {', '.join(item['contradiction_topics']) or 'none'}",
                "",
            ]
        )

    (ROOT / "outputs" / "performance_analysis.md").write_text("\n".join(markdown), encoding="utf-8")
    (ROOT / "outputs" / "performance_metrics.json").write_text(
        json.dumps({"summary": summary, "details": details}, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2))


def main() -> int:
    engine = MultiSourceRAG(ROOT)
    eval_rows = json.loads((ROOT / "data" / "evaluation_queries.json").read_text(encoding="utf-8"))
    runtime = engine.runtime_status()
    details = evaluate(engine, eval_rows)
    summary = summarize_results(details)
    write_reports(runtime, summary, details)
    if not meets_thresholds(summary):
        print("Evaluation thresholds were not met.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
