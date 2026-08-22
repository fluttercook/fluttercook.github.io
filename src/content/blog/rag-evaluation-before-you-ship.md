---
title: "Retrieval that doesn't lie: build the eval before you build the RAG"
description: "Most RAG failures are retrieval failures wearing a generation costume. Here is how to separate the two with a 50-question golden set, recall@k and MRR, and a regression harness that runs in CI."
seoDescription: "A practical RAG eval guide: hand-label a golden set, measure retrieval with recall@k and MRR, then test generation against perfect retrieval."
keywords:
  - rag evaluation
  - recall at k retrieval metric
  - mean reciprocal rank explained
  - rag golden dataset
  - chunking strategy evaluation
  - hybrid search and reranking
category: "Guide"
topic: "AI Engineering"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-22"
emoji: "🎯"
tags: ["AI", "RAG", "Evaluation", "Python", "Search"]
sources:
  - name: "BEIR — heterogeneous benchmark for zero-shot information retrieval"
    url: "https://github.com/beir-cellar/beir"
  - name: "MTEB — Massive Text Embedding Benchmark"
    url: "https://github.com/embeddings-benchmark/mteb"
  - name: "Ragas — evaluation toolkit for retrieval-augmented generation"
    url: "https://github.com/explodinggradients/ragas"
  - name: "rank-bm25 — BM25 implementations in Python"
    url: "https://pypi.org/project/rank-bm25/"
  - name: "Sentence Transformers — embedding and cross-encoder models"
    url: "https://github.com/UKPLab/sentence-transformers"
  - name: "pytest documentation"
    url: "https://docs.pytest.org/"
related:
  - slug: "cutting-ai-costs-free-tiers-caching-and-routing"
    title: "Using AI without burning cash: free tiers, caching, and routing"
  - slug: "what-the-research-says-about-prompt-engineering"
    title: "What the research actually says about prompt engineering — five claims, fact-checked"
draft: false
---

The bug report always looks the same. "The assistant made something up about our refund window." Someone opens the trace, sees a confident wrong paragraph, and files it against the model. The prompt gets another paragraph of instructions. Maybe the temperature comes down. Maybe someone proposes swapping models.

Then you look one layer up and find the retriever handed the model three chunks: the shipping policy, the terms-of-service preamble, and a chunk that ends mid-sentence right before the refund window is stated. The model did not hallucinate so much as improvise over a hole. No prompt fixes that. No model upgrade fixes that either — a better model given the same three chunks will produce a *more convincing* wrong paragraph.

This is the most common shape of RAG failure, and you cannot see it from the output. The generation is the only part you read, so the generation is the part you blame. The fix is a measurement that separates the two halves, built *before* you tune anything — otherwise every change you make is a coin flip you cannot score. What follows is the smallest version of that measurement I would still call honest: a hand-labelled golden set, two retrieval metrics you can compute with arithmetic, a generation test that assumes perfect retrieval, and a CI gate so nobody silently regresses it.

## A RAG system is two systems, and only one of them is usually broken

Split the pipeline at the boundary where the context is assembled:

1. **Retrieval.** Question in, an ordered list of chunk IDs out. Success means the chunk containing the answer is somewhere in the top *k* you pass to the model.
2. **Generation.** Question plus chunks in, answer out. Success means the answer is grounded in those chunks and actually addresses the question.

Now the diagnostic. For each failing question, ask two things:

- Was the answer-bearing chunk in the retrieved context? If no, it is a retrieval bug. Nothing you do to the prompt matters.
- If yes, and the answer was still wrong, it is a generation bug — the model had the material and mangled it.

That is the whole idea. Everything below is machinery for answering those two questions repeatedly and cheaply — answering them by hand for one bug report is easy, and answering them for fifty questions after every chunking change is not.

## Fifty questions you labelled yourself beat five thousand you generated

The golden set is a list of question → expected-source pairs. The expected source is a **chunk ID**, not an answer string. You are recording *where the answer lives*, which is a fact about your corpus and stays stable even as the model changes.

Where the questions come from matters more than how many there are. Best: real questions from your logs, support tickets, or the Slack channel where people ask the thing your RAG is meant to replace. Next best: questions from whoever owns the domain — the support lead, the compliance person — phrased the way *they* hear them. Last resort: synthetic questions generated from your own documents.

Synthetic questions are seductive and mostly measure the wrong thing. A model reading chunk 47 and writing "what is the refund window?" produces a question whose vocabulary is already borrowed from chunk 47. Your embedding model will find it easily. Real users write "how long do I have to send it back" and never use the word *refund*. The vocabulary gap between the question and the document is the entire difficulty of retrieval, and generated questions are designed — accidentally, but reliably — to have no gap.

Fifty is enough to be useful. At fifty items, each question is worth two percentage points of the mean, so a difference of one or two questions is noise and you should not chase it — but a change that moves five or ten questions is real and visible. Fifty is also small enough that one person can label it in an afternoon, which is the second reason for the number.

Hand-labelling is not a chore you are grudgingly accepting; it is where most of the value is. Labelling forces you to open the corpus and find the chunk, and along the way you find things no metric reports: the answer split across two chunks, the same policy stated twice with different numbers, the authoritative version sitting in a PDF nobody indexed.

Keep the file boring — one JSON object per line, in the repo, in version control:

```jsonl
{"qid": "q001", "question": "how long do i have to send something back", "relevant_chunk_ids": ["policy-refunds#3"], "answer_must_mention": ["30 days"]}
{"qid": "q002", "question": "do i pay for return shipping", "relevant_chunk_ids": ["policy-refunds#5", "policy-shipping#2"], "answer_must_mention": ["prepaid label"]}
```

`relevant_chunk_ids` is a list because some answers genuinely need two chunks. `answer_must_mention` is a cheap grounding check for later — a string that must appear in any correct answer. Not every question has one; leave it empty rather than inventing one.

One durability note: chunk IDs must survive re-indexing. If they are array positions, every chunking change invalidates the whole set. Derive them from something stable — `{document_slug}#{ordinal}` — and store the document ID too, so you can fall back to document-level scoring when boundaries move.

## recall@k and MRR, in plain arithmetic

Two metrics carry most of the weight. Neither is complicated once you see the formula next to a worked example.

**recall@k** answers: *of the chunks that should have been found, what fraction appeared in the top k?* That is `|retrieved_top_k ∩ relevant| / |relevant|`. For most golden questions there is exactly one relevant chunk, so recall@k is 1 if the chunk is in the top k and 0 if it is not, and the mean over your set is simply the fraction of questions where retrieval succeeded. That is the number to put on a dashboard.

**MRR** — mean reciprocal rank — answers: *how high up was the first correct chunk?* For one question the reciprocal rank is `RR = 1 / rank_of_first_relevant`, or 0 if none was retrieved; MRR is the mean of RR across all questions.

Worked example. Question `q001` has one relevant chunk, `policy-refunds#3`. Retrieval returns, in order: `policy-shipping#1`, `policy-refunds#3`, `terms#7`, `policy-refunds#4`, `faq#2`. The relevant chunk is at rank 2, so recall@1 = 0/1 = **0.0**, recall@3 = recall@5 = 1/1 = **1.0**, and RR = 1/2 = **0.5**.

Now suppose the whole set is three questions with reciprocal ranks 1.0 (found at rank 1), 0.5 (rank 2), and 0.0 (never found). MRR = (1.0 + 0.5 + 0.0) / 3 = **0.5**.

You need both, because they answer different questions. recall@k tells you whether the answer is *in the box you hand the model*; MRR tells you where it sits in that box. A system can have excellent recall@10 and mediocre MRR — the right chunk is always found, but at rank 8, under seven distractors. That looks fine on a recall dashboard and still answers badly, because the model reads seven irrelevant chunks first. Rising MRR at constant recall is a real improvement even though the headline number did not move. Here is the calculation, with no dependencies:

```python
from statistics import mean


def recall_at_k(retrieved_ids: list[str], relevant_ids: list[str], k: int) -> float:
    """Fraction of relevant chunks that appear in the top k results."""
    if not relevant_ids:
        raise ValueError("golden item has no relevant chunks")
    hits = set(retrieved_ids[:k]) & set(relevant_ids)
    return len(hits) / len(relevant_ids)


def reciprocal_rank(retrieved_ids: list[str], relevant_ids: list[str]) -> float:
    """1 / rank of the first relevant chunk; 0.0 if none was retrieved."""
    relevant = set(relevant_ids)
    for rank, chunk_id in enumerate(retrieved_ids, start=1):
        if chunk_id in relevant:
            return 1.0 / rank
    return 0.0


def score_retrieval(results: list[tuple[list[str], list[str]]], ks=(1, 3, 5, 10)) -> dict:
    """results: list of (retrieved_ids, relevant_ids), one entry per question."""
    report = {f"recall@{k}": mean(recall_at_k(r, g, k) for r, g in results) for k in ks}
    report["mrr"] = mean(reciprocal_rank(r, g) for r, g in results)
    return report
```

Pick your reporting `k` to match the number of chunks you actually put in the prompt. Measuring recall@20 while shipping five chunks is measuring a system you do not run.

## Then measure generation with retrieval taken out of the equation

Once retrieval is scored, run the generation half twice over the same golden set:

- **Oracle mode.** Feed the model exactly the chunks listed in `relevant_chunk_ids`. Retrieval is perfect by construction. Whatever fails here is a genuine generation problem — prompt, formatting, refusal behaviour, the model losing an instruction.
- **Live mode.** Feed the model whatever your retriever actually returned.

The gap between the two scores is your retrieval tax. If oracle mode scores well and live mode does not, stop editing prompts — the work is in retrieval. If oracle mode is also weak, the model is not using material it was handed, and prompt work is justified. This is the one comparison that reliably tells you which half to spend the week on.

```python
from dataclasses import dataclass


@dataclass
class GoldenItem:
    qid: str
    question: str
    relevant_chunk_ids: list[str]
    answer_must_mention: list[str]


def grade(answer: str, item: GoldenItem) -> bool:
    """Cheap deterministic grading. Escalate to a judge only when this can't decide."""
    if item.answer_must_mention:
        return all(s.lower() in answer.lower() for s in item.answer_must_mention)
    return judge(item.question, answer)  # LLM-as-judge, or a human review queue


def run_eval(golden: list[GoldenItem], retrieve, generate, get_chunks, k: int = 5) -> dict:
    retrieval_pairs, live_correct, oracle_correct = [], [], []

    for item in golden:
        retrieved_ids = retrieve(item.question, k=k)
        retrieval_pairs.append((retrieved_ids, item.relevant_chunk_ids))
        live = generate(item.question, get_chunks(retrieved_ids))
        live_correct.append(grade(live, item))
        oracle = generate(item.question, get_chunks(item.relevant_chunk_ids))
        oracle_correct.append(grade(oracle, item))

    report = score_retrieval(retrieval_pairs, ks=(1, k))
    report["answer_accuracy_live"] = mean(live_correct)
    report["answer_accuracy_oracle"] = mean(oracle_correct)
    report["retrieval_tax"] = report["answer_accuracy_oracle"] - report["answer_accuracy_live"]
    return report
```

`retrieve`, `generate`, and `get_chunks` are yours — the harness does not care which vector store or model provider sits behind them, and keeping that boundary clean is what lets you swap either one and compare. Note that `grade` prefers a deterministic string check and only falls back to a judge. Judges are useful, and they are also a second model with its own failure modes; every question you can grade with a substring is one whose score you can trust without a meta-evaluation.

## Chunking is an experiment variable, not a config you set once

Chunk size is usually chosen in the first hour of the project, from a tutorial, and never revisited. It is one of the highest-leverage variables in the system, and it interacts with everything — which is exactly why you cannot reason it out and have to measure it.

The tension is simple. Small chunks embed precisely (one topic, one vector) but truncate context, so the model gets a fragment that names the policy without stating it. Large chunks carry context but embed mushily — one vector averaging six topics matches everything weakly and nothing strongly. Where the optimum sits depends on your documents.

With the harness above, a sweep is a loop:

| Variable | Why it moves the numbers | What to watch |
| --- | --- | --- |
| Chunk size | Precision of the embedding vs. completeness of the passage | recall@k rising while answer accuracy falls means chunks are too small |
| Overlap | Answers that straddle a boundary get a whole copy in one chunk | Recall improves, index size and cost grow |
| Split boundary | Splitting on headings/paragraphs keeps semantic units intact | Compare against fixed-token splitting on the same set |
| Header injection | Prefixing each chunk with its document and section titles gives the embedding topical anchoring | Often helps most on short, ambiguous chunks |
| Embedding model | Different training data, different vocabulary gaps | Re-run the whole sweep; the best chunk size can move with the model |

Run each configuration over the same fifty questions and keep the reports in a table. Re-embedding the corpus per configuration costs real money and time, so sweep coarsely first — three sizes, not ten — and refine around the winner. And do not trust a chunking win that shows up in retrieval metrics but not in answer accuracy: that usually means you optimised for finding chunks rather than for answering questions.

## Hybrid search and reranking, and when each is worth the latency

When recall is the problem, two techniques help in different ways and cost differently.

**Hybrid search** runs a lexical retriever (BM25) alongside the vector retriever and merges the two ranked lists. It exists because embeddings are bad at exact tokens: part numbers, error codes, product names, acronyms, anything with no useful semantic neighbourhood. If a user searches `ERR_4021` and your corpus contains `ERR_4021` verbatim, BM25 finds it and a semantic model may not. Merging is usually done with reciprocal rank fusion, which combines by rank position rather than by score and therefore does not require the two systems' scores to be comparable — a genuine practical advantage, since they are not.

The cost is a second index to build and keep in sync. Both retrievers run in parallel, so wall-clock latency rises by roughly the slower of the two rather than the sum.

**Reranking** takes the top *n* from your first-stage retriever — say 50 — and rescores them with a cross-encoder, a model that reads the question and the chunk *together* rather than embedding them separately. That joint reading is why it is more accurate, and also why it is slower: you cannot precompute anything, so it is *n* model passes per query.

| | Hybrid search | Reranking |
| --- | --- | --- |
| Fixes | Missed exact tokens, rare terms, IDs | Right chunk retrieved but ranked low |
| Shows up as | Low recall@k, RR = 0 on specific queries | Decent recall@10, poor recall@3 and MRR |
| Cost | One extra index; parallel query | n scoring passes per query, serial after retrieval |
| Latency shape | Roughly the slower retriever | Grows with n; the main tuning knob |
| Try it when | Your corpus has codes, names, or jargon | Your golden set shows the answer sitting at rank 5-15 |

Read the decision straight off the golden set. If reciprocal rank is 0 for a cluster of questions — the chunk was never retrieved at all — reranking cannot help, because it only reorders what the first stage already found; you need hybrid search or a better embedding. If the chunk is consistently retrieved but sits at rank 8, reranking is exactly the tool.

Measure the latency on your own hardware and corpus rather than trusting a figure from a blog post — including this one. Published numbers come from someone else's chunk lengths, batch sizes, and hardware.

## Wire it to CI so a chunking change cannot pass silently

An eval you run when you remember is an eval that quietly stops running. Store a baseline of the current numbers in the repo, and on every pull request that touches the retrieval path — chunker, embedding config, index settings, retrieval parameters — run the golden set and fail the build if any metric drops more than a fixed tolerance below baseline:

```python
import json
import pytest

BASELINE = json.load(open("evals/baseline.json"))
TOLERANCE = 0.05  # absolute; below this, n=50 can't tell signal from noise


@pytest.mark.parametrize("metric", ["recall@5", "mrr", "answer_accuracy_live"])
def test_no_regression(report, metric):
    got, want = report[metric], BASELINE[metric]
    assert got >= want - TOLERANCE, f"{metric} regressed: {got:.3f} < {want:.3f} - {TOLERANCE}"
```

Three things make this work in practice.

**Set the tolerance from the size of your set, not from optimism.** With fifty questions one question is two points, so a tolerance below about five points fails on noise, you start re-running the job until it passes, and the gate becomes decorative. If you want a tighter tolerance, the answer is more labelled questions, not a smaller number.

**Ratchet the baseline forward.** When a change genuinely improves a metric, update `baseline.json` in the same pull request. The baseline should only move up, and the diff on that file becomes a readable history of what actually helped.

**Keep the model call out of the fast path.** Retrieval metrics need no LLM — they are set operations over IDs, run in seconds, and can gate every PR. Generation metrics cost tokens and time; run those nightly or behind a label. That split is what makes the suite sustainable, and sustainability is the only property that matters for a regression gate.

## FAQ

**Fifty questions really is enough?**

It is enough to catch the failures that matter and to make chunking decisions with a straight face. It is not enough to distinguish two close configurations — at n=50 a two-point difference is one question. Treat fifty as the point where the eval starts paying for itself, and grow it by adding every question that ever produced a bad answer in production. That habit alone will get you to two hundred well-chosen questions in a few months, which is a far better set than two hundred generated ones on day one.

**Can I generate the golden set with an LLM to save time?**

You can generate *candidate* questions and then rewrite and verify them by hand, which saves some typing. What you cannot skip is looking at the corpus to assign the chunk IDs, because that is the step that surfaces the document problems. Generated questions also tend to share vocabulary with the source chunk, which inflates your retrieval scores and hides exactly the vocabulary gap the eval exists to measure.

**What about the metrics in Ragas and similar toolkits — faithfulness, answer relevancy?**

They are useful, and they mostly measure the generation half. Add them once retrieval is under control; they are the wrong place to start, because a faithfulness score computed over the wrong chunks is a precise measurement of an irrelevant thing. Note also that most of those metrics are themselves model calls, so they cost tokens and carry their own variance — pin the judge model and version if you are going to trend the numbers over time.

**Is this worth it for a small internal tool with twenty documents?**

The golden set is, and it might be twenty questions rather than fifty. Skip the CI harness until something changes often enough to break. The part you should not skip at any size is the oracle-mode comparison, because it is the difference between fixing your system and rewriting your prompt for a week over a retrieval bug.

---

*The metric definitions, formulas, and worked examples here are standard information retrieval and are stated as fact; the recommendations — fifty questions, five-point tolerance, retrieval in CI and generation nightly — are my working defaults, not measured optima, and your corpus may argue with them. Every latency claim is described as a mechanism rather than a number on purpose: measure it on your own data. Library APIs and model behaviour change, so verify anything version-dependent against the current documentation before relying on it.*
