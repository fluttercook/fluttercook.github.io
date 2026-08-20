---
title: "Free AI coding agents: how to use OpenCode's free models without regretting it"
description: "OpenCode ships genuinely free hosted models with no API key. Here's what the free tier actually costs you, which work belongs on it, and the escalation ladder that keeps the bill sane."
seoDescription: "A practical guide to OpenCode Zen's free models: request limits, what the data-training policy means for your code, what never to paste into a free tier, and when to escalate to paid models."
keywords:
  - opencode free models
  - free ai coding agent
  - opencode zen
  - free llm for coding
  - ai coding agent data privacy
  - opencode vs claude code
  - free tier ai coding limits
category: "Guide"
topic: "AI Coding"
level: "Beginner"
author: "Trung Hieu"
publishDate: "2026-08-20"
emoji: "🆓"
tags: ["AI", "AI Agents", "OpenCode", "Developer Tools", "Security"]
sources:
  - name: "OpenCode — the open source AI coding agent"
    url: "https://opencode.ai/"
  - name: "OpenCode Zen — model list, pricing and free models"
    url: "https://opencode.ai/zen"
  - name: "OpenCode docs — free AI coding agents guide"
    url: "https://open-code.ai/en/guides/free-ai-coding-agents"
draft: false
---

The barrier to trying an AI coding agent used to be an API key and a credit card. [OpenCode](https://opencode.ai/) removed both: its Zen gateway ships hosted models you can select and start using immediately, at no cost and with no key.

Which means the last excuse for not learning how agentic coding works is gone. It also means a lot of people are about to point a free model at a private repository without thinking about what that involves.

Both things are worth taking seriously. Here's what the free tier is actually good for, what it costs you in a currency that isn't money, and how to structure your work so you're not paying for a frontier model to rename variables.

## What "free" means here

Three separate things get bundled under the word, and they have different limits:

**The tool is free.** OpenCode itself is open source. There's no cap on the client, no seat licence, no metering. Bring your own API key from any provider and it behaves like any other agent harness.

**The hosted models are free with a quota.** [OpenCode Zen](https://opencode.ai/zen) is the built-in gateway. Its free tier runs at **$0/month with roughly 100 requests per day**, no credit card, access to the Zen model lineup. The models are grouped into tiers rather than sold individually — a default tier with large context, an advanced tier with the largest context window, and a fast tier with a small context window and much lower latency.

**Free is not unlimited, and it is not private.** Those are the two things people skip, and they're the two that matter.

### The quota is smaller than it sounds

100 requests a day sounds generous until you watch an agent work. A single "fix this failing test" can burn five to fifteen requests as the agent reads files, runs the suite, edits, re-runs, and reads the error again. Agentic loops consume requests in bursts.

Practically: expect a handful of real tasks per day, not a full workday of continuous agent use. That's fine for learning. It is not a workflow you can commit to a deadline.

### Your code is the other price

This is the part that deserves a flat statement rather than a footnote: **on the free tier, prompts and completions are generally retained and used to improve future models.** That is the business model. One model in the lineup is documented as never storing or training on your data — if privacy is the requirement, that's the one to check for and verify against the current docs, because these policies change.

There's a saying that gets repeated here — if you're not paying for the product, you're the product — and in this case it's not a metaphor. The payment is your code.

Note also that model names and free-tier composition churn *fast*. The lineup shifted twice in the months before this was written. Treat any specific model name you read in a blog post, including this one, as a snapshot. Check [the Zen model list](https://opencode.ai/zen) for what's actually free today, and check the data policy at the same time.

## What never goes into a free-tier model

Not a vague "be careful." A list:

- **Credentials of any kind** — API keys, tokens, passwords, connection strings, `.env` contents, private keys
- **Private source you don't own the disclosure rights to** — employer code, client code, anything under NDA
- **Customer data** — real user records, PII, anything from a production database
- **Internal documents** — architecture docs, contracts, roadmaps, incident write-ups
- **Anything under a compliance regime** — health, financial, or regulated data

The rule underneath: **if you'd need permission to email it to a stranger, don't paste it into a model whose retention policy you haven't read.**

One trap specific to agents rather than chat: an agent reads files you didn't explicitly hand it. Point it at a repo root and it may read `.env`, `config/secrets.yml`, or a fixture full of real customer records — none of which you meant to send. Chat models only see what you paste; agents see what they open.

So before running any agent, free or paid, on a repo you didn't create for the purpose:

```bash
git ls-files | grep -Ei '\.env|secret|credential|\.pem$|\.key$|token'
```

Anything that turns up should be in `.gitignore`, in an ignore file the agent respects, or moved out of the tree entirely.

## The escalation ladder

The useful mental model isn't free-versus-paid. It's three tiers, matched to what a task actually needs:

| Tier | Use it for | Why |
| --- | --- | --- |
| **Free** | Learning the tool, side projects, throwaway scripts, exploring an unfamiliar codebase, bulk mechanical edits | Zero cost, and the failure mode is a wasted retry |
| **Paid mid** | Real work — daily feature development, bug fixing, refactors, review | Reliability and rate limits you can plan around; data handling you can point at in writing |
| **Frontier** | Genuinely hard problems — subtle concurrency bugs, architecture decisions, large multi-file refactors, anything where being wrong is expensive | Costs real money per task; worth it exactly when a wrong answer costs more |

Most people get this backwards in both directions. They run frontier models on boilerplate, and they run free models on the gnarly bug that's eaten two days. Both waste money — one in tokens, one in your time.

**The tell for escalating:** if you've re-prompted three times and the answer is still wrong in the same way, the model isn't the bottleneck you think it is. Either escalate a tier, or — more often — your prompt is missing context the model can't infer. Try the context first; it's free.

## Getting genuinely useful work out of a free tier

Free models are smaller and less patient. Adapt the work to fit rather than expecting them to behave like a frontier model.

**Give it a smaller job.** "Refactor the auth module" is a frontier-model task. "In `auth/session.py`, extract the token-refresh logic into its own function and update the two call sites" is a free-model task. Smaller scope also burns fewer requests, which matters when you have a hundred.

**Point at files explicitly.** Letting an agent discover which files matter costs requests and often goes wrong with a smaller model. Naming the three files it needs saves both.

**Batch mechanical work.** Renames, adding type hints, converting a test suite from one assertion style to another, writing docstrings from existing signatures — this is exactly what free models are good at, and the results are cheap to verify.

**Read a codebase with it.** One of the best uses of a free tier is asking a fast model to explain an unfamiliar repo. "Trace what happens when a request hits `/api/orders`" is low-risk, high-value, and doesn't need frontier reasoning.

**Use the fast tier for fast things.** The small-context fast tier is genuinely better for quick lookups and single-file edits than the big-context tier — lower latency, and context you don't use is context that can distract.

## The other free option

Worth knowing about: **Hermes Agent** is also free and works over messaging — you drive the agent from Telegram or Discord rather than a terminal. Different ergonomics entirely. If the appeal is kicking off a task from your phone and reading the result later, that's a better fit than a CLI. The same data-handling caution applies, with an extra wrinkle: a chat platform keeps its own copy of everything you send.

## A starting setup that won't burn you

1. **Install OpenCode.** Setup is genuinely a couple of minutes.
2. **Start on a repo you own** and that contains nothing confidential. Not the work monorepo. A side project.
3. **Check the current free lineup and its data policy** at [opencode.ai/zen](https://opencode.ai/zen) before your first real task, not after.
4. **Run the secret sweep** above on any repo before pointing an agent at it.
5. **Do three real tasks** — a bug fix, a small refactor, an explain-this-code session. That's enough to know whether the tool fits how you work.
6. **When you find yourself relying on it**, move to a paid mid-tier model. The moment agent output goes into work someone pays for, both the rate limit and the retention policy stop being acceptable.

Step 6 is the one people postpone, usually until a rate limit hits mid-sprint. Move before that, not after.

## The honest summary

The free tier is an excellent way to learn and a bad way to ship. That isn't a criticism — it's what a free tier is for, and OpenCode is unusually upfront about the trade.

Learn on free. Work on paid. Escalate to frontier only when a task is genuinely hard. And read the retention policy before the first prompt, not after you've pasted something you can't unpaste.

## FAQ

**Is OpenCode itself free, or just the models?**
The tool is open source and unmetered. Zen's free tier is the hosted-model part, with a daily request cap. You can also plug in your own API key from any provider.

**How many requests do I actually get?**
The free tier is documented at roughly 100 requests per day. Agent loops consume several requests per task, so plan on a handful of substantial tasks rather than continuous use.

**Is my code used for training?**
On the free tier, generally yes — prompts and completions are retained and used to improve models. At least one model in the lineup is documented as excluded from this. Verify against the current docs, because these terms change.

**Can I use it for client work?**
Not on a free tier with a training-retention policy, unless the client has explicitly agreed in writing. Use a paid tier with contractual data handling.

**Which free model should I start with?**
Start on the default tier for general coding, switch to the advanced tier when a task needs more context or more reasoning, and use the fast tier for quick single-file work. Specific model names change often — check the current list rather than trusting any blog post, including this one.

**Is a free model good enough to learn agentic coding?**
Yes, and that's the strongest argument for it. Learning how to scope tasks, supply context, and verify output transfers completely to paid models. The skill is the durable part, not the model.

---

*This piece expands on a note circulating in Vietnamese developer communities about OpenCode's free models, whose central warnings — free isn't unlimited, your data trains the next model, never paste secrets — are the right ones. Model names and quotas here reflect what was published at the time of writing and change frequently; the links go to the current source of truth.*
