# Content Plan: 20 OSS Projects + 20 New Flutter Features

Branch: `content/flutter-oss-features-2026`
Worktree: `/Users/trunghieuvn/GitHub/fluttercook-content-2026`
Date: 2026-09-10
Target: fluttercook.github.io + trunghieu-it.blogspot.com (+ fluttercook.blogspot.com)

Each topic = **one EN post** (`src/content/blog/<slug>.md`) + **one VI post** (`src/content/blog-vi/<slug>.md`).
Hero images live at `public/blog/images/<slug>.png` and are referenced as `/blog/images/<slug>.png`.

---

## Part A — 20 New Flutter Features (3.41 → 3.47, 2026)

| # | Slug | Focus | Release |
|---|------|-------|---------|
| 1 | `flutter-standalone-material-ui-cupertino-ui` | Standalone `material_ui` / `cupertino_ui` 1.0, migration, compat bridge | 3.47 |
| 2 | `flutter-impeller-default-desktop` | Impeller default on macOS/Windows/Linux, SDF text, opt-out | 3.47 |
| 3 | `flutter-swift-package-manager-default` | SwiftPM replaces CocoaPods as default; plugin migration | 3.44 |
| 4 | `flutter-hybrid-composition-plus-plus` | HCPP platform views, Vulkan SurfaceControl, enable flag | 3.44 |
| 5 | `flutter-agentic-hot-reload` | Agentic Hot Reload + MCP auto-connect to running apps | 3.44 |
| 6 | `flutter-agent-skills-mcp` | Dart/Flutter Agent Skills + MCP tool consolidation | 3.44 |
| 7 | `flutter-genui-a2ui` | GenUI SDK, A2UI protocol, generative UI beyond chat text | 3.44 |
| 8 | `flutter-firebase-ai-logic` | Firebase AI Logic, Server Prompt Templates, Gemini client-side | 3.44 |
| 9 | `flutter-genkit-dart` | Genkit Dart full-stack AI apps from Flutter | 3.44 |
| 10 | `flutter-widget-previews-stable` | Widget Previewer stable, caching, PreviewThemeData | 3.47 |
| 11 | `flutter-multi-window-desktop` | Multi-window APIs, popups, windowHandle, Canonical | 3.44/3.47 |
| 12 | `flutter-desktop-flavors` | Flavors on Windows/Linux + assets per flavor | 3.47 |
| 13 | `flutter-wasm-deferred-loading` | Wasm by default path + deferred loading flag | 3.47 |
| 14 | `flutter-platform-specific-assets` | `platforms:` in pubspec assets | 3.41 |
| 15 | `flutter-uiscene-ios-lifecycle` | UIScene mandate, iOS 27, min iOS 15 | 3.47 |
| 16 | `flutter-fragment-shader-api` | getUniform by name, sync image decode, high-bit textures | 3.41/3.44 |
| 17 | `flutter-cupertino-menu-anchor` | CupertinoMenuAnchor + RawMenuAnchor menus | 3.44 |
| 18 | `flutter-content-sized-views` | Add-to-App content-sized FlutterView | 3.41 |
| 19 | `flutter-public-release-windows` | Public release windows / branch cutoffs 2026 | 3.41 |
| 20 | `flutter-gemma-litert-ondevice` | flutter_gemma, LiteRT-LM, on-device Gemma 4 | 3.44 |

## Part B — 20 Open-Source Flutter Projects

Deep architecture / learning posts (not thin star-count recipes).

| # | Slug | Project | Why learn from it |
|---|------|---------|-------------------|
| 1 | `oss-immich-architecture` | [immich-app/immich](https://github.com/immich-app/immich) | Large-scale photo backup UI, performance, offline |
| 2 | `oss-spotube-architecture` | [KRTirtho/spotube](https://github.com/KRTirtho/spotube) | Music client, platform channels, media |
| 3 | `oss-fluffychat-architecture` | [fluffychat/fluffychat](https://github.com/fluffychat/fluffychat) | Matrix chat, E2EE UX, multi-platform |
| 4 | `oss-localsend-architecture` | [localsend/localsend](https://github.com/localsend/localsend) | LAN protocol, desktop+mobile, zero backend |
| 5 | `oss-rustdesk-flutter` | [rustdesk/rustdesk](https://github.com/rustdesk/rustdesk) | Rust core + Flutter shell hybrid |
| 6 | `oss-hiddify-next` | [hiddify/hiddify-app](https://github.com/hiddify/hiddify-app) | VPN client, network stack, cross-platform |
| 7 | `oss-ente-photos` | [ente-io/ente](https://github.com/ente-io/ente) | Encrypted photos, crypto UX in Flutter |
| 8 | `oss-saber-notes` | [saber/saber](https://github.com/saber/saber) | Handwriting notes, canvas, local-first |
| 9 | `oss-flutter-deer` | [OpenFlutter/flutter_deer](https://github.com/OpenFlutter/flutter_deer) | Classic multi-flavor production template |
| 10 | `oss-flame-engine` | [flame-engine/flame](https://github.com/flame-engine/flame) | Game engine on Flutter, component tree |
| 11 | `oss-jaspr-dart-web` | [schultek/jaspr](https://github.com/schultek/jaspr) | Server-driven Dart web, Flutter mental model |
| 12 | `oss-shadcn-flutter` | [nank1ro/shadcn-flutter](https://github.com/nank1ro/shadcn-flutter) | Design-system porting, tokens |
| 13 | `oss-forui` | [forui-dev/forui](https://github.com/forui-dev/forui) | Opinionated Material alternative |
| 14 | `oss-lotti-journal` | [lotti/lotti](https://github.com/lotti/lotti) | Journaling, audio, complex local DB |
| 15 | `oss-venera-reader` | [venera-app/venera](https://github.com/venera-app/venera) | Comic reader, custom layout, caching |
| 16 | `oss-harmony-music` | (search current) Harmony Music player | Offline music player patterns |
| 17 | `oss-aegis-authenticator` | [beemdevelopment/Aegis](https://github.com/beemdevelopment/Aegis) | Security-sensitive mobile UX |
| 18 | `oss-cashew-budget` | [guysmiley7/cashew](https://github.com/guysmiley7/cashew) | Finance UI, charts, local persistence |
| 19 | `oss-serverpod` | [serverpod/serverpod](https://github.com/serverpod/serverpod) | Full-stack Dart, codegen, Flutter client |
| 20 | `oss-bloc-architecture` | [felangel/bloc](https://github.com/felangel/bloc) | Canonical state-management architecture |

> Verify GitHub URLs and star counts at write time via `webfetch` of the repo page or GitHub API. If a repo moved, use the live URL.

---

## SEO requirements (every post)

1. **Frontmatter** must include: title, description, seoDescription, keywords (8–12), category, topic, level, author, publishDate, emoji, tags, sources (3–8 real URLs), related (2–3 sibling slugs), draft:false.
2. **Title**: ≤ 70 chars, includes primary keyword, not clickbait.
3. **seoDescription**: 140–160 chars, includes primary + secondary keyword.
4. **H2 structure**: intro hook → what it is → why it matters 2026 → how to use (code) → pitfalls → FAQ-ish close → sources.
5. **Images**: each post embeds `![alt text](/blog/images/<slug>.png)` after the first H2. Alt text must describe the diagram, not “image”.
6. **Internal links**: 2–3 `related` + at least one markdown link to a sibling article path `/blog/<slug>/`.
7. **Length**: EN 900–1400 words body; VI is a full translation (not a summary), same structure.
8. **Voice**: match existing FlutterCook posts — concrete, cites docs/GitHub, no marketing fluff, no “in today’s fast-paced world”.

## Image style (shared)

- 1600×900 landscape PNG.
- Flat editorial diagram style: dark navy `#0B1220` background, cards `#152238`, accent cyan `#22D3EE`, secondary amber `#FBBF24`, text `#E5EEF8`.
- Max 5 labeled boxes + arrows. No photorealism, no tiny text under 24px.
- Prompt template uses the style above + topic-specific subject.

## Publish targets

1. `npm run build` in worktree.
2. `python3 scripts/publish_to_blogger.py --blog trunghieu-it --collection blog --lang en --slugs ... --publish`
3. Same for VI and for `--blog fluttercook` (may fail AUTHOR role — report status).
4. GitHub Pages push of the worktree branch after merge to main (user approval for push).
