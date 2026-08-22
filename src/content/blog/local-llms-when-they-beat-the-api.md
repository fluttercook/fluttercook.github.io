---
title: "Running a model on your own machine: the four cases where it actually wins"
description: "Local LLMs are neither a replacement for frontier APIs nor a toy. There are four workloads where running your own weights is the correct engineering answer — and a lot of arithmetic you can do before downloading anything."
seoDescription: "When local LLMs beat an API: privacy limits, high-volume classification, offline work, latency loops — plus how to size a model to your VRAM."
keywords:
  - local llm vs api
  - run llm locally
  - llm quantization 4-bit
  - estimate vram for llm
  - ollama llama.cpp mlx
  - memory bandwidth token generation
category: "Analysis"
topic: "AI Engineering"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-22"
emoji: "🖥️"
tags: ["AI", "LLM", "Local Inference", "Performance", "Developer Tools"]
sources:
  - name: "llama.cpp — inference engine and GGUF tooling"
    url: "https://github.com/ggml-org/llama.cpp"
  - name: "Ollama"
    url: "https://github.com/ollama/ollama"
  - name: "MLX — array framework for Apple silicon"
    url: "https://github.com/ml-explore/mlx"
  - name: "mlx-lm — LLM tooling on MLX"
    url: "https://github.com/ml-explore/mlx-lm"
  - name: "LM Studio"
    url: "https://lmstudio.ai/"
  - name: "vLLM — high-throughput serving engine"
    url: "https://github.com/vllm-project/vllm"
related:
  - slug: "cutting-ai-costs-free-tiers-caching-and-routing"
    title: "Using AI without burning cash: free tiers, caching, and routing"
  - slug: "free-ai-coding-agents-opencode-safely"
    title: "Free AI coding agents: how to use OpenCode's free models without regretting it"
draft: false
---

There are two confident answers to "should I run a model locally," and both are wrong. One says local models are now good enough that paying for an API is a waste. The other says anything you can fit on a laptop is a toy and you should stop wasting your evening.

The useful answer is that "local versus API" isn't a question about models at all. It's a question about a specific workload, and it turns on four properties of that workload: whether the data is allowed to leave the machine, how many tokens a month you push through, whether there is a network, and how much of your latency budget a round trip eats. If none of those four is binding, the API is almost certainly the right call, and the honest reason is capability — on genuinely hard reasoning, a frontier model you rent still beats a quantised model you own.

What follows is the concession first, then the four cases where local is not a compromise but the correct answer, then the mechanics: how to work out whether a model fits in your memory before you download 40 GB, what 4-bit quantisation actually takes away, and why the thing that limits your token rate is almost never the thing people assume.

## The concession first: hard reasoning still belongs to the API

Start here, because everything else reads as motivated reasoning if you skip it.

The models you can run on one consumer machine are, for the most part, small models. The gap between them and a frontier model is not uniform across tasks — it is narrow on formatting, extraction, classification, summarisation of short text, and routine code completion, and it widens sharply on multi-step reasoning, long-context synthesis, unusual domain knowledge, and agentic loops where one wrong step poisons the next twenty.

That last one deserves emphasis, because it's where local disappoints people most and where they least expect it. An agent that reads a file, decides, edits, re-reads, and decides again compounds its own errors. A model that is 90% reliable per step is not 90% reliable over a ten-step task. This is why "I tried a local model as my coding agent and it went in circles" is such a common report — it isn't a tooling problem, and a better prompt won't fix it.

So the default stays: rent the big model. The four cases below are the ones where that default is wrong.

## Case 1 — data that legally cannot leave the machine

This is the case that actually decides most enterprise deployments, and it is a contractual question dressed up as a technical one.

If you're handling patient records, legal discovery, unreleased financials, client source code under NDA, or anything inside a compliance boundary that forbids third-party processing, then the model has to come to the data. Not because an API vendor is untrustworthy, but because "we send it to a third party and they promise not to keep it" is a sentence someone has to sign, and sometimes nobody will.

Be precise about which version of the constraint you have, because they have different answers:

- **"No third-party processing at all."** Air-gapped, or an explicit prohibition. Local is the only answer.
- **"No training on our data, no retention."** Major vendors offer zero-retention and enterprise agreements, and healthcare deployments in the US routinely run under a signed BAA. This is a procurement problem, not an engineering one.
- **"Data must stay in a specific jurisdiction."** Region-pinned endpoints exist. Check before you build a datacentre.
- **"We can't get legal to approve anything new this quarter."** Extremely common, rarely stated out loud, and local genuinely is the fast path — a model running on hardware you already own is often a smaller approval than a new data processor.

The engineering consequence of case 1 is that you should be *paranoid about egress*, not just about the model. A local model behind an app that ships telemetry, sends crash reports containing prompt text, or logs to a hosted observability service has not solved the problem. If the requirement is "nothing leaves," verify it at the network layer, not in the architecture diagram.

## Case 2 — volume, where per-token price is the whole cost

The second case is the arithmetic one, and it applies to a narrow but real shape of workload: an enormous number of small, similar, low-difficulty calls. Classifying support tickets. Tagging catalogue items. Routing inbound email. Extracting three fields from a document. Filtering a firehose before the expensive model sees it.

The reason this shape favours local is that a small model is genuinely good enough for it, and at high volume the per-token price stops being a rounding error. Work it out with your own numbers:

```
items per month          × tokens per item = tokens per month
tokens per month ÷ 1e6   × price per Mtok  = monthly API cost
```

Five million tickets a month at ~600 input tokens each is 3 billion input tokens. Even at a hypothetical $0.10 per million input tokens — cheap, at the small-model end — that's $300 a month, every month, for work that a machine you buy once could grind through overnight. Flip the volume down to fifty thousand items and the same calculation says $3, and you should absolutely not be buying a GPU for that.

Two things make this case less obvious than it looks, and both cut against local:

**Your engineering time is the biggest line item at small scale.** A weekend of setup, plus ongoing ownership of an inference server, is worth several years of a $300/month bill. The crossover point is much further out than the raw token math suggests.

**Batch pricing already exists.** Asynchronous batch endpoints from the major vendors are meaningfully discounted, and high-volume classification is exactly the workload they're designed for. Compare against the batch price, not the interactive one, or you'll talk yourself into hardware you don't need.

Where local does win at volume, win properly: use a serving engine built for throughput rather than a chat app. [vLLM](https://github.com/vllm-project/vllm) with continuous batching keeps the GPU saturated in a way that a single-stream tool never will, and throughput — not latency — is the number that matters when nobody is waiting.

## Case 3 — no network, or a network you can't depend on

Air-gapped facilities, ships, aircraft, mines, rural clinics, a factory floor with hostile RF, a laptop on a plane. This case is unglamorous and completely decisive: a feature that requires an API call is a feature that doesn't exist when the link is down.

There's a softer version of the same case that applies to teams with perfectly good connectivity. Local weights are *pinned*. The model you tested against is the model you'll be running in eighteen months, with the same quirks and the same failure modes, because it's a file on a disk. A hosted model can be updated underneath you, deprecated on a published schedule, or rate-limited during someone else's traffic spike. If you've spent months tuning prompts and building an eval suite around one model's behaviour, that stability has real value — and it is the one advantage of local that has nothing to do with hardware.

The mirror image is also true, and worth saying: pinned weights don't improve. You inherit the model's knowledge cutoff permanently, and upgrading is a migration project rather than a version string.

## Case 4 — loops where the round trip is the latency budget

The fourth case is about the physics of the network, not the price of it.

Any API call carries a floor: DNS, TLS, the round trip itself, queueing at the provider, then time-to-first-token. For a chat interface that floor is invisible. For an interaction that happens *between keystrokes*, it's the entire budget:

- **Code completion / fill-in-the-middle.** The suggestion is worthless if it arrives after you've typed the next token yourself.
- **On-device transcription.** Streaming speech with a visible partial transcript; `whisper.cpp` is the well-trodden path here, and it runs on phones.
- **UI affordances** — live rewrite, smart selection, inline translation — where a spinner turns a delightful feature into an annoying one.

Local wins twice here. It removes the round trip, and it changes the economics of *speculative* work: when a call costs nothing but a few milliseconds of an idle GPU, you can afford to run it on every keystroke and throw away 90% of the results. You would never do that against a metered API, which means some interactions are only designable locally.

The caveat is that "local" doesn't automatically mean "fast." A model that's swapping to disk, or one whose first token waits behind a 6,000-token prompt being processed from scratch, will be slower than a well-provisioned API. Which brings us to the arithmetic.

## Will it fit, and what sets the speed ceiling?

Two numbers decide whether a given model is usable on your machine, and you can compute both before downloading anything.

### Memory: parameters × bits, plus the KV cache

Weights dominate. The rule of thumb is bytes-per-parameter × parameter count, where bytes-per-parameter is set by quantisation:

| Precision | Bytes per parameter | ≈ GB per 1B params | 7B model | 70B model |
| --- | --- | --- | --- | --- |
| FP16 / BF16 | 2 | ~2.0 | ~14 GB | ~140 GB |
| 8-bit | 1 | ~1.05 | ~7.5 GB | ~75 GB |
| 4-bit (real GGUF) | ~0.55–0.65 | ~0.6 | ~4.5 GB | ~40 GB |

The 4-bit row is above the naïve 0.5 bytes for a reason worth knowing: practical 4-bit formats don't store every tensor at 4 bits. Embeddings and some attention projections are kept wider, and each block of weights carries its own scale and offset. Effective bits-per-weight lands nearer 4.5–5, which is why a "4-bit" file is bigger than half its 8-bit sibling.

Then add the **KV cache**, which people forget and which grows linearly with context:

```
kv_bytes = 2 × layers × kv_heads × head_dim × context_length × bytes_per_element
```

A model with 32 layers, 8 KV heads (grouped-query attention), head dimension 128, at 8,192 tokens in FP16:

```
2 × 32 × 8 × 128 × 8192 × 2 = 1,073,741,824 bytes  ≈ 1 GB
```

Two things fall out of that. Doubling your context doubles that GB. And grouped-query attention is why it's 1 GB and not 4 — the same model with 32 KV heads instead of 8 would need four times as much. If you're memory-starved, shrinking context is often a bigger win than shrinking the model, and llama.cpp can quantise the cache itself (`--cache-type-k q8_0`) for a further cut.

Budget roughly: **weights + KV cache + ~1 GB of runtime overhead**, and leave headroom. On a discrete GPU, exceeding VRAM means layers spill to system RAM across PCIe and throughput collapses — it doesn't fail, it just becomes unusable, which is worse. On Apple silicon the memory is unified, but macOS still caps how much the GPU may wire down (roughly three-quarters of total RAM by default; `sysctl iogpu.wired_limit_mb` is the knob, and it's a system setting, so understand what you're doing before changing it).

### Speed: generation reads the whole model, every token

Here's the part that reorders most people's intuitions. Generating one token at batch size 1 requires reading **every weight in the model** out of memory, to do what is mathematically a stack of matrix–vector products. The compute is trivial; the memory traffic is not. So the ceiling is:

```
max tokens/sec ≈ memory bandwidth (GB/s) ÷ model size in memory (GB)
```

Take that bandwidth number from your own hardware's spec sheet and divide. It's a ceiling, not a prediction — real throughput lands meaningfully below it — but it tells you the shape of the answer immediately, and it explains why quantising a model speeds it up: you halved the bytes that must cross the bus per token, not the arithmetic.

Prompt processing behaves completely differently. All prompt tokens are processed in parallel, so matrix–vector becomes matrix–matrix and the workload becomes **compute-bound**. Contrast the two phases for a 7B model at 4-bit (~4.5 GB), using the standard estimate of ~2 FLOPs per parameter per token:

| Phase | 8,000-token prompt | 500 generated tokens |
| --- | --- | --- |
| Compute | ~112 TFLOPs | ~7 TFLOPs |
| Memory read | ~4.5 GB (once) | ~2,250 GB (4.5 GB × 500) |

Sixteen times the compute for the prompt; five hundred times the memory traffic for the generation. That single table explains most local-LLM performance complaints. It's why a long system prompt hurts far more locally than it does against an API (which has warm batching and, often, prompt caching to amortise it), why "time to first token" and "tokens per second" have to be measured separately, and why a machine with modest compute but wide memory can generate comfortably while crawling through a long document.

Measure rather than guess: `llama-bench` in the llama.cpp repo reports prompt-processing and token-generation rates as separate numbers, on your hardware, with your quantisation.

## What 4-bit actually trades away

Quantisation is the price of admission for local inference, and the usual description of it — "barely any quality loss" — is true in a way that hides where the loss actually shows up.

- **8-bit is close enough to lossless** for practical purposes on most tasks. If it fits at 8-bit, run 8-bit and stop thinking about it.
- **4-bit is where the interesting trade lives.** Aggregate metrics like perplexity move very little, which is exactly why perplexity is a misleading way to evaluate it. Degradation is concentrated: long multi-step reasoning, exact-output tasks like code that must compile, recall of rare facts and proper nouns, non-English performance, and behaviour at the far end of a long context. Chat, summarisation, and classification hold up well.
- **Below 4-bit, degradation stops being subtle.** 3-bit and 2-bit quants exist and have their uses when a model otherwise won't fit at all, but treat them as a different model, not a cheaper one.

The commonly repeated rule is that for a fixed memory budget, a larger model at 4-bit beats a smaller model at 8-bit. It's a reasonable default, and it's also exactly the sort of claim you should verify on your own task rather than accept — the whole point of the previous bullet is that where a 4-bit model degrades depends on what you're asking it to do.

Format names you'll actually encounter: **GGUF** k-quants (`Q4_K_M` is the common default, `Q5_K_M` and `Q6_K` when you have room), often built with an importance matrix so calibration data steers which weights keep precision; **AWQ** and **GPTQ** on the GPU-serving side; and MLX's own 4-bit and 8-bit formats on Apple silicon. They're not interchangeable — the format follows the runtime you picked.

## The tooling, and what each piece is actually for

Four things, with real and mostly non-overlapping jobs.

| Tool | What it is | Reach for it when |
| --- | --- | --- |
| [llama.cpp](https://github.com/ggml-org/llama.cpp) | The C/C++ engine underneath much of this ecosystem. GGUF, CPU + partial GPU offload, `llama-server`, `llama-bench` | You want control: exact context size, layer offload, cache quantisation, or you're benchmarking |
| [Ollama](https://github.com/ollama/ollama) | A model manager and daemon with a one-line install and a pull-by-name library | You want it working in five minutes, or you want other apps on the machine to share one running model |
| [LM Studio](https://lmstudio.ai/) | A desktop GUI over GGUF and MLX, with a local server mode | You're evaluating models by feel, or you're not a terminal person |
| [MLX](https://github.com/ml-explore/mlx) / [mlx-lm](https://github.com/ml-explore/mlx-lm) | Apple's array framework and its LLM tooling, built for unified memory | You're on Apple silicon and want the runtime designed for that memory architecture |

Enough to get a model answering on localhost:

```bash
# Ollama: pull and chat
ollama pull <model-name>
ollama run <model-name>

# llama.cpp: serve a GGUF with an explicit context and full GPU offload
llama-server -m ./model.Q4_K_M.gguf -c 8192 -ngl 99

# Apple silicon via mlx-lm
pip install mlx-lm
mlx_lm.generate --model <mlx-community/model-id> --prompt "Summarise this:"
```

Both Ollama and `llama-server` expose an OpenAI-compatible surface, which is the practical reason to prefer them for anything you're integrating: the client code is identical to your API code, and switching between local and hosted becomes a base-URL change. That also gives you the sane migration path — build against the API, then move the parts that qualify.

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

resp = client.chat.completions.create(
    model="<model-name>",
    messages=[
        {"role": "system", "content": "Reply with exactly one of: BILLING, BUG, FEATURE, OTHER."},
        {"role": "user", "content": ticket_text},
    ],
    temperature=0,
    max_tokens=4,
)
```

That snippet is case 2 in miniature: a narrow job, a constrained output, `temperature=0`, and a tiny `max_tokens` so the memory-bound generation phase barely runs. Route the hard tickets to the frontier model and let the local one eat the other 95%. Hybrid is the answer far more often than either purist position.

## FAQ

**Is a local model good enough to replace my coding assistant?**
For inline completion, often yes — it's a short-context, latency-sensitive, low-difficulty task, which is the profile local handles best. For a multi-step agent that edits files and runs tests, usually not, because per-step error rates compound over a long trajectory. Splitting those two jobs across two models is a normal and sensible setup.

**How much RAM do I actually need?**
Work it out rather than guessing: weights (≈0.6 GB per billion parameters at 4-bit) plus KV cache (the formula above, which scales with your context length) plus about a gigabyte of overhead, then leave headroom. On a discrete GPU, overshooting VRAM doesn't error — it spills to system memory and throughput collapses, which is a much more confusing failure.

**Does quantisation make the model faster, or just smaller?**
Both, and for the same reason. Token generation is limited by how many bytes must be read from memory per token, so halving the model's size roughly doubles the ceiling on generation rate. It doesn't help prompt processing nearly as much, since that phase is compute-bound and dequantisation adds a little work of its own.

**If my data is sensitive, isn't an enterprise API tier enough?**
Frequently, yes — zero-retention terms, signed agreements and region-pinned endpoints cover a lot of real requirements, and they're less work than owning inference. Local becomes necessary when the constraint is absolute (no third-party processing, or no network at all), or when getting the agreement signed is slower than standing up a server.

**Is buying a GPU cheaper than paying for an API?**
Only at sustained high volume on work a small model can do. Multiply your monthly tokens by a realistic small-model price — and compare against the batch-endpoint price, not the interactive one — before you compare against hardware plus electricity plus your own time. For most teams the honest answer is that the API is cheaper and the reason to go local is one of the other three cases.

---

*The arithmetic here — memory footprint, KV cache size, the bandwidth ceiling on generation — is mechanical and you should redo it with your own model's configuration rather than trusting the illustrative numbers. The judgements about where 4-bit quantisation degrades, and about where the local/API crossover sits, are my read of the trade-offs and not measurements; benchmark your own task. Tool flags, model formats and vendor terms all change, so check the linked repositories and each provider's current terms before committing to a design.*
