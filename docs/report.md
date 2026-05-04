# Report: Multi-Source RAG for Technical Support

## System overview

This project implements a multi-source RAG system for a fictional product called `NimbusFlow`. The goal is to answer support questions by retrieving from three distinct source families:

- official product documentation
- community/customer forum threads
- technical blog posts

The system is intentionally self-contained at the code level, and uses the OpenAI API for semantic retrieval and answer synthesis only when `OPENAI_API_KEY` is configured. If the key is absent or an API call fails, the app falls back to a local lexical path so the UI and evaluation harness remain usable. The included corpus and benchmark are small and fictional, so the metrics are best read as regression checks for this assignment rather than production evidence.

## Requirement-by-requirement approach

### 1. Three different types of data

The corpus is stored under [data](/Users/akshatboudh/Desktop/assignment/data) and indexed through [data/manifest.json](/Users/akshatboudh/Desktop/assignment/data/manifest.json).

- Documentation is stored as Markdown guides and release notes.
- Forums are stored as structured JSON threads with customer posts, accepted answers, and support replies.
- Blogs are stored as Markdown articles that preserve narrative context and version history.

### 2. Source-specific chunking strategy

Chunking is implemented in [src/chunkers.py](/Users/akshatboudh/Desktop/assignment/src/chunkers.py).

- Documentation is chunked by `##` sections and `###` subsections because support answers often align with official settings pages, limits, or workflows.
- Forums are chunked per post, while each chunk also includes the original customer question. Accepted answers are marked and later boosted during reranking.
- Blogs are chunked with overlapping paragraph windows within each heading. This keeps explanatory context while avoiding very large narrative chunks.

### 3. Retrieval that weighs and combines multiple sources

Retrieval is implemented in [src/rag_engine.py](/Users/akshatboudh/Desktop/assignment/src/rag_engine.py).

When embeddings are configured, the pipeline uses:

- OpenAI embeddings with `text-embedding-3-small`
- cosine similarity over normalized embedding vectors for semantic retrieval
- a local lexical score based on TF-IDF as a secondary relevance signal
- source priors:
  - documentation highest
  - forums slightly lower
  - blogs slightly lower again
- query-aware source multipliers so issue-focused queries can pull in forums while policy/configuration queries lean toward documentation
- a per-source cap during initial retrieval to prevent one corpus from dominating the result set too early

When embeddings are unavailable, the same retrieval interface falls back to local lexical scoring and keeps the source-prior and diversity logic.

### 4. Reranking mechanism

Reranking uses a deterministic weighted formula over the retrieved candidates:

- hybrid retrieval score
- semantic similarity
- lexical similarity
- lexical overlap with the query
- source authority
- recency score
- accepted-answer boost for forums
- support-engineer role boost for relevant forum posts

This produces a final `rerank_score` that favors newer and more authoritative evidence while still respecting lexical relevance.

### 5. Contradiction handling

Each source in the manifest carries structured claims such as:

- `personal_token_expiry`
- `restore_rpo`
- `scim_sync_delay`

After reranking, the engine inspects the claims attached to the top chunks:

- if multiple values appear for the same topic, the system flags a contradiction
- it then picks a preferred claim using source authority, recency, and confidence
- the answer explicitly reports that disagreement instead of hiding it

This is important for technical support because older forum threads can be correct for earlier versions but wrong for the current product behavior.

### 6. Logging of source usage

Every response writes a structured JSONL record to [logs/query_logs.jsonl](/Users/akshatboudh/Desktop/assignment/logs/query_logs.jsonl).

Each record includes:

- the query
- runtime mode and active models
- source usage counts by source type
- top retrieved chunks with retrieval and rerank scores
- any contradictions detected

The web UI also exposes recent logs through `/api/logs`.

## Retrieval and reranking analysis

The evaluation harness is implemented in [scripts/evaluate.py](/Users/akshatboudh/Desktop/assignment/scripts/evaluate.py) using [data/evaluation_queries.json](/Users/akshatboudh/Desktop/assignment/data/evaluation_queries.json).

The evaluation compares a small seeded set of support questions, including a few adversarial version-conflict prompts:

- weighted retrieval before reranking
- reranking after feature boosts
- exact contradiction topic matching, including rejection of unexpected extra topics
- source diversity in the final top 5
- whether the expected preferred source reaches the top reranked slot under the stricter preferred-source gate

Thresholds in the script make regressions visible, but passing them does not imply broad coverage beyond the seeded NimbusFlow corpus.

Generated metrics are written to:

- [outputs/performance_analysis.md](/Users/akshatboudh/Desktop/assignment/outputs/performance_analysis.md)
- [outputs/performance_metrics.json](/Users/akshatboudh/Desktop/assignment/outputs/performance_metrics.json)

## Example queries and responses

Ten seeded support questions are stored in [outputs/example_queries.json](/Users/akshatboudh/Desktop/assignment/outputs/example_queries.json) and expanded into generated outputs by [scripts/generate_examples.py](/Users/akshatboudh/Desktop/assignment/scripts/generate_examples.py).

Generated outputs are written to:

- [outputs/example_queries.md](/Users/akshatboudh/Desktop/assignment/outputs/example_queries.md)
- [outputs/example_queries_results.json](/Users/akshatboudh/Desktop/assignment/outputs/example_queries_results.json)

## Limitations and next steps

- The answer synthesis stage depends on the OpenAI API when enabled, so offline use falls back to a deterministic synthesizer.
- Contradiction handling relies on structured claims in the manifest; a production system would likely learn or extract claims automatically.
- Retrieval quality now depends on embedding availability; if the API is unavailable, the system degrades to lexical-only retrieval.
