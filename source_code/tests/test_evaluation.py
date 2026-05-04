from __future__ import annotations

import unittest

from scripts import evaluate
from src.chunkers import chunk_source
from src.rag_engine import MultiSourceRAG


class EvaluationHelperTests(unittest.TestCase):
    def test_summarize_empty_rows_avoids_divide_by_zero(self) -> None:
        summary = evaluate.summarize_results([])

        self.assertEqual(summary["query_count"], 0)
        self.assertEqual(summary["retrieval_hit_rate_at_5"], 0.0)

    def test_preferred_source_checks_top_rank(self) -> None:
        row = {
            "query": "token expiry",
            "expected_source_ids": ["doc-release-notes"],
            "expected_preferred_source_id": "doc-release-notes",
            "expected_topics": [],
            "expect_contradiction": False,
        }
        result = evaluate.evaluate_row(
            row,
            retrieved=[{"source_id": "doc-release-notes", "source_type": "documentation"}],
            reranked=[{"source_id": "blog-4-2-migration", "source_type": "blog"}],
            contradictions=[],
        )

        self.assertFalse(result["preferred_source_top"])

    def test_contradiction_hit_rejects_unexpected_extra_topics(self) -> None:
        self.assertFalse(
            evaluate.contradiction_hit(
                {"personal_token_expiry", "service_token_expiry"},
                {"personal_token_expiry"},
                expect_contradiction=True,
            )
        )

    def test_contradiction_hit_rejects_any_non_expected_contradiction(self) -> None:
        self.assertFalse(
            evaluate.contradiction_hit(
                {"service_token_expiry"},
                {"personal_token_expiry"},
                expect_contradiction=False,
            )
        )

    def test_threshold_failure_sets_nonzero_exit_status(self) -> None:
        summary = {
            "query_count": 1,
            "retrieval_hit_rate_at_5": 1.0,
            "rerank_hit_rate_at_5": 0.5,
            "retrieval_mrr_at_5": 1.0,
            "rerank_mrr_at_5": 0.5,
            "contradiction_accuracy": 1.0,
            "preferred_source_top_rate": 0.5,
            "avg_source_diversity_top5": 1.0,
        }

        self.assertFalse(evaluate.meets_thresholds(summary))


class RagEdgeCaseTests(unittest.TestCase):
    def test_select_diverse_results_handles_unknown_source_type(self) -> None:
        engine = MultiSourceRAG.__new__(MultiSourceRAG)
        scored = [
            {"source_type": "documentation", "source_id": "a"},
            {"source_type": "internal-note", "source_id": "b"},
        ]

        selected = engine._select_diverse_results(scored, limit=2)

        self.assertEqual([item["source_id"] for item in selected], ["a", "b"])

    def test_forum_chunker_handles_missing_accepted_post(self) -> None:
        entry = {
            "id": "forum-test",
            "source_type": "forum",
            "title": "Forum Test",
            "authority": 0.5,
            "updated_at": "2026-01-01T00:00:00Z",
            "claims": [],
        }
        content = {
            "title": "Forum Test",
            "posts": [
                {"id": "p1", "role": "customer", "author": "A", "body": "Question", "created_at": "2026-01-01T00:00:00Z"}
            ],
        }

        chunks = chunk_source(entry, content)

        self.assertEqual(chunks[0]["section_title"], "Forum post p1")


if __name__ == "__main__":
    unittest.main()
