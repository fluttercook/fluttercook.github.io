---
title: "Lovable left Next.js in 6 months: the numbers, and the parts you can actually reuse"
description: "Lovable moved its whole product from Next.js on Vercel to TanStack Start on Cloudflare workerd in six months. Median TTFB down 49%, dev server 5x lighter — and one 11-minute OOM incident. What's worth copying, and what isn't."
seoDescription: "An analysis of Lovable's migration from Next.js to TanStack Start on Cloudflare workerd: six months, five route groups, median TTFB down 49%, the 128 MB per-isolate ceiling, and what a small team should take from it."
keywords:
  - lovable next.js tanstack start
  - migrate off next.js
  - tanstack start cloudflare workers
  - v8 isolate 128mb limit
  - framework agnostic architecture
  - incremental frontend migration
category: "Analysis"
topic: "Web Engineering"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-08-21"
emoji: "🚚"
tags: ["Web", "Next.js", "TanStack", "Cloudflare", "Architecture"]
sources:
  - name: "Lovable — How we migrated lovable.dev away from Next.js"
    url: "https://lovable.dev/blog/how-we-migrated-lovable-dev-away-from-nextjs"
  - name: "TanStack Start"
    url: "https://tanstack.com/start"
  - name: "Cloudflare Workers — platform limits (memory, CPU, isolates)"
    url: "https://developers.cloudflare.com/workers/platform/limits/"
  - name: "MDN — View Transition API"
    url: "https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API"
draft: false
---

Lovable published the log of their migration: off Next.js on Vercel, onto **TanStack Start running on Cloudflare workerd**. Six months for the code, two more for the rollout, on a product serving tens of millions of visitors.

The original is worth reading in full — [How we migrated lovable.dev away from Next.js](https://lovable.dev/blog/how-we-migrated-lovable-dev-away-from-nextjs). This isn't a retelling of it. I'm taking the published numbers and then separating the two things a "we switched frameworks" post usually blends together: **the part that only makes sense at their scale**, and **the part a five-person team can use next week**.

## Why they moved, and why the reason isn't "Next.js is bad"

Three motives, none of them a complaint about the framework:

1. **Dogfooding.** Lovable generates apps for users, and those apps run on Lovable's own worker infrastructure. The main product ran on something else. Every time the platform had a rough edge, the product team wasn't the first to feel it.
2. **Single-app scale.** The main site is one large app under heavy load — a genuinely different problem from the "60 million small apps" one their platform had already solved.
3. **Stack consolidation.** Two runtimes, two deploy models, two sets of internal tooling. That cost doesn't show up on an invoice; it shows up per engineer.

The architectural detail worth noting on the platform side: every published user app runs as **its own worker in a V8 isolate**, with an entry worker dispatching by hostname and isolates reused under an LRU policy. The efficiency numbers from that model are exactly what made pulling the main product onto the same runtime attractive.

## The numbers

This is the part that gets misquoted most, so here it is as published:

| Metric | Before | After |
| --- | --- | --- |
| Build time | 12+ min | 6–9 min |
| TTFB (median) | — | **−49%** |
| TTFB (p90) | — | initially **2× worse**, settled at −16% |
| Dev server memory | ~8 GB | ~1.5 GB |
| Dev server startup | ~70 s | ~10 s |
| Requests served per isolate | under 10 | 500 – 10,000 |
| Codebase size | 350K lines | 910K lines |
| Custom build plugins | 0 (Next.js shipped them) | **17** |

The last two rows are the most honest lines in that table, and the two most often dropped when this story gets retold.

**p90 was initially twice as bad.** The median improved immediately; the tail got worse before it got better. If the only thing on your dashboard is the median, you'll declare victory while your slowest cohort is eating the regression.

**17 build plugins.** That's the real price of leaving a batteries-included framework. You don't delete complexity, you move it from something someone else maintains to something you maintain. For Lovable the trade buys runtime control, which they need. For most teams it's 17 new things that can break at 2 a.m.

## How they did it: cut along user journeys, not along folders

This is the most transferable engineering in the whole story, and almost none of it is about which framework won.

**A proxy worker in front of everything.** It routes per-route *and* per-user, so the same URL can land on the old or the new stack depending on who you are. That's the precondition for percentage rollouts without forking the whole app.

**Five route groups, split by user journey.** Not by "which pages are easiest to port" but by "move one complete user flow across". That keeps a single user, within a single session, mostly on one stack.

**About 90% of the code was pushed out of the framework.** Everything shared lives behind a `#shared/` alias, and a **lint rule** forbids it from importing framework-specific APIs. This is my favourite detail: the architectural boundary is enforced by something that fails CI, not by a promise in `CONTRIBUTING.md`.

**Platform dependencies became adapters.** Interfaces plus dependency injection, wired through TypeScript path aliases. The framework becomes a thin shell calling into the core, instead of the core growing roots into the framework.

**The sticky things were replaced early.** `next/font`, `next/image`, auth, i18n — all pulled out up front, while still on Next.js. Smart: those are exactly the dependencies that, left to the end, turn the last day into a big-bang cutover.

**Feature flags must be deterministic.** The same user always gets the same decision. A flag that rolls per request will bounce people between stacks mid-flow.

**View Transitions API to hide the seam.** Navigating between the two stacks is a hard navigation — a real browser load. View Transitions make that jump look like an SPA transition. This trick generalises to any incremental migration, including migrating off Rails onto anything.

**AI agents worked in capped batches.** Plans were capped at 12 PRs of roughly 800–1600 lines each. That ceiling isn't about agent throughput — it's the size a human can still review.

## Memory is the real constraint, not CPU

This is where the isolate model diverges most from ordinary Node, and the section I suspect most people will skim and then pay for later.

Under isolates, the **memory ceiling is 128 MB per isolate**, and isolates are reused across requests. Anything you hold at module scope stays there — multiplied by however many apps share that isolate.

Three tactics, in order of payoff:

- **Parse large JSON inside the request handler, not at module top level.** Same data, different placement, 2–12× less memory. Module-scope objects live forever; handler-scope ones get collected.
- **Drop API fields you don't use.** You pay memory for every field you fetch and ignore.
- **Keep client-only bundles off the server.** Their expensive example: the TypeScript compiler is about 9 MB of code but roughly **18 MB of memory** once loaded.

And then the incident:

> At 20% rollout of the dashboard, error rates hit 50%. The cause wasn't the new code — an unrelated static JSON file had pushed isolates past the 128 MB ceiling. Fixed in 11 minutes.

Look closely at the shape of that failure. The change that caused it **wasn't in the thing being rolled out**. Memory is a shared resource inside the isolate, so it breaks the comfortable assumption that a 20% rollout puts 20% of users at risk. Eleven minutes is what it costs a team that already had the right dashboard and a real kill switch.

## What about "AI writes better code on TanStack Start"?

They report that agents hallucinate less on the new codebase, and attribute it to consistency: Next.js has been through several very different API generations (pages router, app router, major-version shifts), so the training data is full of mutually contradictory patterns for the same question.

I think the mechanism is right but the conclusion over-generalises. What makes agents wrong isn't "Next.js" — it's **multiple valid ways to do the same thing coexisting in reach**. A consistent Next.js codebase that only uses the app router, with lint rules blocking legacy patterns, will give agents a far better hit rate than a TanStack Start codebase written in five styles. That variable is under your control without changing frameworks at all.

Put bluntly: if you're considering a stack change *so that AI writes fewer bugs*, try enforcing consistency first. It's a great deal cheaper than six months.

## Should you do this? Almost certainly not

The conditions that made this rational for Lovable:

- They **already** operated worker infrastructure for tens of millions of user apps. The destination runtime wasn't new to them.
- Their main product ran on a different stack than the one they sell — a real strategic cost, not an aesthetic one.
- They had the headcount to maintain 17 build plugins and a proxy layer while still shipping features.

If those three aren't true for you, the arithmetic inverts. Six months of a product team is a quarter and a half with no new features, traded for a TTFB improvement your users may not be able to measure.

## The parts worth taking, even if you change nothing

Four things I'd lift from this today:

1. **Build a `#shared/` boundary and enforce it with lint.** It's the cheapest insurance against framework lock-in there is. You don't need to know where you're going — you just need the core not rooted anywhere. Doable in a sprint, valuable whether or not you ever migrate.
2. **Put platform dependencies behind interfaces.** Storage, auth, images, email. Not for the marketing sense of "swap providers easily", but so your logic is testable without standing up the world.
3. **Roll out along user journeys, behind deterministic flags.** True of any risky change, not just framework migrations. And put **p90 and p99** on the dashboard, not just the median.
4. **Treat memory as the first-order constraint if you run on edge/serverless.** "Parse in the handler, not at module scope" applies right now on Cloudflare Workers, Vercel Edge, Deno Deploy — anywhere isolates are reused.

One closing observation that isn't in the original: the codebase went from 350K to 910K lines. Some of that is six months of new features, but it can't all be. Leaving a batteries-included framework means writing those batteries yourself. That 910K is the true shape of the bill, and it deserves to sit next to "median TTFB down 49%" every time this story gets retold.

## FAQ

**Is TanStack Start a drop-in replacement for Next.js on new projects?**
For client-heavy apps that want runtime control and edge deployment, it's worth serious consideration. What you give up is convention: you assemble more yourself. Lovable had to write 17 build plugins — treat that number as a fair signal of how much assembly to expect.

**Is the 128 MB per-isolate limit a hard number?**
It's the memory ceiling for a Worker isolate on Cloudflare. Check Cloudflare's current limits documentation for your plan before designing around it — platform limits move over time.

**Is incremental migration always better than a rewrite?**
When the finish line keeps moving — that is, when the product must keep shipping during the migration — yes. A single-shot rewrite only wins if you can freeze the product, and very few teams can freeze for six months.

**Why did p90 regress while the median improved?**
The median reflects the warm path: isolate ready, caches hot. The tail reflects cold starts, isolates evicted from the LRU, and routes not yet tuned. A runtime change improves the warm path first and the cold path later.

---

*All figures here are as published by Lovable in the [original post](https://lovable.dev/blog/how-we-migrated-lovable-dev-away-from-nextjs); the analysis, pushback and recommendations are mine. Cloudflare's platform limits change over time — verify against the official docs before designing around any number in this article.*
