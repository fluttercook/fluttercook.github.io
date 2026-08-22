---
title: "Agent memory: files, a vector store, or just a bigger context window"
description: "Memory is three different problems sharing one name — recalling a fact, recalling a decision, recalling a procedure. Each wants a different mechanism, and picking the wrong one is why your agent confidently repeats a mistake from March."
seoDescription: "Files vs vector store vs context window for AI agent memory: what each is genuinely good at, a write policy, the staleness problem, and a hybrid index design."
keywords:
  - ai agent memory
  - vector store vs files
  - context window as memory
  - agent memory design
  - rag retrieval failure modes
  - memory staleness llm
category: "Analysis"
topic: "AI Engineering"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-22"
emoji: "🗃️"
tags: ["AI", "AI Agents", "Memory", "RAG", "Context Engineering"]
sources:
  - name: "Anthropic — Effective context engineering for AI agents"
    url: "https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents"
  - name: "Anthropic — Building effective agents"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
  - name: "Claude Code — Manage Claude's memory"
    url: "https://docs.claude.com/en/docs/claude-code/memory"
  - name: "pgvector — vector similarity search for Postgres"
    url: "https://github.com/pgvector/pgvector"
  - name: "SQLite — FTS5 full-text search"
    url: "https://sqlite.org/fts5.html"
related:
  - slug: "building-an-ai-agent-team-chief-of-staff-pattern"
    title: "The chief-of-staff pattern: turning scattered AI chats into an agent team"
  - slug: "cutting-ai-costs-free-tiers-caching-and-routing"
    title: "Using AI without burning cash: free tiers, caching, and routing"
draft: false
---

Someone asks how to give their agent memory, and the answers arrive as a shopping list: a vector database, a summarisation step, a bigger context window, maybe a knowledge graph if the conversation has gone on long enough. All of these are real mechanisms. None of them is an answer, because the question hasn't been split yet.

"Memory" names three unrelated problems. Recalling **a fact the user stated** — they deploy from `main`, they hate emoji in commit messages, their staging database is the one in `eu-west-1`. Recalling **a decision the agent made** — in March it moved checkout state off Riverpod, and there was a reason. Recalling **how a task is normally done** — the release runbook, the five steps before opening a PR, the thing you always forget about code signing.

These have different shapes. A fact is short, stable, and there is exactly one right answer. A decision is a small document with a date and a rationale, and its value is mostly in the rationale. A procedure is an ordered list that must be retrieved *completely* — half a runbook is worse than none, because the agent will confidently execute steps one through four and stop.

Give all three to the same mechanism and at least two of them get served badly. Below is what each mechanism is actually good at, what a sane write policy looks like, why staleness eventually breaks every memory system, and a hybrid that has the useful property of being fixable by a human at 11pm.

## Plain files are the only memory a human can repair

A file-backed memory is a directory of markdown that the agent reads and writes, loaded either wholesale or by explicit path. Claude Code's `CLAUDE.md` is this idea in its smallest form: a file that gets prepended to the session, with the tooling to import other files and to append new lines to it.

The usual argument for files is that they're simple. That's true and it's not the important part. The important part is that a file is **greppable, diffable, and editable by a human**:

- `grep` beats semantic search when you know the token you're looking for — a filename, a flag, an error string. Exact match has no false neighbours.
- `git diff` shows you what your agent decided to believe this week. A vector store gives you no such review surface; embeddings changed and you'll find out through behaviour.
- When a memory is wrong, you open it and delete the line. Thirty seconds, no re-embedding, no eventual consistency, no wondering whether the old vector is still in there.

That third property is worth more than retrieval quality, and it's the one that gets discounted in design discussions because it isn't a feature you can benchmark. A memory system's failure mode is not "it retrieved nothing." It's "it retrieved something wrong and the agent acted on it." Recovery time from that state is the metric that matters, and files win it by a wide margin.

The limits are real. Files don't scale to a hundred thousand documents, and a directory that has grown past what fits comfortably in context needs an index or a search step in front of it — which is the hybrid at the end of this post. But the ceiling is much higher than people assume, because useful long-term memory is small. A year of genuinely durable facts about one person and one codebase is not megabytes.

## What a vector store is genuinely good at

Vector search answers one question well: *what in this corpus is about the same thing as this query, even though it uses different words?* That's a real capability and nothing else on this list has it. If the user says "the thing we did about slow scrolling on cheap Androids" and the note is titled "jank on low-end devices," embeddings find it and `grep` does not.

So the honest use cases are:

- A corpus too large to read — support tickets, meeting transcripts, a documentation set, years of chat logs.
- Queries phrased by a human who does not know the corpus's vocabulary.
- Recall where **approximately right is useful** — surfacing candidates a person or the agent will then verify.

The failure mode is structural, not a tuning problem. Similarity search returns the top *k* neighbours of the query vector, always. There is no "nothing here is relevant" result, because the ranking is relative. Ask about a decision you never recorded and you get the three most similar decisions you *did* record — same domain, same vocabulary, plausible tone, wrong answer. An agent has no reliable way to tell that apart from a hit, and it will cite it in the same confident voice.

Two ways this bites specifically in agent memory:

**Procedures get chunked.** A runbook split into 400-token chunks retrieves as steps 2, 3 and 6. The agent has no signal that steps 4 and 5 exist. Anything ordered and complete-or-nothing is a bad fit for chunked retrieval — store it as one document and fetch it whole by name.

**Facts get outvoted.** "Deploys go through `make release`" is one short sentence competing against a long thread where three deploy commands were discussed and rejected. Length and topical density drive similarity; correctness doesn't participate.

If you do want vectors, note that you probably don't need a dedicated database. [pgvector](https://github.com/pgvector/pgvector) puts them in the Postgres you already run, next to the rows they describe, inside the same transaction and the same backup. And a plain keyword index — [SQLite FTS5](https://sqlite.org/fts5.html) — handles more agent-memory queries than its reputation suggests, because agents search for identifiers far more often than for vibes. Hybrid keyword-plus-vector retrieval beats either alone often enough that starting with keyword-only and adding vectors when you can point at the queries it misses is a defensible order of operations.

## The context window is memory you rent by the token

Stuffing everything into the prompt is the most tempting option, because it needs no infrastructure and it has the best possible retrieval quality: the model isn't retrieving at all, it's reading. For a single session that ends when you close the tab, this is correct and you should stop engineering.

As a memory system it has three problems.

It is the **most expensive** per unit of recall. You pay for every token on every turn, including the four hundred lines of context that turn out to be irrelevant to this particular question. Caching softens this considerably — repeated prefixes get billed at a reduced rate — but caching rewards a *stable* prefix, and memory that grows every session is the opposite of stable. Every append invalidates the cache from that point on, which is a real argument for keeping the always-loaded portion small and letting it change rarely.

It is the **least durable**. The window is per-session. A summarisation or compaction step preserves *something* across the boundary, but a summary is lossy in a specific and unhelpful way: it keeps narrative and drops identifiers. The exact table name, the exact flag, the exact error string are precisely the tokens a summariser judges as noise, and precisely the ones you needed.

And more context is **not monotonically better**. Long inputs dilute attention; a critical instruction sitting in the middle of a very long prompt competes with everything around it, and irrelevant-but-plausible material actively pulls the model toward wrong answers. "Just use a bigger window" trades a retrieval problem for an attention problem and calls it a solution.

| | Plain files | Vector store | Context window |
|---|---|---|---|
| Best at | exact recall, human editing | fuzzy recall over a large corpus | reasoning over what's already loaded |
| Human can fix it | open and edit the line | re-embed and hope | not applicable |
| Reviewable | `git diff` | no | no |
| Cost shape | ~free to store, tokens to load | infra + embedding calls | per-token, every turn |
| Durability | permanent | permanent | session only |
| Signature failure | file grows until nobody reads it | three plausible-but-wrong neighbours | truncation and dilution |

## Write policy: most of what an agent learns is not worth keeping

The mechanism debate is loud, but the thing that determines whether a memory system stays useful after two months is the **write policy** — and almost nobody writes one down. An agent left to decide for itself what to remember will remember everything, because everything felt important at the moment it happened.

The distinction that holds up: persist **stable preferences and decisions**, not **episodic detail**.

Worth writing: "prefers `make release` over raw build commands." "Checkout state is deliberately plain `InheritedWidget`, not Riverpod — see the decision note." "Do not touch `lib/legacy/` without asking."

Not worth writing: "the user asked me to fix a null check in `cart_page.dart`." That's the transcript's job. It's true, it's specific, and it will never again change what the agent should do — which is the actual test.

A policy small enough to paste into a system prompt:

```text
Write to memory only when ALL of these hold:
- It will still be true next month.
- It changes what you would DO, not just what you would say.
- It cannot be re-derived from the repo in under a minute.
- The person would recognise the one-line version as theirs.

Never write: file contents, command output, anything containing a
credential, or a narration of what happened this session.

Format: one line, present tense, with the reason if there is one.
Bad:  "We talked about state management and decided some things."
Good: "Checkout uses InheritedWidget, not Riverpod — the provider
       graph was rebuilding the payment sheet. 2026-03-11."
```

Two more rules that only become obvious after a system has rotted:

**Prefer editing over appending.** When a new fact contradicts an old one, the agent should replace the line, not add a second one. Memory that only grows accumulates contradictions, and a retriever handed two contradictory lines will cheerfully return the older one.

**Attribute everything.** A memory whose provenance is "the user said so" outranks one whose provenance is "I inferred this from the code once." Keep the date. You will need it in the next section.

## Staleness: the memory that names a file that no longer exists

Every memory system's real failure isn't retrieval — it's a memory that was accurate in February and is now a lie. The note says configuration lives in `lib/config/env.dart`. That file was split three months ago. The agent reads the memory, doesn't find the file, and either invents a plausible replacement or "helpfully" recreates it.

There's no clean solution, but there are cheap partial ones.

**Make memories verifiable and then verify them.** A memory that mentions a concrete path can be checked mechanically. Run this in CI, or at the start of a session, and you catch the loudest class of rot for free:

```bash
# Every file path quoted in memory/ that no longer exists on disk
grep -rhoE '`[A-Za-z0-9_./-]+\.(dart|md|ya?ml|json|sh|ts)`' memory/ \
  | tr -d '`' | sort -u \
  | while read -r p; do
      [ -e "$p" ] || echo "stale reference: $p"
    done
```

**Date every entry and let the agent see the date.** A retrieved memory rendered as `2026-03-11 — checkout uses InheritedWidget` carries a signal that the same text without a date does not. It doesn't stop the model from trusting old information, but it gives it something to weigh, and it gives *you* something to sort by when pruning.

**Tie memory lifetime to what it describes.** A memory about a person's preferences ages slowly. A memory about a file's location ages exactly as fast as the file moves. If you only have budget for one rule, make it this: prefer memories about *intent* over memories about *layout*. "Config is centralised in one module, not scattered per-feature" survives a refactor. "Config is in `lib/config/env.dart`" does not.

**Prune on read, not on a schedule.** Nobody runs the quarterly memory cleanup. But an agent that just discovered a memory was wrong is holding the exact information needed to fix it, and that is the moment to make the correction cheap — one edit to one file, in the same session, with the human right there.

## The hybrid: an index of pointers, detail on demand

Here's the arrangement that survives contact with a real project. One index file, loaded every session, containing nothing but one-line claims and pointers. Everything else is on disk and fetched by name when a line turns out to matter.

```markdown
# memory/INDEX.md — loaded at the start of every session

## Preferences (stable, from the user)
- Releases go through `make release`, never a raw build command.
- Summaries as tables, not bullet lists.
- Never modify `lib/legacy/` without asking first.

## Decisions (one line + where the reasoning lives)
- 2026-03-11 Checkout state stays InheritedWidget, not Riverpod.
  → decisions/2026-03-checkout-state.md
- 2026-05-02 Impeller on iOS only; Android stayed on the old path.
  → decisions/2026-05-impeller.md

## Procedures (fetch whole, never chunked)
- Cutting a release → runbooks/release.md
- Adding a locale → runbooks/i18n.md
- Rotating signing keys → runbooks/signing.md
```

Why this shape works:

**The index is small enough to always load.** No retrieval step, no similarity threshold, no chance of missing a fact because the query was phrased oddly. The always-on portion is a page, not a library.

**One line is enough to decide.** The agent doesn't need the reasoning behind the Riverpod decision to *avoid re-litigating it* — it needs to know the decision exists. It opens the linked file only when it's actually about to touch checkout state.

**Procedures stay whole.** `runbooks/release.md` is fetched by path, in full, in order. No chunk boundary can eat step 4.

**A human can audit it in a minute.** Read twelve lines, delete the two that are wrong. Try that with an embedding index.

**It degrades honestly.** If the index has no line about deployment, the agent finds nothing and says so — instead of retrieving the three most deployment-adjacent things it knows and improvising.

Add vector search on top when you have a corpus the index can't summarise — thousands of past conversations, a large document set — and keep it as a *supplement* to the index rather than a replacement for it. The index carries what must never be missed; similarity search carries what's merely nice to find.

## Matching mechanism to problem

Back to the three problems, now with answers:

| Problem | Mechanism | Why |
|---|---|---|
| A fact the user stated | one line in the always-loaded index | short, must never be missed, must be human-editable |
| A decision the agent made | one dated line + a linked note | the line prevents re-litigation, the note carries the reasoning |
| How a task is normally done | a whole file fetched by path | ordered and complete-or-nothing; chunking is the bug |
| Anything in a corpus too big to index | keyword search first, vectors if it misses | approximate is fine when a verification step follows |

The uncomfortable implication is that the sophisticated component is the least important one. The index file and the write policy do most of the work, and they're both plain text. That's not a reason to skip the vector store when you genuinely have a big corpus — it's a reason not to start there, because a vector store on top of no write policy is a faster way to retrieve the wrong thing.

## FAQ

**Do I need a vector database for agent memory at all?**
Only if you have a corpus a human wouldn't want to read — thousands of tickets, transcripts, or documents. For one person and one codebase, a directory of markdown plus keyword search covers nearly everything, and it's repairable when it's wrong. Add vectors when you can name the specific queries keyword search is failing.

**Isn't loading a memory file every session wasteful compared to retrieving only what's needed?**
It's cheaper than it looks if you keep it to a page and keep it stable, because a stable prefix caches well while a retrieval step adds latency, an embedding call, and a chance of missing the one line that mattered. Retrieval earns its keep on the detail files, not on the index.

**How do I stop the agent writing junk to memory?**
Give it an explicit write policy with a "will this still be true next month" test, and make writes visible — memory in git, reviewed in a diff like any other change. An agent that can write memory without review will eventually write something that quietly changes its behaviour, and you'll debug it as a model regression.

**What about summarising the conversation into memory automatically?**
Summaries are fine for narrative and bad for identifiers — they preserve "we discussed the deploy process" and drop the exact command. If you auto-summarise, extract structured claims rather than prose, and require every claim to be a full sentence that stands alone outside the conversation that produced it.

**Should the agent be allowed to delete memories?**
Yes, and it's more important than letting it add them. A system that can only append accumulates contradictions until retrieval becomes a coin flip. Pair deletion with version control so any wrong removal is one `git revert` away.

---

*The mechanism descriptions here — how similarity search ranks, how prefix caching behaves, what chunking does to ordered documents — are stable properties, but the specific tooling around agent memory moves fast, so check current provider documentation before wiring anything up. The index-plus-pointers design and the write policy are opinion, drawn from what tends to rot first; treat them as a starting shape to argue with, not a spec.*
