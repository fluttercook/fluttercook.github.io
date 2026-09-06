---
title: "Observability for LLM apps: tracing a non-deterministic system"
description: "You cannot reproduce a bad answer by re-running the request. What you can do is capture enough of the run that you never need to. Here is what to record, what to sample, and what to leave out."
seoDescription: "How to instrument LLM applications: what to log per request and per step, OpenTelemetry spans for agent runs, cost and latency attribution, PII handling, sampling, and turning traces into an eval set."
keywords:
  - llm observability tracing
  - opentelemetry llm spans
  - agent debugging traces
  - llm cost tracking per request
  - prompt logging pii
  - llm evaluation from logs
category: "Guide"
topic: "AI"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-07"
emoji: "🔭"
tags: ["AI", "Observability", "Tracing", "LLM", "Operations"]
sources:
  - name: "OpenTelemetry — traces specification"
    url: "https://opentelemetry.io/docs/concepts/signals/traces/"
  - name: "OpenTelemetry semantic conventions for GenAI"
    url: "https://opentelemetry.io/docs/specs/semconv/gen-ai/"
  - name: "Messages API — Anthropic API documentation"
    url: "https://docs.anthropic.com/en/api/messages"
  - name: "Building effective agents — Anthropic engineering"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
  - name: "Structured logging — OpenTelemetry logs"
    url: "https://opentelemetry.io/docs/concepts/signals/logs/"
  - name: "OWASP Top 10 for LLM Applications"
    url: "https://owasp.org/www-project-top-10-for-large-language-model-applications/"
related:
  - slug: "ai-agent-tool-design"
    title: "Designing tools an AI agent can actually use"
  - slug: "ai-guardrails-prompt-injection-defense"
    title: "Prompt injection: what actually defends against it"
draft: false
---

"A customer says the assistant told them we offer a 90-day return window. We don't."

In a normal service you find the request, replay it, and read the code path. In an LLM application, replaying gives you a different answer, the retrieval may have changed, and the code path was identical for the thousand requests that behaved correctly. **The trace is not a debugging aid here; it is the only record that the event happened at all.**

## Record the whole run, not the endpoint

A single user message can produce a dozen model calls, retrievals and tool invocations. Logging only the final response tells you what went wrong and nothing about where.

Model the run as a trace with nested spans:

```
trace: conversation_turn          user_id, conversation_id, turn_index
├── span: retrieve                query, k, latency, chunk_ids, scores
├── span: llm_call                model, temperature, tokens_in/out, stop_reason
│   └── span: tool.search_orders  arguments, result_size, error, latency
├── span: llm_call                (second turn, after tool result)
└── span: guardrail_check         verdict, rule_id
```

The OpenTelemetry GenAI semantic conventions give you standard attribute names for the model-call spans, which is worth adopting even if you are not yet exporting to a tracing backend — naming things `gen_ai.request.model` rather than `model_name` means you can move to a standard tool later without rewriting instrumentation.

The attributes I regret not having, every time they are missing:

- **The prompt actually sent**, after templating — not the template. The bug is usually in the interpolation.
- **The retrieved chunk IDs and their scores**, not the concatenated context string. IDs let you ask "was the right document even retrieved?", which splits every RAG failure into two very different problems.
- **The full tool arguments and results.** Truncating these to 200 characters saves storage and destroys the trace's usefulness.
- **`stop_reason` or its equivalent.** A response cut off by a token limit looks like a bad answer and is a configuration bug.
- **The prompt or config version.** Without it, a regression after a deployment is unattributable.

## Cost and latency belong on the span

Every model call has a price, and in an agent loop the price is a function of a control-flow decision nobody reviewed. Attach tokens and cost to each span and aggregate up the trace:

```python
span.set_attribute("gen_ai.usage.input_tokens", usage.input_tokens)
span.set_attribute("gen_ai.usage.output_tokens", usage.output_tokens)
span.set_attribute("app.cost_usd", price(model, usage))
span.set_attribute("app.cache_read_tokens", usage.cache_read_input_tokens)
```

Then look at the **distribution**, never the mean. LLM latency and cost are heavily skewed: the p50 is fine and the p99 is a run that looped eleven times before giving up. Averages hide exactly the runs you need to see.

Two derived metrics I have found consistently worth alerting on:

- **Steps per run.** A rise means the agent is struggling — usually a tool started failing, or a description changed.
- **Cost per successful outcome**, not cost per request. Failed runs cost money too, and a change that reduces per-request cost while lowering the success rate is a regression.

## The privacy problem, faced directly

Prompts contain whatever the user typed, and retrieved context contains whatever is in your documents. A naive trace store is a copy of your most sensitive data in a system with weaker access controls than the original.

What has worked for me:

- **Redact at the point of capture**, not in a downstream job. A pattern-based redactor for emails, phone numbers, card-shaped digits and national IDs, applied before the span leaves the process.
- **Store content and metadata separately.** Metadata — durations, token counts, chunk IDs, error codes, verdicts — is not sensitive and can be retained for a long time. Content is sensitive and should have a short retention.
- **Reference, don't copy.** Store chunk IDs rather than chunk text; the text is already in your document store, with its own access controls.
- **Make full-content capture opt-in per environment**, and default it off in production. A sampled subset plus explicit capture for flagged conversations covers most debugging needs.
- **Give users a deletion path** that actually reaches the trace store. If a deletion request cannot remove traces, you have a compliance problem regardless of what your policy document says.

## Sampling without losing the failures

Full-fidelity tracing of every run is expensive at volume. Uniform sampling is the wrong reduction, because it discards failures at the same rate as successes, and failures are the entire point.

Use tail sampling: buffer the trace, decide at the end.

```python
def should_keep(trace):
    if trace.had_error or trace.guardrail_triggered:
        return True
    if trace.steps > STEP_THRESHOLD or trace.cost_usd > COST_THRESHOLD:
        return True
    if trace.user_feedback in ("thumbs_down", "reported"):
        return True
    if trace.latency_ms > LATENCY_P99:
        return True
    return random.random() < 0.02   # baseline for the healthy population
```

Keep the 2% baseline. Without a sample of successful runs you have no comparison, and every anomaly looks significant.

## Close the loop: traces become your eval set

This is the part teams skip, and it is where the payoff is.

Every production failure is a test case you did not have to invent. A workflow that works:

1. A user reports a bad answer, or a guardrail fires, or feedback is negative.
2. The trace is pulled, reviewed, and the correct behaviour is written down.
3. The inputs — the user message, the retrieved chunks, the tool results — become a fixture in your evaluation set.
4. Every prompt or model change runs against that set before deployment.

Six months of this produces an evaluation suite grounded in things that actually went wrong, which is far more valuable than any set of cases you could brainstorm up front. **A team without this loop is re-fixing the same class of failure indefinitely**, because nothing prevents a change from reintroducing it.

## FAQ

**Do I need a dedicated LLM observability product?**

Not to start. Structured logs with a trace ID, queried in whatever you already run, cover a surprising amount. Adopt standard attribute names early so migrating is cheap.

**How long should I keep traces?**

Metadata for months; full content for days to weeks, driven by your privacy posture. Promote anything that became an eval fixture into a separate, permanent store.

**Should I log the system prompt on every call?**

Log its version or hash on every call, and the full text once per version. Repeating a long system prompt on every span is expensive and adds nothing.

**How do I trace streaming responses?**

Start the span at request time, end it when the stream completes, and record time-to-first-token separately — it is the latency the user actually perceives.

**What about traces for evaluation runs?**

Instrument them identically and tag the environment. Being able to compare a failing eval case with the production trace it came from is worth the small extra work.

---

*OpenTelemetry trace concepts and the GenAI semantic conventions are documented in the references linked above; attribute names in that specification evolve, so check the current version before standardising on them. The attribute checklist, the sampling policy, the privacy practices and the traces-to-evals loop are my own judgement from operating LLM applications in production.*
