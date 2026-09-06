---
title: "Synthetic data for evals: building a test set you can trust"
description: "Generating test cases with a model is fast, cheap and quietly circular. Done carefully it gives you an evaluation suite before you have traffic; done carelessly it certifies your system against its own assumptions."
seoDescription: "How to build LLM evaluation sets with synthetic data: seeding from real artefacts, generating hard negatives and edge cases, avoiding self-confirmation bias, human validation, and knowing what synthetic data cannot cover."
keywords:
  - synthetic data llm evaluation
  - llm eval set generation
  - rag evaluation dataset
  - llm as judge validation
  - test cases for ai features
  - eval golden dataset
category: "Guide"
topic: "AI"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-04"
emoji: "🧪"
tags: ["AI", "Evaluation", "Testing", "LLM", "Quality"]
sources:
  - name: "Building effective agents — Anthropic engineering"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
  - name: "Evaluating model performance — Anthropic documentation"
    url: "https://docs.anthropic.com/en/docs/test-and-evaluate/develop-tests"
  - name: "Evals — OpenAI documentation"
    url: "https://platform.openai.com/docs/guides/evals"
  - name: "Ragas — RAG evaluation framework"
    url: "https://docs.ragas.io/"
  - name: "Cohen's kappa — inter-rater reliability"
    url: "https://en.wikipedia.org/wiki/Cohen%27s_kappa"
  - name: "JSON Schema specification"
    url: "https://json-schema.org/"
related:
  - slug: "ai-observability-tracing-llm-apps"
    title: "Observability for LLM apps: tracing a non-deterministic system"
  - slug: "ai-model-routing-cascades"
    title: "Model routing and cascades: paying for the intelligence you need"
draft: false
---

You have a RAG system, no users yet, and a prompt you keep changing. Every change feels like an improvement and you have no way to tell. Writing a hundred test questions by hand takes two days and you will not do it.

So you ask a model to generate them. This works, and it is worth doing, and it has one failure mode that invalidates the whole exercise if you do not design around it.

## The circularity problem

If you generate questions by showing a model your documents, you get questions your documents answer well, phrased the way your documents phrase things. Your retrieval then scores beautifully — on a test set constructed from the same assumptions as the system under test.

Real users ask about things your documents cover badly, in words your documents never use, with false premises baked in. **A synthetic eval set built naively measures internal consistency, not usefulness.** It will pass while your users fail.

Everything below is about breaking that circle.

## Seed from real artefacts, not from imagination

The strongest synthetic data is grounded in something real. In descending order of value:

1. **Real user queries**, even from a different product or a search log. These carry actual phrasing, real typos, real assumptions.
2. **Support tickets, sales-call notes, community forum posts.** These are questions people actually asked, in their own words.
3. **Your documentation's own gaps** — the sections that are thin, contradictory, or out of date. Generate questions targeting those deliberately.
4. **Model-invented questions from your documents.** Useful for coverage, weakest for realism, and this is where most people start and stop.

A practical generator prompt is more specific than "write questions about this document":

```
Here is a support conversation between a customer and an agent.

Write 5 questions a *different* customer might ask that relate to the same
underlying problem, but:
- Use different vocabulary than the conversation does
- Include one question based on a mistaken assumption
- Include one that this documentation does NOT answer
- Vary the length: one very terse, one rambling with irrelevant detail

Return JSON: [{"question": ..., "expected_behaviour": ..., "category": ...}]
```

The instructions to vary vocabulary and to include unanswerable questions are the parts that break circularity. Without them you get five paraphrases of the document's own headings.

## Generate the hard cases explicitly

A test set of reasonable questions tells you almost nothing, because reasonable questions mostly work. Budget most of your generation effort on categories where systems actually fail:

| Category | Example | What it tests |
| --- | --- | --- |
| Unanswerable | "What's your policy on X?" where there is none | Does it say "I don't know" or invent? |
| False premise | "Why does your app charge a setup fee?" when it doesn't | Does it correct the premise or play along? |
| Multi-hop | "Is the enterprise refund window longer than standard?" | Does it retrieve two facts and compare? |
| Near-miss vocabulary | "cancel" when docs say "terminate" | Retrieval robustness |
| Ambiguous | "How much does it cost?" with three products | Does it ask, or guess? |
| Adversarial | Instructions embedded in the question | Guardrail behaviour |
| Temporal | "What changed last month?" | Handling of dates and staleness |
| Out of scope | Medical or legal advice | Refusal behaviour |
| Multilingual | The same question in Vietnamese and English | Cross-language parity |

**If your eval set has no unanswerable questions, your success rate is meaningless**, because a system that answers everything confidently scores 100% and is dangerous.

## Human validation is the step that makes it real

Generated cases include wrong expected answers, ambiguous questions and duplicates. Reviewing all of them defeats the purpose; reviewing none of them means you are optimising against noise.

The compromise that has worked for me:

1. Generate 3-5x more cases than you need.
2. Deduplicate by embedding similarity — synthetic generation repeats itself heavily.
3. Have a person review a **stratified sample**: every case in the high-risk categories, plus 10-20% of the routine ones.
4. Track the rejection rate per category. A category rejected 40% of the time has a broken generator prompt, and fixing that is more valuable than reviewing more cases.
5. Promote reviewed cases into a frozen "golden set" that never changes without a deliberate decision.

That golden set is the thing you actually regress against. Everything else is a larger, noisier set you can use for exploration.

## Using a model as a judge, carefully

Grading free-text answers by hand does not scale, so you use a model. Three rules make this trustworthy enough to act on:

- **Grade against a reference, not in the abstract.** "Does this answer contain the same key facts as this reference answer?" is a far more reliable judgement than "is this answer good?"
- **Ask for a structured verdict with a reason** — a category and one sentence — rather than a score out of ten. Numeric scores from models cluster and drift; categorical verdicts are more stable.
- **Validate the judge against humans once.** Have a person grade 50 cases, compare, and measure agreement. If the judge disagrees with people on a fifth of cases, its aggregate numbers cannot support a decision.

And keep deterministic checks wherever the task allows them. Exact match on extracted fields, schema validity, whether the cited chunk ID is the correct one, arithmetic consistency — these cost nothing, never drift, and cover more of a typical eval than people expect.

## What synthetic data cannot give you

Be honest about the boundary:

- **Real distribution.** You will not guess what fraction of users ask about billing versus onboarding. Only traffic tells you that, and it determines where quality actually matters.
- **Genuinely novel phrasing.** Generated text is more uniform and more grammatical than what people type.
- **Domain judgement.** Whether an answer is *correct* for your business — the refund policy, the medical caveat, the legal wording — needs a human who knows the domain, not a model that read the docs.
- **Emotional and adversarial reality.** Angry users, confused users, and people deliberately probing your system behave in ways generation does not reproduce.

So treat synthetic data as **scaffolding**: it gets you to a testable system before launch, and it should be progressively replaced by real cases from production traces afterwards. A year in, your eval set should be mostly real, with synthetic data filling only the categories real traffic is too rare to cover.

## FAQ

**How many cases do I need?**

Enough that a change of a few percent is not noise — practically, 100-200 in a frozen golden set, weighted toward the hard categories.

**Should I generate with the same model I am testing?**

Prefer a different model or a different prompt style for generation. Same-model generation amplifies the circularity problem.

**Can I share a synthetic eval set publicly?**

Check it for leaked real data first — generated cases seeded from your documents can contain customer names verbatim.

**How often should I regenerate?**

Do not regenerate the golden set; grow it. Regenerating changes the measuring stick and makes historical comparisons meaningless.

**Is one eval set enough?**

No. Separate retrieval quality from answer quality from safety behaviour — they fail independently, and a single aggregate number hides which one moved.

---

*The evaluation practices referenced here draw on the provider and framework documentation linked above. The category table, the seeding hierarchy, the stratified-review process, the judge-validation rule and the assessment of synthetic data's limits are my own judgement from building evaluation suites for LLM features; the right mix for your application depends on your domain and your traffic.*
