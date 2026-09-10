# Kế hoạch nội dung tháng 9/2026

**194 bài trong tháng** — 7 bài/ngày trong tuần, 5 bài/ngày cuối tuần.
Mỗi bài viết cả EN và VI cùng slug, nên **10–14 file/ngày**.

Mỗi ngày là **một cụm chủ đề**, không phải mấy bài rời rạc — để các bài trong ngày
trỏ chéo vào nhau qua `related`, và cụm đó đứng được thành một trang chủ đề.
Mỗi cụm có 15 chủ đề nhưng chỉ 5–7 cái lên lịch; phần còn lại nằm ở mục
**Dự trữ** ngay dưới, đủ cho tháng 10 và 11 mà không phải nghĩ lại từ đầu.

Nguồn đích: `src/content/blog/` + `src/content/blog-vi/` trong repo này, rồi mirror sang
trunghieu-it, fluttercook và flutter9 — cron trên `sync.fighttech.vn` tự chạy (xem repo `fighttechvn`).

## Trước khi chạy — đọc phần này

- **Luật viết giữ nguyên**: không bịa số, không bịa URL, chỉ dẫn nguồn chính thức
  (docs.flutter.dev, api.flutter.dev, dart.dev, developer.android.com, developer.apple.com, pub.dev, MDN).
  Chỗ nào không xác minh được thì viết rõ là không xác minh được.
- **QA bắt buộc trước khi push**: `qa_articles.py` (parity EN/VI, frontmatter, `related`, mọi URL nguồn phải 200)
  rồi `npm run build`.
- **Slug trùng**: 48 bài đã có trong repo đã được loại khỏi danh sách này. Kiểm lại trước mỗi ngày phòng khi có bài mới chen vào.
- **Đăng lên Blogger là việc của cron**, không làm tay: đẩy bài vào `main`, cron trên server
  nhả dần theo `SYNC_LIMIT` mỗi lần chạy.

## Phân bổ

| | Số ngày | Bài lên lịch | Dự trữ | Nghiêng về site |
|---|---:|---:|---:|---|
| 🐦 Track Flutter | 15 | 97 | 128 | fluttercook |
| 🤖 Track AI/Dev | 15 | 97 | 128 | trunghieu-it |
| **Tổng** | **30** | **194** | **256** | |

22 ngày trong tuần × 7 bài + 8 ngày cuối tuần × 5 bài = 194 bài,
tức 388 file. Kho chủ đề còn 256 cái chưa dùng.

Hai track xen kẽ theo ngày. Cả hai vẫn mirror sang cả ba blog — phân chia ở đây là để
mỗi site có một trọng tâm nhận diện được, không phải để chặn nội dung.

---

## Ngày 1 — 2026-09-01 (Thứ Ba) · 🐦 Flutter · Layout & constraints

**7 bài** (14 file EN+VI)

1. `flutter-constraints-go-down-sizes-go-up` — the one sentence that explains every layout error, worked through four widgets
2. `flutter-unbounded-height-errors` — why RenderFlex gets unbounded height, and the four fixes ranked by honesty
3. `flutter-expanded-flexible-spacer` — three flex children that look alike; when each is the wrong one
4. `flutter-stack-positioned-alignment` — absolute positioning that survives rotation and text scaling
5. `flutter-intrinsic-sizing-cost` — what IntrinsicHeight actually walks, and the cheaper shapes
6. `flutter-layoutbuilder-vs-mediaquery` — which rebuilds when, and why the difference bites on tablets
7. `flutter-responsive-breakpoints` — one layout, three form factors, zero Platform.isX checks

<details><summary>Dự trữ trong cụm — 8 chủ đề</summary>

- `flutter-safearea-insets-viewpadding` — SafeArea, viewInsets and viewPadding are three different numbers
- `flutter-aspect-ratio-fittedbox` — sizing media without overflow when the source ratio is unknown
- `flutter-wrap-vs-flex-overflow` — when wrapping text is a layout decision, not a style one
- `flutter-baseline-alignment-text` — aligning mixed-size text on its baseline instead of its box
- `flutter-custom-multichild-layout` — CustomMultiChildLayout when children's positions depend on each other
- `flutter-overflow-debugging` — reading the yellow-black stripes back to the exact offending widget
- `flutter-fractionally-sized-box` — percentage layouts that do not break in landscape
- `flutter-table-vs-datatable-vs-grid` — tabular data where columns actually line up

</details>

## Ngày 2 — 2026-09-02 (Thứ Tư) · 🤖 AI/Dev · Embeddings & vector search

**7 bài** (14 file EN+VI)

1. `embeddings-what-the-vector-actually-means` — geometry first: what distance in embedding space does and does not tell you
2. `choosing-an-embedding-model` — the four axes that matter, and the benchmark trap
3. `chunking-strategies-compared` — fixed, recursive, semantic and structural, judged on retrieval not aesthetics
4. `vector-index-hnsw-ivf-flat` — three index families, three failure modes, one decision table
5. `pgvector-in-production` — when your existing Postgres is the right vector store
6. `metadata-filtering-with-vector-search` — pre-filter, post-filter, and why the difference changes your recall
7. `hybrid-search-bm25-plus-dense` — the lexical half your dense retriever keeps missing

<details><summary>Dự trữ trong cụm — 8 chủ đề</summary>

- `embedding-drift-and-reindexing` — what breaks when you change models, and the migration that avoids downtime
- `cosine-dot-euclidean-which-metric` — why normalisation makes two of these the same question
- `matryoshka-embeddings-truncation` — trading dimensions for storage without retraining
- `multilingual-embeddings` — cross-language retrieval and where it quietly fails
- `embedding-batching-and-cache` — the two changes that cut embedding cost most
- `sparse-vs-dense-retrieval` — SPLADE-style sparse vectors as the middle ground
- `vector-db-vs-postgres-decision` — the scale where a dedicated store starts paying for itself
- `embedding-evaluation-harness` — a retrieval test suite you can run on every model swap

</details>

## Ngày 3 — 2026-09-03 (Thứ Năm) · 🐦 Flutter · Scrolling & slivers

**7 bài** (14 file EN+VI)

1. `flutter-slivers-mental-model` — the viewport asks, the sliver answers: the protocol under every scroll view
2. `flutter-customscrollview-recipes` — the five sliver combinations that cover most real screens
3. `flutter-sliverappbar-collapsing` — pinned, floating, snap: what each flag actually does to the scroll
4. `flutter-listview-builder-performance` — itemExtent, prototypeItem, and the cost of not knowing your height
5. `flutter-nested-scroll-view` — the widget everyone gets wrong, and the two layouts it is for
6. `flutter-infinite-scroll-pagination` — loading pages without double-firing at the list edge
7. `flutter-scroll-controller-patterns` — reading position without rebuilding the world

<details><summary>Dự trữ trong cụm — 8 chủ đề</summary>

- `flutter-sticky-headers-slivers` — section headers that stick, built from SliverPersistentHeader
- `flutter-pull-to-refresh-custom` — RefreshIndicator, and what to do when you need your own
- `flutter-scroll-physics-platform` — why iOS bounces and Android glows, and how to override honestly
- `flutter-keep-alive-in-lists` — AutomaticKeepAlive when scrolling away must not reset state
- `flutter-reorderable-list` — drag-to-reorder that keeps its keys straight
- `flutter-scrollable-positioned-list` — jumping to an item when heights are not uniform
- `flutter-two-dimensional-scrolling` — the 2D scrolling foundation and when a table needs it
- `flutter-scroll-jank-checklist` — the six things to check before blaming the framework

</details>

## Ngày 4 — 2026-09-04 (Thứ Sáu) · 🤖 AI/Dev · Agents & tool use

**7 bài** (14 file EN+VI)

1. `agent-loop-anatomy` — the smallest correct agent loop, and every place it can hang
2. `tool-design-for-agents` — tools are an API for a model, and models read the schema
3. `agent-error-recovery` — what to hand back when a tool fails, so the next turn is smarter
4. `agent-planning-vs-reacting` — plan-first and react-as-you-go, and the tasks each suits
5. `multi-agent-when-it-helps` — the coordination cost, and when one agent is simply better
6. `agent-sandboxing-and-permissions` — running model-chosen commands without handing over the machine
7. `agent-termination-conditions` — how loops actually end, and the budget that stops runaways

<details><summary>Dự trữ trong cụm — 8 chủ đề</summary>

- `subagent-context-isolation` — why a fresh context beats a longer one for fan-out work
- `agent-tool-result-truncation` — trimming a 2MB tool result without destroying the signal
- `agent-state-across-turns` — what belongs in context, in a file, and in a database
- `human-in-the-loop-checkpoints` — the three actions worth stopping for, and how to ask
- `agent-determinism-and-replay` — making an agent run reproducible enough to debug
- `agent-parallel-tool-calls` — when concurrency is safe and when it corrupts shared state
- `mcp-server-design-basics` — exposing your system to agents without exposing everything
- `agent-cost-per-task` — measuring what one completed task actually costs

</details>

## Ngày 5 — 2026-09-05 (Thứ Bảy) · 🐦 Flutter · Navigation & routing

**5 bài** (10 file EN+VI)

1. `flutter-navigator-2-explained` — the declarative API, explained by what problem it was built for
2. `go-router-getting-it-right` — routes, shells and redirects that survive a deep link
3. `flutter-deep-links-setup` — the Android and iOS plumbing, end to end
4. `flutter-nested-navigation-tabs` — per-tab back stacks that behave like the platform expects
5. `flutter-route-guards-auth` — redirect on auth state without a flash of the wrong screen

<details><summary>Dự trữ trong cụm — 10 chủ đề</summary>

- `flutter-passing-data-between-routes` — arguments, extras, and why the URL should carry the id
- `flutter-back-button-handling` — PopScope, predictive back, and unsaved-changes dialogs
- `flutter-hero-animations-routes` — shared-element transitions that do not tear on push
- `flutter-custom-page-transitions` — writing a transition that matches your design, not Material's
- `flutter-url-strategy-web` — clean URLs on Flutter web and what the server must send
- `flutter-navigation-testing` — asserting on routes instead of on pixels
- `flutter-modal-vs-route` — dialogs, sheets and full-screen: which belongs in the stack
- `flutter-restoration-state` — surviving process death on Android with RestorationMixin
- `flutter-router-and-state-management` — keeping route state and app state from fighting
- `flutter-navigation-analytics` — one observer, every screen view, no per-page code

</details>

## Ngày 6 — 2026-09-06 (Chủ Nhật) · 🤖 AI/Dev · Evals for LLM systems

**5 bài** (10 file EN+VI)

1. `first-eval-set-in-an-afternoon` — thirty real inputs beat a thousand synthetic ones
2. `llm-as-judge-when-to-trust` — the judge is a model too, and it has its own biases
3. `pairwise-vs-absolute-scoring` — why A-or-B is easier to get right than 1-to-5
4. `eval-for-classification-tasks` — the confusion matrix still applies, and it still helps
5. `regression-testing-prompts` — a pytest suite that fails on a prompt edit, not on the weather

<details><summary>Dự trữ trong cụm — 10 chủ đề</summary>

- `golden-outputs-for-llms` — snapshot testing when the output is not deterministic
- `measuring-hallucination` — grounding checks that are cheaper than a human read
- `eval-driven-prompt-iteration` — changing one thing at a time when the metric is noisy
- `statistical-significance-small-evals` — how many cases before a 3-point move means anything
- `online-vs-offline-evaluation` — the production signal your test set cannot give you
- `annotation-guidelines-that-work` — getting two humans to agree before you ask a model to
- `eval-cost-control` — sampling and caching so the suite runs on every PR
- `red-teaming-your-own-feature` — finding the inputs that break it before a user does
- `multi-turn-conversation-evals` — scoring a dialogue when each turn depends on the last
- `eval-dashboards-that-get-read` — the four numbers worth putting on a wall

</details>

## Ngày 7 — 2026-09-07 (Thứ Hai) · 🐦 Flutter · Forms & input

**7 bài** (14 file EN+VI)

1. `flutter-form-validation-patterns` — Form, FormField and the validation timing users expect
2. `flutter-textfield-controllers-focus` — controllers, focus nodes and the disposal that gets forgotten
3. `flutter-input-formatters` — masking phone numbers and currency without fighting the cursor
4. `flutter-keyboard-avoidance` — the layout that actually scrolls the focused field into view
5. `flutter-autofill-and-password-managers` — the hints that make iOS and Android fill your form
6. `flutter-custom-form-field` — wrapping any widget in FormField so validation just works
7. `flutter-debounced-search-field` — typing-ahead search that does not hammer the API

<details><summary>Dự trữ trong cụm — 8 chủ đề</summary>

- `flutter-date-time-pickers` — platform pickers, custom pickers, and time zones
- `flutter-multi-step-form-wizard` — state that survives back-navigation between steps
- `flutter-file-and-image-picking` — permissions, cancellation, and the paths that expire
- `flutter-rich-text-editing` — when TextField stops being enough
- `flutter-form-accessibility` — labels, errors and focus order a screen reader can follow
- `flutter-input-error-messaging` — error text that tells the user what to do next
- `flutter-form-testing` — driving a form in a widget test, including the keyboard
- `flutter-offline-form-submission` — queueing a submit when the network is not there

</details>

## Ngày 8 — 2026-09-08 (Thứ Ba) · 🤖 AI/Dev · Prompt patterns in production

**7 bài** (14 file EN+VI)

1. `system-prompt-structure` — the ordering that makes caching and comprehension both work
2. `few-shot-examples-that-earn-their-tokens` — picking examples by the errors they prevent
3. `prompt-versioning-and-rollback` — treating the prompt as a deployable artifact
4. `delimiters-and-injection-resistance` — separating instructions from data you did not write
5. `chain-of-thought-when-it-helps` — the task shapes where reasoning pays, and where it costs
6. `output-length-control` — getting short answers without losing the content
7. `prompt-templates-and-escaping` — the user input that quietly breaks your template

<details><summary>Dự trữ trong cụm — 8 chủ đề</summary>

- `role-and-persona-prompts` — what a persona actually changes, and what it does not
- `negative-instructions-problem` — why 'do not' underperforms 'instead, do'
- `prompt-compression-techniques` — cutting a prompt in half without losing behaviour
- `multilingual-prompting` — instruction language, content language, and output language
- `prompt-testing-across-models` — what breaks when you swap the model underneath
- `dynamic-prompt-assembly` — building a prompt from retrieved parts without a mess
- `prompt-library-organisation` — where prompts live in a repo so they get reviewed
- `meta-prompting-write-the-prompt` — using a model to draft prompts, and checking its work

</details>

## Ngày 9 — 2026-09-09 (Thứ Tư) · 🐦 Flutter · Networking & the data layer

**7 bài** (14 file EN+VI)

1. `flutter-http-client-choices` — http, dio and the standard library, judged on what you need
2. `flutter-repository-pattern` — the seam that makes your data layer testable
3. `flutter-json-serialization` — hand-written, code-gen and macros, with the migration cost
4. `flutter-error-handling-network` — turning exceptions into states the UI can render
5. `flutter-retry-and-backoff` — retrying safely when the request is not idempotent
6. `flutter-request-cancellation` — cancelling in-flight work when the screen disappears
7. `flutter-api-caching-layer` — stale-while-revalidate without a full offline stack

<details><summary>Dự trữ trong cụm — 8 chủ đề</summary>

- `flutter-auth-token-refresh` — one refresh, many queued requests, no thundering herd
- `flutter-graphql-vs-rest` — what changes in the client when the API shape changes
- `flutter-websocket-realtime` — reconnection, heartbeat and the state machine you need
- `flutter-file-upload-progress` — multipart uploads with progress and resume
- `flutter-mocking-http-in-tests` — fake clients that fail the way the network fails
- `flutter-pagination-cursor-vs-offset` — the client-side difference and why cursors win
- `flutter-network-inspector-devtools` — reading the Network tab back to your Dart code
- `flutter-certificate-pinning` — pinning that does not brick your app on rotation

</details>

## Ngày 10 — 2026-09-10 (Thứ Năm) · 🤖 AI/Dev · Fine-tuning & adapters

**7 bài** (14 file EN+VI)

1. `when-fine-tuning-is-the-answer` — the three symptoms that prompting cannot fix
2. `dataset-construction-for-finetuning` — the format, the size question, and the leakage trap
3. `lora-explained-by-the-maths` — low-rank updates, and what rank actually buys you
4. `qlora-and-quantised-training` — training on hardware you already own
5. `finetuning-hyperparameters` — the four knobs worth touching, and their symptoms
6. `catastrophic-forgetting` — why the model got worse at everything else
7. `evaluating-a-finetune` — the held-out set that tells you it worked

<details><summary>Dự trữ trong cụm — 8 chủ đề</summary>

- `serving-multiple-adapters` — one base model, many LoRAs, one GPU
- `instruction-tuning-vs-domain-tuning` — two different goals that need different data
- `preference-tuning-basics` — DPO-style alignment in terms a builder can act on
- `synthetic-training-data` — generating data without training on your own noise
- `finetuning-for-structured-output` — when a schema is cheaper than a finetune
- `finetune-deployment-and-rollback` — shipping weights like you ship code
- `cost-of-a-finetune` — the arithmetic before you commit the GPU hours
- `finetuning-small-models` — where a tuned small model beats an untuned large one

</details>

## Ngày 11 — 2026-09-11 (Thứ Sáu) · 🐦 Flutter · Persistence & local storage

**7 bài** (14 file EN+VI)

1. `flutter-storage-options-compared` — prefs, secure storage, files, SQLite and the object stores
2. `flutter-shared-preferences-limits` — what it is for, and the day it stops being enough
3. `flutter-secure-storage-keychain` — Keychain and Keystore, and what 'secure' actually covers
4. `flutter-sqlite-migrations` — schema versions that survive an app-store update
5. `flutter-drift-queries-and-joins` — type-safe SQL without giving up SQL
6. `flutter-file-io-paths` — documents, support, cache: which directory survives what
7. `flutter-large-file-handling` — streaming instead of loading 200MB into memory

<details><summary>Dự trữ trong cụm — 8 chủ đề</summary>

- `flutter-database-in-an-isolate` — keeping queries off the UI thread
- `flutter-data-encryption-at-rest` — encrypting a local database, and where the key lives
- `flutter-backup-and-restore` — letting users take their data with them
- `flutter-cache-eviction-policy` — deciding what to delete before the OS decides for you
- `flutter-hive-and-object-stores` — the NoSQL option and its honest trade-offs
- `flutter-testing-the-data-layer` — in-memory databases and deterministic fixtures
- `flutter-data-migration-between-stores` — moving from prefs to SQLite without losing users
- `flutter-storage-debugging` — inspecting on-device data during development

</details>

## Ngày 12 — 2026-09-12 (Thứ Bảy) · 🤖 AI/Dev · Inference serving & ops

**5 bài** (10 file EN+VI)

1. `inference-server-basics` — what sits between your app and the weights
2. `continuous-batching-explained` — why throughput and latency stop being the same trade
3. `kv-cache-management` — the memory that decides your concurrency ceiling
4. `speculative-decoding` — a small model guessing for a large one
5. `gpu-memory-planning` — sizing a deployment before you rent the card

<details><summary>Dự trữ trong cụm — 10 chủ đề</summary>

- `autoscaling-llm-workloads` — cold starts when the model takes minutes to load
- `request-queueing-and-admission` — shedding load before the queue eats your latency
- `streaming-responses-end-to-end` — SSE from server to client without buffering surprises
- `multi-tenant-inference` — fairness when one user sends 100k tokens
- `model-warm-pools` — paying idle cost to avoid a cold-start cliff
- `inference-latency-budget` — TTFT, ITL and the number your users actually feel
- `gpu-vs-cpu-inference` — the model sizes where CPU is not ridiculous
- `failover-between-providers` — a router that survives one provider's bad afternoon
- `inference-observability` — the metrics that catch a regression before support does
- `batch-inference-pipelines` — offline jobs where latency does not matter and cost does

</details>

## Ngày 13 — 2026-09-13 (Chủ Nhật) · 🐦 Flutter · Accessibility

**5 bài** (10 file EN+VI)

1. `flutter-accessibility-first-pass` — the ten-minute audit that finds most of it
2. `flutter-semantics-tree` — what the accessibility tree is, and how to read yours
3. `flutter-screen-reader-testing` — driving TalkBack and VoiceOver over your own app
4. `flutter-semantic-labels` — labels, hints and values, and the difference that matters
5. `flutter-focus-order-keyboard` — traversal that follows the visual order

<details><summary>Dự trữ trong cụm — 10 chủ đề</summary>

- `flutter-text-scaling` — surviving a 200% font scale without clipping
- `flutter-colour-contrast` — meeting contrast ratios in a themed app
- `flutter-touch-target-sizes` — the minimum size, and where designs break it
- `flutter-reduce-motion` — respecting the OS setting in your animations
- `flutter-accessible-forms` — errors a screen reader announces at the right moment
- `flutter-live-regions` — announcing async changes without stealing focus
- `flutter-excluding-decorative-widgets` — hiding the noise from assistive tech
- `flutter-accessibility-in-tests` — asserting semantics in widget tests
- `flutter-accessible-custom-widgets` — giving a CustomPaint widget a meaning
- `flutter-accessibility-ci-gate` — catching regressions automatically

</details>

## Ngày 14 — 2026-09-14 (Thứ Hai) · 🤖 AI/Dev · Multimodal

**7 bài** (14 file EN+VI)

1. `vision-models-what-they-see` — resolution, tiling, and why your chart was misread
2. `document-understanding-pdfs` — layout-aware extraction versus naive text dumps
3. `ocr-versus-vision-models` — the tasks where classical OCR still wins
4. `image-input-cost-and-tokens` — how images are billed, and how to shrink the bill
5. `screenshot-driven-ui-testing` — a model reading your UI, and where it is unreliable
6. `audio-transcription-pipelines` — diarisation, timestamps and the long-file problem
7. `text-to-speech-in-products` — latency, streaming and the voice-consistency problem

<details><summary>Dự trữ trong cụm — 8 chủ đề</summary>

- `video-understanding-basics` — frame sampling that keeps the signal
- `multimodal-rag` — retrieving images and text into the same context
- `chart-and-table-extraction` — structured output from a picture of a table
- `image-generation-in-products` — prompt control, consistency and the moderation layer
- `multimodal-evals` — scoring an answer that depends on a picture
- `on-device-vision` — the small models that run in your app
- `multimodal-prompt-injection` — an instruction hidden inside an image
- `choosing-a-multimodal-model` — the capability matrix that matters for your task

</details>

## Ngày 15 — 2026-09-15 (Thứ Ba) · 🐦 Flutter · i18n & text rendering

**7 bài** (14 file EN+VI)

1. `flutter-localization-setup` — ARB files, gen-l10n, and a workflow translators can use
2. `flutter-plurals-and-genders` — ICU messages that read correctly in every locale
3. `flutter-date-number-formatting` — intl, locales and the timezone bugs behind them
4. `flutter-rtl-layouts` — mirroring a UI properly, not just flipping it
5. `flutter-font-fallback-cjk` — when your font has no glyph and the box appears
6. `flutter-text-overflow-strategies` — ellipsis, fade and the layout that avoids both
7. `flutter-rich-text-spans` — TextSpan, WidgetSpan and tappable inline links

<details><summary>Dự trữ trong cụm — 8 chủ đề</summary>

- `flutter-custom-fonts-subsetting` — shipping a font without shipping 8MB
- `flutter-text-selection-and-copy` — selectable text that behaves like the platform
- `flutter-markdown-rendering` — rendering untrusted markdown safely
- `flutter-locale-switching-runtime` — changing language without restarting the app
- `flutter-translation-keys-hygiene` — naming keys so context survives the spreadsheet
- `flutter-pseudolocalization` — finding layout breakage before the translations land
- `flutter-text-measurement` — measuring text off-screen when you need the height
- `flutter-i18n-testing` — asserting a screen in three locales

</details>

## Ngày 16 — 2026-09-16 (Thứ Tư) · 🤖 AI/Dev · Data pipelines for AI

**7 bài** (14 file EN+VI)

1. `ingestion-pipeline-shape` — source to chunk to vector, with the failure points named
2. `document-parsing-formats` — PDF, DOCX, HTML and the ones that need special handling
3. `incremental-reindexing` — updating an index when 3 of 40,000 documents changed
4. `deduplication-at-scale` — near-duplicate detection before it pollutes retrieval
5. `pii-detection-and-redaction` — stripping what should never reach a model
6. `data-quality-gates` — the checks that stop bad documents entering the index
7. `metadata-schema-design` — the fields you will wish you had captured

<details><summary>Dự trữ trong cụm — 8 chủ đề</summary>

- `pipeline-idempotency` — re-running a job without doubling the corpus
- `streaming-vs-batch-ingestion` — freshness against cost, decided by the use case
- `handling-permissions-in-rag` — retrieval that respects who is asking
- `pipeline-observability` — knowing which stage dropped the document
- `versioning-your-corpus` — reproducing a retrieval result from last month
- `multi-source-normalisation` — one schema over Slack, Notion and a wiki
- `cost-of-an-ingestion-run` — the arithmetic before you index 10 million documents
- `pipeline-testing-fixtures` — a small corpus that exercises every branch

</details>

## Ngày 17 — 2026-09-17 (Thứ Năm) · 🐦 Flutter · Images, media & camera

**7 bài** (14 file EN+VI)

1. `flutter-image-widget-deep-dive` — the decode pipeline behind one Image widget
2. `flutter-image-caching-strategy` — memory cache, disk cache, and the eviction you control
3. `flutter-svg-and-vector-assets` — vectors that scale without a runtime cost surprise
4. `flutter-camera-plugin-guide` — preview, capture, orientation and the lifecycle traps
5. `flutter-image-compression` — shrinking an upload without destroying it
6. `flutter-video-playback` — controllers, lifecycle and the black-frame problem
7. `flutter-audio-playback-background` — keeping audio alive when the app is not

<details><summary>Dự trữ trong cụm — 8 chủ đề</summary>

- `flutter-image-cropping-editing` — a crop UI that respects EXIF orientation
- `flutter-gallery-permissions` — the permission flows on both platforms, honestly
- `flutter-thumbnail-generation` — generating previews off the UI thread
- `flutter-progressive-image-loading` — placeholder to blur to full, without layout shift
- `flutter-custom-image-provider` — your own ImageProvider for a non-standard source
- `flutter-media-memory-profiling` — finding the screen that holds 300MB of bitmaps
- `flutter-shader-and-image-filters` — blur, colour and the cost of each
- `flutter-media-testing` — widget tests that do not need a real camera

</details>

## Ngày 18 — 2026-09-18 (Thứ Sáu) · 🤖 AI/Dev · AI coding workflows

**7 bài** (14 file EN+VI)

1. `repo-conventions-file-for-agents` — the file that stops an agent guessing your house style
2. `scoping-a-task-for-an-agent` — the brief that gets a usable diff on the first try
3. `reviewing-agent-written-code` — what to read first when you did not write it
4. `agent-assisted-refactoring` — mechanical changes across 200 files, verified
5. `test-first-with-an-agent` — writing the test before the implementation, on purpose
6. `agents-and-legacy-code` — using a model to understand code nobody remembers
7. `commit-hygiene-with-agents` — diffs that a human reviewer can actually follow

<details><summary>Dự trữ trong cụm — 8 chủ đề</summary>

- `agent-guardrails-in-a-repo` — hooks and checks that catch the bad edit early
- `debugging-with-an-agent` — handing over a stack trace so the answer is not a guess
- `documentation-that-agents-maintain` — docs that stay true because they are checked
- `migration-projects-with-agents` — framework upgrades as a repeatable pipeline
- `when-not-to-use-an-agent` — the tasks where typing it yourself is faster
- `agent-context-for-monorepos` — pointing at the right 2% of a large repo
- `pair-programming-with-a-model` — the interaction loop that stays productive
- `measuring-agent-productivity` — what to measure instead of lines of code

</details>

## Ngày 19 — 2026-09-19 (Thứ Bảy) · 🐦 Flutter · Background work & notifications

**5 bài** (10 file EN+VI)

1. `flutter-background-execution-limits` — what each OS actually permits, stated plainly
2. `flutter-workmanager-scheduling` — deferred work that survives a reboot
3. `flutter-background-fetch-ios` — iOS background modes and their real cadence
4. `flutter-foreground-service-android` — long-running work with a visible notification
5. `flutter-local-notifications` — scheduling, channels, and the permission prompt

<details><summary>Dự trữ trong cụm — 10 chủ đề</summary>

- `flutter-push-notifications-setup` — FCM and APNs end to end, including the failures
- `flutter-notification-deep-links` — tapping a notification into the right screen state
- `flutter-background-sync-strategy` — when to sync, and how not to drain the battery
- `flutter-app-lifecycle-states` — what resumed, inactive and paused mean per platform
- `flutter-background-downloads` — large downloads that continue when backgrounded
- `flutter-geofencing-and-location` — background location without the permission rejection
- `flutter-silent-push-processing` — data-only messages and their delivery guarantees
- `flutter-notification-testing` — testing something the simulator will not deliver
- `flutter-battery-and-doze` — Doze, App Standby and what they do to your schedule
- `flutter-background-work-debugging` — logs from a process you cannot attach to

</details>

## Ngày 20 — 2026-09-20 (Chủ Nhật) · 🤖 AI/Dev · Cost & performance engineering

**5 bài** (10 file EN+VI)

1. `token-accounting-basics` — counting before you optimise
2. `model-routing-by-difficulty` — the cheap model first, escalation on failure
3. `caching-layers-for-llm-apps` — exact-match, semantic and prompt cache, stacked
4. `batch-api-economics` — the work that can wait, and what it saves
5. `context-window-budgeting` — spending tokens where they change the answer

<details><summary>Dự trữ trong cụm — 10 chủ đề</summary>

- `retrieval-cost-vs-quality` — the k that stops paying for itself
- `output-token-reduction` — structured output as a cost lever
- `cost-attribution-per-feature` — knowing which feature is eating the budget
- `rate-limits-and-concurrency` — designing for the limit instead of retrying into it
- `cost-alerting-and-budgets` — the alarm before the invoice
- `self-hosting-break-even` — the volume where your own GPU is cheaper
- `prompt-cache-hit-rate` — measuring it, then raising it
- `latency-vs-cost-trade-offs` — the choices users notice and the ones they do not
- `cost-regression-testing` — a CI check on tokens per request
- `free-tier-engineering` — building within the limits on purpose

</details>

## Ngày 21 — 2026-09-21 (Thứ Hai) · 🐦 Flutter · Build, release & CI/CD

**7 bài** (14 file EN+VI)

1. `flutter-flavors-setup` — dev, staging and prod without three codebases
2. `flutter-build-configuration` — dart-define, env files and secrets that stay out of git
3. `flutter-code-signing-ios` — certificates, profiles and the CI that renews them
4. `flutter-android-signing-play` — keystores, Play App Signing and the recovery plan
5. `flutter-ci-github-actions` — a pipeline that builds, tests and ships
6. `flutter-fastlane-basics` — automating the store upload
7. `flutter-app-size-reduction` — finding and cutting the megabytes that matter

<details><summary>Dự trữ trong cụm — 8 chủ đề</summary>

- `flutter-obfuscation-and-symbols` — obfuscating without losing readable crash reports
- `flutter-staged-rollouts` — shipping to 5% and knowing when to stop
- `flutter-crash-reporting` — symbolicated stack traces from release builds
- `flutter-over-the-air-updates` — what is allowed, and what gets you rejected
- `flutter-versioning-strategy` — build numbers that never collide
- `flutter-store-review-rejections` — the recurring reasons, and how to avoid them
- `flutter-release-checklist` — the list worth running before every submission
- `flutter-build-caching-ci` — cutting CI time without stale-artifact bugs

</details>

## Ngày 22 — 2026-09-22 (Thứ Ba) · 🤖 AI/Dev · Safety, privacy & compliance

**7 bài** (14 file EN+VI)

1. `prompt-injection-defence` — the layers that actually reduce the risk
2. `data-retention-for-llm-apps` — what you keep, for how long, and where
3. `pii-and-model-providers` — the questions to ask before sending user data
4. `output-moderation-pipeline` — checking a response before the user sees it
5. `consent-and-transparency-ux` — telling users AI is involved, usefully
6. `audit-logging-ai-decisions` — the record you will need when someone asks why
7. `jailbreak-resistance-testing` — adversarial inputs as a test suite

<details><summary>Dự trữ trong cụm — 8 chủ đề</summary>

- `least-privilege-for-agents` — scoping credentials an agent can reach
- `data-residency-constraints` — when the model has to run in a specific country
- `model-cards-and-disclosure` — documenting what your feature can and cannot do
- `bias-testing-in-features` — measuring outcome differences across groups
- `secure-tool-execution` — running generated code without running your machine
- `incident-response-for-ai` — what to do when the model says something bad
- `third-party-risk-ai-vendors` — the diligence that is not security theatre
- `privacy-preserving-analytics` — learning from usage without storing prompts

</details>

## Ngày 23 — 2026-09-23 (Thứ Tư) · 🐦 Flutter · Security on mobile

**7 bài** (14 file EN+VI)

1. `mobile-threat-model-basics` — the attacker who has your APK, and what they can do
2. `flutter-api-key-handling` — why the key in your binary is already public
3. `flutter-root-jailbreak-detection` — what it buys, and what it does not
4. `flutter-biometric-authentication` — local_auth, and what a successful check proves
5. `flutter-oauth-pkce-flow` — the correct mobile OAuth flow, step by step
6. `flutter-session-and-token-storage` — where tokens live, and their lifetime
7. `flutter-tls-and-pinning` — pinning without the outage

<details><summary>Dự trữ trong cụm — 8 chủ đề</summary>

- `flutter-reverse-engineering-defence` — raising the cost, honestly measured
- `flutter-webview-security` — the settings that make an embedded WebView safe
- `flutter-deep-link-validation` — an incoming URL is untrusted input
- `flutter-clipboard-and-screenshots` — protecting sensitive screens
- `flutter-dependency-auditing` — knowing what your 400 transitive packages do
- `flutter-secure-logging` — logs that do not leak the user
- `flutter-permission-minimisation` — asking for less and explaining why
- `flutter-security-testing` — the checks worth automating

</details>

## Ngày 24 — 2026-09-24 (Thứ Năm) · 🤖 AI/Dev · Retrieval architecture

**7 bài** (14 file EN+VI)

1. `rag-reference-architecture` — the boxes, and what each one owns
2. `query-rewriting-and-expansion` — fixing the question before searching
3. `multi-hop-retrieval` — questions that need two lookups
4. `reranking-in-the-pipeline` — where it goes, and what it costs
5. `retrieval-for-code` — why code needs different chunking
6. `structured-plus-unstructured` — joining a database answer to a document answer
7. `citation-and-grounding` — answers that point back at their evidence

<details><summary>Dự trữ trong cụm — 8 chủ đề</summary>

- `handling-no-good-answer` — the case your demo never tested
- `conversational-retrieval` — resolving 'it' against the last three turns
- `freshness-in-retrieval` — recency as a ranking signal, not a filter
- `retrieval-latency-optimisation` — the stages worth parallelising
- `graph-retrieval-basics` — when relationships beat similarity
- `long-context-vs-retrieval` — the crossover point, and how to find yours
- `retrieval-failure-taxonomy` — naming the five ways it goes wrong
- `incremental-rag-rollout` — shipping retrieval to one surface first

</details>

## Ngày 25 — 2026-09-25 (Thứ Sáu) · 🐦 Flutter · Desktop & multi-window

**7 bài** (14 file EN+VI)

1. `flutter-desktop-state-2026` — what is production-ready and what still is not
2. `flutter-window-management` — size, position and restoring where the user left it
3. `flutter-menus-and-shortcuts` — native menu bars and keyboard shortcuts
4. `flutter-drag-and-drop-desktop` — files in, files out
5. `flutter-system-tray` — background apps with a tray presence
6. `flutter-desktop-file-dialogs` — native pickers and sandboxed paths
7. `flutter-multi-window-patterns` — a second window that shares state correctly

<details><summary>Dự trữ trong cụm — 8 chủ đề</summary>

- `flutter-desktop-packaging` — MSIX, DMG and Linux packages
- `flutter-desktop-auto-update` — updating an app the store does not manage
- `flutter-mouse-and-hover` — cursors, hover states and right-click
- `flutter-desktop-text-editing` — the shortcuts users expect from a text field
- `flutter-desktop-performance` — where desktop differs from mobile
- `flutter-platform-integration-desktop` — talking to the OS from a desktop app
- `flutter-desktop-testing` — integration tests on a real window
- `flutter-desktop-distribution-signing` — notarisation and SmartScreen

</details>

## Ngày 26 — 2026-09-26 (Thứ Bảy) · 🤖 AI/Dev · Observability for LLM apps

**5 bài** (10 file EN+VI)

1. `what-to-log-in-an-llm-app` — the fields that make a trace useful later
2. `tracing-a-multi-step-chain` — spans that show where the time went
3. `sampling-strategies-for-traces` — keeping the interesting 1%
4. `user-feedback-signals` — thumbs, edits and abandonment as data
5. `detecting-quality-regressions` — the alert that fires before the tickets do

<details><summary>Dự trữ trong cụm — 10 chủ đề</summary>

- `prompt-and-version-tagging` — attributing a bad answer to a specific prompt
- `error-taxonomy-for-llm-features` — classifying failures so the fix is obvious
- `replaying-production-traffic` — testing a change against real inputs safely
- `dashboards-for-ai-features` — the panels an on-call engineer needs
- `slo-for-a-probabilistic-feature` — committing to something you can measure
- `cost-and-quality-on-one-chart` — seeing the trade-off as it moves
- `privacy-safe-trace-storage` — traces you are allowed to keep
- `anomaly-detection-on-outputs` — noticing the day the model changed
- `debugging-from-a-single-trace` — the workflow from ticket to root cause
- `observability-tooling-choices` — build, buy, or the middle path

</details>

## Ngày 27 — 2026-09-27 (Chủ Nhật) · 🐦 Flutter · Flutter web

**5 bài** (10 file EN+VI)

1. `flutter-web-when-it-fits` — the app shapes where it is the right call
2. `flutter-web-initial-load` — the first paint problem and what actually helps
3. `flutter-web-seo-reality` — what crawlers see, and the honest workarounds
4. `flutter-web-js-interop` — calling JavaScript from Dart the current way
5. `flutter-web-routing-and-history` — URLs that behave like a website

<details><summary>Dự trữ trong cụm — 10 chủ đề</summary>

- `flutter-web-responsive-desktop` — one codebase, mouse and touch
- `flutter-web-pwa-setup` — install prompts, offline and the service worker
- `flutter-web-embedding-in-a-page` — Flutter as a component inside an existing site
- `flutter-web-text-and-selection` — the text behaviours the web expects
- `flutter-web-file-handling` — upload and download in the browser sandbox
- `flutter-web-canvaskit-vs-html` — the renderers, their sizes and their trade-offs
- `flutter-web-performance-profiling` — browser devtools against a Flutter app
- `flutter-web-accessibility` — the accessibility layer and its limits
- `flutter-web-deployment` — hosting, headers and caching
- `flutter-web-debugging-production` — source maps and release-mode bugs

</details>

## Ngày 28 — 2026-09-28 (Thứ Hai) · 🤖 AI/Dev · Small models & the edge

**7 bài** (14 file EN+VI)

1. `small-model-capability-map` — what fits under 8B, task by task
2. `distillation-basics` — teaching a small model from a large one
3. `quantisation-formats-explained` — GGUF, AWQ, GPTQ and what each costs you
4. `on-device-inference-mobile` — running a model inside your app
5. `edge-deployment-constraints` — memory, thermal and battery as design inputs
6. `hybrid-local-and-cloud` — routing between the phone and the API
7. `small-models-for-classification` — the task where small models are simply correct

<details><summary>Dự trữ trong cụm — 8 chủ đề</summary>

- `embedding-models-on-device` — local semantic search with no server
- `model-loading-and-warmup` — the first-run experience
- `privacy-as-a-product-feature` — shipping local inference as the selling point
- `benchmarking-on-your-own-hardware` — the numbers that generalise to your users
- `model-update-distribution` — shipping new weights to installed apps
- `fallback-when-local-fails` — degrading to the cloud gracefully
- `tooling-for-edge-models` — the runtimes worth knowing
- `small-model-fine-tuning` — specialising a small model for one job

</details>

## Ngày 29 — 2026-09-29 (Thứ Ba) · 🐦 Flutter · Dart language & tooling

**7 bài** (14 file EN+VI)

1. `dart-null-safety-in-practice` — the patterns that remove the bang operator
2. `dart-pattern-matching` — records, patterns and the code they replace
3. `dart-sealed-classes-state` — exhaustive state without a default case
4. `dart-extension-methods` — extending a type you do not own, tastefully
5. `dart-mixins-explained` — what a mixin is, and when it beats composition
6. `dart-generics-and-variance` — the type errors that stop being mysterious
7. `dart-async-await-internals` — the event loop under your await

<details><summary>Dự trữ trong cụm — 8 chủ đề</summary>

- `dart-streams-deep-dive` — single, broadcast, and the subscription you forgot
- `dart-error-handling-patterns` — exceptions, results, and picking one
- `dart-code-generation` — build_runner, and the cost of generated code
- `dart-analyzer-and-lints` — a lint set your team will not disable
- `dart-macros-status` — what they change, and what to do meanwhile
- `dart-package-publishing` — publishing to pub.dev, including the boring parts
- `dart-cli-tools` — writing a command-line tool in Dart
- `dart-performance-idioms` — the allocations worth avoiding in hot code

</details>

## Ngày 30 — 2026-09-30 (Thứ Tư) · 🤖 AI/Dev · AI product & UX patterns

**7 bài** (14 file EN+VI)

1. `designing-for-model-uncertainty` — an interface that admits it might be wrong
2. `streaming-ui-patterns` — what to show while the tokens arrive
3. `edit-not-regenerate` — letting users fix instead of reroll
4. `progressive-disclosure-of-reasoning` — showing the work without a wall of text
5. `empty-and-error-states-ai` — the states teams forget to design
6. `undo-for-ai-actions` — reversibility as a trust mechanism
7. `suggestion-versus-automation` — where on the spectrum your feature belongs

<details><summary>Dự trữ trong cụm — 8 chủ đề</summary>

- `onboarding-an-ai-feature` — teaching the mental model in three screens
- `feedback-loops-in-the-ui` — collecting signal without nagging
- `latency-perception-tricks` — the honest ones, and the ones that backfire
- `multi-turn-interface-design` — conversation is not always the right shape
- `attribution-and-sources-ui` — citations users actually click
- `cost-visible-features` — when to show the user what it costs
- `ai-feature-discoverability` — the feature nobody found
- `measuring-ai-feature-success` — the metric beyond engagement

</details>

---

## Sau tháng 9

Kho dự trữ còn **256 chủ đề** đã có slug và góc nhìn, giữ nguyên cụm — đủ chạy hết
tháng 10 và phần lớn tháng 11 ở cùng nhịp mà không phải lên ý tưởng lại.

Ba cụm đáng bổ sung khi kho cạn:

- **Kiến trúc ứng dụng Flutter** — modularisation, dependency injection, feature-first structure
- **Nền tảng dữ liệu** — Postgres, hàng đợi, event sourcing cho backend của app mobile
- **Tổng kết theo bản phát hành** — bám release Flutter/Dart, viết trong tuần nó ra
