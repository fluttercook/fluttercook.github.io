---
title: "Streaming UX: designing for tokens arriving one at a time"
description: "Streaming makes a slow model feel fast, and introduces a set of interface problems that batch responses never had: reflowing layout, half-finished markdown, cancellation, and errors that arrive after you have already shown output."
seoDescription: "Practical guidance for streaming LLM responses in a UI: SSE plumbing, incremental markdown rendering, scroll anchoring, cancellation, mid-stream errors, tool-call progress, and what to do on mobile networks."
keywords:
  - llm streaming ui
  - server sent events streaming ai
  - flutter stream llm response
  - incremental markdown rendering
  - cancel llm request
  - streaming ux design
category: "Guide"
topic: "AI"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-03"
emoji: "🌊"
tags: ["AI", "UX", "Streaming", "Flutter", "Frontend"]
sources:
  - name: "Streaming Messages — Anthropic documentation"
    url: "https://docs.anthropic.com/en/api/messages-streaming"
  - name: "Streaming API responses — OpenAI documentation"
    url: "https://platform.openai.com/docs/api-reference/streaming"
  - name: "Server-sent events — MDN"
    url: "https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events"
  - name: "Stream class — Dart API"
    url: "https://api.dart.dev/stable/dart-async/Stream-class.html"
  - name: "ScrollController class — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/ScrollController-class.html"
  - name: "Response time limits — Nielsen Norman Group"
    url: "https://www.nngroup.com/articles/response-times-3-important-limits/"
related:
  - slug: "ai-model-routing-cascades"
    title: "Model routing and cascades: paying for the intelligence you need"
  - slug: "ai-guardrails-prompt-injection-defense"
    title: "Prompt injection: what actually defends against it"
draft: false
---

A twelve-second response with a spinner feels broken. The same twelve seconds with text appearing after 400ms feels fast. Nothing about the model changed — only what the user could see while waiting.

That is the whole argument for streaming, and it is a good one. What follows is the set of problems you inherit along with it.

## The plumbing, briefly

Both major providers stream over server-sent events: a long-lived HTTP response of `data:` lines, each carrying a JSON event. The events that matter are the ones that append text, the ones that signal a content block starting or finishing, and the terminal event that carries the stop reason and final usage numbers.

Two structural rules:

- **Never stream directly from a browser or mobile client to the provider.** Doing so puts your API key on the device. Proxy through your own endpoint, which also gives you a place to log, rate-limit and enforce guardrails.
- **Your proxy should stream out as it streams in**, not buffer. If you `await` the full upstream response before writing anything downstream, you have paid for streaming's complexity and kept none of its benefit.

On the Dart side the natural shape is a broadcast-free `Stream<String>` of deltas:

```dart
Stream<String> streamCompletion(String prompt, {CancelToken? cancel}) async* {
  final request = http.Request('POST', _endpoint)
    ..headers.addAll(_headers)
    ..body = jsonEncode({'prompt': prompt, 'stream': true});

  final response = await _client.send(request);
  if (response.statusCode != 200) {
    throw ApiException(response.statusCode);
  }

  await for (final line in response.stream
      .transform(utf8.decoder)
      .transform(const LineSplitter())) {
    if (!line.startsWith('data: ')) continue;
    final payload = line.substring(6);
    if (payload == '[DONE]') return;
    final delta = _extractDelta(jsonDecode(payload));
    if (delta != null) yield delta;
  }
}
```

The `LineSplitter` matters: SSE chunks do not arrive aligned to line boundaries, and naive splitting on `\n` per chunk will corrupt JSON at the seams.

## Do not rebuild the world on every token

The naive Flutter implementation calls `setState` for each delta with a `Text(fullBuffer)` below it. At thirty tokens a second, on a long answer, this rebuilds and re-lays-out a growing paragraph thirty times a second and the frame budget disappears.

Three fixes, in order of how much they help:

1. **Isolate the rebuild.** Put the accumulating text in a `ValueNotifier<String>` and wrap only the text widget in a `ValueListenableBuilder`. The rest of the page — header, sidebar, message history — stops rebuilding entirely.
2. **Coalesce deltas.** Buffer incoming tokens and flush on a timer at roughly 60ms. The perceived smoothness is unchanged; the rebuild count drops by a factor of two or three. Users cannot distinguish token-by-token from 16-tokens-at-a-time.
3. **Freeze completed messages.** In a chat transcript, only the last message is streaming. Render everything above it as a separate, const-friendly subtree so it never participates in the streaming rebuilds.

## Markdown that is always half-finished

If you render markdown incrementally, every frame shows a document with an unclosed construct. A stream that has emitted `` `**import`` will render `**import` as literal text, then flip to bold two tokens later. Code fences are worse: the opening ``` arrives long before the closing one, so a naive renderer shows the code as a paragraph until the block ends, then reflows the entire message.

What works:

- **Detect an unterminated code fence and close it for rendering purposes.** Count the fences in the buffer; if the count is odd, append a synthetic closing fence before parsing. The block renders as code from the first line, and grows in place.
- **Do the same for inline constructs at the very end of the buffer.** A trailing `**` or a single `` ` `` with no partner should be hidden rather than shown raw.
- **Never animate layout during streaming.** No implicit size animations on the message container, no fade-in per token. Reflow plus animation reads as flicker.

The alternative some products choose is to render plain text while streaming and swap to formatted markdown at the end. It is simpler and it looks like a glitch at the moment of the swap. I prefer the incremental approach with fence-closing.

## Scroll behaviour is the detail people get wrong

Auto-scrolling to the bottom on every token is correct until the user scrolls up to re-read something, at which point it becomes a fight they lose.

The rule: **auto-scroll only while the viewport is already near the bottom.**

```dart
void _maybeStickToBottom() {
  if (!_controller.hasClients) return;
  final position = _controller.position;
  final distanceFromBottom = position.maxScrollExtent - position.pixels;
  if (distanceFromBottom > 80) return; // user scrolled away; leave them alone
  _controller.jumpTo(position.maxScrollExtent);
}
```

Use `jumpTo`, not `animateTo` — an animation started thirty times a second never completes and produces visible stutter. And show a "jump to latest" affordance once the user has scrolled away, so leaving them alone does not mean stranding them.

## Cancellation, and why it is a product feature

Users change their mind mid-answer. A stop button is not a nicety:

- It saves output tokens you would otherwise pay for.
- It frees the connection and the user's attention.
- It signals that the system is under their control, which matters more than the token savings.

Implement it properly: abort the underlying HTTP request so the upstream generation actually stops, not just the UI subscription. Cancelling the Dart stream while the socket stays open bills you for the full completion. And keep the partial text on screen with a clear "stopped" marker rather than clearing it — the user usually stopped because they already had what they needed.

## Errors that arrive after you have shown output

This is the case batch responses do not have. You are 200 tokens into a visible answer and the connection drops, or the provider returns a mid-stream error event, or a content filter fires.

You cannot un-show the text. So:

- **Mark the message as incomplete** with a visible affordance and a retry action. Never silently leave a truncated answer looking finished.
- **Check the terminal event's stop reason.** A completion that ended because it hit the token limit is not the same as one that finished naturally, and the UI should distinguish them — usually with a "continue" action.
- **Retry from the beginning, not the middle.** Resuming a stream by concatenating a second generation onto a partial one produces incoherent text at the seam. Regenerate and replace.
- **Handle the empty stream.** A response that produces a terminal event with no text is a real occurrence; a UI that shows an empty bubble forever is a bug report.

## Tool calls make the stream lumpy

Once the model can call tools, the stream is no longer a smooth flow of prose. It emits some text, pauses for two seconds while a tool runs, then resumes. That pause looks identical to a hang.

Fill it with a specific status, not a spinner: "Searching documentation…", "Reading three files…". Naming the operation converts dead time into visible progress, and gives the user grounds to cancel if the model is doing something they did not want. If your tool arguments themselves stream in as a partial JSON object, do not try to parse and display them incrementally — wait for the complete arguments, then show the named action.

## Mobile networks

Streaming assumes a connection held open for tens of seconds, which is exactly the assumption mobile networks break.

- Set a read timeout on the **gap between events**, not on the total duration. A stream can legitimately run for a minute; a fifteen-second silence in the middle is a dead connection.
- Handle the app moving to the background — on iOS in particular, expect the socket to be killed. Decide deliberately whether to abandon the generation or move it server-side and let the client re-attach to a job ID.
- Consider whether streaming is worth it at all for short outputs. For a classification returning a single word, streaming adds connection complexity and saves nothing perceptible.

## FAQ

**Does streaming cost more?**

No. You are billed for the same tokens; only the delivery changes.

**Can I stream structured JSON output?**

You can, but do not render it incrementally — partial JSON is not parseable. Show a progress indicator and render on completion.

**How fast should tokens appear for it to feel good?**

Time to first token is what dominates the impression. Under about a second reads as responsive; after that, streaming rate matters less than people assume.

**Should I add a typing cursor?**

A blinking block at the end of the text is genuinely useful — it distinguishes "still generating" from "finished and short".

**What about accessibility?**

Screen readers handle rapidly-changing regions badly. Announce that a response is generating, then announce the finished text once, rather than making the streaming region a live region.

---

*The streaming protocols and API behaviours described here come from the provider documentation linked above; verify event names and field shapes against the current docs, as these evolve. The rendering strategies, the scroll rule, the error-handling recommendations and the judgement about when streaming is not worth it are my own, from building streaming interfaces in Flutter and on the web.*
