---
title: "AI code review nobody mutes: the problem is precision, not capability"
description: "A reviewer bot that posts thirty comments on a pull request gets turned off within a week, and its three real findings die with the twenty-seven nits. Designing for precision: repo conventions instead of best practices, a hard comment cap, falsifiable findings, an adversarial refutation pass, and the one metric that tunes it."
seoDescription: "Design an AI code reviewer teams actually read: repo-specific conventions, diff-scoped context, a severity cap, falsifiable findings, a refutation pass, and action-rate tuning."
keywords:
  - ai code review
  - automated pull request review
  - llm code review precision
  - ai reviewer false positives
  - code review bot ci
  - github actions ai review
category: "Guide"
topic: "Developer Tooling"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-22"
emoji: "🔍"
tags: ["AI", "Code Review", "Developer Tools", "CI/CD"]
sources:
  - name: "GitHub Docs — GitHub Actions"
    url: "https://docs.github.com/en/actions"
  - name: "GitHub REST API — Pull request reviews"
    url: "https://docs.github.com/en/rest/pulls/reviews"
  - name: "GitHub Docs — Pull requests"
    url: "https://docs.github.com/en/pull-requests"
  - name: "Claude Code GitHub Action"
    url: "https://github.com/anthropics/claude-code-action"
  - name: "Dart — Linter rules"
    url: "https://dart.dev/tools/linter-rules"
related:
  - slug: "building-an-ai-agent-team-chief-of-staff-pattern"
    title: "The chief-of-staff pattern: turning scattered AI chats into an agent team"
  - slug: "what-the-research-says-about-prompt-engineering"
    title: "What the research actually says about prompt engineering — five claims, fact-checked"
draft: false
---

The failure mode is always the same. Someone wires an AI reviewer into CI on a Monday. It posts thirty comments on the first pull request: twenty-seven are variable naming, "consider extracting this into a helper", and a suggestion to add a test that already exists two files over. Three are real, and one of those is a genuine data-loss bug in a retry path.

Nobody finds the three. By Wednesday people scroll past the bot's review to reach the human one. By the following Monday it is a non-blocking check with notifications muted — a dead integration that still burns tokens on every push.

The bot was not bad at finding bugs. It found the bug. It was bad at **not saying things**, and in code review that is the entire job. A reviewer's budget is not compute, it is your teammates' willingness to keep reading, and that belief updates fast. If the first ten comments a developer reads contain one useful one, they have learned a rule — *skim it, it is usually nothing* — and that rule is applied to comment eleven, which is the data-loss bug. You did not fail to find it. You failed to get it read.

Which gives you an uncomfortable but load-bearing asymmetry: **a missed bug costs you less than a wrong comment.** A missed bug leaves you exactly where you were before the bot existed, with humans reviewing. A wrong comment costs a reader's attention and some of their trust, permanently, across every future comment. So the design problem is precision, not recall, and almost every knob worth turning is a knob that makes the bot say less.

## Anything a deterministic tool can decide must never reach the model

The largest single source of noise is a model re-deriving opinions a linter already holds, worse and less consistently. Push everything decidable down to a tool that is silent, fast, and fires in the editor before the PR exists.

| Question | Who should answer it |
| --- | --- |
| Is this formatted correctly? | `dart format` |
| Unused import, dead code, missing `await`? | `dart analyze` |
| Does this `await` leave a `BuildContext` unsafe? | the `use_build_context_synchronously` lint |
| Is this an unawaited future? | the `unawaited_futures` lint |
| Does the naming match the repo? | an analyzer rule or a `custom_lint` plugin |
| Does the retry path reuse its idempotency key after a cold restart? | the model |

If you can write it as a lint rule, write it as a lint rule. It never hallucinates and it never consumes review attention, because it never reaches the PR. The model's job is only the last row: defects that need two files and a sequence of events held in your head at once.

## Generic best practices are the noise generator

A model with no repo context falls back on the average of all code it has seen. That is how you get "consider adding error handling" on a function whose entire purpose is to propagate the error to a caller that handles it.

Fix this with a conventions file the reviewer reads on every run. The important part is not the rules — it is that **every rule carries an explicit counterexample**. The carve-out is what buys precision.

```markdown
## Error handling
Repository and data-source methods return `Result<T, AppError>`
(lib/core/result.dart). Throwing out of a repository method is a bug.
NOT A FINDING: `throw` inside a private helper the repository already
wraps, or anything under test/.

## Migrations
A change to a table under db/schema/ requires a paired file in
db/migrations/ in the same PR.
NOT A FINDING: a change to a view, or an index-only change.
```

Derive these from evidence, not taste. The best source is your own review history: pull the last few hundred human review comments off merged PRs, cluster them, keep what recurs across different reviewers. A rule a human has actually made three times is worth automating. A rule nobody has ever made is one you invented, and it will generate noise forever.

## Scope: the diff, plus exactly what the diff touches

Handing the model whole files is the second-biggest noise source, because it will review the parts nobody changed. Reviewers hate that more than they hate being wrong — the comment is often correct and still infuriating, because the author did not write that line and will not be fixing it here.

Assemble context deliberately: the changed hunks as a unified diff; for each symbol the diff modifies, its current definition and its call sites one hop out; the test file covering the changed file if one exists; the conventions file. Then tell the model that nothing else in the repository exists, and that unchanged code appears only as context and is never a legitimate target. That one instruction removes a large class of comments in a single line. And review the diff **since the last reviewed SHA**, not the whole PR again — otherwise every force-push reposts the same three comments and the thread becomes unreadable on its own.

## A hard cap, a deleted tier, and one falsifiable claim per finding

Severity without a cap is decoration. The cap is what forces the model to rank, and ranking is the behaviour you actually want.

| Tier | What it means | What happens |
| --- | --- | --- |
| **S1** | Data loss, corruption, auth bypass, a credential in the diff, a crash on a reachable path | Inline comment |
| **S2** | Contract break: exported API, serialized format, or a schema change without its migration | Inline comment |
| **S3** | Violates a rule written in the conventions file | Inline only if the cap has room |
| **S4** | Everything else — naming, readability, "consider extracting", perf hunches, test opinions | **Deleted** |

S4 is deleted, not collapsed into a details block. A collapsed section still trains people to open it, so it still costs attention, and it is exactly where the noise lives. If it is not worth an inline comment, it is not worth existing.

Make the cap a small fixed number — five is a reasonable start — and do **not** scale it with diff size. The cap is on the reader's attention, and their attention does not grow because your PR is bigger. If more than five S1/S2 findings survive, post five and say how many were suppressed: a PR with eight genuine correctness findings needs splitting, not a longer review.

Then the second half of the problem. "This could cause a race condition" is unfalsifiable, and unfalsifiable comments are the worst kind — the reader cannot dismiss one without doing work, so they either do the work and resent it or dismiss it and feel vaguely guilty. Force structure instead; make the model emit an object, not prose:

```json
{
  "file": "lib/sync/queue_flusher.dart",
  "line": 142,
  "severity": "S1",
  "claim": "Retried flushes generate a new idempotency key after the queue is re-hydrated from disk.",
  "trigger": "The app is killed mid-flush and restarts before the server's 2xx arrives.",
  "consequence": "The server treats the retry as a new request and creates a duplicate order.",
  "evidence": ["lib/sync/queue_flusher.dart:131-149", "lib/sync/queue_store.dart:88"],
  "falsifiable_by": "If QueueStore.hydrate() preserves item.idempotencyKey, this finding is wrong.",
  "confidence": 0.7
}
```

`falsifiable_by` is the field that does the work: it names **one** thing to check. The reviewer opens one file, looks at one method, and either fixes a real bug or closes the comment in ten seconds with no residue. Findings that cannot produce that line are, in practice, the vague ones — dropping them at the schema level is a free precision win. Render the comment leading with the trigger, not the abstraction:

> **S1 — duplicate order on restart-during-flush.** If the app is killed mid-flush and restarts before the 2xx arrives, `hydrate()` rebuilds the item without its original idempotency key, so the retry posts as a new request.
> *Wrong if:* `QueueStore.hydrate()` already restores `item.idempotencyKey`.

## Propose, then refute

The proposer prompt is mostly a list of prohibitions, which is the right shape for a precision-first tool.

```text
You are reviewing ONE pull request diff.

You are given:
  CONVENTIONS - the written rules of this repository.
  DIFF        - unified diff of the changed hunks only.
  CONTEXT     - for each changed symbol: its current definition, its
                callers one hop out, and its test file.
Nothing else in the repository exists as far as you are concerned.

Report a finding ONLY if all four hold:
  a. The defect is introduced or made reachable BY THIS DIFF.
  b. You can name a concrete trigger: an input, a sequence, a state.
  c. You can name the consequence in words an on-call engineer would use.
  d. Someone can prove you wrong by checking ONE thing that you name.

Never report:
  - anything `dart analyze` or `dart format` decides
  - style, naming, file layout, or "consider extracting"
  - missing tests, unless this diff changes a behaviour an existing test
    asserts and that test was not updated
  - performance, unless you can point at a loop bound or an allocation
    that scales with user-controlled input
  - anything on a line shown to you only as CONTEXT

Severity: S1 correctness/security, S2 contract break, S3 violates a rule
written in CONVENTIONS. Do not emit S4.

Output a JSON array, at most 8 objects, matching the schema below.
An empty array is a correct and common answer.
```

That last line earns its place. Without explicit permission to find nothing, models treat an empty result as failure to do the task and manufacture something to fill the silence.

Then the highest-leverage single change in the whole design, at the cost of one extra call per finding: a second pass whose only job is to destroy the findings. Give it the finding and the same context, but not the proposer's reasoning and not its confidence score, so it cannot anchor on the justification.

```text
You are the refuter. Below is a finding another reviewer proposed and the
exact context that reviewer was given. Your job is to KILL it.

Work through these in order:
1. Is the trigger reachable? Look for the guard that prevents it.
2. Is the consequence real, or handled downstream in the context shown?
3. Is the claim about a line this diff did not change?
4. Does CONVENTIONS explicitly permit this pattern?
5. Is the finding true but unverifiable from the context given - would
   checking it require reading code that is not here?

Return exactly: {"verdict": "KILL" | "SURVIVES", "reason": "..."}

Default to KILL. "I cannot verify this either way" is a KILL.
You are not scored on how many findings you let through.
```

Two details matter more than the wording. **The default must be KILL** — an unverifiable finding dies, because posting it makes a human do the verification you could not. And the refuter must be told it is not scored on throughput; without that, models drift toward letting things pass to seem agreeable. Case 5 is the one that surprises people: findings that are probably true but not checkable from the given context are the most expensive comments you can post, because they generate a long thread that ends in "actually that's fine, see the other service".

## Wiring it into CI without handing out your keys

Four stages, each a separate step so you can inspect the intermediate JSON when a bad comment escapes.

```yaml
name: ai-review
on: pull_request

permissions:
  contents: read
  pull-requests: write

jobs:
  review:
    runs-on: ubuntu-latest
    env:
      MODEL_API_KEY: ${{ secrets.MODEL_API_KEY }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Collect diff and one-hop context
        run: |
          tools/review/collect.sh \
            "${{ github.event.pull_request.base.sha }}" \
            "${{ github.event.pull_request.head.sha }}" > /tmp/context.json
      - run: tools/review/propose.sh /tmp/context.json > /tmp/proposed.json
      - run: |
          tools/review/refute.sh /tmp/context.json /tmp/proposed.json \
            > /tmp/survivors.json
      - run: tools/review/post.sh /tmp/survivors.json --max 5
```

**Post one review, not N comments.** The reviews endpoint accepts a `comments` array in a single request, so the author gets one notification instead of five. Send `"event": "COMMENT"`.

**Dedupe across pushes.** End each comment body with an invisible marker — `<!-- rv:sha256(file + normalized_claim) -->` — read existing comments before posting, and skip anything already there. Hash the path plus normalized claim text rather than the line number, because rebases break line-based deduping.

**Never check out fork code with a privileged token.** Workflows triggered by `pull_request` from a fork get a read-only `GITHUB_TOKEN` and no secrets, which is the protection you want. The tempting workaround is `pull_request_target`, which runs with the base repo's secrets — combining that with a checkout of the PR head hands your API keys to anyone who opens a pull request. For fork coverage, run the model in the restricted job and post from a separate `workflow_run` job that never executes fork code.

## Action rate is the only number that tunes anything

Comment count, findings per PR and "issues detected" are vanity. The metric that matters is the fraction of posted comments that cause a change:

**Action rate** = (comments whose anchored lines changed before merge, plus comments a human replied to in agreement) ÷ comments posted.

Instrumenting it is mechanical. Each comment already carries its finding ID in the dedupe marker. A job walks recently merged PRs, pulls review comments through the REST API, and for each one diffs the anchored file between the comment's commit and the merge commit to see whether the flagged range moved. Thread resolution state is available through GitHub's GraphQL API, but treat it as a weak signal — people resolve threads to clear the UI, not to signal agreement.

Then tune against it. Action rate falling: raise the bar — drop S3 entirely, lower the cap, raise the confidence floor. Action rate high but the bot nearly silent: you are over-filtering, so lower the confidence floor one notch and watch what comes back. Volume rising while action rate holds: the conventions file is earning its keep.

The aggregate is less useful than the breakdown. Group action rate **by the convention rule that produced the finding**, sort ascending, and delete the worst rule. A small number of rules usually produce most of the noise, and removing one is a bigger precision win than any prompt edit. My own threshold, and this is opinion rather than measurement: if fewer than half your posted comments produce a change, you are spending trust faster than you earn it, and the fix is to post less rather than to explain better.

## "The bot approved it" must never be a thing anyone can say

Silence from the reviewer has two possible causes: there was no defect, or the defect was outside what the reviewer could see. Those look identical from outside, and the whole design above makes the second one common — you scoped it to the diff, capped it at five, and told a refuter to kill anything it could not verify. Low recall is the price you agreed to pay.

**Do not let it emit `APPROVE`.** The reviews API takes `APPROVE`, `REQUEST_CHANGES` or `COMMENT`. Only ever send `COMMENT`. An approval is a social claim — that someone competent looked and will be associated with the outcome — and the tool cannot back it. **Do not let it satisfy a review requirement**: keep required reviewers and CODEOWNERS exactly as they were, because if the bot's check can turn a PR green, someone will eventually ship on it. And **do not let it block**. The only category with a real argument for blocking is a credential committed in the diff, and that is a deterministic secret scanner's job, not a model's. So in practice the bot blocks on nothing.

What it should be is a very good colleague who reads the diff first, says three things a quarter that save you a weekend, and is otherwise quiet. That is a much smaller product than the one people usually build, and it is the only version still installed six months later.

## FAQ

**Won't a cap of five make it miss real bugs?**
Yes, sometimes. That is the deliberate trade: a missed finding leaves you where you were before the bot existed, while a wrong finding permanently degrades how the next one is read. You are not replacing human review, so the floor is not zero — the humans are still there.

**Do I need a frontier model for this?**
The proposer benefits most from a strong model, since spotting a cross-file sequencing bug is the hard part. The refuter is a much narrower task — read a claim, check it against provided context, default to no — and is a reasonable place for a smaller model. Measure action rate before and after downgrading either one instead of guessing.

**Where do conventions come from if we've never written them down?**
From your merged PRs. Export the human review comments from the last few months, cluster them by theme, and keep what recurs across different reviewers. Write each as a rule plus at least one explicit "NOT A FINDING" counterexample, then delete any rule whose findings show a poor action rate after a few weeks.

**What about very large PRs or monorepos?**
Scope context by the CODEOWNERS path owning the changed files, and keep the cap per PR rather than per package. If more than five genuine S1/S2 findings survive refutation, the honest output is five comments plus a note that the PR is too large to review properly.

---

*The severity ladder, the five-comment cap and the fifty-percent action-rate threshold are my opinions, not measured results — starting points to tune against your own numbers. The GitHub Actions behaviour described (fork token restrictions, the reviews endpoint's `event` values, batching comments into one review) is documented, but CI platforms change; verify workflow permissions and API shapes against the current GitHub docs before shipping this.*
