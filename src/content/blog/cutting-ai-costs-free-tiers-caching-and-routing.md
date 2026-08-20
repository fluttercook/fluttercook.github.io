---
title: "Using AI without burning cash: free tiers, caching, and routing"
description: "Three levers decide your AI bill: not paying for what's free, not paying twice for the same tokens, and not paying frontier prices for junior work. Here's what each is worth, with real numbers."
seoDescription: "A practical guide to cutting LLM costs: current free-tier limits from Cerebras, Groq and OpenRouter, aggregating them with FreeLLMAPI, and the paid-side levers — prompt caching, the Batch API, model routing and context hygiene — with worked cost math."
keywords:
  - reduce llm api cost
  - free llm api
  - cerebras free tier
  - prompt caching cost saving
  - batch api discount
  - llm model routing
  - freellmapi
category: "Guide"
topic: "AI Engineering"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-20"
emoji: "💸"
tags: ["AI", "Cost Optimization", "LLM", "Developer Tools", "API"]
sources:
  - name: "Cerebras Inference — rate limits by tier"
    url: "https://inference-docs.cerebras.ai/support/rate-limits"
  - name: "Groq — rate limits"
    url: "https://console.groq.com/docs/rate-limits"
  - name: "OpenRouter — API rate limits and free model caps"
    url: "https://openrouter.ai/docs/api-reference/limits"
  - name: "Gemini API — additional terms of service (paid vs unpaid)"
    url: "https://ai.google.dev/gemini-api/terms"
  - name: "FreeLLMAPI — self-hosted free-tier aggregator"
    url: "https://github.com/tashfeenahmed/freellmapi"
  - name: "Anthropic — pricing"
    url: "https://claude.com/pricing"
draft: false
---

Most people try to cut their AI bill by picking a cheaper model. That's the smallest of the levers available, and usually the one that costs the most in quality.

The bill is set by three things, in this order:

1. **What you pay for that's actually free.** Several providers give away real capacity with no card.
2. **What you pay for twice.** The same 20,000-token system prompt, resent on every request, at full price.
3. **What you pay frontier rates for that doesn't need them.** Classification, extraction, renaming, formatting.

Fix them in that order. The first is free money, the second is usually a 5–10x reduction on the same model, and only then does model choice matter. Here's what each one is actually worth right now, with numbers from the providers' own docs rather than from memory.

## Tier 0: what's genuinely free today

Free tiers are real, and they're bigger than most people assume. But the numbers that matter aren't the daily totals everyone quotes — they're the *per-minute* ones, because that's what actually stops you mid-task.

| Provider | Free models | Per minute | Per day | Card needed |
| --- | --- | --- | --- | --- |
| **Cerebras** | `gpt-oss-120b`, `gemma-4-31b` | 5 RPM, 30K TPM | 1M TPD (and 1M per *hour*) | No |
| **Groq** | `openai/gpt-oss-120b` / `20b`, `qwen/qwen3.6-27b` | 30 RPM, 8K TPM | 1K RPD, 200K TPD | No |
| **Groq** (compound) | `groq/compound`, `compound-mini` | 30 RPM, 70K TPM | 250 RPD | No |
| **OpenRouter** | any `:free` model | 20 RPM | 50 RPD — or 1,000 RPD once you've bought ≥10 credits all-time | No (credits optional) |
| **Google AI Studio** | Gemini free tier | per-account | per-account | No |

A few things this table hides that will bite you:

**TPM is the real ceiling, not TPD.** Cerebras gives you a million tokens a day but only 30,000 tokens a minute. A single request carrying a 40,000-token document doesn't get throttled — it gets rejected. Free tiers are shaped for lots of small requests, not for a few large ones. If your workload is "summarize this 60-page PDF," free tiers are the wrong shape regardless of the daily headline.

**Cerebras also meters per hour.** 1M tokens per hour *and* 1M per day means the day's entire budget can be spent in one hour. There's no smoothing.

**Google's limits are per-account, not published as a fixed table.** They're shown in the AI Studio rate-limit dashboard for your key. Any number you read in a blog post — including this one — is someone else's account.

**Free RPD counts are small enough that agent loops eat them.** 50 requests/day on OpenRouter is roughly three agentic tasks, since each task fans out into read-file / run-test / edit / re-read cycles.

### The part that isn't priced in dollars

The free tier's second price is your data, and at least one provider states it plainly. Google's Gemini API terms draw the line at payment: on **unpaid** services, Google uses submitted content "to provide, improve, and develop Google products and services," and human reviewers "may read, annotate, and process your API input and output" — disconnected from your account and API key first. On **paid** services, Google "doesn't use your prompts... or responses to improve our products," and logs them only briefly for abuse detection.

That's the same trade every free tier makes in some form, with varying transparency. Read each provider's own terms rather than assuming — but assume the default is *retained*.

The operational rule that falls out of this is simple: **the free tier is for work you'd be comfortable publishing.** Learning, prototypes, personal projects, open-source code, public documents. Not client code, not customer records, not anything under an NDA. This isn't a caution about the vendors' good faith — it's about what you agreed to when you skipped the credit card.

## Aggregating the free tiers: FreeLLMAPI

Once you're using three or four free tiers, the friction is no longer quota — it's plumbing. Different base URLs, different keys, different 429 behaviour, and no failover when one runs dry mid-task.

[FreeLLMAPI](https://github.com/tashfeenahmed/freellmapi) (MIT, ~19k stars) is the current answer to that. You self-host it, paste in your provider keys, and it exposes a single OpenAI-compatible `/v1` endpoint — plus Anthropic Messages and Gemini surfaces — in front of all of them. It advertises roughly **4 billion tokens per month across 29 providers and 358 free model endpoints**, tracks per-key RPM/RPD/TPM/TPD, and on a 429 or 5xx applies a cooldown and falls through to the next model in the chain. Keys sit AES-256-GCM-encrypted in a local SQLite file; a dashboard runs at `localhost:3001`.

The number moves, and that's worth noting: a widely shared post about this project quoted 1.3 billion tokens/month, and the repo now says 4 billion. Treat any specific figure as a snapshot, including the one above.

Three caveats before you wire it into anything:

- **The README says it out loud:** the project is "for personal experimentation and learning, not production." Take that at face value. A self-hosted router in front of a dozen free tiers is a single point of failure with a dozen upstream failure modes.
- **You still own each provider's terms.** Aggregation doesn't change what you agreed to per account, and free tiers are generally sized for one application, not for a fan-out router.
- **The quick install is `curl … | bash`.** That's a remote script executing with your shell's privileges. Read it before you run it — the same advice applies to every install one-liner, not just this one.

Used within those limits it's genuinely good: it turns "which free tier still has quota" from a thing you think about into a thing that resolves itself.

## When free stops being the right answer

Free tiers fail on three axes, and they fail predictably:

| You need | Free tier gives you |
| --- | --- |
| Predictable latency | Best-effort, shared capacity |
| A rate limit you can plan a sprint around | 5–30 RPM, small TPM |
| A written data-processing commitment | Content used to improve the provider's models |

The moment output from a model reaches something a customer sees or something someone paid for, none of those three are acceptable any more. That's the migration trigger — not a token count.

## The paid-side levers, ordered by what they return

This is where most of the money actually is, and where almost nobody looks first. Prices below are Anthropic's published rates; the same *mechanics* exist at every major provider, only the multipliers differ.

### 1. Prompt caching — the single biggest lever (~90% off repeated input)

If any part of your request is the same every time — a system prompt, a tool list, a knowledge base, a style guide — you're currently paying full price to resend it on every call.

Caching charges about **1.25x to write** a prefix and about **0.1x to read** it. So it pays for itself on the *second* call: 1.25 + 0.1 = 1.35 versus 2.0 for two uncached sends. Everything after that is ~90% off.

Two rules decide whether it works:

- **It's a prefix match.** Rendering order is `tools` → `system` → `messages`. A single changed byte anywhere in the prefix invalidates everything after it. Put stable content first; put timestamps, request IDs and the user's actual question *after* the last cache breakpoint.
- **There's a minimum.** Prefixes under roughly 1,024 tokens silently don't cache. No error — just no savings.

The most common silent killer is a `datetime.now()` or a UUID injected into the system prompt. Verify rather than assume: `usage.cache_read_input_tokens` should be non-zero on repeated calls. If it's zero every time, something in your prefix is moving.

### 2. Batch API — 50% off anything that isn't interactive

Backfills, nightly evals, classifying a table, translating a content archive, generating embeddings for a corpus: none of these need a response in two seconds. Submitting them as a batch job is a flat **50% discount** for accepting asynchronous delivery.

This is the cheapest optimization in the list because it requires no prompt changes at all — only a different call site and a poll loop. Results come back in arbitrary order, so key them by your own `custom_id`, never by position.

### 3. Route by task, not by habit

Current Anthropic tiers, per million tokens:

| Model | Input | Output | Good fit |
| --- | --- | --- | --- |
| Claude Haiku 4.5 | $1 | $5 | Classification, extraction, routing, tagging, short summaries |
| Claude Sonnet 5 | $3 | $15 | Day-to-day development, drafting, review |
| Claude Opus 5 | $5 | $25 | Hard reasoning, architecture, multi-file refactors, anything expensive to get wrong |

Most teams get this backwards at both ends: a frontier model formatting JSON, and a cheap model on the concurrency bug that's eaten two days. The first wastes tokens; the second wastes something more expensive than tokens.

A useful heuristic: **if you can write down the correct answer's shape in advance, the cheapest tier can probably produce it.** Classification has a known output space. Architecture doesn't.

### 4. Turn the effort down before you turn the model down

On current models, reasoning depth is a request parameter (`output_config.effort`, `low` through `max`) and thinking tokens are billed like any other output. Dropping a routine task from `high` to `low` cuts spend without changing models — and for genuinely simple work, it often *improves* the result by cutting preamble.

Reach for this before downgrading the model. A cheaper model changes what the system can do; lower effort mostly changes how much it deliberates.

### 5. Context hygiene — the cost nobody sees

The API is stateless: **you resend the entire conversation on every turn, and you're billed for all of it.** A 200-turn chat isn't 200 small requests. It's one small request plus 199 increasingly large ones. Left alone, a long agent session spends the majority of its budget re-reading its own history.

Three fixes, in increasing order of effort:

- **Start a new session** when the topic changes. Free, and the most underused.
- **Context editing** — clear old tool results (`clear_tool_uses_20250919`) or thinking blocks from history. Stale tool output is the bulk of an agent's context and almost none of its value.
- **Compaction** — server-side summarization of earlier turns when the window fills. Note that compaction blocks must be echoed back, or the state silently resets.

### 6. Remember output costs ~5x input

Across every tier above, output is priced at roughly five times input. "Be concise" is not a style preference, it's a line item. Ask for structured output instead of prose where you can — a JSON object with four fields is a fraction of the tokens of a paragraph explaining the same four fields, and it parses.

## What this adds up to

A support assistant: a 20,000-token knowledge base in the system prompt, a ~500-token question, a ~300-token answer, 10,000 requests a month.

| Setup | Monthly |
| --- | --- |
| Opus 5, no caching | **~$1,100** |
| Sonnet 5, no caching | ~$660 |
| Sonnet 5 + prompt caching | ~$155 |
| Sonnet 5 + caching, half the volume batched | **~$116** |

The math on row three, so you can check it: assume steady traffic and a 95% cache hit rate on the 20K prefix. Cache reads are 190M tokens at $0.30/M (~$57), cache writes 10M at $3.75/M (~$38), the uncached questions 5M at $3/M ($15), output 3M at $15/M ($45).

**~9x, without changing a single answer the user sees.** The model tier accounts for a third of the improvement; caching accounts for most of the rest. That ratio is typical, and it's why "pick a cheaper model" is the wrong first move.

(Rates used are standard published pricing. Introductory or promotional pricing shifts the absolute numbers but not the ratios — the levers are multiplicative, not additive.)

## The order to do this in

1. **Measure first.** Count tokens with the provider's `count_tokens` endpoint rather than estimating, and find out what fraction of your input is identical across requests. That fraction *is* your caching upside.
2. **Cache the stable prefix.** Verify with `cache_read_input_tokens`. Everything else is downstream of this.
3. **Move anything non-interactive to batch.** No prompt changes, 50% off.
4. **Split your traffic by task.** Cheapest tier for shaped outputs, mid tier for real work, frontier only where being wrong is expensive.
5. **Then tune effort and trim context.**
6. **Put learning, prototypes and public-code work on free tiers** — and keep everything else off them.

One honest caveat on step 6: don't let free-tier chasing cost more in engineering hours than it saves in dollars. Wiring a multi-provider router to save $5 a month is a bad trade at any salary. Free tiers are for the work where you'd otherwise have paid nothing, because you'd have not done it at all.

## FAQ

**Which free tier is best?**
Depends on your request shape. Cerebras has the highest daily volume and the lowest per-minute ceiling (5 RPM / 30K TPM), which suits few, small, fast calls. Groq's 30 RPM with 200K TPD suits chattier workloads. OpenRouter's breadth of models is the draw, but 50 requests/day without purchased credits is very tight.

**Is aggregating free tiers against providers' terms?**
Aggregation itself isn't inherently a violation, but each account's terms still bind you individually, and free tiers are sized for one application rather than a fan-out router. Read the terms per provider; the aggregator explicitly puts that responsibility on you.

**Will prompt caching change my model's answers?**
No. It changes how the input is billed and how fast it's processed, not what the model sees. A cache hit and a cache miss present identical content to the model.

**How long does a cache entry live?**
Five minutes by default, refreshed on each hit, with a one-hour option available. For steady traffic the default is enough; for bursty traffic — a job every 20 minutes — you pay the write cost each time, which is why the 95% hit rate above is an assumption, not a promise.

**Is the Batch API slower in a way that matters?**
It's asynchronous by design, so it's unsuitable for anything a user is waiting on. For overnight and background work, the delay is invisible and the 50% is not.

**Should I self-host an open model to cut costs?**
Only at sustained high volume. Below that, GPU rental plus your own engineering time exceeds API pricing, and you inherit the ops. The free tiers above are the cheap way to get open-weights models without the ops.

---

*Rate limits, prices and free-model lineups in this post are as published by each provider at the time of writing and change frequently. Every figure links to its source — check those before making a budget decision. The FreeLLMAPI section describes the project's own stated capabilities and its own stated caveat that it is intended for personal experimentation rather than production.*
