---
title: "On-device AI in Flutter: what fits on a phone"
description: "Running a language model locally removes the API bill, the network dependency and the privacy question, and replaces them with a download size, a memory ceiling and a thermal budget. Here is how to tell which trade you are making."
seoDescription: "A practical look at on-device AI in Flutter apps: which tasks fit a small local model, quantisation and memory limits, packaging and download strategy, threading, battery and thermals, and hybrid local-plus-cloud designs."
keywords:
  - on device ai flutter
  - flutter local llm
  - flutter_gemma
  - quantized model mobile
  - litert mediapipe flutter
  - offline ai mobile app
category: "Deep Dive"
topic: "AI"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-08-01"
emoji: "📱"
tags: ["AI", "Flutter", "Mobile", "Performance", "Privacy"]
sources:
  - name: "LiteRT — Google AI Edge documentation"
    url: "https://ai.google.dev/edge/litert"
  - name: "LLM Inference guide — Google AI Edge"
    url: "https://ai.google.dev/edge/mediapipe/solutions/genai/llm_inference"
  - name: "flutter_gemma package — pub.dev"
    url: "https://pub.dev/packages/flutter_gemma"
  - name: "Core ML — Apple Developer documentation"
    url: "https://developer.apple.com/documentation/coreml"
  - name: "ONNX Runtime documentation"
    url: "https://onnxruntime.ai/docs/"
  - name: "Writing custom platform-specific code — Flutter documentation"
    url: "https://docs.flutter.dev/platform-integration/platform-channels"
related:
  - slug: "ai-model-routing-cascades"
    title: "Model routing and cascades: paying for the intelligence you need"
  - slug: "flutter-isolates-off-main-thread"
    title: "Flutter isolates: what actually goes off the UI thread, and what doesn't"
draft: false
---

The pitch is genuinely attractive: no API key, no per-token cost, no network round trip, and user data that never leaves the device. For a note-taking app, a keyboard, or anything handling health or financial records, that last point alone can decide the architecture.

Then you look at the numbers. A small quantised language model is a download of one to three gigabytes, needs most of that resident in RAM while it runs, and generates tokens at a rate that would embarrass a 2019 API. Both of those pictures are accurate. The question is which one applies to your feature.

## What actually runs well on a phone

The tasks where a small local model is genuinely good are narrower than the demos suggest, and they cluster around one property: **short input, short output, no world knowledge required.**

| Task | On-device viability | Why |
| --- | --- | --- |
| Text classification, intent detection | Excellent | Tiny models, often not LLMs at all |
| Embeddings for local semantic search | Excellent | Small model, runs once per document, no generation |
| Autocomplete, next-phrase suggestion | Good | Short outputs, latency-sensitive, benefits from being local |
| Summarising a short note | Workable | A few hundred tokens in and out |
| Speech-to-text | Good | Mature dedicated models, well-optimised runtimes |
| Image classification, OCR | Excellent | Not language models; long-solved on device |
| Open-ended chat | Poor | Users compare it to frontier models and it loses |
| Anything factual | Poor | A 2B-parameter model's world knowledge is thin and confidently wrong |
| Long-document analysis | Poor | Context window and memory both run out |
| Code generation | Poor | Quality gap is largest exactly here |

**The dominant failure mode is not technical, it is expectation.** If your UI looks like a chat assistant, users bring frontier-model expectations to a model a thousand times smaller. Frame the feature narrowly — "suggest tags", "rewrite this sentence", "search my notes" — and the same model reads as good.

## The three numbers that decide feasibility

Before writing any code, check your feature against these:

1. **Download size.** A 2B-parameter model at 4-bit quantisation lands in the low gigabytes. You cannot ship that inside the app bundle: both stores have limits well below it, and a 2GB install kills your conversion rate regardless. It must be an on-demand download, which means a UI for it, resume support, and a story for users who decline.
2. **Peak RAM.** The model weights must be resident during inference, plus the KV cache, which grows with context length. On a mid-range Android device with 4GB total, this is the constraint that actually bites. Exceeding it does not degrade gracefully — the OS kills your app, and it does so on exactly the devices you tested on least.
3. **Tokens per second.** Generation speed on mobile silicon is a small multiple of reading speed on a good device and below it on a bad one. Combined with a load time of several seconds for a cold model, this rules out anything that needs to feel instant unless you keep the model warm — which reintroduces the memory problem.

Measure all three on the *worst* device you intend to support, not on your development phone. The spread between a current flagship and a three-year-old mid-range Android is larger than any optimisation you will apply.

## The runtime layer

Flutter has no built-in inference engine, so every approach routes through platform code:

- **Google AI Edge (LiteRT, and the MediaPipe LLM inference task)** is the most direct path for Gemma-family models across Android and iOS.
- **The `flutter_gemma` package** on pub.dev wraps that stack for Dart, and is the shortest route to a working prototype. Check its README for current platform support and API shape before designing around it — community plugins in this space move quickly.
- **Core ML** on Apple platforms gives the best hardware utilisation on iOS, at the cost of an Apple-only code path and a model conversion step.
- **ONNX Runtime** is the most portable option if you already have ONNX models and need desktop as well as mobile.
- **A method channel to llama.cpp** gives you the widest model selection and the most control, and the most platform code to maintain. Worth it only if the packaged options do not support your model.

Whichever you pick, **isolate it behind an interface from day one**:

```dart
abstract interface class LocalInference {
  Future<bool> isAvailable();
  Future<void> load({void Function(double progress)? onProgress});
  Stream<String> generate(String prompt, {int maxTokens = 256});
  Future<void> unload();
}
```

Two implementations — the real one and a cloud-backed fallback — behind that interface is the design that survives. This space changes fast enough that the runtime you choose today is unlikely to be the one you ship in two years, and the interface is what keeps that from being a rewrite.

## Threading: the part Flutter developers get wrong

Inference is a long-running CPU/GPU operation. Run it on the platform main thread and you freeze the UI; the jank is not subtle.

- Native inference must run on a background thread **on the native side**. Dart isolates do not help here — the work is not in Dart.
- Stream results back over the channel token by token rather than returning a completed string, for the same UX reasons streaming matters against an API.
- Any Dart-side pre- and post-processing that is measurably expensive — tokenising, parsing, formatting a long result — belongs in an isolate.
- Handle the app going to the background: on iOS, expect inference to be suspended, and design for a generation that stops halfway and never resumes.

## Battery and thermals are a real constraint

Sustained inference is one of the heaviest things an app can do to a phone. Continuous generation warms the device noticeably and drains the battery at a rate users attribute to your app specifically — correctly.

More importantly, sustained load triggers thermal throttling, and **your benchmark numbers will not hold after two minutes of use.** Measure a sustained workload, not a single cold run.

Practical mitigations: never generate speculatively, cap output length hard, unload the model after a period of inactivity, and consider deferring bulk work — indexing a whole note archive, generating embeddings for every document — to when the device is charging and idle.

## The hybrid design is usually the right answer

Local-only and cloud-only are both worse than the obvious middle:

- **Local for the small, frequent, private, latency-sensitive things** — classification, embeddings, autocomplete, search over the user's own data.
- **Cloud for the hard ones** — long documents, real reasoning, anything requiring current world knowledge.
- **Local as the offline fallback**, degraded but functional, with the UI saying plainly that it is running in offline mode.

This is the same routing decision as choosing between a small and a large API model, with two extra terms in the equation: the local path has zero marginal cost and perfect privacy, and it is available when the network is not. Weigh those against a quality gap that is much larger than the one between two cloud models.

Whatever you build, **tell the user which mode produced the answer**. "Generated on your device" is a feature worth advertising when it is true, and hiding the distinction turns a privacy advantage into a trust problem the first time someone notices a network request.

## FAQ

**Can I ship the model inside the app bundle?**

Only for genuinely small models — classifiers, embedding models, speech models. Language models must be downloaded on demand.

**Does a local model still need updating?**

Yes, and you need a versioning and migration story for it. Plan for the download to happen more than once.

**Is on-device output automatically private?**

The inference is. Check that your app is not logging prompts or outputs to analytics, which quietly undoes the guarantee.

**What about Flutter web and desktop?**

Desktop is easier — more RAM, mains power. Web is impractical for language models today; the download alone is disqualifying.

**How do I test this in CI?**

You cannot meaningfully test inference quality on emulators. Test the interface with a fake implementation, and run real-model checks on a small physical device farm.

---

*Runtime capabilities, package APIs and platform limits described here come from the documentation linked above and change quickly — verify current details, especially for community packages, before committing to a design. The task-viability table, the three feasibility numbers, the threading guidance and the hybrid recommendation are my own judgement from building on-device features in Flutter; measure against your own target devices.*
