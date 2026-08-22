---
title: "Context engineering: a big window is not permission to fill it"
description: "Frontier models now take a million tokens of input. That changed what is possible, not what is wise. A practical method for deciding what goes into the context, in what order, and what to cut first when it overflows."
seoDescription: "How to decide what goes into an LLM's context window: ordering, compaction, reasoning context vs reference material, and a worked token budget for an agent."
keywords:
  - context engineering
  - llm context window
  - what to put in context window
  - prompt caching prefix order
  - context compaction llm agent
  - token budget for ai agent
category: "Guide"
topic: "AI Engineering"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-22"
emoji: "🪟"
tags: ["AI", "LLM", "Context Engineering", "Agents", "RAG"]
sources:
  - name: "Claude Docs — Context windows"
    url: "https://platform.claude.com/docs/en/build-with-claude/context-windows"
  - name: "Claude Docs — Prompt caching"
    url: "https://platform.claude.com/docs/en/build-with-claude/prompt-caching"
  - name: "Claude Docs — Context editing"
    url: "https://platform.claude.com/docs/en/build-with-claude/context-editing"
  - name: "Claude Docs — Compaction"
    url: "https://platform.claude.com/docs/en/build-with-claude/compaction"
  - name: "Claude Docs — Token counting"
    url: "https://platform.claude.com/docs/en/build-with-claude/token-counting"
  - name: "Claude Docs — Tool search tool"
    url: "https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool"
related:
  - slug: "cutting-ai-costs-free-tiers-caching-and-routing"
    title: "Using AI without burning cash: free tiers, caching, and routing"
  - slug: "building-an-ai-agent-team-chief-of-staff-pattern"
    title: "The chief-of-staff pattern: turning scattered AI chats into an agent team"
draft: false
---

The context window on frontier models is now a million tokens. That is roughly a mid-sized codebase, or a few hundred pages of documentation, or a very long afternoon of agent tool calls. The obvious reaction is to stop thinking about what to include and just include everything — dump the schema, the whole README, all forty tools, the full conversation, and let the model sort it out.

That works right up until it doesn't, and when it stops working it does so quietly. The model doesn't error. It answers, confidently, using the wrong one of the three conflicting config files you pasted. Latency creeps from four seconds to twenty. The bill goes up on every single turn, not once, because the API is stateless and you resend the whole thing each time. Nothing in your logs says "too much context" — you just have an assistant that feels slightly dumber than it did last month.

**Context engineering** is the discipline of deciding what occupies that window. It is not prompt engineering — prompt wording is a small part of it. It's closer to cache design or working-set management: you have a fixed, expensive, per-turn resource, and everything you put in it competes with everything else for the model's attention.

Here is how I budget it, in the order I actually make the decisions.

## The window is a budget you choose, not a bucket you fill

The first mental shift: the model's maximum context is a hard limit set by the vendor. Your **working budget** is a soft limit you set yourself, and it should be much smaller.

Three separate things get worse as you approach the maximum, and they get worse independently:

**Cost scales with every turn, not with the conversation.** A 300K-token context in turn 12 of an agent loop is not a one-time 300K charge — it's 300K tokens re-sent on turn 12, and roughly that much again on turn 13. Long agent runs are quadratic in tokens with respect to turn count unless you actively intervene. This is the failure mode people notice first, usually on an invoice.

**Latency scales with input length.** Time to first token grows with how much there is to read. An agent that makes fifteen tool calls pays that growing prefill cost fifteen times. Caching helps enormously here, which is a large part of why cache design and context design are the same problem.

**Relevance gets diluted.** This is the one that's hard to see. A model has to locate the material that matters among the material that doesn't. Adding a document that is 90% irrelevant to the current question doesn't add 10% of a document's worth of value — it adds a full document's worth of things to disambiguate against. Near-duplicates are the worst offenders: two versions of the same config, an old and a new API signature, a deprecated function next to its replacement. The model has no reliable way to know which one you meant, and it will sometimes pick the wrong one.

That third effect is why "just put everything in" degrades quality and cost *at the same time*. They aren't a tradeoff you're navigating. They're the same mistake.

## Reasoning context and reference material are different things

The single most useful distinction in this whole subject: some material the model must **reason with**, and some it only needs to **look up**.

Reasoning context is everything the model needs held simultaneously in mind to produce a correct answer. If you're asking it to reconcile two API designs, both designs have to be in the window. If you're asking it to fix a bug, the failing test and the function under test both have to be there. You cannot retrieve your way out of this — the reasoning genuinely requires the pieces side by side.

Reference material is everything it might need, conditionally, depending on where the reasoning goes. The full error-code table. The other 200 files in the repo. The changelog for the last two years. This material should not be in the window. It should be behind a tool.

```typescript
// Not this: 40K tokens of API reference in the system prompt, every turn.
// This: a tool the model calls only when it actually needs a symbol.
const tools: Anthropic.Tool[] = [
  {
    name: "lookup_api",
    description:
      "Look up the signature and docs for one symbol in the SDK reference. " +
      "Use when you need exact parameter names or types. Returns one entry.",
    input_schema: {
      type: "object",
      properties: { symbol: { type: "string" } },
      required: ["symbol"],
      additionalProperties: false,
    },
    strict: true,
  },
];
```

The trade is real and worth naming: a tool call costs a round trip, and the model sometimes fails to call it when it should. A stuffed context costs tokens on every turn forever. For anything consulted occasionally, the tool wins by a wide margin. For anything consulted on essentially every turn, inline it and cache it.

A useful test: **if you can't say which specific question in the last ten turns this material answered, it belongs behind a tool.**

The same logic applies to tool definitions themselves. Thirty tool schemas is easily several thousand tokens of context that sit in front of every request, and a model choosing among thirty tools is measurably worse at choosing than one picking among six. Anthropic's tool search tool exists for exactly this: mark rarely-used tools `defer_loading: true` and let the model search for them, keeping only the common ones resident. (At least one tool must stay non-deferred, and the search tool itself can never be deferred, or the request is rejected.)

## Order is not cosmetic

Context is rendered into one flat sequence. For the Claude API that order is `tools` → `system` → `messages`, and two separate mechanisms make the ordering matter.

The mechanical one is caching. Prompt caching is a **prefix match**: the cached region runs from the start of the request to your breakpoint, and a single changed byte anywhere before that point invalidates everything after it. Cached reads cost roughly a tenth of normal input tokens; writing the cache costs about 1.25x. So the payoff arrives on the second call, and everything after that is close to a ninety percent discount on the stable portion.

That gives you a hard rule: **most stable first, most volatile last.** Frozen system prompt, then a deterministically ordered tool list, then long-lived retrieved documents, then conversation history, then the user's actual question. A timestamp or a request ID injected into the system prompt is the classic silent cache killer — no error, no warning, just a permanently cold cache and a bill that never drops.

```typescript
const response = await client.messages.create({
  model: "claude-opus-5",
  max_tokens: 16000,
  system: [
    { type: "text", text: FROZEN_INSTRUCTIONS },
    { type: "text", text: retrievedDocs, cache_control: { type: "ephemeral" } },
  ],
  messages: [
    ...history,
    // Volatile material goes after the last breakpoint, never before it.
    { role: "user", content: `Today is ${today}.\n\n${question}` },
  ],
});
```

The behavioural mechanism is subtler. Instructions placed far from the end of a long context compete with everything that follows them for the model's attention. The practical consequence is that the *actual task* — the thing you want done right now — should be the last thing in the window, stated plainly, not buried at the top of a system prompt written six months ago. If you have constraints that keep getting ignored on long contexts, moving them to the final user turn is the first thing to try. On models that support mid-conversation system messages, that's a cleaner channel for the same job: it carries operator authority without editing the cached prefix.

## A worked budget for an agent

Concrete example. A support agent that reads internal documentation, queries a ticketing system, and drafts replies. The model's window is a million tokens. I'm going to give it a working budget of **60,000**.

That number isn't timidity, it's a design decision: 60K is the point where this particular agent still has everything it needs and nothing it doesn't. Going to 200K wouldn't make it better at anything, it would make each of its ten-to-twenty turns three times more expensive and slower to start.

| Slot | Budget | Cached? | What lives here |
| --- | --- | --- | --- |
| System instructions | 2,000 | Yes | Role, escalation policy, tone rules, refusal boundaries |
| Tool definitions | 4,000 | Yes | 6 resident tools; 20 more behind tool search |
| Retrieved documentation | 20,000 | Yes (per session) | Top 6–8 chunks for this ticket's topic |
| Conversation + tool results | 30,000 | Partially | Rolling; compacted on a schedule |
| The current task | 1,000 | No | The ticket, the customer's last message, today's date |
| Headroom | ~3,000 | — | Slack for a long tool result before the next compaction |

Two things about this table are more important than the numbers.

First, **the largest slot is the one you control least.** Conversation history and tool results grow on their own, unbounded, in a way the other slots don't. That's where all your engineering effort should go. A system prompt that's 2,000 tokens instead of 3,000 saves you nothing worth having; a tool-result strategy that keeps history at 30K instead of 150K is the whole game.

Second, **retrieval has a fixed slot, and the slot is the point.** "Top 6–8 chunks" is a budget, not a quality target. If your retriever returns twenty chunks and you pass all twenty because they scored above threshold, you don't have a budget — you have a leak. Set the slot size first and let it force the reranking to actually rank.

## What to cut first when it overflows

It will overflow. Here's the order I remove things, cheapest damage first:

1. **Raw tool-result bodies from old turns.** A file the agent read nine turns ago, a 4,000-token API response it extracted one field from. The *fact* that the call happened matters; the payload almost never does. This is usually 60–80% of the overflow and costs essentially nothing to lose.
2. **Retrieved chunks the model never referenced.** If a chunk hasn't been quoted, cited, or acted on across several turns, it was a retrieval miss. Drop it.
3. **Duplicated and superseded material.** Three revisions of the same file, the pre- and post-edit versions. Keep the current one. This one improves quality when you cut it, not just cost.
4. **The middle of the conversation.** Summarise it. The opening turns carry the task definition and the recent turns carry the state; the negotiation in between compresses well.
5. **Tool definitions for tools this session hasn't touched.** Move them behind deferred loading.
6. **Reference documentation.** Move it behind a lookup tool, accepting the extra round trips.
7. **The system prompt.** Last, and by rewriting it, never by truncating it. Truncation cuts your safety and escalation rules, which are usually at the end.

Note what's *not* on this list: the current task, the last few turns, and the material the model is actively reasoning with. If you find yourself cutting those, the working budget was set wrong or the task is too big for one context and needs to be split across sub-agents.

## Compaction is a scheduled step, not a rescue

Most teams write compaction as an emergency handler: catch the context-length error, panic-summarise, retry. That's the worst possible time to do it, because you're now summarising under a deadline, with no budget left, using whatever crude heuristic you wrote at 2am.

Treat it as a normal part of the loop instead. Two mechanisms exist and they do different jobs:

**Context editing clears.** It removes old tool results (and optionally thinking blocks) outright — no summarisation, no extra model call. Cheap, deterministic, and the right default for tool-heavy agents where old payloads are pure noise.

```typescript
const response = await client.beta.messages.create({
  model: "claude-opus-5",
  max_tokens: 16000,
  betas: ["context-management-2025-06-27"],
  context_management: { edits: [{ type: "clear_tool_uses_20250919" }] },
  tools,
  messages,
});
```

**Compaction summarises.** When the conversation itself carries meaning that clearing would destroy — decisions made, constraints discovered, things the user corrected — you need a summary, not a delete. Server-side compaction handles this automatically as the conversation approaches a threshold.

```typescript
const response = await client.beta.messages.create({
  model: "claude-opus-5",
  max_tokens: 16000,
  betas: ["compact-2026-01-12"],
  context_management: { edits: [{ type: "compact_20260112" }] },
  messages,
});

// Append the whole content array. The compaction block is state — extract
// only the text and you silently lose it, and the next request recompacts.
messages.push({ role: "assistant", content: response.content });
```

The failure mode worth internalising: if you're hand-rolling this, your summariser must preserve **decisions and constraints**, not narrative. "The user wants a REST API" is worth keeping. "The assistant then explained the difference between REST and GraphQL" is not. Most naive summarisers get this backwards because they optimise for readability rather than for what the next turn needs.

## Measure it, or you are guessing

Two numbers make all of this observable, and both are cheap.

**Token counts before you send.** The counting endpoint is free and exact, which beats every character-based estimate you might write.

```typescript
const { input_tokens } = await client.messages.countTokens({
  model: "claude-opus-5",
  system,
  tools,
  messages,
});
if (input_tokens > WORKING_BUDGET) {
  messages = await compact(messages, input_tokens - WORKING_BUDGET);
}
```

**Cache hit rate after.** `usage.cache_read_input_tokens` should be substantial and stable on every repeat request. If it's zero across calls that share a prefix, something in that prefix is moving — a date, a UUID, a `Set` iterated in nondeterministic order, a tool list assembled from an object's keys. Log the ratio of cache reads to fresh input tokens per request and alert when it drops. It is the single best proxy for "did someone break the context layout", and it usually catches the regression in the same deploy that caused it.

If you track one thing beyond those, track **tokens per completed task** rather than tokens per request. Context engineering that cuts per-request tokens but causes the agent to need four more turns has made things worse, and per-request metrics will tell you it made things better.

## FAQ

**Does a bigger context window make RAG obsolete?**

No, it changes what retrieval is for. When windows were small, retrieval was a workaround for capacity. Now it's a relevance filter — the job is deciding which 20K tokens of your corpus deserve to compete for the model's attention on this specific question. That job doesn't disappear when the window grows; if anything the discipline matters more, because nothing forces you to be selective any more.

**Is it better to summarise history myself or use server-side compaction?**

Start with the server-side version — it's one config field, it triggers automatically, and it handles the bookkeeping. Roll your own when you have domain structure worth preserving that a generic summariser won't know about, such as an explicit list of confirmed requirements or a state machine the agent is walking. If you do roll your own, keep decisions and constraints verbatim and compress everything else.

**How much should I actually put in the system prompt?**

Less than you want to. The system prompt should hold things that are true on every single turn: role, hard boundaries, output format, escalation rules. Anything conditional — "if the user asks about billing, here are the refund tiers" — is reference material and belongs behind a tool or in retrieval. Long system prompts also tend to accumulate rules written for an older model that now actively hurt, so re-read yours whenever you upgrade models.

**Why does my agent ignore an instruction that's clearly in the context?**

Usually position and competition. An instruction buried at token 4,000 of a 90,000-token context is competing with 86,000 tokens of other material, much of which may implicitly contradict it. Move the constraint to the final turn, remove whatever is contradicting it, and shrink the context. If it still gets ignored after that, it's a wording problem, not a context problem — and that's when prompt engineering is the right tool.

**Do these API details apply to providers other than Anthropic?**

The mechanisms do — prefix caching, ordering effects, retrieval as a relevance filter, summarise-don't-truncate. The specific parameter names, beta headers, and cache economics in this article are Anthropic's, and they change. Every major provider offers some form of prefix caching with similar prefix-match semantics, but check your own provider's docs for minimum cacheable lengths and discount rates before designing around them.

---

*The budget table and the cut-order list are my working defaults, not measured optima — treat them as a starting shape to tune against your own traffic. The API parameters, beta headers, and cache pricing multipliers are current as of writing and are exactly the kind of thing that changes; verify against the linked documentation before you ship.*
