---
title: "Choosing an embedding model: the questions that actually matter"
description: "Leaderboard rank is the least useful signal. Dimension count, context window, multilingual coverage, cost at your scale and the pain of ever changing your mind matter far more."
seoDescription: "How to choose an embedding model for retrieval: dimensions and storage cost, sequence length, multilingual support, symmetric vs asymmetric search, self-hosted vs API, and evaluating on your own data."
keywords:
  - choosing embedding model
  - embedding dimensions cost
  - multilingual embeddings retrieval
  - vector database dimension
  - mteb leaderboard limitations
  - rag embedding evaluation
category: "Analysis"
topic: "AI"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-09"
emoji: "🧭"
tags: ["AI", "Embeddings", "RAG", "Search", "Architecture"]
sources:
  - name: "MTEB leaderboard — Hugging Face"
    url: "https://huggingface.co/spaces/mteb/leaderboard"
  - name: "Sentence Transformers documentation"
    url: "https://www.sbert.net/"
  - name: "Embeddings — OpenAI API documentation"
    url: "https://platform.openai.com/docs/guides/embeddings"
  - name: "Embeddings — Anthropic documentation"
    url: "https://docs.anthropic.com/en/docs/build-with-claude/embeddings"
  - name: "pgvector — PostgreSQL vector extension"
    url: "https://github.com/pgvector/pgvector"
  - name: "FAISS — similarity search library"
    url: "https://faiss.ai/"
related:
  - slug: "ai-chunking-strategies-that-matter"
    title: "Chunking for retrieval: the decision that quietly caps your RAG quality"
  - slug: "ai-agent-tool-design"
    title: "Designing tools an AI agent can actually use"
draft: false
---

The usual process is: open a leaderboard, sort by average score, take the top model that fits the budget, move on. It produces a defensible choice roughly half the time, and the half where it fails, it fails expensively — because switching embedding models means re-embedding everything and rebuilding every index.

Here are the questions that predict the outcome better than rank does.

## Does it work on *your* text?

A benchmark average is a weighted mixture of tasks, most of which are not yours. A model that leads overall can trail badly on the one thing you need — legal clauses, product SKUs, Vietnamese customer support tickets, code.

The evaluation that matters takes an afternoon:

1. Collect 50-100 real queries from your logs (or write them, if you have no traffic yet).
2. For each, mark which documents in your corpus *should* be retrieved. This labelling is the actual work.
3. Embed the corpus with each candidate model, run the queries, measure recall@k for the k you actually feed to the model.

**Recall@k is the metric to optimise, not similarity score.** Your generator sees the top k chunks; if the right chunk is in there, ranking within k barely matters. If it is not, nothing downstream can recover.

Include queries that should return *nothing*. A model that returns confident nearest neighbours for out-of-scope questions will feed your generator irrelevant context, and that is where hallucinations come from in retrieval systems.

## Dimensions are a storage and latency decision

Dimension count is the parameter with the most direct engineering consequence.

| Dimensions | Storage per 1M chunks (float32) | Notes |
| --- | --- | --- |
| 384 | ~1.5 GB | Fast, cheap, adequate for many domains |
| 768 | ~3 GB | Common middle ground |
| 1536 | ~6 GB | Typical for large API models |
| 3072 | ~12 GB | Diminishing returns for most corpora |

Storage is the visible cost; index build time, memory during search, and per-query latency all scale similarly. And these are *before* replication and index overhead — an HNSW index adds substantially to the raw vector size.

Two mitigations worth knowing:

- **Quantisation.** Storing vectors as int8 cuts memory roughly fourfold with modest recall loss on most corpora. Binary quantisation goes further and is viable as a first-stage filter followed by exact rescoring of the top few hundred.
- **Truncation.** Some models are trained so that a prefix of the vector remains usable — you can store 512 of 1536 dimensions and keep most of the quality. Check whether your candidate supports this before assuming it.

My default: start at 768 or below, and only move up if your own recall measurement says the larger model earns it. It usually earns less than the leaderboard gap suggests.

## Sequence length, and the trap in it

Every embedding model has a maximum input length, and text beyond it is truncated — usually silently. A model with a 512-token limit given a 2,000-token chunk embeds the first quarter and discards the rest, which is exactly the failure that produces a retrieval system that "sometimes just misses things."

But a long context window is not the fix people assume. **A single vector for a 8,000-token document averages away everything specific about it.** Long chunks retrieve poorly for specific questions regardless of the model's stated limit, because the embedding is a summary of a summary.

So sequence length constrains chunking rather than replacing it: pick a chunk size that fits comfortably inside the limit with room to spare, and treat the limit as a ceiling you never approach.

## Symmetric or asymmetric?

Two different tasks get conflated:

- **Symmetric**: query and document are the same kind of text. "Find similar support tickets."
- **Asymmetric**: a short question retrieving long passages. Standard RAG.

Models are trained for one or the other, and many expect a **prefix** to tell them which side they are embedding — something like `query: …` versus `passage: …`. Omitting the prefix a model was trained with degrades retrieval measurably, and it is a silent failure: everything runs, results are just worse.

If you take one operational detail from this article, take that one. Read the model card for required prefixes, and apply them consistently at index time and query time.

## Multilingual, and Vietnamese in particular

If your corpus or your users are not exclusively English, the general leaderboard is close to useless as a signal. Multilingual models trade some English quality for cross-language capability, and their quality per language varies enormously with how much of that language was in training.

Questions to answer explicitly:

- Do queries in one language need to retrieve documents in another? That is cross-lingual retrieval, a harder requirement than merely handling multiple languages.
- Does the tokenizer handle your language efficiently? A model that spends three tokens per Vietnamese syllable both costs more and effectively has a shorter context.
- Are diacritics handled? Users type without them constantly. Test `"thanh toan"` retrieving documents containing "thanh toán" — if it fails, you need normalisation or a hybrid lexical fallback, no matter which model you choose.

## API or self-hosted

| | API model | Self-hosted |
| --- | --- | --- |
| Setup | Minutes | GPU or a slow CPU path |
| Cost shape | Per token, forever | Fixed infrastructure |
| Bulk re-embedding | Can be genuinely expensive | Only time |
| Data residency | Leaves your infrastructure | Stays put |
| Version stability | Provider may deprecate | Frozen until you move |

The line I use: **if you re-embed your corpus more than occasionally, self-host.** Re-embedding is not rare — it happens whenever you change chunking strategy, which you will, twice, in the first few months.

The version-stability row deserves emphasis. An API embedding model that is deprecated forces a full re-index on the provider's schedule rather than yours. Ask what the deprecation policy is before you build on one.

## Plan for changing your mind

Whatever you pick will be wrong eventually. Cheap insurance:

- **Store the source text alongside the vector**, always. Re-embedding from your own store beats re-fetching from origin systems.
- **Record the model name and version in every row.** Mixed-model indexes produce nonsense similarity scores, and without this column you will not know it is happening.
- **Keep the embedding call behind one interface** so swapping the provider is a single file.
- **Support dual-write during migration**: index into a new column, evaluate, cut over, drop the old. This makes a model change a routine deployment rather than an outage.

## FAQ

**Should I fine-tune an embedding model?**

Only after chunking and hybrid search are exhausted. Fine-tuning needs labelled pairs and re-embedding on every update; it pays off mainly for genuinely specialised vocabulary.

**Is a hybrid of keyword and vector search worth it?**

Usually yes, and it is the highest-value addition after a reasonable model choice. Vectors miss exact identifiers — product codes, error numbers, names — that lexical search finds trivially.

**How do I compare models fairly?**

Same chunks, same queries, same k, same prefixes. Change one variable at a time, and be suspicious of a large jump — it is often a prefix or truncation difference, not model quality.

**Do embeddings expire?**

The vectors do not, but your content does. Re-embed changed documents; there is no benefit to re-embedding unchanged ones with the same model.

**Can I mix models in one index?**

No. Vectors from different models are not comparable, even at the same dimension count.

---

*Model characteristics such as dimension counts, sequence limits, prefix requirements and quantisation support vary by model and are documented on each model's card and in the references linked above — verify them for the specific model you choose rather than relying on the ranges here. The evaluation procedure, the dimension recommendation, the API-versus-self-hosted line and the migration checklist are my own judgement from building retrieval systems.*
