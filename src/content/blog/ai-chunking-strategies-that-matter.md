---
title: "Chunking for retrieval: the decision that quietly caps your RAG quality"
description: "Chunk size is not a tuning knob you turn until the numbers look good. It encodes an assumption about what a question is, and every downstream problem in your RAG system traces back to it."
seoDescription: "Practical chunking strategies for RAG: fixed-size vs structural splitting, overlap, metadata and context prefixing, parent-document retrieval, tables and code, and how to measure whether a change helped."
keywords:
  - rag chunking strategy
  - chunk size overlap retrieval
  - semantic chunking documents
  - parent document retrieval
  - markdown header splitting
  - rag context window chunks
category: "Analysis"
topic: "AI"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-08"
emoji: "✂️"
tags: ["AI", "RAG", "Retrieval", "Embeddings", "Architecture"]
sources:
  - name: "Text splitters — LangChain documentation"
    url: "https://python.langchain.com/docs/concepts/text_splitters/"
  - name: "Node parsers and text splitters — LlamaIndex documentation"
    url: "https://docs.llamaindex.ai/en/stable/module_guides/loading/node_parsers/"
  - name: "Contextual retrieval — Anthropic engineering"
    url: "https://www.anthropic.com/news/contextual-retrieval"
  - name: "Sentence Transformers documentation"
    url: "https://www.sbert.net/"
  - name: "tiktoken — token counting library"
    url: "https://github.com/openai/tiktoken"
  - name: "pgvector — PostgreSQL vector extension"
    url: "https://github.com/pgvector/pgvector"
related:
  - slug: "ai-embeddings-choosing-a-model"
    title: "Choosing an embedding model: the questions that actually matter"
  - slug: "ai-observability-tracing-llm-apps"
    title: "Observability for LLM apps: tracing a non-deterministic system"
draft: false
---

A retrieval system that answers "what is our refund window?" correctly and fails on "does the refund window differ for enterprise customers?" usually does not have a model problem. It has a chunk that contains the general policy and a different chunk, retrieved never, that contains the exception.

Chunking decides what a single retrievable unit *is*. Get it wrong and no amount of reranking, prompt engineering or model upgrading recovers the information you split apart.

## Fixed-size splitting is a baseline, not a strategy

The default everyone starts with — split every N characters with M overlap — is worth understanding precisely, because it is the thing you will be comparing against.

```python
def fixed_chunks(text, size=1000, overlap=200):
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks
```

What it gets right: uniform chunks, predictable cost, no assumptions about document format.

What it gets wrong: it cuts through sentences, tables, code blocks and — worst — through the relationship between a heading and the text under it. A chunk beginning mid-sentence with no indication of which section it came from is a chunk that embeds poorly and reads badly when the generator sees it.

Two immediate improvements, both cheap:

- **Split on structure first, size second.** Break on headings, then paragraphs, then sentences, and only fall back to character counts when a unit exceeds your budget. Most splitter libraries call this recursive splitting and it should be your floor, not your ceiling.
- **Measure in tokens, not characters.** A 1,000-character limit is roughly 250 English tokens and considerably fewer for Vietnamese or for code. If you size in characters you are sizing in a unit neither the embedder nor the generator uses.

## Overlap buys less than people think

Overlap exists to stop an answer being severed at a boundary. It works, but it is a blunt instrument: 200 tokens of overlap on 1,000-token chunks means 20% more vectors, 20% more storage, 20% more search cost, and near-duplicate results crowding your top k.

I use 10-15% overlap for prose and **zero** for structurally split content, where the boundaries are already meaningful. If overlap is doing a lot of work in your system, that is evidence your splitting is cutting in the wrong places, and the fix is better boundaries rather than more redundancy.

## The single highest-value change: give each chunk its context

An isolated chunk loses everything the surrounding document established. "This applies only to accounts created before the migration" means nothing without knowing what "this" is.

The fix is to prepend context to the text you embed:

```python
def contextualise(chunk, doc_title, section_path, doc_date):
    header = f"Document: {doc_title}\nSection: {' > '.join(section_path)}\nUpdated: {doc_date}\n\n"
    return header + chunk
```

That header is embedded along with the chunk, so a query mentioning the product name or the section topic now matches chunks that never spell it out. In my experience **this is the largest single-change improvement available in most RAG systems**, and it costs one string concatenation at index time.

A more thorough version generates a one-sentence summary of how each chunk fits into its document and prepends that. It costs a model call per chunk at index time, which is real money on a large corpus, but it addresses cases a static header cannot — implicit references, pronouns, continuation from a previous section.

Either way, keep the raw chunk separately from the embedded text, so the generator receives clean content rather than your header boilerplate.

## Small chunks retrieve, large chunks answer

These two goals conflict directly. Small chunks embed precisely and match specific questions; large chunks give the generator enough surrounding material to actually answer.

**Parent-document retrieval** resolves the conflict: index small, return large.

```python
# Index: split into ~200-token children, each pointing at its parent
for parent in documents:
    for child in split(parent, size=200):
        index.add(embed(contextualise(child)), metadata={"parent_id": parent.id})

# Query: search children, deduplicate, fetch parents
hits = index.search(embed(query), k=10)
parent_ids = dict.fromkeys(h.metadata["parent_id"] for h in hits)  # ordered, unique
context = [store.get(pid) for pid in list(parent_ids)[:3]]
```

The deduplication matters: several children of one parent will often match, and without it your three "results" are one document three times.

A related, cheaper trick: retrieve small chunks and expand each to include its immediate neighbours before passing to the generator. Less precise than true parent-document retrieval, but it needs no second store.

## Content that does not chunk

Some content breaks every generic splitter:

- **Tables.** Split a table and the rows lose their headers. Keep tables whole where they fit, and where they do not, repeat the header row in each piece and add a caption describing the table's subject.
- **Code.** Split by function or class, never by line count. A fragment of a function body is close to useless in retrieval.
- **Conversations and tickets.** Split by turn boundaries, and keep the resolution attached to the problem statement — a chunk containing only the complaint retrieves for the right queries and answers none of them.
- **Long reference lists and glossaries.** Each entry is its own chunk. These are the one case where very small chunks are exactly right.
- **PDFs with columns or scanned pages.** Fix the extraction before you think about chunking; text in the wrong reading order cannot be rescued by a splitter.

## Measuring whether a change helped

Chunking changes are easy to make and easy to fool yourself about. The discipline:

1. Keep a fixed evaluation set of queries with known-correct source documents.
2. Change **one** thing.
3. Measure recall@k on the same set, with the same embedding model and the same k.
4. Read the ten worst failures individually. Aggregate metrics tell you whether it moved; only reading failures tells you why.

Re-chunking means re-embedding, so build the pipeline assuming you will do it repeatedly: keep source text in your own store, version the chunking configuration alongside the vectors, and make a full rebuild a single command. A team that cannot cheaply re-chunk stops experimenting, and stops improving.

## FAQ

**What chunk size should I start with?**

Roughly 200-400 tokens for children in a parent-document setup, or 500-800 tokens for a flat index. Then measure — the right answer depends on your documents and your questions, not on a general recommendation.

**Is semantic chunking — splitting where embedding similarity drops — worth it?**

Sometimes, for unstructured prose with no headings. For documents with real structure, structural splitting is cheaper and usually better.

**Should chunk metadata be embedded or stored separately?**

Both. Embed the context header so it influences matching; store structured fields separately so you can filter on them before the vector search.

**How do I handle documents that change?**

Chunk deterministically so unchanged sections produce identical chunk IDs, then re-embed only what moved. Content-hashing each chunk makes this straightforward.

**Does a long-context model remove the need for chunking?**

No. You still have to choose what goes in the window, and retrieval quality — not window size — is what decides whether the right passage is there.

---

*Splitter behaviour, recursive and structural splitting, and contextual-retrieval techniques are described in the framework and engineering references linked above. The overlap percentages, the parent-document sizing, the content-type guidance and the measurement discipline are my own judgement from building retrieval systems; the right numbers for your corpus can only come from measuring on it.*
