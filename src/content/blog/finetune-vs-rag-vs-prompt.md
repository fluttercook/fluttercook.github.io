---
title: "Fine-tune, retrieve, or write a better prompt: a decision you can defend"
description: "These three get compared as if they solve the same problem. They don't. Prompting changes instructions, retrieval changes knowledge, fine-tuning changes behaviour — map the symptom to the layer and the argument ends."
seoDescription: "When to fine-tune vs use RAG vs improve the prompt: a symptom-to-technique map, what fine-tuning really costs, where LoRA fits, and a decision table."
keywords:
  - fine tuning vs rag
  - when to fine tune an llm
  - rag or prompt engineering
  - lora fine tuning cost
  - llm output format consistency
  - fine tuning dataset maintenance
category: "Analysis"
topic: "AI Engineering"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-22"
emoji: "🎛️"
tags: ["AI", "LLM", "RAG", "Fine-tuning", "Architecture"]
sources:
  - name: "OpenAI — Fine-tuning guide"
    url: "https://platform.openai.com/docs/guides/fine-tuning"
  - name: "OpenAI — Structured Outputs"
    url: "https://platform.openai.com/docs/guides/structured-outputs"
  - name: "Hugging Face PEFT — parameter-efficient fine-tuning"
    url: "https://huggingface.co/docs/peft/index"
  - name: "LoRA: Low-Rank Adaptation of Large Language Models"
    url: "https://arxiv.org/abs/2106.09685"
  - name: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
    url: "https://arxiv.org/abs/2005.11401"
related:
  - slug: "what-the-research-says-about-prompt-engineering"
    title: "What the research actually says about prompt engineering — five claims, fact-checked"
  - slug: "cutting-ai-costs-free-tiers-caching-and-routing"
    title: "Using AI without burning cash: free tiers, caching, and routing"
draft: false
---

Every few weeks someone puts the same slide on the screen: three boxes labelled **Prompt Engineering**, **RAG**, and **Fine-tuning**, with arrows suggesting you graduate from left to right as your problem gets serious. Then the room argues about which one to pick, as if they were three vendors bidding for the same job.

They are not competing for the same job. They act on three different parts of the system, and once you name which part, the argument usually ends in about a minute:

- **Prompting changes the instructions.** What the model is being asked to do, and under what constraints.
- **Retrieval changes the knowledge.** Which facts are physically present in the context window when the model answers.
- **Fine-tuning changes the behaviour.** What the model does by default, in what form, when the instructions run out.

Almost every bad decision in this area comes from applying one layer to a problem that lives in another. Fine-tuning a model so it "knows" your product catalogue is the classic — you spend six weeks producing a model that is confidently wrong about last week's prices, and you cannot even tell which weights to blame. Stuffing a retrieval pipeline in front of a model whose actual problem is that it writes six paragraphs when you wanted one is the same mistake in the other direction.

So don't start from the technique. Start from the symptom.

## Four layers, not three

The slide is also missing a box. There are four things you can change, and they differ mainly in how expensive a *change* is once you're in production.

| Layer | What it changes | Changed by | Cost of one change |
| --- | --- | --- | --- |
| **Prompt** | The instructions and constraints | Editing a string | Minutes. Reversible. |
| **Schema / tools** | What output is structurally *possible* | A JSON schema, a tool definition | Hours. Reversible. |
| **Retrieval** | Which facts are in front of the model | Ingesting or reindexing a document | Minutes per document, once the pipeline exists |
| **Fine-tuning** | The model's default behaviour and form | A training run over labelled examples | Days to weeks. A new artefact to maintain. |

The middle layer is the one teams skip, and it's the one that solves the single most common complaint. "It won't hold the output format" is usually not a training problem — it's a decoding problem, and constrained decoding solves it structurally rather than statistically. OpenAI's Structured Outputs with `strict: true`, or the equivalent constrained-generation feature in whatever stack you use, makes a malformed response *impossible* rather than merely unlikely. No dataset required.

## Start from the symptom, not from the technique

Here is the map I actually use. Read the left column as something a stakeholder said out loud.

| What you observe | What's actually missing | Reach for |
| --- | --- | --- |
| "It doesn't know our product / pricing / policy" | Knowledge | Retrieval |
| "It made up an internal API that doesn't exist" | Knowledge, plus permission to refuse | Retrieval + an explicit "say you don't know" instruction |
| "It's stale — the doc changed last Tuesday" | Knowledge freshness | Retrieval. Never fine-tuning. |
| "It's too verbose" / "wrong tone" | Instructions | Prompt |
| "It follows five of my six rules" | Instruction load | Prompt restructuring: split the call, or move a rule into a schema |
| "The JSON is malformed one call in fifty" | Structural guarantees | Schema / constrained decoding |
| "It's right, but it doesn't sound like our support team" | Form and style | Fine-tuning (after few-shot fails) |
| "It's right on normal cases and wrong on our weird ones" | Task-specific behaviour | Few-shot examples first, then fine-tuning |
| "It works, but the system prompt is thousands of tokens on every call" | Cost and latency | Prompt caching first, then fine-tuning |
| "Answers differ for users who shouldn't see the same data" | Access control | Retrieval. Fine-tuning cannot do this at all. |

Two rows in that table are load-bearing, and they're the ones people skip past.

**Freshness and access control are structural disqualifiers for fine-tuning.** If a fact can change, or if different users are allowed to see different facts, it cannot live in weights. A retrieval index has rows you can update, delete, and filter by permission. Weights have none of those affordances. There is no `DELETE` for a fact a model absorbed during training, and no `WHERE tenant_id = ?`.

## Prompting is the only layer with a same-day undo

Start here every time, not because prompting is powerful but because it is *cheap to be wrong*. A prompt change ships in a commit, gets reviewed like code, and reverts in seconds. Nothing else in this list does.

Where prompting genuinely runs out:

- **It cannot install facts the model doesn't have.** Pasting the whole handbook into the prompt is retrieval with a manual step — and it's retrieval done badly, because you're paying for the entire handbook on every call.
- **Adherence degrades as constraints pile up.** A prompt with a dozen simultaneous rules is not twelve times as reliable as one with a single rule. When you notice yourself adding rule fourteen, the fix is usually to split the work into two calls, or to demote a rule into something the decoder enforces. (I've written separately about [what the research actually says about prompt engineering](/blog/what-the-research-says-about-prompt-engineering/) and which of the folk techniques survive scrutiny.)
- **Every token is billed on every call.** A long system prompt is a fixed tax on the whole workload.

That last one is the legitimate motive for fine-tuning that people reach for too early — and there's a cheaper intervention first. Prompt caching lets a stable prefix be reused across calls at a reduced rate, which removes most of the cost argument without producing a dataset. Try that before you try training. There's more on that lever in the [cost article](/blog/cutting-ai-costs-free-tiers-caching-and-routing/).

## Retrieval is a knowledge patch, and only a knowledge patch

The [original RAG paper](https://arxiv.org/abs/2005.11401) framed it plainly: put a non-parametric memory next to the parametric one, so knowledge lives somewhere you can edit. That framing is still the right way to decide whether you need it.

Retrieval is the answer when any of these are true:

- the facts change on a schedule you don't control
- the facts are private and were never in any pre-training corpus
- there are far more facts than fit in a context window
- you need to show the user *where* an answer came from
- different users are entitled to different subsets of the facts

What you take on when you say yes: an ingestion pipeline, chunking decisions that affect answer quality in non-obvious ways, an index that must stay in sync with the source of truth, one extra network hop of latency, and an entirely new failure mode — the model can now be wrong because retrieval handed it the wrong three paragraphs, which looks identical to the model being wrong on its own.

That last problem is deep enough to deserve its own treatment; measuring whether retrieval is fetching the right thing is a separate discipline from measuring whether the model answered well, and it needs its own test set. For the purposes of *this* decision, the thing to internalise is simply that saying yes to retrieval means you now own a search system in addition to an LLM feature.

## Fine-tuning buys form, latency, and price — not knowledge

What fine-tuning genuinely, reliably buys you:

- **Consistent form.** Tone, structure, register, house conventions — the things that take a page of style guide to describe and still get applied unevenly. Demonstrations teach this far better than descriptions do.
- **A shorter prompt.** Behaviour you'd otherwise spell out every call gets folded into the model. Fewer input tokens per request, less to go wrong.
- **Lower latency and cost per call**, as a consequence of the shorter prompt — and sometimes because a smaller base model, tuned on your narrow task, matches a larger untuned one.
- **Task shapes that resist description.** An idiosyncratic label taxonomy, your team's dialect of SQL, a classification boundary that everyone recognises but nobody can write down. If your best attempt at the prompt is "you'll know it when you see it," you have a fine-tuning problem.

What it does not buy is knowledge you can trust. Facts absorbed into weights are unattributed, unversioned, undeletable, and quietly blurry — and nothing tells you when one has gone stale. A fine-tune is a fork of your understanding of the task, frozen at a date.

Here's the honest cost side. Not the training bill — the training bill is usually the smallest item on this list.

1. **A labelled dataset.** This is the actual work: examples that are correct *and consistent with each other*. Disagreement between two labellers doesn't average out; it arrives in the model as noise, and it shows up later as a behaviour nobody can explain.
2. **Dataset maintenance.** The task shifts. A rule changes. Now some fraction of your examples teach the wrong thing, and you have to find which ones.
3. **A retraining loop.** Every meaningful change to the task means another run, another artefact, another rollout.
4. **An evaluation suite you now own.** You can no longer lean on the vendor's benchmarks, because the model is no longer theirs. You need a held-out set, regression checks against the previous version, and a check that you haven't degraded everything the model used to be good at outside the narrow task.
5. **A model to keep in sync.** This is the one that bites eighteen months later. Base models get deprecated and superseded. When a better base ships, your fine-tune is still sitting on the old one, and moving means redoing the run — and revalidating everything, because a dataset that taught the old base well does not automatically teach the new one the same lesson.

The mechanics themselves are easy, which is exactly why the costs above get underestimated. A supervised fine-tuning set is just conversations:

```json
{"messages": [{"role": "system", "content": "You are a support triage assistant."}, {"role": "user", "content": "card declined at checkout, third time today"}, {"role": "assistant", "content": "{\"category\": \"billing.payment_failure\", \"severity\": \"high\", \"needs_human\": true}"}]}
{"messages": [{"role": "system", "content": "You are a support triage assistant."}, {"role": "user", "content": "how do I change my avatar"}, {"role": "assistant", "content": "{\"category\": \"account.profile\", \"severity\": \"low\", \"needs_human\": false}"}]}
```

```python
job = client.fine_tuning.jobs.create(
    training_file=train_file.id,
    validation_file=val_file.id,   # hold this out. always.
    model="<base-model-id>",
    suffix="triage-v3",            # version it; you will have a v4
)
```

Two lines of that snippet are the whole argument. The `validation_file` is not optional politeness — without a held-out set you have no way to distinguish a model that learned the task from one that memorised your examples. And the `suffix` is a version number, because there will be a v4, and something in production will need to be pinned to v3 while you evaluate it.

## LoRA and adapters: the cheap middle

Full fine-tuning updates every weight, which means a full copy of the model per task. [LoRA](https://arxiv.org/abs/2106.09685) does something much lighter: freeze the base weights, and train a small low-rank update alongside them. The trained artefact is a few megabytes rather than a full model, so you can keep many adapters over one shared base and swap them per task, per tenant, or per experiment.

With [PEFT](https://huggingface.co/docs/peft/index) this is a handful of lines on top of a normal training loop:

```python
from peft import LoraConfig, get_peft_model

config = LoraConfig(
    r=16,                    # rank of the update
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules=["q_proj", "v_proj"],
    task_type="CAUSAL_LM",
)
model = get_peft_model(base_model, config)
model.print_trainable_parameters()   # a small fraction of the base
```

This is genuinely the pragmatic middle of the market, and it changes the economics enough that "we can't afford to fine-tune" is rarely true any more. But be precise about what it lowers. LoRA reduces the **compute cost and the storage cost** of training. It does not reduce the dataset cost, the labelling-consistency cost, the evaluation cost, or the keeping-in-sync cost — and those were always the expensive parts. A cheap training run over a bad dataset produces a bad model faster.

## The ordering rule, and why it's about maintenance

Exhaust each layer before adding the next: **prompt → schema → retrieval → fine-tune**. Not because the later ones are harder to build — with a managed API, fine-tuning can be a shorter afternoon than a retrieval pipeline — but because each step up permanently multiplies the surface you have to maintain.

| You've adopted | You now own, forever |
| --- | --- |
| Prompt | A string in version control, and evals for it |
| + Schema | A contract, plus migration when the contract changes |
| + Retrieval | An ingestion pipeline, an index, sync, and retrieval-quality evals |
| + Fine-tuning | A dataset, a labelling process, a training pipeline, model-version evals, and a base-model migration you don't control the timing of |

Read that bottom row as a staffing question rather than a technical one. Somebody has to still be doing all of it in a year.

Also worth saying explicitly, because the framing as a three-way choice hides it: **these compose, and the best systems use more than one.** The common mature shape is fine-tuning for form plus retrieval for facts — a tuned model that reliably produces your house output structure, fed current documents at request time. Choosing one to the exclusion of the others is itself usually the error.

## The decision table

| Situation | Prompt | Retrieval | Fine-tune |
| --- | --- | --- | --- |
| Model lacks private or current facts | No | **Yes** | No |
| Facts change weekly | No | **Yes** | Actively harmful |
| Answers must cite a source | No | **Yes** | No |
| Different users see different data | No | **Yes** | Impossible |
| Output too long, wrong tone, wrong emphasis | **Yes** | No | Only if prompting plateaus |
| Output format breaks occasionally | Helps | No | **Schema first** |
| House style, applied thousands of times a day | Try first | No | **Yes** |
| Task is obvious to a human, hard to write down | Few-shot first | No | **Yes** |
| Huge fixed prompt is the cost driver | Caching first | No | **Yes** |
| Need a smaller/faster model on one narrow task | No | No | **Yes** |
| It's a prototype and you're still learning the task | **Yes** | Maybe | **No** |

The last row is the one I'd defend hardest. Fine-tuning encodes a decision about what "good" means. Make that commitment before the task has stopped moving and you'll spend the next quarter maintaining a model that captures an opinion you no longer hold.

## FAQ

**Can't I just fine-tune on our documentation so the model knows it?**

You can run the job, and the result will feel encouraging in the first ten manual tests — the model picks up your vocabulary and tone, which reads as knowledge. Then it invents a parameter that doesn't exist, with no citation and no way to trace which document taught it that. Fine-tuning on docs teaches the *style* of your docs reliably and their *content* unreliably. If the goal is factual answers about documents, that's retrieval.

**How many training examples do I need?**

Nobody can answer this from the outside, and anybody who quotes a single number for all tasks is guessing. The honest method is empirical: assemble a modest set, train, measure on a held-out set, then double the data and measure again. When the curve flattens, more examples are no longer your bottleneck — quality and consistency of labels are. Narrow, well-defined tasks with consistent labelling need far less data than broad, subjective ones.

**Do large context windows make retrieval obsolete?**

They remove the "it doesn't fit" reason, which was only one of five. They don't help with freshness, per-user access control, provenance, or cost — and pushing an entire corpus through the context on every request is an expensive way to avoid building an index. Big context windows make retrieval *easier* by relaxing chunking pressure; they don't make it unnecessary.

**We fine-tuned and it got better at our task but worse everywhere else. What happened?**

That's the expected outcome, not a bug: you moved the model toward your distribution, and it moved away from everything else. This is why the evaluation suite has to include capabilities you weren't trying to change. If the model also needs to stay generally competent, a lighter-touch adapter and a smaller learning rate are more appropriate than aggressive full fine-tuning — or the general work should route to the untuned base model instead.

**Which one is cheapest?**

Per call, a fine-tuned model with a short prompt is usually cheapest, and that's the number people compare. Per quarter, it's rarely close: the dataset, the labelling, the evals, and the base-model migrations are recurring human costs that don't appear on the invoice. Prompting is the cheapest thing to be wrong about, which at the start matters far more than being cheapest to run.

---

*The layer model here — instructions, knowledge, behaviour — is my own framing for making this decision quickly, not an industry standard; the underlying claims about what each technique can and cannot do are not opinion. Anything version-dependent (available fine-tuning endpoints, structured-output support, base-model deprecation schedules) changes often — check the provider's own documentation before you build on it.*
