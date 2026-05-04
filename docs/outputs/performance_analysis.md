# Performance Analysis

## Runtime

- openai_configured: True
- embedding_model: text-embedding-3-small
- response_model: gpt-5-mini
- embedding_status: ready

## Summary

- query_count: 12
- retrieval_hit_rate_at_5: 1.0
- rerank_hit_rate_at_5: 1.0
- retrieval_mrr_at_5: 1.0
- rerank_mrr_at_5: 1.0
- contradiction_accuracy: 1.0
- preferred_source_top_rate: 1.0
- avg_source_diversity_top5: 2.5
- avg_source_id_diversity_top5: 3.167

## Interpretation

- Retrieval hit rate shows whether the weighted retrieval stage surfaced at least one expected source in the top 5.
- Rerank hit rate and MRR show whether the weighted reranking stage improved the final ordering.
- Contradiction accuracy checks whether the system surfaced disagreements when expected and stayed quiet otherwise.
- Source diversity measures whether the final answer is informed by multiple source types instead of collapsing onto a single corpus.
- Preferred source top rate checks whether the most authoritative expected source wins the top reranked slot.
- This is a small seeded benchmark, not a statistically broad production evaluation.

## Query-level Results

### Do personal API tokens expire after NimbusFlow 4.2?

- retrieval hit@5: True
- rerank hit@5: True
- retrieval RR: 1.0
- rerank RR: 1.0
- contradiction ok: True
- preferred source top: True
- source diversity: 2
- source-id diversity: 3
- top retrieved: doc-release-notes, forum-token-thread, forum-token-thread, forum-token-thread, blog-4-2-migration
- top reranked: doc-release-notes, forum-token-thread, doc-release-notes, doc-support-guide, forum-token-thread
- contradiction topics: personal_token_expiry

### My desktop agent is stuck on verifying certificate behind a proxy. What should I check?

- retrieval hit@5: True
- rerank hit@5: True
- retrieval RR: 1.0
- rerank RR: 1.0
- contradiction ok: True
- preferred source top: True
- source diversity: 3
- source-id diversity: 3
- top retrieved: forum-agent-thread, forum-agent-thread, doc-support-guide, forum-agent-thread, blog-agent-tuning
- top reranked: doc-support-guide, forum-agent-thread, forum-agent-thread, forum-agent-thread, blog-agent-tuning
- contradiction topics: none

### How quickly does SCIM deprovision a removed contractor?

- retrieval hit@5: True
- rerank hit@5: True
- retrieval RR: 1.0
- rerank RR: 1.0
- contradiction ok: True
- preferred source top: True
- source diversity: 2
- source-id diversity: 3
- top retrieved: forum-scim-thread, doc-admin-guide, forum-scim-thread, forum-scim-thread, doc-support-guide
- top reranked: doc-admin-guide, forum-scim-thread, forum-scim-thread, forum-scim-thread, doc-support-guide
- contradiction topics: scim_sync_delay

### What is the API rate limit and how should a client react to 429 errors?

- retrieval hit@5: True
- rerank hit@5: True
- retrieval RR: 1.0
- rerank RR: 1.0
- contradiction ok: True
- preferred source top: True
- source diversity: 2
- source-id diversity: 2
- top retrieved: doc-support-guide, doc-support-guide, doc-support-guide, blog-4-2-migration, blog-4-2-migration
- top reranked: doc-support-guide, doc-support-guide, doc-support-guide, blog-4-2-migration, blog-4-2-migration
- contradiction topics: none

### Can I restore a workspace from two weeks ago?

- retrieval hit@5: True
- rerank hit@5: True
- retrieval RR: 1.0
- rerank RR: 1.0
- contradiction ok: True
- preferred source top: True
- source diversity: 2
- source-id diversity: 3
- top retrieved: doc-support-guide, blog-restore-post, blog-restore-post, doc-support-guide, blog-restore-post
- top reranked: doc-support-guide, doc-support-guide, doc-admin-guide, blog-restore-post, blog-restore-post
- contradiction topics: restore_retention, restore_rpo

### What changed for audit exports in NimbusFlow 4.2?

- retrieval hit@5: True
- rerank hit@5: True
- retrieval RR: 1.0
- rerank RR: 1.0
- contradiction ok: True
- preferred source top: True
- source diversity: 2
- source-id diversity: 5
- top retrieved: doc-support-guide, doc-admin-guide, doc-release-notes, blog-restore-post, blog-4-2-migration
- top reranked: doc-release-notes, doc-support-guide, doc-admin-guide, blog-restore-post, blog-4-2-migration
- contradiction topics: none

### Should unattended jobs use personal tokens or service accounts?

- retrieval hit@5: True
- rerank hit@5: True
- retrieval RR: 1.0
- rerank RR: 1.0
- contradiction ok: True
- preferred source top: True
- source diversity: 3
- source-id diversity: 4
- top retrieved: blog-4-2-migration, doc-release-notes, forum-token-thread, doc-release-notes, forum-token-thread
- top reranked: doc-release-notes, blog-4-2-migration, doc-release-notes, doc-admin-guide, forum-token-thread
- contradiction topics: personal_token_expiry, service_token_expiry

### How many IdP groups can I map to NimbusFlow roles?

- retrieval hit@5: True
- rerank hit@5: True
- retrieval RR: 1.0
- rerank RR: 1.0
- contradiction ok: True
- preferred source top: True
- source diversity: 3
- source-id diversity: 4
- top retrieved: doc-admin-guide, doc-admin-guide, doc-support-guide, blog-4-2-migration, forum-scim-thread
- top reranked: doc-admin-guide, doc-admin-guide, doc-support-guide, blog-4-2-migration, forum-scim-thread
- contradiction topics: none

### Does the desktop agent use a private CA bundle?

- retrieval hit@5: True
- rerank hit@5: True
- retrieval RR: 1.0
- rerank RR: 1.0
- contradiction ok: True
- preferred source top: True
- source diversity: 3
- source-id diversity: 3
- top retrieved: doc-support-guide, forum-agent-thread, forum-agent-thread, forum-agent-thread, blog-agent-tuning
- top reranked: doc-support-guide, forum-agent-thread, forum-agent-thread, forum-agent-thread, blog-agent-tuning
- contradiction topics: none

### Why do older posts mention nightly snapshots?

- retrieval hit@5: True
- rerank hit@5: True
- retrieval RR: 1.0
- rerank RR: 1.0
- contradiction ok: True
- preferred source top: True
- source diversity: 3
- source-id diversity: 3
- top retrieved: blog-restore-post, forum-token-thread, forum-token-thread, forum-token-thread, blog-restore-post
- top reranked: blog-restore-post, forum-token-thread, forum-token-thread, doc-release-notes, forum-token-thread
- contradiction topics: none

### A forum says personal tokens last forever. What should I trust for version 4.2?

- retrieval hit@5: True
- rerank hit@5: True
- retrieval RR: 1.0
- rerank RR: 1.0
- contradiction ok: True
- preferred source top: True
- source diversity: 3
- source-id diversity: 3
- top retrieved: blog-4-2-migration, doc-release-notes, blog-4-2-migration, blog-4-2-migration, forum-token-thread
- top reranked: doc-release-notes, doc-release-notes, blog-4-2-migration, blog-4-2-migration, forum-token-thread
- contradiction topics: personal_token_expiry

### If SCIM removal is delayed, should I wait an hour or force sync from the identity settings?

- retrieval hit@5: True
- rerank hit@5: True
- retrieval RR: 1.0
- rerank RR: 1.0
- contradiction ok: True
- preferred source top: True
- source diversity: 2
- source-id diversity: 2
- top retrieved: doc-admin-guide, doc-admin-guide, doc-admin-guide, forum-scim-thread, forum-scim-thread
- top reranked: doc-admin-guide, doc-admin-guide, doc-admin-guide, forum-scim-thread, forum-scim-thread
- contradiction topics: scim_sync_delay
