---
title: "What the research actually says about prompt engineering — five claims, fact-checked"
description: "Five viral claims about prompt engineering, checked against the papers they cite. Two hold up, three don't — and the real findings are more useful than the folklore."
seoDescription: "Fact-checking five popular prompt engineering claims against real research: leading questions and sycophancy, chain-of-thought vs persona prompts, hallucinated citations, multi-constraint failure, and few-shot examples."
keywords:
  - prompt engineering research
  - does chain of thought still work
  - persona prompting research
  - llm sycophancy leading questions
  - multi constraint prompting failure
  - prompt engineering best practices 2026
  - ai hallucinated citations neurips
category: "Deep Dive"
topic: "Prompt Engineering"
level: "Beginner"
author: "Trung Hieu"
publishDate: "2026-08-20"
emoji: "🔬"
tags: ["AI", "Prompt Engineering", "LLM", "Research", "ChatGPT", "Claude"]
sources:
  - name: "Tag Questions and the Generational Reversal of Sycophancy Across 45 Language Models (arXiv 2607.23976)"
    url: "https://arxiv.org/abs/2607.23976"
  - name: "When \"A Helpful Assistant\" Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models (arXiv 2311.10054)"
    url: "https://arxiv.org/abs/2311.10054"
  - name: "Large Language Models as Optimizers — the \"take a deep breath\" paper (arXiv 2309.03409)"
    url: "https://arxiv.org/abs/2309.03409"
  - name: "GPTZero — hallucinated citations in NeurIPS 2025 accepted papers"
    url: "https://gptzero.me/news/neurips/"
  - name: "Compound Deception in Elite Peer Review: A Failure Mode Taxonomy of 100 Fabricated Citations at NeurIPS 2025 (arXiv 2602.05930)"
    url: "https://arxiv.org/abs/2602.05930"
  - name: "Instruction Stacking Collapse: A Benchmark and the Capability-Dependent Value of Prompt Compilation (arXiv 2608.02639)"
    url: "https://arxiv.org/abs/2608.02639"
  - name: "When Instructions Multiply: Measuring and Estimating LLM Capabilities of Multiple Instructions Following (arXiv 2509.21051)"
    url: "https://arxiv.org/abs/2509.21051"
  - name: "Order Matters: Investigate the Position Bias in Multi-constraint Instruction Following (arXiv 2502.17204)"
    url: "https://arxiv.org/abs/2502.17204"
  - name: "SEQUOR: A Multi-Turn Benchmark for Realistic Constraint Following (arXiv 2605.06353)"
    url: "https://arxiv.org/abs/2605.06353"
draft: false
---

A summary of "the science behind prompt engineering" has been going around, built on five research findings. It is a good list of ideas. But the numbers attached to them are the kind that get copied from post to post without anyone opening the paper, so I opened the papers.

Two of the five claims check out. Three do not — at least not in the form they are being repeated. In one case the real research points in the *opposite* direction from the advice.

That is not a reason to throw the list away. The underlying advice is mostly sound. But if you are going to change how you work based on a study, it is worth knowing which study, and what it actually measured.

Here is each claim, what I could verify, and what I would actually do about it.

## Quick summary

| Claim | Verdict |
| --- | --- |
| Leading questions push models toward the answer you implied | ✅ Confirmed |
| "Think step by step" now loses to a short role prompt (IBM, 430,000 evaluations) | ❌ Study not found — and persona research points the other way |
| ~1 in 4 audited NeurIPS 2025 papers had a fabricated citation (Microsoft, 2.6M references) | ⚠️ Real problem, wrong numbers |
| Models collapse past ~3 simultaneous constraints (Meta, 15 models) | ⚠️ Effect is real and well-documented; that specific study, not found |
| Removing examples raised accuracy from 74% to 83.8% (EPFL/Apple/Mistral) | ❌ Could not verify |

## 1. Don't ask "…right?" — this one is real

**The claim:** a Cornell Tech study tested 45 models, changed only a few words of the question, and found that phrasing like "X is the better choice, right?" drags the answer toward X.

**Verdict: confirmed.** The paper is [*Tag Questions and the Generational Reversal of Sycophancy Across 45 Language Models*](https://arxiv.org/abs/2607.23976). A "tag question" is exactly that trailing `…, right?` or `…, isn't it?`. The study holds the substance of the question fixed and varies only the tag, across 45 models, and measures how much the agreement rate moves.

The interesting wrinkle the popular summary drops: the effect is not uniform across model generations. Newer models do not simply behave better — the pattern reverses in places. So "modern models are less sycophantic" is not a safe assumption either.

**What to do about it.** Strip the answer out of your question. The difference is not subtle:

```text
❌ Renting is the smarter move for someone in my situation, right?
✅ Compare buying vs renting for my situation: 32, freelance income
   averaging $4k/month with 30% variance, $60k saved, planning to
   stay in this city 3+ years. State which assumptions drive
   your answer most.
```

The second version has more words but fewer instructions. That is the point — you gave it facts to reason over, not a conclusion to ratify.

This applies far beyond life advice. `Is this the right way to structure this API?` invites agreement. `Critique this API structure against the alternatives you'd consider` invites work.

## 2. "Think step by step" vs a short role — the claim doesn't hold up

**The claim:** IBM ran 430,000+ evaluations over 8 prompt styles, found that "think step by step" underperformed a plain question, and that the winner was a question plus a short role like *"from the perspective of a reliability engineer."*

**Verdict: I could not find this study.** Searching for it turns up nothing matching the description or the evaluation count. If it exists, it is not where the summaries say it is.

More importantly, the closest well-documented research points the **other way** on the persona half. [*When "A Helpful Assistant" Is Not Really Helpful*](https://arxiv.org/abs/2311.10054) (Findings of EMNLP 2024) tested persona system prompts systematically across many roles and factual QA tasks, and found they do **not** reliably improve accuracy — in several settings the persona-prompted score came in *below* the plain baseline. Follow-up work has repeatedly reproduced the same shape: telling a model it is an expert does not make it more accurate on questions with verifiable answers.

So the popular advice — "drop step-by-step, add a role" — is, on current evidence, half unsupported and half backwards.

**Where the underlying instinct is still right.** The first half of the claim gestures at something real. The famous "take a deep breath and work through this step by step" line comes from [*Large Language Models as Optimizers*](https://arxiv.org/abs/2309.03409), and the original summary is correct that it was discovered on PaLM 2-L in 2023. That was an era where the model would not decompose a problem unless you asked. Current reasoning models decompose by default, and bolting the phrase on top adds nothing.

**What to do about it:**

- Don't add "think step by step" to a reasoning model. It already does.
- Do use it with small/fast models, or when you specifically need the intermediate steps visible so you can check them.
- Treat personas as **tone and audience control, not accuracy control.** "Explain this like a reliability engineer briefing an exec" is a legitimate instruction about register and framing. It is not a way to make the model know more.

That last distinction is the practical one. Personas shape *how* the answer reads. They do not shape *whether it is true*.

## 3. Confident ≠ correct — right conclusion, wrong numbers

**The claim:** Microsoft audited 2.6 million references and found roughly 1 in 4 audited NeurIPS 2025 papers contained at least one AI-fabricated citation.

**Verdict: the phenomenon is thoroughly documented; those figures are not.** The audit everyone is actually referring to is [GPTZero's](https://gptzero.me/news/neurips/), not Microsoft's. It scanned 4,841 of the ~5,290 papers accepted at NeurIPS 2025 and confirmed **100+ hallucinated citations across 51 papers**.

That is closer to 1% of papers than 25%. Which is a very different number — and still alarming, because every one of those papers cleared peer review with at least three reviewers.

The follow-up taxonomy paper, [*Compound Deception in Elite Peer Review*](https://arxiv.org/abs/2602.05930), is the more useful read. It classifies the 100 fabrications and the distribution tells you what to watch for:

| Failure mode | Share |
| --- | --- |
| Total fabrication — paper doesn't exist at all | 66% |
| Partial attribute corruption — real paper, wrong authors/year/venue | 27% |
| Identifier hijacking — real DOI pointing at the wrong work | 4% |
| Placeholder hallucination — literal "Firstname Lastname" | 2% |
| Semantic hallucination — real citation, doesn't support the claim | 1% |

**What to do about it.** Note that 27% + 4% = **31% of fabrications involve a real, findable paper**. Those are the dangerous ones. A search that returns *something* feels like verification and isn't.

So the check has to be specific:

1. Does the paper exist? (Search the exact title.)
2. Are the **authors and year** right? This is where a third of the errors live.
3. Does the paper actually **say the thing it is cited for**? Open it and find the sentence.

Step 3 is the one people skip, and it is the reason this very article exists — the claims I am fact-checking all *sounded* like they had sources.

## 4. Don't stack ten rules into one prompt — real effect, unverified source

**The claim:** Meta tested 15 models with 1–12 requirements per prompt. At 8 requirements, per-requirement compliance was ~41%, all-8-at-once was ~5.7%, and 12 of 15 models became unstable past 3 requirements.

**Verdict: I could not find that specific study,** but the effect it describes is one of the better-documented failure modes in current LLM research. Several 2025–2026 benchmarks measure it directly:

- [*Instruction Stacking Collapse*](https://arxiv.org/abs/2608.02639) stacks 24 verifier-checked instructions, applying 1 to 20 at a time, across production models. Follow rate degrades **non-linearly** as the stack grows — the drop accelerates rather than sloping gently.
- [*When Instructions Multiply*](https://arxiv.org/abs/2509.21051) measures and estimates capability as instruction count rises.
- [*SEQUOR*](https://arxiv.org/abs/2605.06353) shows the same degradation across long multi-turn conversations, and finds it gets substantially worse when constraints arrive *sequentially over time* rather than all at once — which is exactly how real conversations work.
- [*Order Matters*](https://arxiv.org/abs/2502.17204) finds position bias within multi-constraint prompts: **where** a constraint sits in your prompt affects whether it survives.

So: don't quote "41% and 5.7%." But absolutely act on the finding, because the direction is not in dispute, and the SEQUOR result means it applies to your ongoing chats, not just your one-shot prompts.

**What to do about it.** Split generation from compliance-checking:

```text
Pass 1 — generate:
  Write the migration guide. Two hard requirements: cover Android
  and iOS separately, and every code block must be runnable as-is.

Pass 2 — audit (fresh message, draft attached):
  Check this draft against each item below. For each, answer
  PASS or FAIL with a quote from the draft as evidence.
  Do not rewrite anything yet.
  1. Under 1,500 words
  2. No em dashes
  3. Every external claim linked
  4. Second person throughout
  5. Ends with a checklist

Pass 3 — fix:
  Fix only the items marked FAIL. Leave everything else untouched.
```

Checking is easier than generating-while-checking. And *"quote the evidence"* matters: without it the model will confidently mark items PASS that plainly failed — which is claim #3 all over again.

Given the position-bias finding, one more habit: put your non-negotiable constraint at the **end** of the prompt, closest to where generation begins.

## 5. Goals beat examples — could not verify

**The claim:** a study from EPFL, Apple and Mistral AI found that adding examples to a prompt scored 74%, and removing them in favour of a clearly stated goal scored 83.8%.

**Verdict: could not verify.** I found no paper matching that combination of institutions and figures. There is legitimate research showing few-shot examples can hurt in specific settings — code synthesis is a documented case — but "examples are worse than goals, 74% vs 83.8%" is not a result I can point you to.

**What survives without the number.** The advice is still reasonable, for a mundane mechanical reason: examples are *underspecified*. Give the model three newsletters and say "like these," and it has to guess which property you meant. Length? Tone? The joke in paragraph two? It will often pick the most superficial shared feature — and superficial features are exactly what makes AI writing read as AI writing.

Compare:

```text
❌ Here are 3 of my newsletters. Write #4 like these.

✅ My newsletter open rate fell from 34% to 21% over three months.
   Same Tuesday 9am send, same format, same list size, no change
   in subject-line style. Before you conclude anything, tell me
   what data you'd need to distinguish deliverability problems
   from content fatigue.
```

The second gives the model a problem to solve instead of a texture to imitate. It also ends by asking what it *doesn't* know — which surfaces the model's assumptions before they get baked into an answer.

Keep examples for genuinely mechanical work: output formats, JSON shapes, classification labels, a house style guide with explicit rules. Drop them when you want judgment.

## What actually generalises

Strip out the unverified numbers and a consistent picture is left:

**State the goal and the constraints, not the answer and the format.** Claim 1 and claim 5 are the same finding from opposite sides. A leading question hands over a conclusion; a pile of examples hands over a template. Both replace the model's reasoning with your guess about the output.

**Verify separately from generating.** Claims 3 and 4 pair up. Models are unreliable at satisfying many constraints at once, and unreliable at reporting their own accuracy. Both get better when checking is a distinct pass with evidence required.

**Prompt advice expires.** "Take a deep breath" was real, measured, published — and it was measured on PaLM 2-L in 2023. It aged out. Anything you read today, including this, has a shelf life tied to a model generation.

**And check the source before you repeat it.** Three of five claims in a widely-shared, confidently-written summary did not survive a look at the citations. That is the actual lesson, and it applies to AI output and human posts equally.

## FAQ

**Should I stop writing "think step by step"?**
On current reasoning models, yes — it is redundant. Keep it for smaller or faster models, or when you need to inspect the intermediate steps.

**Do personas hurt?**
Evidence says they do not reliably help accuracy, and sometimes hurt it on factual tasks. They are still fine — and useful — for controlling tone, audience and framing.

**How many constraints can I safely put in one prompt?**
Published benchmarks show degradation starting early and worsening non-linearly. Two or three hard requirements per pass, then audit the rest separately, is a defensible working rule.

**Is chain-of-thought dead?**
No. It is built in now. The prompt phrase is redundant; the technique is not.

**How do I check an AI-supplied citation quickly?**
Search the exact title, then verify authors and year, then open it and find the sentence supporting the claim. About a third of fabrications point at a real paper, so "it exists" is not enough.

---

*The five claims examined here come from a widely-shared Vietnamese summary of a post by Ruben Hassid on the science behind prompt engineering. The ideas are worth engaging with, which is why they deserved checking rather than repeating. Every paper referenced above is linked; where I could not find a source, I have said so rather than passing the number along.*
