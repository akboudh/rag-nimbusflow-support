# Multi-Source RAG for Technical Support

This project implements a multi-source RAG system for a fictional product called `NimbusFlow`, a developer operations platform with desktop sync, SSO, APIs, backups, and audit tooling.

The system retrieves from three distinct knowledge sources:

- product documentation
- customer forums
- technical blog posts

It includes:

- source-specific chunking
- hybrid retrieval across documentation, forums, and blogs
- OpenAI embeddings and OpenAI answer generation when configured
- deterministic reranking
- contradiction detection and source preference handling
- per-response source logging
- an interactive local web UI
- a small seeded evaluation script and seeded example queries

## Quick start

Configure the OpenAI API:

```bash
cp .env.example .env
```

Add your key to `.env`, then run the local app:

```bash
python3 server.py
```

Open:

```text
http://127.0.0.1:8000
```

Generate the seeded example query report:

```bash
python3 scripts/generate_examples.py
```

Run the evaluation suite:

```bash
python3 scripts/evaluate.py
```

## Project structure

- [server.py](/Users/akshatboudh/Desktop/assignment/server.py)
- [src/rag_engine.py](/Users/akshatboudh/Desktop/assignment/src/rag_engine.py)
- [src/source_loader.py](/Users/akshatboudh/Desktop/assignment/src/source_loader.py)
- [src/chunkers.py](/Users/akshatboudh/Desktop/assignment/src/chunkers.py)
- [src/logging_utils.py](/Users/akshatboudh/Desktop/assignment/src/logging_utils.py)
- [data/manifest.json](/Users/akshatboudh/Desktop/assignment/data/manifest.json)
- [docs/report.md](/Users/akshatboudh/Desktop/assignment/docs/report.md)
- [outputs/example_queries.md](/Users/akshatboudh/Desktop/assignment/outputs/example_queries.md)
- [outputs/performance_analysis.md](/Users/akshatboudh/Desktop/assignment/outputs/performance_analysis.md)

## Notes

- The system is intentionally self-contained and uses only the Python standard library.
- The default OpenAI models are `text-embedding-3-small` for retrieval embeddings and `gpt-5-mini` for answer generation.
- Retrieval uses hybrid scoring: semantic similarity from OpenAI embeddings plus local lexical scoring and source-aware weighting. Without an API key, it uses the lexical path only.
- Contradictions are surfaced when retrieved chunks carry conflicting structured claims for the same topic.
- Evaluation metrics are for the included fictional corpus and should be treated as regression checks, not broad production-quality benchmarks.
- If `OPENAI_API_KEY` is not configured or an API request fails, the app falls back to lexical retrieval and deterministic answer synthesis so the local demo still runs.
