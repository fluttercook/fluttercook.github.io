---
title: "Model routing and cascades: paying for the intelligence you need"
description: "Sending every request to your largest model is the simplest architecture and usually the wrong one. Routing and cascading cut cost and latency substantially — if you can tell, before answering, which requests are hard."
seoDescription: "How to route LLM requests between models: static routing by task, classifier-based routing, cascades with escalation, self-verification signals, measuring the quality cost, and when a single model is the right answer."
keywords:
  - llm model routing
  - model cascade llm
  - reduce llm api cost
  - small model vs large model
  - llm request classifier
  - llm latency optimization
category: "Deep Dive"
topic: "AI"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-08-02"
emoji: "🔀"
tags: ["AI", "Architecture", "Cost", "LLM", "Performance"]
sources:
  - name: "Models overview — Anthropic documentation"
    url: "https://docs.anthropic.com/en/docs/about-claude/models"
  - name: "Prompt caching — Anthropic documentation"
    url: "https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching"
  - name: "Models — OpenAI documentation"
    url: "https://platform.openai.com/docs/models"
  - name: "Building effective agents — Anthropic engineering"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
  - name: "FrugalGPT — arXiv"
    url: "https://arxiv.org/abs/2305.05176"
  - name: "OpenTelemetry semantic conventions for GenAI"
    url: "https://opentelemetry.io/docs/specs/semconv/gen-ai/"
related:
  - slug: "ai-streaming-ux-token-by-token"
    title: "Streaming UX: designing for tokens arriving one at a time"
  - slug: "ai-on-device-flutter-gemma"
    title: "On-device AI in Flutter: what fits on a phone"
draft: false
---

Your bill arrives and 90% of it is requests like "summarise this in one sentence" and "is this message spam?" — sent to the same frontier model you use for multi-step reasoning, because that was the one you wired up first.

The fix is obvious in principle: use a smaller model where a smaller model suffices. The difficulty is entirely in the word *suffices*, and in knowing which requests those are before you have the answer.

## Three architectures, not one

People say "routing" for three different things, and they have different risk profiles.

| Approach | How it decides | Cost | Risk |
| --- | --- | --- | --- |
| **Static routing** | The code path determines the model | Lowest complexity | Wrong assignment is invisible until quality complaints |
| **Classifier routing** | A small model or heuristic picks per request | One extra call | Misclassification sends hard work to a weak model |
| **Cascade** | Try small, escalate on failure | Sometimes two full calls | Escalation criteria are the whole problem |

**Start with static routing.** It captures most of the available savings for almost none of the complexity, and it is the one people skip because it feels too simple.

## Static routing: the free win

You already know which of your features are easy. In a typical application:

- Classification, tagging, routing an email into a queue, extracting a date, checking a language — small model.
- Summarising a short document, rewriting a sentence, generating a title, formatting a response — small model.
- Multi-step reasoning, code generation, analysing a long document, anything where a wrong answer has a cost — large model.
- Anything that calls tools in a loop — large model, because tool selection errors compound across turns.

Wire the model choice into the feature, not into a global config. Then measure per feature. A feature whose quality is unaffected by the downgrade should stay downgraded permanently; one that visibly degrades goes back and you have learned something concrete.

Do this before anything clever. In most applications it removes the majority of the bill, and the remaining decisions are then about a much smaller pool of genuinely ambiguous requests.

## Classifier routing: paying a small call to save a large one

When requests arrive as free text with no feature boundary — a general chat interface, an inbox, a support queue — you cannot route statically. You need a decision per request.

The economics are simple and worth checking explicitly: the classifier call must cost meaningfully less than the difference between the two models it is choosing between. A classifier costing a fifth of the large model that only diverts a third of traffic is not paying for itself.

Two practical notes:

- **Route on required capability, not on topic.** "Is this a coding question?" is the wrong question; "does this need multi-step reasoning, or is it a lookup?" is the right one.
- **Heuristics beat classifiers more often than expected.** Input length, presence of a code block, number of conversation turns, whether tools are available, whether the user is on a paid plan — these are free to compute and capture a lot of the signal. Reach for a model only when the cheap signals genuinely do not separate the cases.

And bias the routing asymmetrically. Sending an easy request to the large model wastes money; sending a hard request to the small model produces a wrong answer a user sees. Those costs are not symmetric, so the threshold should not be at 50% confidence.

## Cascades: try cheap, escalate on failure

A cascade runs the small model first and escalates when the result is unsatisfactory. It is appealing because the decision is made *after* seeing an attempt rather than guessed beforehand.

The entire design problem is the escalation signal. In descending order of reliability:

1. **Deterministic validation.** The output must parse as JSON, satisfy a schema, contain a required field, cite a real document ID, produce arithmetic that checks out. If it fails, escalate. This is the only signal I fully trust, and it is why cascades work far better for structured tasks than for prose.
2. **Explicit abstention.** Instruct the small model that returning `{"insufficient": true}` is an acceptable and expected answer, and make abstaining cheap for it. Models will use this if you give them permission; they will not if the prompt implies an answer is mandatory.
3. **Downstream verification.** The retrieved chunk does not contain the claimed fact; the generated code does not compile; the extracted total does not match the line items. Real checks against the world.
4. **Self-reported confidence.** Asking the model how confident it is. Weak, poorly calibrated, and the thing most cascade tutorials build on. Use it as a tiebreaker at best.

If none of the first three apply to your task, a cascade will not work well and classifier routing is the better structure.

The cost model is worth being precise about. If escalation happens with probability *p*, your expected cost per request is the small-model cost plus *p* times the large-model cost. **When *p* rises above roughly 30-40%, you are paying for two calls often enough that you may as well have gone straight to the large model** — and you have added latency on top. Instrument *p* and alert when it drifts; it will drift as your traffic changes.

## What routing does to latency

Routing has a latency profile people forget to account for:

- **Static routing** strictly improves latency. Smaller models are faster.
- **Classifier routing** adds the classifier's latency to every request, including the ones that end up on the small model. Keep it tiny, or run it on cheap local heuristics.
- **Cascades** add the small model's full latency to every escalated request. For a streaming interface this is worse than it sounds: the user sees nothing during the first attempt, then nothing again while the second starts.

For anything user-facing and streaming, that last point often disqualifies cascades outright. They are best suited to background and batch work where an extra second does not matter.

## Do not route away your prompt cache

This is the interaction that surprises people. Prompt caching gives a substantial discount on repeated prefixes — a long system prompt, a fixed set of tool definitions, a document you ask many questions about. **Caches are per-model.** Splitting your traffic across two models splits your cache hit rate across two caches.

If your workload has a large shared prefix and high cache hit rates, the cached large model can genuinely cost less than the uncached small model. Measure your actual bill under both arrangements rather than reasoning from list prices. This is the most common way a routing project ends up saving nothing.

## Measuring whether it worked

A routing change alters cost, latency and quality simultaneously, and you must watch all three or you are flying blind on the one that matters.

- Log the **chosen model and the reason** on every request. Without this you cannot debug a quality complaint, because you will not know which model produced the bad answer.
- Track escalation rate and classifier distribution over time. Both drift.
- Run your eval set against each routing arm separately. An aggregate quality number hides the case where small-model traffic degraded 15% while large-model traffic stayed flat.
- Keep a **kill switch** that forces every request to the large model. When quality complaints arrive, flipping it is the fastest way to confirm or eliminate routing as the cause.

## When one model is the right answer

Routing is an optimisation, and optimisations have a break-even point:

- **Low volume.** If your monthly bill is small, routing complexity costs more in engineering time than it saves. Revisit at scale.
- **Uniformly hard workload.** If every request genuinely needs the frontier model, routing only adds failure modes.
- **Early product.** Your prompts and features are still changing. Routing decisions made now will be wrong in a month, and you will not notice.
- **High stakes per request.** Medical, legal, financial. The savings do not justify a class of failures where the cheap model answered something it should not have.

Cheaper prompts, prompt caching, and simply asking for shorter outputs often deliver more savings than routing, with none of the quality risk. Exhaust those first.

## FAQ

**How much can routing realistically save?**

It depends entirely on your traffic mix. Static routing on a workload with a large easy fraction is the biggest single lever; a uniformly hard workload saves nothing.

**Should the router itself be an LLM?**

Only if cheap signals fail. Length, structure and feature context resolve most cases for free.

**Can I cascade more than two levels?**

You can, and it is rarely worth it. Each level adds latency and an escalation criterion that can be wrong.

**How do I pick which small model?**

By evaluating candidates on your own eval set, not by benchmark rankings. The differences that matter to you are task-specific.

**Does routing break conversation continuity?**

It can. Switching models mid-conversation changes tone and formatting noticeably. Pin the model for the duration of a conversation.

---

*Model capabilities, pricing and caching behaviour come from the provider documentation linked above and change frequently — verify current details before designing around them. The routing taxonomy, the escalation-signal ranking, the break-even reasoning and the recommendation to start with static routing are my own judgement from building cost-sensitive LLM systems.*
