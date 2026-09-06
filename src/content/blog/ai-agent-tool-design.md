---
title: "Designing tools an AI agent can actually use"
description: "An agent that misuses your tools is usually not a model problem. It is a naming problem, a schema problem, or an error-message problem — and all three are yours to fix."
seoDescription: "Practical guidance on designing tool definitions for LLM agents: naming, JSON Schema descriptions, granularity, error messages that teach, idempotency, and how to evaluate a tool set."
keywords:
  - llm tool design
  - function calling best practices
  - ai agent tools schema
  - mcp tool definition
  - llm tool error handling
  - agent tool granularity
category: "Analysis"
topic: "AI"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-10"
emoji: "🛠️"
tags: ["AI", "Agents", "Tool Use", "API Design", "LLM"]
sources:
  - name: "Tool use — Anthropic API documentation"
    url: "https://docs.anthropic.com/en/docs/build-with-claude/tool-use"
  - name: "Model Context Protocol — specification"
    url: "https://modelcontextprotocol.io/"
  - name: "Function calling — OpenAI API documentation"
    url: "https://platform.openai.com/docs/guides/function-calling"
  - name: "JSON Schema specification"
    url: "https://json-schema.org/"
  - name: "Building effective agents — Anthropic engineering"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
  - name: "OpenAPI Specification"
    url: "https://spec.openapis.org/oas/latest.html"
related:
  - slug: "ai-observability-tracing-llm-apps"
    title: "Observability for LLM apps: tracing a non-deterministic system"
  - slug: "ai-embeddings-choosing-a-model"
    title: "Choosing an embedding model: the questions that actually matter"
draft: false
---

The first agent I shipped had a tool called `query`. It took a string and returned rows. The model used it constantly, wrongly, and with growing desperation, because `query` told it nothing about what could be queried, what the schema was, or what a failure meant.

Renaming it `search_orders_by_customer_email` and giving the parameter a real description fixed most of the behaviour without touching the model or the prompt. That is the general shape of tool design: **the model's competence with your tools is mostly a function of how well you described them.**

## The definition is documentation for a reader who cannot ask questions

A tool definition is read once, cold, by something that cannot open your codebase or ping you on Slack. Everything it needs must be in the schema.

```json
{
  "name": "search_orders",
  "description": "Search a customer's orders by email address. Returns at most 50 orders, newest first. Only orders from the last 24 months are indexed — for older orders use fetch_order_archive. Returns an empty list if the customer has no orders; this is not an error.",
  "input_schema": {
    "type": "object",
    "properties": {
      "email": {
        "type": "string",
        "description": "Customer email, exactly as stored. Case-insensitive. Not a partial match — use search_customers first if you only have a name."
      },
      "status": {
        "type": "string",
        "enum": ["pending", "shipped", "delivered", "cancelled"],
        "description": "Optional filter. Omit to return all statuses."
      }
    },
    "required": ["email"]
  }
}
```

Four things in that definition are doing real work, and each corresponds to a failure I have watched happen:

- **The limit is stated.** Without "at most 50", a model asked to count a customer's orders will confidently report 50.
- **The boundary is stated.** "Last 24 months" plus a pointer to the other tool prevents the model from concluding an old order does not exist.
- **The empty case is stated.** Otherwise an empty result gets narrated to the user as a failure.
- **The parameter says what it is not.** "Not a partial match" prevents the loop where the model tries `"john"`, gets nothing, tries `"john%"`, gets nothing, and apologises.

Write descriptions for the failure modes, not for the happy path. The happy path is usually inferable from the name.

## Granularity: the trade-off nobody warns you about

Given a database, you can expose one tool (`run_sql`) or forty (`get_customer`, `list_orders`, `update_shipping_address`, …). Both are wrong at the extremes.

| Approach | Works well | Fails at |
| --- | --- | --- |
| One generic tool | Flexible, small definition set | Model must know your schema; errors are opaque; no way to constrain what it can do |
| Many specific tools | Clear intent, enforceable permissions, good errors | Tool list bloats the context; the model must pick among near-duplicates |

My working rule: **one tool per user-meaningful action, not per database operation.** "Cancel an order" is one tool even if it writes three tables. Meanwhile `get_customer_by_id` and `get_customer_by_email` should be one tool with an either/or parameter, because from the model's perspective they are one intent.

When the tool count passes roughly twenty, the problem shifts from description quality to selection: near-duplicate tools with similar descriptions get confused with each other. At that point either consolidate, or split the agent so each sub-agent sees only its own subset.

## Errors are a second chance to teach

The most under-used surface in agent design is the error return. A tool that fails with `{"error": "Invalid input"}` has wasted a turn. A tool that fails with a correction usually gets it right on the next call.

```python
# Poor
return {"error": "not found"}

# Better
return {
    "error": "no_customer_with_email",
    "message": "No customer found with email 'jon@example.com'. "
               "Check the spelling, or call search_customers with a partial "
               "name to find the correct address.",
    "did_you_mean": ["john@example.com"],
}
```

Rules I apply to every tool error:

- Say what was wrong with **the input**, not what happened internally. "Stack trace" is not actionable.
- Name the tool that should be called instead, if one exists.
- Include near-miss data when you cheaply can — the `did_you_mean` above turns two wasted turns into zero.
- Distinguish **retryable** from **terminal**. A rate limit should say "retry after 5 seconds"; a permissions failure should say "do not retry, tell the user."

That last point matters more than it sounds. Without it, an agent hitting a permission error will retry indefinitely with small variations, burning tokens and looking broken.

## Design for repetition and partial failure

Agents retry. They retry after timeouts they cannot distinguish from failures, and they retry when a previous step's output was ambiguous.

Make every mutating tool **idempotent or explicitly guarded**. Accept a client-supplied idempotency key, or return a clear "already done" rather than performing the action twice:

```json
{
  "status": "already_cancelled",
  "message": "Order 1182 was already cancelled at 2026-08-02T11:04Z. No action taken."
}
```

That response is far better than either silently succeeding or returning an error, because it tells the model the *desired end state holds* — which is what it actually wanted to know.

For anything genuinely destructive, do not rely on the model's judgement at all. Return a confirmation token that the tool requires on a second call, so that a human-facing layer can intervene between the two.

## Evaluate the tool set, not just the prompt

The uncomfortable part: you cannot tell whether a tool set is good by reading it. Build a small evaluation before you iterate.

1. Write 20-40 realistic user requests, including ones your tools **cannot** satisfy.
2. Record, for each: did the model pick the right tool, fill parameters correctly, recover from errors, and stop when it should?
3. Read the failures as design feedback, not model feedback.

The impossible-request cases are the ones people skip and the ones that matter most. A good tool set produces "I can't do that with the tools I have"; a bad one produces a confident wrong tool call. **If your agent never says it cannot do something, your evaluation set is too easy.**

When a failure appears, the fix is almost always one of: rename the tool, add a sentence to a description, merge two tools, or improve an error message. Prompt changes are the last resort, because they do not transfer when the tool is used by a different agent.

## FAQ

**Should descriptions include examples?**

One example in the description helps for tools with non-obvious formats (date ranges, query syntax). More than one usually means the schema itself should be clearer.

**How long can a description be?**

Long enough to prevent misuse; every token is context you spend on every request. A few sentences per tool and one per parameter is a reasonable budget.

**Do I need MCP for this?**

No — MCP is a transport and packaging standard for tools. The design principles here apply whether you expose tools through MCP, a provider's native function calling, or your own loop.

**Should tools return JSON or prose?**

Structured data for anything the model must reason over precisely; prose is fine for summaries. Be consistent, because mixed shapes make failures harder to parse.

**How do I stop an agent calling a tool in a loop?**

Cap the iterations in your loop, and make errors terminal where retrying cannot help. Do not rely on instructions alone.

---

*Tool-definition mechanics, JSON Schema structure and function-calling flows are documented in the provider and specification references linked above. The granularity rule, the error-message checklist, the idempotency guidance and the evaluation approach are my own judgement from building and debugging agent tool sets; model behaviour differs between providers and versions, so validate against the one you deploy.*
