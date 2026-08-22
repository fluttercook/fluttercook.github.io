---
title: "Prompt caching in practice: the win is in the ordering, not the flag"
description: "Turning on prompt caching is one line. Getting hits is an architecture decision: everything invariant has to come first, and everything per-request has to come last. Here's how to order a prompt so the cache actually fires, and how to prove it did."
seoDescription: "How prompt caching really works: prefix matching, what silently invalidates a cache, how to order an agent prompt, and how to verify hits from the usage fields."
keywords:
  - prompt caching
  - llm cache prefix
  - cache_control breakpoint
  - cache hit rate llm api
  - prompt caching agent loop
  - cache_read_input_tokens
category: "Deep Dive"
topic: "AI Engineering"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-22"
emoji: "🧊"
tags: ["AI", "LLM", "Prompt Engineering", "Performance", "API"]
sources:
  - name: "Anthropic — Prompt caching"
    url: "https://platform.claude.com/docs/en/build-with-claude/prompt-caching"
  - name: "OpenAI — Prompt caching"
    url: "https://platform.openai.com/docs/guides/prompt-caching"
  - name: "Google — Gemini API context caching"
    url: "https://ai.google.dev/gemini-api/docs/caching"
related:
  - slug: "cutting-ai-costs-free-tiers-caching-and-routing"
    title: "Using AI without burning cash: free tiers, caching, and routing"
  - slug: "building-an-ai-agent-team-chief-of-staff-pattern"
    title: "The chief-of-staff pattern: turning scattered AI chats into an agent team"
draft: false
---

The first time most people enable prompt caching, they add one field to the request, deploy, and see nothing change. The bill is the same. Latency is the same. The feature is on and it does nothing.

That's the normal outcome, and it isn't a bug. Prompt caching is not a per-request switch that says "reuse whatever you can." It is a **prefix match on the exact bytes of the rendered prompt**. The provider hashes your prompt from the very first byte forward and looks for a stored entry it can resume from. If byte 47 of your 30,000-token prompt is different from last time — because it's a clock reading — there is no reusable prefix, and the other 29,900 tokens get processed from scratch at full price.

So the flag is not the work. The work is restructuring the prompt so the invariant part is physically first and the per-request part is physically last. That's a change to your prompt-assembly code, not to your API call. Once the ordering is right, the flag is nearly free money. While the ordering is wrong, no amount of cache markers will help.

This post is about that reordering: what a prefix actually is, the handful of things that silently destroy it, how to lay out an agent loop, why a growing conversation is the easy case and RAG is the hard one, and how to verify you're getting hits instead of hoping.

## A prefix is a prefix — everything after the change is gone

Think of the prompt as one long byte string. The provider stores intermediate model state (the KV cache) computed up to some point in that string. On the next request it can skip recomputing that region only if the new request's bytes are **identical from position zero up to that point**.

There is no fuzzy matching, no "close enough," no per-block reuse. It's a strict prefix.

```text
Request 1:  [ system 8k ][ tools 3k ][ history 12k ][ question A ]
Request 2:  [ system 8k ][ tools 3k ][ history 12k ][ question B ]
                                                    ^ divergence
            └────────── 23k reusable ─────────────┘  recompute 40 tokens
```

Now move one volatile byte to the front:

```text
Request 1:  [ 2026-08-22T09:14:02Z ][ system 8k ][ tools 3k ][ history 12k ][ A ]
Request 2:  [ 2026-08-22T09:14:47Z ][ system 8k ][ tools 3k ][ history 12k ][ B ]
            ^ divergence at byte 3
            └── 0 reusable. 23k tokens recomputed. ──┘
```

Same content, same size, same cache flag. One is a 23,000-token hit and the other is a total miss, and the only difference is where the timestamp lives. This single fact explains almost every "caching didn't work for us" story.

It also explains an ordering rule you can apply mechanically: **sort your prompt sections by how often they change, most stable first.** Not by what reads nicely.

## Know the render order, because it's not the order you wrote

Providers assemble the wire format in a fixed order, and that order is what gets hashed — not the order of arguments in your code. On the Claude API the rendered sequence is `tools` → `system` → `messages`. Tool definitions sit at position zero, ahead of your system prompt.

That has a consequence people find surprising: **changing your tool list invalidates your system prompt cache.** Not the other way around. If you build the tool array by iterating a dictionary, or you conditionally include an `admin_delete` tool for some users, or a plugin registry loads in nondeterministic order, then position zero varies and nothing downstream can ever be reused.

Serialize tools deterministically. Sort by name. Do it once, at startup, and keep the array as a module-level constant rather than rebuilding it per request.

```python
# Bad: order depends on dict iteration and on who's calling.
def build_tools(user):
    tools = [TOOLS[name] for name in registry.keys()]
    if user.is_admin:
        tools.append(ADMIN_TOOL)
    return tools

# Good: one frozen array, sorted, built once.
TOOLS = sorted(ALL_TOOLS, key=lambda t: t["name"])
# Admin capability becomes a permission checked inside the handler,
# not a difference in the tool list.
```

Other providers arrange things differently, but the principle is identical: find out what actually renders first, and treat that region as frozen.

## The five things that quietly break it

Almost every miss traces back to one of these. They're worth grepping for directly.

| Pattern | Why it kills the cache |
| --- | --- |
| `datetime.now()` interpolated into the system prompt | Prefix differs on every single request |
| A request ID, trace ID, or `uuid4()` near the top | Same — every request is unique by construction |
| `json.dumps(obj)` without `sort_keys=True`, or iterating a `set` | Byte-level serialization order drifts between processes |
| Conditional system sections (`if flag: system += ...`) | Each flag combination is a separate prefix that must warm separately |
| Tool list built per-user or per-request | Renders at position zero; nothing caches across callers |

The timestamp is the most common and the most defensible-sounding. "The model needs to know today's date" is true. It just doesn't need to know it *at the top of the system prompt*. Move it into the last user message, or — where your provider supports a mid-conversation operator channel — send it as a message appended after the cached history. A date at turn 12 invalidates nothing before turn 12.

The conditional-sections one is subtler and shows up in mature codebases. Every `if` in your prompt builder multiplies the number of distinct prefixes your traffic has to keep warm. Four independent booleans is sixteen prefixes, each needing its own warm-up and its own steady traffic. Usually the fix is to make the section unconditional (paying a few hundred always-cached tokens is cheaper than sixteen cold prefixes) or to move it after the breakpoint.

## Ordering an agent loop

An agent request is the case where this pays the most, because the same enormous preamble is resent on every single iteration of the loop. Order it by stability:

1. **Tool definitions.** Frozen, sorted, identical for every user.
2. **System instructions.** The role, the rules, the output contract. No interpolation.
3. **Stable documents.** Style guides, schema dumps, API references, few-shot examples — anything that's the same for a whole class of requests.
4. **Session-scoped context.** The repo the agent is working in, the ticket it's assigned. Changes per session, not per turn.
5. **Conversation history.** Grows at the end, which is exactly what you want.
6. **This turn's input.** The new user message, the fresh tool results, the current timestamp.

Where the provider gives you explicit cache breakpoints, put them at the *boundaries between stability tiers* — the end of stage 3 and the end of stage 5, typically. Anthropic's API caps you at four breakpoints per request, which is more than enough if you're placing them at real boundaries and not sprinkling them.

The mistake I see most often here is placing the marker at the end of the entire prompt. That feels natural — cache everything! — but if the last block differs per request, every request writes a brand-new entry and never reads one. You pay the write premium forever and read nothing. The breakpoint belongs at the end of the **shared** portion.

```json
{
  "system": [
    { "type": "text", "text": "<frozen instructions + style guide>",
      "cache_control": { "type": "ephemeral" } }
  ],
  "messages": [
    { "role": "user", "content": [
      { "type": "text", "text": "<shared few-shot block>",
        "cache_control": { "type": "ephemeral" } },
      { "type": "text", "text": "<this request's question — no marker>" }
    ]}
  ]
}
```

One more agent-loop specific detail: on the Claude API a breakpoint searches backward a limited number of content blocks to find a prior entry (documented as 20). A single agentic turn that fires a dozen parallel tools can blow past that window, and the next request's breakpoint silently finds nothing. If your turns produce long block runs, place an intermediate breakpoint inside the turn. Check your provider's docs for whether an equivalent limit exists.

## A growing conversation is the good case; RAG is the bad one

These two look similar — both add text to the prompt — and they behave in opposite ways.

**Conversation history grows at the end.** Turn 5's prompt is a strict byte prefix of turn 6's prompt. That's the ideal shape: each turn reads everything the previous turn wrote, and the cached region grows monotonically. A long agent session is the single best caching workload there is, and it needs almost no effort beyond not disturbing the front of the prompt mid-conversation.

This is why "let me just update the system prompt to tell it we've switched modes" is such an expensive habit. Editing top-level system content changes the prefix ahead of *the entire history* — every turn you accumulated gets reprocessed uncached. If your provider supports appending an operator instruction as a message after the history, use that. If it doesn't, put the instruction in the user turn. Either way, do not touch the front.

**Retrieved chunks change per query.** RAG is the anti-pattern by construction: the retriever returns different documents for different questions, so if you place retrieved context at the top — which is where most tutorials put it — you have a per-query prefix and nothing to reuse.

The fix is ordering again. Retrieved chunks are per-request content and belong late, next to the question:

```text
[ tools ][ system ][ stable corpus / schema ][ ---breakpoint--- ][ retrieved chunks ][ question ]
```

If a *fixed* set of documents is in play for a whole class of queries — a product manual, a legal corpus, a codebase you always ground against — that's not RAG in the volatile sense. It's a stable document, it goes in tier 3, and it caches beautifully. Some providers offer an explicit context-caching API for exactly this shape, where you upload the corpus once and reference it by handle. Worth checking whether yours does before you rebuild it yourself.

A useful test: ask whether two consecutive real user requests would produce byte-identical text for this section. If yes, it's stable content. If no, it's per-request content and it goes at the end.

## Cache lifetime decides whether low traffic ever hits at all

Cache entries expire. The mechanism everyone forgets is that the clock is typically **refreshed by use** — each hit extends the entry's life — but an idle gap longer than the lifetime drops it, and the next request pays a full write again.

This produces a failure mode that's invisible in a load test and obvious in production: an endpoint that serves a request every few minutes during business hours caches beautifully, and the same endpoint at 3am caches never. Worse, a low-traffic internal tool can end up in a state where it *only ever writes* — every request arrives after expiry, pays the write premium, and no request ever reads. That's strictly more expensive than not caching at all.

Anthropic documents a short default lifetime measured in minutes, plus a longer opt-in tier that costs more to write. Other providers differ, and these values change; check the current docs rather than trusting a number in a blog post, including this one. What's stable is the reasoning:

- **Request interval shorter than the lifetime** — caching just works, no extra machinery.
- **Bursty traffic with long idle gaps** — either use the longer-lived tier, or pre-warm the prefix at the start of each burst.
- **Genuinely sparse traffic and a small prefix** — leave caching off. You'd only pay write premiums.

The economics rhyme across providers: a cache read costs a fraction of a normal input token, and a cache write costs somewhat *more* than a normal input token. So the break-even is a small number of reads per write — a couple for short-lived entries, more for long-lived ones since they cost more to create. The design question isn't "is caching cheaper" (it is, when it hits) but "will this prefix be read enough times before it expires."

If your provider supports it, pre-warming is a real tool for the bursty case: fire one request against the shared prefix at worker startup or at the beginning of a scheduled window, so the first real user request hits a warm cache instead of paying cold latency. Anthropic supports a `max_tokens: 0` request for exactly this — it runs prefill, writes the cache, and returns immediately without generating. Don't pre-warm continuously-served prefixes; real traffic already keeps those warm and the extra write is pure cost.

## Verify with the usage fields — assuming is how this goes wrong

Every provider that offers caching reports what happened in the response's usage object, and the whole point of this section is that **you must look**. Caching fails silently. There is no error, no warning, no degraded-mode log line. A misconfigured cache and a perfectly configured one produce identical responses.

On the Claude API the three fields are:

| Field | Meaning |
| --- | --- |
| `cache_creation_input_tokens` | Tokens written to the cache this request — you paid the write premium |
| `cache_read_input_tokens` | Tokens served from cache — you paid the reduced rate |
| `input_tokens` | Tokens processed at full price |

The trap in that table: **`input_tokens` is the uncached remainder only, not the total.** Total prompt size is the sum of all three. Plenty of dashboards report `input_tokens` alone and make a well-cached agent look impossibly cheap, or make people think their 40k-token prompt shrank on its own.

Log the ratio, per request, from day one:

```python
u = response.usage
total = u.input_tokens + u.cache_creation_input_tokens + u.cache_read_input_tokens
hit_rate = u.cache_read_input_tokens / total if total else 0.0
log.info("cache", extra={
    "read": u.cache_read_input_tokens,
    "written": u.cache_creation_input_tokens,
    "fresh": u.input_tokens,
    "hit_rate": round(hit_rate, 3),
})
```

Then read the shape:

| What you see across repeated requests | What it means |
| --- | --- |
| `read` grows, `written` near zero after the first | Working as intended |
| `written` large on *every* request, `read` always zero | Your breakpoint is after the volatile part, or a silent invalidator is at the front |
| Both zero despite a marker | Prefix is below the provider's minimum cacheable length — this fails silently, with no error |
| `read` fine in dev, zero in prod | Per-instance variance: unsorted serialization, per-pod config, or a env-dependent system section |

When `read` is stuck at zero and you can't see why, stop guessing and diff the bytes. Serialize the full rendered request body for two consecutive calls, write both to disk, and run `diff` on them. The invalidator is always visible in that diff, and it's usually one line you'd never have suspected.

```python
import json, pathlib
pathlib.Path(f"/tmp/req-{n}.json").write_text(json.dumps(payload, indent=2, sort_keys=True))
# then: diff /tmp/req-1.json /tmp/req-2.json
```

Two more things worth knowing before you conclude your setup is broken. First, a cache entry generally can't be read until the request that writes it has started responding — so N parallel requests with the same prefix all miss. For fan-out, send one, wait for it to start streaming, then fire the rest. Second, caches are scoped to the model: switching models mid-conversation, even to a cheaper sibling for a sub-task, starts from cold. Spawn the cheap sub-task as its own call with its own prefix rather than swapping models inside the main loop.

## FAQ

**Do I need to change my prompts to use caching, or just enable it?**
You almost always need to change them. Enabling caching on a prompt that carries a timestamp, a request ID, or a per-user tool list at the front produces zero hits, because the reusable prefix is empty. The reordering is the feature; the flag just tells the provider you want it.

**Where exactly should the cache breakpoint go?**
At the end of the last section that is byte-identical across requests — not at the end of the prompt. If the block carrying your marker changes per request, every request writes a fresh entry and reads nothing, which costs more than no caching at all.

**Why is my cache hit rate zero even though nothing in my prompt changes?**
Check three things in order: whether your prefix is long enough to be cacheable at all (there is a provider-specific minimum, and being under it fails silently), whether your tool array or JSON serialization has nondeterministic ordering, and whether requests are arriving further apart than the cache lifetime. Then diff two rendered request bodies.

**Does a growing conversation break the cache?**
No — it's the best case. History grows at the end of the prompt, so each turn's prompt is a strict prefix of the next one, and the cached region keeps growing. What breaks it is editing the system prompt or tool list mid-conversation, which changes bytes ahead of the entire history.

**Should I cache retrieved RAG chunks?**
Not if they change per query — put them late, right before the question, and cache everything ahead of them. If a fixed corpus is shared across many queries, that's a stable document rather than per-query retrieval, and it belongs early where it will cache well.

---

*The prefix-matching mechanism, the render order, and the usage-field semantics described here are documented behaviour of the Claude API; the ordering advice and the debugging workflow are my own opinion, formed from getting this wrong. Cache lifetimes, price multipliers, minimum cacheable lengths, and breakpoint limits are provider- and model-specific and they change — verify every one of them against the current docs linked above rather than against this article.*
