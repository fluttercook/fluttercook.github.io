---
title: "Cost per request: the number most AI features never compute"
description: "You know your monthly API bill. You probably don't know what one request costs, which means you can't tell a pricing problem from a usage problem. Here's the full model — including the multipliers that turn a half-cent call into a four-cent user action."
seoDescription: "Build a per-request cost model for an LLM feature: base token math, agent-loop turns, quadratic conversation growth, retrieval, retries — then rank the levers and instrument it."
keywords:
  - llm cost per request
  - ai feature unit economics
  - token cost calculation
  - agent loop cost
  - llm cost observability
  - cost per user action
category: "Analysis"
topic: "AI Engineering"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-22"
emoji: "🧮"
tags: ["AI", "LLM", "Cost Optimization", "Observability"]
sources:
  - name: "Anthropic — token counting endpoint"
    url: "https://docs.claude.com/en/docs/build-with-claude/token-counting"
  - name: "Anthropic — prompt caching"
    url: "https://docs.claude.com/en/docs/build-with-claude/prompt-caching"
  - name: "Anthropic — pricing"
    url: "https://claude.com/pricing"
  - name: "OpenAI — pricing"
    url: "https://platform.openai.com/docs/pricing"
  - name: "Gemini API — understanding and counting tokens"
    url: "https://ai.google.dev/gemini-api/docs/tokens"
  - name: "tiktoken — OpenAI's BPE tokenizer"
    url: "https://github.com/openai/tiktoken"
related:
  - slug: "cutting-ai-costs-free-tiers-caching-and-routing"
    title: "Using AI without burning cash: free tiers, caching, and routing"
  - slug: "building-an-ai-agent-team-chief-of-staff-pattern"
    title: "The chief-of-staff pattern: turning scattered AI chats into an agent team"
draft: false
---

Every team shipping an AI feature knows their monthly API bill. Almost none of them know what a single request costs. Those are different numbers, and only the second one is actionable.

The bill is a total. It cannot tell you whether the total is large because each request is expensive or because there are far more requests than you planned for. Those two problems have opposite fixes — one is an architecture problem, the other is a packaging problem — so a team that only has the total tends to respond the same way regardless: someone spends a week trimming the system prompt. As you'll see below, that is usually the smallest lever available, and it's the first one everyone reaches for.

The bill is also a single scalar for an account that might serve six features. If summarization is cheap and the new agentic workflow is expensive, the invoice averages them into one meaningless number that goes up.

What follows builds the missing number from scratch: what one user action costs, end to end, including every multiplier that sits between the two-term textbook formula and reality. What to do once you can see the number — free tiers, model routing, batch pricing — is covered in [Using AI without burning cash](/blog/cutting-ai-costs-free-tiers-caching-and-routing/). Here the goal is only to make the number exist.

> **Every rate in this post is a made-up placeholder.** I use **$1.00 per million input tokens** and **$5.00 per million output tokens** throughout, because round numbers make the arithmetic checkable by hand. They are not any provider's real prices. Substitute your provider's current published rates — linked in the sources at the bottom — before you make a decision with any of this.

## The two-term formula is the easy part

The base cost of one API call is:

```text
cost = (input_tokens  / 1_000_000) * input_rate
     + (output_tokens / 1_000_000) * output_rate
```

Take a "summarize this support ticket" feature: a 3,000-token prompt (system instructions plus the ticket thread), a 400-token summary out.

```text
input:  3,000 / 1e6 * $1.00 = $0.0030
output:   400 / 1e6 * $5.00 = $0.0020
total                       = $0.0050
```

Half a cent. At 200,000 tickets a month that's $1,000, and if that's what your dashboard shows, the model was right.

Two things about this formula are worth noticing before we complicate it. First, **output is priced several times higher than input on essentially every provider**, so "be concise" is a line item, not a style note. Second, this formula is correct for exactly one shape of feature: one user action, one API call, no retries, no history. Most features are not that shape, and every deviation is a multiplier.

## Multiplier 1: one user action is not one API call

An agent that plans, calls tools, and then answers doesn't make one request. It makes one request per turn, and the API is stateless — **every turn re-sends the entire conversation so far**, including the system prompt, the tool definitions, and every tool result that came back.

Concretely, take an agent with:

- a 2,000-token stable prefix (system prompt plus tool schemas),
- a 500-token user request,
- 6 turns: five tool calls at 150 output tokens each, then a 400-token final answer,
- 800 tokens of tool result appended per turn, so the history grows by 950 tokens each turn.

| Turn | Input tokens | Output tokens |
| --- | --- | --- |
| 1 | 2,500 | 150 |
| 2 | 3,450 | 150 |
| 3 | 4,400 | 150 |
| 4 | 5,350 | 150 |
| 5 | 6,300 | 150 |
| 6 | 7,250 | 400 |
| **Total** | **29,250** | **1,150** |

```text
input:  29,250 / 1e6 * $1.00 = $0.02925
output:  1,150 / 1e6 * $5.00 = $0.00575
per user action              = $0.0350
```

Three and a half cents. The naive estimate — 2,500 in, 400 out, one call — was $0.0045. **The loop costs about 7.8x what a single-call estimate predicts**, and nothing about that ratio is visible from the invoice.

The general form, with `n` turns, a fixed prefix `S` (system + tools + original request), and `g` tokens of growth per turn:

```text
total_input_tokens = n * S + g * n * (n - 1) / 2
```

That second term is quadratic in `n`. Doubling the loop from 6 turns to 12 takes total input from 29,250 to 92,700 — **3.2x the tokens for 2x the turns**. This is why an agent that "sometimes takes a few extra steps" is not a small problem: the marginal turn is always the most expensive one so far.

## Multiplier 2: a conversation pays for its own history

The same quadratic applies to any multi-turn chat, and here it's easier to miss because each individual turn still feels cheap.

Take a 1,000-token system prompt, a 100-token user message and a 300-token reply per exchange — so the history grows 400 tokens per turn, and turn `n` sends `1,100 + 400*(n-1)` input tokens.

| Turn | Input tokens | Cost of this turn | Cumulative | This turn vs. turn 1 |
| --- | --- | --- | --- | --- |
| 1 | 1,100 | $0.0026 | $0.0026 | 1.0x |
| 5 | 2,700 | $0.0042 | $0.0170 | 1.6x |
| 10 | 4,700 | $0.0062 | $0.0440 | 2.4x |
| 20 | 8,700 | $0.0102 | $0.1280 | 3.9x |
| 30 | 12,700 | $0.0142 | $0.2520 | 5.5x |

A 30-turn conversation costs $0.252. If you estimated it as "30 turns at the cost of turn 1" you'd have budgeted $0.078 — off by 3.2x. **The most engaged users are super-linearly the most expensive**, which is the opposite of the intuition most pricing pages are built on.

The mitigation is architectural, not financial: start a new session when the topic changes, drop stale tool results from the history, or use whatever server-side compaction your provider offers. Every one of those reduces `g`, and `g` is multiplied by `n(n-1)/2`.

## Multiplier 3: retrieved context is a config value, not a user input

In a RAG feature, the retrieved chunks usually dwarf the question. With `k = 8` chunks of ~600 tokens each, every request carries 4,800 tokens of context regardless of whether the user typed three words or thirty.

The important property is that **`k` is a number in your config, so per-request cost changes when someone edits a config file**. A recall complaint gets fixed by bumping `k` from 8 to 20; retrieved context goes from 4,800 to 12,000 tokens; input cost per request goes from $0.0053 to $0.0125. That's a 2.4x change to the unit economics of the feature, shipped in a one-line diff, in a PR whose title is about answer quality.

Corpus growth pushes the same way indirectly. A bigger corpus means more near-miss chunks, so teams raise `k`, add a reranking pass over a wider candidate set, or switch to larger chunks. None of those show up as "we made the feature more expensive" in a changelog. Put `k`, chunk size, and max output length on the same review checklist as anything else that moves cost, and print the per-request token delta in the PR.

## Multiplier 4: you pay for the attempts that failed

Everything above assumed every call succeeded. Four things break that:

- **Validation retries.** If a structured output fails schema validation and you retry, an independent failure rate `p` gives you `1 / (1 - p)` attempts on average — a 10% failure rate is a 1.11x multiplier. Modest. But a failed attempt still bills its output tokens, and a truncated JSON response usually means the model generated a *lot* of output before hitting the ceiling.
- **Tool-repair loops.** An agent that calls a tool wrong, reads the error, and tries again doesn't add one call — it adds a turn, and turns are quadratic (Multiplier 1).
- **Guardrail and judge passes.** If you run a second model over every output to check it, that's not a multiplier, it's a whole additional line item. Price it separately and put it in the same ledger.
- **Reasoning tokens.** On providers that expose extended thinking, reasoning tokens are billed as output even when they never appear in the answer. A short visible answer is not evidence of a cheap request.

Abandoned streams deserve a check rather than an assumption: whether a cancelled stream bills the tokens already generated is provider-specific, and abandonment is common in a chat UI.

## The levers, ranked — and the ranking depends on your shape

Now run the levers against the 6-turn agent from Multiplier 1, where the baseline is **$0.0350 per user action**.

| Lever | What it does | New cost | Change |
| --- | --- | --- | --- |
| Shrink the loop (6 turns → 3) | Cuts `n`, which cuts the quadratic term | $0.0139 | **−60%** |
| Cache the growing prefix | Turn `k` re-reads turn `k−1`'s prefix at cache-read rates | $0.0170 | **−51%** |
| Route half the traffic to a 10x cheaper model | Population-level average, per-request cost unchanged | $0.0193 | −45% |
| Halve the final answer (400 → 200 tokens) | Output is only 16% of this request's cost | $0.0340 | −3% |
| Trim the system prompt by 30% | 600 fewer tokens, resent 6 times | $0.0314 | −10% |

The caching row assumes placeholder cache rates of 1.25x the input rate to write and 0.1x to read, with an incremental breakpoint each turn: 7,250 tokens written, 22,000 read. Agent loops are unusually good caching candidates precisely *because* of the quadratic — the same action re-sends its own prefix several times within seconds, so the cache pays off without any cross-request traffic assumption. Placement and invalidation are their own topic; the [prompt caching docs](https://docs.claude.com/en/docs/build-with-claude/prompt-caching) are the place to start.

**Prompt trimming is last, and caching makes it worse.** Once the prefix is cached, those 600 tokens are billed at the cache-read rate, so the 10% saving collapses to roughly 1%. The most commonly attempted optimization is the least effective one, and the second most common optimization *removes its remaining value*.

**The ranking is not universal.** In this agent, output is 16% of the cost, so capping output length does almost nothing. In a document-generation feature — short prompt, 4,000-token output — output is the overwhelming majority of the cost and capping it is the top lever, while shrinking the loop is meaningless because there's no loop. **There is no correct default ranking. There is only your measured shape**, which is the entire argument for instrumenting this.

## Instrument it: one row per API call, joined by action

The unit of logging is the **API call**, not the feature. The unit of analysis is the **user action**. You get from one to the other with an `action_id` threaded through every call a single user action triggers.

Compute the cost at write time from the token counts the API returns — never re-derive it later from a rate table that has since changed, and never estimate tokens with a client-side tokenizer for accounting. Client-side counters like [tiktoken](https://github.com/openai/tiktoken) and the providers' `count_tokens` endpoints are for pre-flight budgeting; the `usage` object on the response is the billed truth.

```typescript
// PLACEHOLDER rates, $ per 1M tokens. Replace with your provider's published rates.
const RATES = {
  "model-large": { in: 1.0, out: 5.0, cacheWrite: 1.25, cacheRead: 0.1 },
  "model-small": { in: 0.1, out: 0.5, cacheWrite: 0.125, cacheRead: 0.01 },
} as const;

type Usage = {
  input_tokens: number;
  output_tokens: number;
  cache_creation_input_tokens?: number;
  cache_read_input_tokens?: number;
};

function costUsd(model: keyof typeof RATES, u: Usage): number {
  const r = RATES[model];
  return (
    u.input_tokens * r.in +
    u.output_tokens * r.out +
    (u.cache_creation_input_tokens ?? 0) * r.cacheWrite +
    (u.cache_read_input_tokens ?? 0) * r.cacheRead
  ) / 1_000_000;
}
```

One correctness trap: check whether your provider's `input_tokens` **includes or excludes** cached tokens. On the Claude API the three counts are disjoint — `input_tokens` covers only the uncached portion — so summing them is right. If your provider reports an inclusive total, that same code double-counts every cache hit and inflates your number.

Each call emits one row:

```json
{
  "action_id": "01JQ8T5V2K9",
  "feature": "ticket_agent",
  "model": "model-large",
  "turn": 3,
  "attempt": 1,
  "input_tokens": 4400,
  "cache_read_input_tokens": 2000,
  "output_tokens": 150,
  "cost_usd": 0.00535,
  "rates_version": "2026-08-01",
  "latency_ms": 1840,
  "outcome": "tool_use"
}
```

`rates_version` is the field people skip and regret. Prices change; without it, historical rows stop being reproducible and you can never answer "did our cost per action actually go up, or did the price?"

Roll it up per action, then look at the distribution rather than the mean:

```sql
WITH per_action AS (
  SELECT feature, action_id,
         sum(cost_usd)                     AS cost_usd,
         sum(input_tokens + output_tokens) AS tokens,
         count(*)                          AS calls
  FROM llm_calls
  WHERE ts >= now() - interval '7 days'
  GROUP BY feature, action_id
)
SELECT feature,
       count(*)      AS actions,
       avg(calls)    AS calls_per_action,
       avg(cost_usd) AS mean_cost,
       percentile_cont(0.50) WITHIN GROUP (ORDER BY cost_usd) AS p50,
       percentile_cont(0.95) WITHIN GROUP (ORDER BY cost_usd) AS p95,
       sum(cost_usd) AS total
FROM per_action
GROUP BY feature
ORDER BY total DESC;
```

`calls_per_action` is the single most diagnostic column in that query. If it's 1.0, you have a simple feature and the two-term formula is your whole model. If it's 6.4 and you designed for 3, you have found your cost problem without reading any other number.

And alert on **cost per action**, not on the bill. The bill moves when traffic moves, which is not news. Cost per action moves when your code changes — a prompt edit, a `k` bump, a model swap, a loop that started taking an extra turn on a class of input it didn't used to see. That's the signal.

## What the number tells you once you have it

With cost per action in hand, two multiplications turn engineering data into business data:

```text
cost_to_serve_a_user = cost_per_action * actions_per_user_per_month
gross_margin         = (price - cost_to_serve) / price
```

Now the diagnosis is mechanical. If cost per action is at target but `actions_per_user_per_month` is five times what you priced for, that's a **usage problem** — fix it with quotas, tiering, or a cheaper path for the high-frequency action, not by rewriting prompts. If a single action costs a meaningful fraction of a user's whole monthly price, that's an **architecture problem** and no amount of packaging saves it.

Watch p95 rather than the mean. LLM cost distributions have long tails — the 30-turn conversation, the agent that took 14 steps, the user who pasted a novel — and the mean hides them behind a comfortable-looking average. If p95 is many multiples of p50, a small number of sessions is setting your bill, and the fix is a cap somewhere (turn limit, context limit, output limit) rather than a broad optimization.

None of this requires a vendor: one table, one `action_id`, and a ten-line cost function. The reason most teams don't have it isn't difficulty — it's that nobody owns the number until the invoice is already alarming.

## FAQ

**Isn't the provider's usage dashboard enough?**
It gives you totals by API key and often by model, which answers "how much" but not "for what". It has no idea which of your features made a call, which calls belonged to the same user action, or what the distribution across requests looks like. You can approximate feature attribution with one API key per feature, which is a reasonable stopgap, but it still won't give you cost per action or a p95.

**How do I estimate cost before I've shipped anything?**
Run your provider's token-counting endpoint over a realistic sample of inputs — not a toy prompt — to get the input side, cap the output side at your `max_tokens`, then multiply by the number of turns you expect the loop to take. Then assume the loop takes more turns than you expect, because it will. Ship behind a flag and replace the estimate with measurements as soon as real traffic exists.

**Do reasoning or "thinking" tokens change the math?**
Yes, and in a way that's easy to miss. Where a provider bills reasoning tokens, they're charged at the output rate even though the user never sees them, so a request that returns two sentences can carry an output bill many times larger than those two sentences suggest. Read them off the `usage` object rather than inferring cost from the visible answer.

**Should I pass per-token costs through to my users?**
Usually not, and this is opinion rather than analysis: token-metered pricing makes your bill unpredictable for the customer and couples your pricing to a vendor's rate card you don't control. Credits or action-based quotas keep the unpredictability on your side, where you can actually manage it — but that only works if you know cost per action, which is the whole point.

**Does any of this apply if I self-host an open-weights model?**
The structure holds; the denominator changes. Instead of a published per-token rate you compute an effective rate from GPU-hour cost divided by measured throughput at your batch size and context length, then feed that into the same formula. The multipliers — loop turns, quadratic history, retrieval size, retries — are identical, because they're properties of your architecture and not of anyone's price list.

---

*The formulas, the arithmetic, and the multiplier structure here are mechanical and you can verify every line by hand. All rates are explicitly invented placeholders chosen for round numbers — substitute your provider's current published rates before drawing any conclusion, and re-check them, since they change. The lever ranking is specific to the example workload and will reorder for your feature; that is the argument, not a caveat. Billing behaviour for cancelled streams, cached tokens, and reasoning tokens is provider-specific and version-dependent — verify it against the current docs.*
