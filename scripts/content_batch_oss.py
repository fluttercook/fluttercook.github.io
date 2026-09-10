"""20 open-source Flutter project architecture posts."""

def oss(
    slug, emoji, title_en, title_vi, desc_en, desc_vi, seo_en, seo_vi,
    keywords, tags, sources, related, body_en, body_vi,
):
    return {
        "slug": slug, "emoji": emoji,
        "category": "Deep Dive", "topic": "Open Source", "level": "Intermediate",
        "tags": tags, "title_en": title_en, "title_vi": title_vi,
        "desc_en": desc_en, "desc_vi": desc_vi,
        "seo_en": seo_en, "seo_vi": seo_vi,
        "keywords": keywords, "sources": sources, "related": related,
        "body_en": body_en, "body_vi": body_vi,
    }


OSS = [
    oss(
        "oss-immich-architecture", "📸",
        "Immich: architecture lessons from a 100k-star Flutter photo stack",
        "Immich: bài học kiến trúc từ stack ảnh Flutter 100k sao",
        "How Immich combines a Flutter mobile client, NestJS API, and ML pipeline — and which patterns you can steal.",
        "Immich ghép client Flutter, API NestJS và pipeline ML thế nào — và pattern nào bạn học được.",
        "Immich Flutter architecture deep dive: mobile client, background sync, self-hosted photo backup patterns to steal.",
        "Immich kiến trúc Flutter: client mobile, background sync, pattern backup ảnh self-hosted đáng học.",
        ["immich flutter", "immich architecture", "self hosted photo backup flutter", "immich mobile client", "flutter large scale app"],
        ["Flutter", "OpenSource", "Photos", "Architecture"],
        [("Immich GitHub", "https://github.com/immich-app/immich"), ("Immich docs", "https://immich.app/docs")],
        ["oss-ente-photos", "oss-localsend-architecture"],
        """Immich is the rare Flutter app most self-hosters have heard of: Google-Photos-like backup, albums, ML search, and a mobile client that must survive flaky networks and huge libraries.

![Immich architecture diagram](/blog/images/oss-immich-architecture.svg)

## What the stack actually is

- **Flutter mobile** clients for iOS/Android (plus web/desktop surfaces elsewhere in the monorepo).
- **NestJS** server with a generated API client — OpenAPI keeps mobile and server honest.
- **Python ML** services for CLIP-style search and recognition.
- **Docker** as the blessed install path for self-hosters.

## Patterns worth stealing

1. **Generated API clients.** Do not hand-write DTOs for a large domain.
2. **Background-first upload.** Treat sync as a product feature, not an afterthought.
3. **Server-owned thumbnails.** Mobile should not re-encode a 48MP original on a mid-range phone.

## Flutter-specific notes

Large galleries punish naive `GridView`s. Immich-style apps need aggressive view recycling, placeholder strategy, and careful isolate use for decode. Study how upload queues persist across app restarts.

## If you copy it naively

- Pulling the whole monorepo into a tiny app.
- Skipping authz on “local network” assumptions.
- Shipping ML search without a graceful empty/error path.

Steal the **client/server contract** and the **sync queue design**. Leave the Docker topology until you need it.
""",
        """Immich là app Flutter hiếm hoi dân self-host đều biết: backup kiểu Google Photos, album, tìm kiếm ML, và client mobile phải sống sót giữa mạng chập chờn cùng thư viện khổng lồ.

![Sơ đồ kiến trúc Immich](/blog/images/oss-immich-architecture.svg)

## Stack thực tế

- Client **Flutter** iOS/Android (cùng surface web/desktop trong monorepo).
- Server **NestJS** với API client sinh tự động — OpenAPI giữ mobile và server trung thực.
- Service **Python ML** cho tìm kiếm kiểu CLIP và nhận diện.
- **Docker** là đường cài đặt chính thức.

## Pattern đáng học

1. **API client sinh tự động.** Đừng viết tay DTO cho domain lớn.
2. **Upload theo nền.** Coi sync là feature sản phẩm, không phải việc thêm.
3. **Thumbnail do server giữ.** Mobile không nên re-encode ảnh 48MP trên phone tầm trung.

## Ghi chú Flutter

Gallery lớn phạt `GridView` ngây thơ. App kiểu Immich cần recycle view mạnh, chiến lược placeholder và isolate decode cẩn thận. Hãy học cách hàng đợi upload sống sót qua restart app.

## Nếu copy một cách ngây thơ

- Kéo cả monorepo vào app nhỏ.
- Bỏ authz vì giả định “mạng cục bộ”.
- Ship tìm kiếm ML không có path rỗng/lỗi.

Hãy học **hợp đồng client/server** và **thiết kế hàng đợi sync**. Docker topology để sau.
""",
    ),
    oss(
        "oss-spotube-architecture", "🎵",
        "Spotube: a privacy-minded Flutter music client",
        "Spotube: client nhạc Flutter ưu tiên privacy",
        "Riverpod, drift, media_kit, and a multi-store release story — how Spotube ships music without a first-party backend.",
        "Riverpod, drift, media_kit và story release đa store — Spotube ship nhạc không backend riêng ra sao.",
        "Spotube Flutter architecture: Riverpod state, drift database, media_kit audio, all-platform music client patterns.",
        "Spotube kiến trúc Flutter: state Riverpod, database drift, media_kit audio, pattern client nhạc đa nền tảng.",
        ["spotube flutter", "spotube architecture", "flutter music player open source", "media_kit flutter", "riverpod music app"],
        ["Flutter", "OpenSource", "Music", "Riverpod"],
        [("Spotube GitHub", "https://github.com/KRTirtho/spotube"), ("media_kit", "https://github.com/media-kit/media-kit")],
        ["oss-harmony-music", "oss-bloc-architecture"],
        """Spotube proves you can ship a polished music experience across mobile and desktop from one Flutter codebase — without owning the catalog backend.

![Spotube architecture](/blog/images/oss-spotube-architecture.svg)

## Stack signals

- **Riverpod** for state and DI.
- **drift** for durable local library data.
- **media_kit** (and related plugins) for playback across platforms.
- Store releases including F-Droid/Flathub — packaging is part of the product.

## What to steal

1. Separate *catalog search* from *local library* state.
2. Make playback a headless service with a thin UI shell.
3. Persist queue and position — music apps are resumed constantly.

## Pitfalls

- Platform audio APIs differ wildly (background modes, lock screens, Bluetooth).
- Legal/ToS constraints around third-party catalogs are not a Flutter problem, but they will kill the app faster than a jank frame.

Use Spotube as a map of the **plugin surface** a real media app needs.
""",
        """Spotube chứng minh bạn ship được trải nghiệm nhạc bóng bẩy đa mobile/desktop từ một codebase Flutter — không cần sở hữu backend catalog.

![Kiến trúc Spotube](/blog/images/oss-spotube-architecture.svg)

## Tín hiệu stack

- **Riverpod** cho state và DI.
- **drift** cho dữ liệu thư viện bền vững.
- **media_kit** (và plugin liên quan) cho playback đa nền tảng.
- Release store gồm F-Droid/Flathub — packaging là một phần sản phẩm.

## Đáng học

1. Tách *tìm catalog* khỏi *thư viện local*.
2. Playback là service headless, UI chỉ là shell mỏng.
3. Persist queue và vị trí — app nhạc bị resume liên tục.

## Cạm bẫy

- API audio nền tảng khác nhau nhiều (background mode, lock screen, Bluetooth).
- Ràng buộc pháp lý/ToS với catalog bên thứ ba không phải vấn đề Flutter, nhưng giết app nhanh hơn một frame jank.

Dùng Spotube như bản đồ **mặt phẳng plugin** mà app media thật cần.
""",
    ),
    oss(
        "oss-fluffychat-architecture", "💬",
        "FluffyChat: Matrix chat in Flutter with real E2EE",
        "FluffyChat: chat Matrix trên Flutter với E2EE thật",
        "How a Matrix client handles rooms, encryption, and multi-platform delivery from Flutter.",
        "Một client Matrix xử lý room, mã hóa và đa nền tảng từ Flutter ra sao.",
        "FluffyChat Matrix Flutter architecture: E2EE, room sync, multi-platform chat client patterns worth studying.",
        "FluffyChat kiến trúc Matrix Flutter: E2EE, sync room, pattern client chat đa nền tảng đáng học.",
        ["fluffychat flutter", "matrix client flutter", "flutter e2ee chat", "flutter matrix sdk", "open source chat app"],
        ["Flutter", "OpenSource", "Chat", "Matrix"],
        [("FluffyChat GitHub", "https://github.com/krille-chan/fluffychat"), ("Matrix spec", "https://spec.matrix.org/")],
        ["oss-localsend-architecture", "oss-ente-photos"],
        """Chat apps look simple until encryption and multi-device sync arrive. FluffyChat is a production Matrix client in Flutter — useful if you care about messaging architecture without inventing a protocol.

![FluffyChat architecture](/blog/images/oss-fluffychat-architecture.svg)

## Architecture beats

- **Matrix SDK** as the protocol brain (with Rust crypto such as Vodozemac underneath).
- Flutter as the shared shell for mobile and desktop form factors.
- Optional push (FCM etc.) layered on top of sync — not instead of it.

## Steal this

1. Keep protocol state out of widgets; expose streams/selectors.
2. Model rooms as first-class domain objects, not screens.
3. Treat device verification UX as a product surface, not a settings footnote.

## Pitfalls

E2EE bugs are trust bugs. Do not home-roll crypto. Offline queueing and out-of-order events will break naive `setState` UIs.

If you need chat, prefer Matrix (or another mature protocol) over a custom socket JSON soup.
""",
        """Chat trông đơn giản cho tới khi mã hóa và sync đa thiết bị xuất hiện. FluffyChat là client Matrix production bằng Flutter — hữu ích nếu bạn quan tâm kiến trúc messaging mà không tự bịa protocol.

![Kiến trúc FluffyChat](/blog/images/oss-fluffychat-architecture.svg)

## Nhịp kiến trúc

- **Matrix SDK** là bộ não protocol (crypto Rust như Vodozemac bên dưới).
- Flutter là shell chung cho mobile và desktop.
- Push tùy chọn (FCM…) xếp lên sync — không thay sync.

## Học theo

1. Giữ protocol state ngoài widget; expose stream/selector.
2. Room là domain object hạng nhất, không phải màn hình.
3. UX verify thiết bị là surface sản phẩm, không phải footnote settings.

## Cạm bẫy

Bug E2EE là bug niềm tin. Đừng tự viết crypto. Offline queue và event lệch thứ tự sẽ phá UI `setState` ngây thơ.

Nếu cần chat, ưu tiên Matrix (hoặc protocol trưởng thành) hơn soup JSON socket tự chế.
""",
    ),
    oss(
        "oss-localsend-architecture", "📡",
        "LocalSend: AirDrop-style transfer with zero cloud",
        "LocalSend: truyền file kiểu AirDrop không cần cloud",
        "A Flutter + Rust LAN protocol on port 53317 — lessons in local-first networking.",
        "Protocol LAN Flutter + Rust trên cổng 53317 — bài học mạng local-first.",
        "LocalSend architecture Flutter Rust: LAN HTTPS file transfer protocol 53317, no cloud server, desktop mobile.",
        "LocalSend kiến trúc Flutter Rust: truyền file LAN HTTPS 53317, không cloud, desktop mobile.",
        ["localsend architecture", "flutter file sharing lan", "localsend protocol", "flutter rust hybrid", "airdrop alternative flutter"],
        ["Flutter", "OpenSource", "Networking", "Rust"],
        [("LocalSend GitHub", "https://github.com/localsend/localsend"), ("LocalSend site", "https://localsend.org/")],
        ["oss-rustdesk-flutter", "oss-immich-architecture"],
        """LocalSend answers a sharp product question: can two devices exchange files without an account or a server? Yes — if you design for LAN discovery, HTTPS, and explicit consent.

![LocalSend architecture](/blog/images/oss-localsend-architecture.svg)

## Design highlights

- Peer protocol over local HTTPS (commonly associated with port **53317**).
- Flutter UI with Rust/native pieces for performance-critical paths.
- No cloud control plane — privacy is the feature.

## Steal this

1. Discovery + consent UX is half the product.
2. Make transfers resumable and visible; silent failures destroy trust.
3. Keep a CLI headless mode for power users and automation.

## Pitfalls

- Mobile OS background limits kill naive long transfers.
- Mixed networks (AP isolation, VPN, captive portals) will generate support load — document them.

Study LocalSend when you need **local-first** product patterns, not just a package to copy.
""",
        """LocalSend hỏi một câu sản phẩm sắc: hai thiết bị đổi file không cần tài khoản server được không? Có — nếu bạn thiết kế discovery LAN, HTTPS và consent rõ ràng.

![Kiến trúc LocalSend](/blog/images/oss-localsend-architecture.svg)

## Điểm thiết kế

- Peer protocol trên HTTPS cục bộ (thường gắn với cổng **53317**).
- UI Flutter với phần Rust/native cho đường nhạy hiệu năng.
- Không có control plane cloud — privacy là feature.

## Học theo

1. Discovery + consent UX là nửa sản phẩm.
2. Transfer phải resume được và hiện rõ; lỗi im lặng phá niềm tin.
3. Giữ CLI headless cho power user và automation.

## Cạm bẫy

- Giới hạn background mobile giết transfer dài ngây thơ.
- Mạng hỗn hợp (AP isolation, VPN, captive portal) sinh support load — hãy tài liệu hóa.

Học LocalSend khi cần pattern **local-first**, không chỉ một package để copy.
""",
    ),
    oss(
        "oss-rustdesk-flutter", "🖥️",
        "RustDesk: Rust core, Flutter shell",
        "RustDesk: lõi Rust, vỏ Flutter",
        "How a remote-desktop product splits performance-critical Rust from a Flutter UI.",
        "Một sản phẩm remote desktop tách Rust hiệu năng cao khỏi UI Flutter ra sao.",
        "RustDesk Flutter hybrid architecture: Rust core FFI, Flutter UI, remote desktop open source patterns.",
        "RustDesk kiến trúc hybrid Flutter: lõi Rust FFI, UI Flutter, pattern remote desktop open source.",
        ["rustdesk flutter", "rust flutter hybrid", "flutter ffi desktop", "open source remote desktop", "rustdesk architecture"],
        ["Flutter", "OpenSource", "Rust", "Desktop"],
        [("RustDesk GitHub", "https://github.com/rustdesk/rustdesk"), ("RustDesk docs", "https://rustdesk.com/docs/en/")],
        ["oss-localsend-architecture", "oss-hiddify-next"],
        """Not every pixel problem is a Dart problem. RustDesk keeps capture/encode/networking in **Rust** and uses Flutter as the interactive shell — a hybrid you should understand before you rewrite a native module in pure Dart.

![RustDesk hybrid](/blog/images/oss-rustdesk-flutter.svg)

## Split of responsibilities

| Concern | Home |
| --- | --- |
| Screen capture, codecs, relay | Rust core |
| Connection UX, settings, session UI | Flutter |
| OS integration | Platform channels / FFI |

## Steal this

1. Draw a hard boundary: hot UI loop vs hot data loop.
2. Prefer FFI for throughput; channels for infrequent events.
3. Keep session state outside widget trees.

## Pitfalls

- Hybrid builds double your CI matrix.
- ABI and packaging for desktop installers are non-trivial.

If your app is UI-heavy, Flutter alone may suffice. If it is pipeline-heavy, copy RustDesk’s **boundary**, not necessarily Rust itself.
""",
        """Không phải mọi vấn đề pixel là vấn đề Dart. RustDesk giữ capture/encode/networking trong **Rust** và dùng Flutter làm shell tương tác — dạng hybrid bạn nên hiểu trước khi rewrite module native bằng Dart thuần.

![Hybrid RustDesk](/blog/images/oss-rustdesk-flutter.svg)

## Phân chia trách nhiệm

| Mục | Nơi |
| --- | --- |
| Capture màn, codec, relay | Lõi Rust |
| UX kết nối, settings, session UI | Flutter |
| Tích hợp OS | Platform channel / FFI |

## Học theo

1. Vẽ biên cứng: vòng UI nóng vs vòng data nóng.
2. Ưu tiên FFI cho throughput; channel cho event thưa.
3. Giữ session state ngoài cây widget.

## Cạm bẫy

- Build hybrid nhân đôi ma trận CI.
- ABI và packaging installer desktop không đơn giản.

App nặng UI có thể chỉ cần Flutter. App nặng pipeline hãy copy **biên giới** của RustDesk, chưa chắc đã copy Rust.
""",
    ),
    oss(
        "oss-hiddify-next", "🔐",
        "Hiddify Next: Flutter UI over a tunnel core",
        "Hiddify Next: UI Flutter trên lõi tunnel",
        "A cross-platform proxy client shows how to pair Flutter with a Go/Sing-box style core.",
        "Client proxy đa nền tảng cho thấy cách ghép Flutter với lõi kiểu Go/Sing-box.",
        "Hiddify Next Flutter architecture: Sing-box core, VPN client UX, multi-protocol proxy patterns.",
        "Hiddify Next kiến trúc Flutter: lõi Sing-box, UX VPN client, pattern proxy đa giao thức.",
        ["hiddify flutter", "flutter vpn client", "sing-box flutter", "flutter network tunnel", "proxy app architecture"],
        ["Flutter", "OpenSource", "Networking"],
        [("Hiddify GitHub", "https://github.com/hiddify/hiddify-app")],
        ["oss-rustdesk-flutter", "oss-localsend-architecture"],
        """Proxy/VPN clients live at the edge of OS permissions. Hiddify Next pairs a Flutter UI with a high-performance tunnel core (Sing-box/Go lineage) so the UI stays expressive while the data path stays boring and fast.

![Hiddify architecture](/blog/images/oss-hiddify-next.svg)

## Lessons

1. **Status is a stream.** Latency, connected server, and errors should be one consistent model.
2. **Config as data.** Import/export profiles; do not hardcode endpoints in widgets.
3. **Platform VPN APIs** are the hard part — isolate them behind a service interface.

## Pitfalls

- Battery and thermal costs of always-on tunnels.
- Store policy differences for VPN apps.

Use this repo when you need a reference for **service-backed Flutter** rather than a pure CRUD app.
""",
        """Client proxy/VPN sống ở rìa quyền OS. Hiddify Next ghép UI Flutter với lõi tunnel hiệu năng cao (dòng Sing-box/Go) để UI vẫn biểu đạt trong khi data path nhàm chán và nhanh.

![Kiến trúc Hiddify](/blog/images/oss-hiddify-next.svg)

## Bài học

1. **Status là stream.** Latency, server đang nối, lỗi phải là một model nhất quán.
2. **Config là data.** Import/export profile; đừng hardcode endpoint trong widget.
3. **API VPN nền tảng** là phần khó — cô lập sau service interface.

## Cạm bẫy

- Pin và thermal khi tunnel always-on.
- Chính sách store khác nhau cho app VPN.

Dùng repo này khi cần tham chiếu **Flutter backed by service**, không chỉ CRUD thuần.
""",
    ),
    oss(
        "oss-ente-photos", "🔐",
        "Ente: end-to-end encrypted photos in Flutter",
        "Ente: ảnh mã hóa đầu-cuối trên Flutter",
        "Crypto UX is a design problem. Ente shows how encrypted galleries stay usable.",
        "UX crypto là vấn đề thiết kế. Ente cho thấy gallery mã hóa vẫn dùng được.",
        "Ente photos Flutter architecture: E2EE gallery, key management UX, encrypted backup patterns.",
        "Ente kiến trúc Flutter: gallery E2EE, UX quản lý khóa, pattern backup mã hóa.",
        ["ente photos flutter", "e2ee photo app", "flutter encrypted gallery", "ente architecture", "privacy photo backup"],
        ["Flutter", "OpenSource", "Crypto", "Photos"],
        [("Ente GitHub", "https://github.com/ente/ente"), ("Ente docs", "https://ente.io/")],
        ["oss-immich-architecture", "oss-saber-notes"],
        """If Immich is the self-hosted default, Ente is the privacy-first counterpart: clients (including Flutter mobile) encrypt before upload, and the server stores blobs it cannot read.

![Ente E2EE flow](/blog/images/oss-ente-photos.svg)

## What to study

1. **Key UX.** Recovery phrases and family sharing beat “trust us” dashboards.
2. **Encrypt-then-upload** pipelines with resumable transfers.
3. Product surfaces for Photos *and* Auth-style secrets.

## Pitfalls

- Users forget passphrases — design account recovery before launch.
- Thumbnail generation must not leak plaintext on shared devices.

Copy the **threat model conversation**, not just the cipher choices.
""",
        """Nếu Immich là mặc định self-host, Ente là bản đối trọng privacy-first: client (gồm Flutter mobile) mã hóa trước khi upload, server chỉ giữ blob không đọc được.

![Luồng E2EE Ente](/blog/images/oss-ente-photos.svg)

## Nên học

1. **UX khóa.** Recovery phrase và chia sẻ gia đình thắng dashboard “tin chúng tôi”.
2. Pipeline **encrypt-then-upload** có resume.
3. Surface sản phẩm cho Photos *và* secret kiểu Auth.

## Cạm bẫy

- User quên passphrase — thiết kế khôi phục tài khoản trước khi launch.
- Sinh thumbnail không được lộ plaintext trên thiết bị dùng chung.

Hãy copy **cuộc đối thoại threat model**, không chỉ lựa chọn cipher.
""",
    ),
    oss(
        "oss-saber-notes", "✍️",
        "Saber: handwriting notes and local-first files",
        "Saber: ghi chú viết tay và file local-first",
        "Canvas input, highlighter compositing, and optional sync — a Flutter notes stack.",
        "Input canvas, composite highlighter và sync tùy chọn — stack ghi chú Flutter.",
        "Saber notes Flutter architecture: handwriting canvas, local-first storage, optional Nextcloud sync.",
        "Saber kiến trúc Flutter: canvas viết tay, lưu local-first, sync Nextcloud tùy chọn.",
        ["saber notes flutter", "flutter handwriting app", "flutter canvas notes", "local first flutter", "stylus flutter"],
        ["Flutter", "OpenSource", "Notes", "Canvas"],
        [("Saber GitHub", "https://github.com/saber-notes/saber")],
        ["oss-lotti-journal", "oss-ente-photos"],
        """Handwriting apps are RenderObject-deep problems: stroke input, highlighter blend, export, and file format choices all matter.

![Saber architecture](/blog/images/oss-saber-notes.svg)

## Lessons

1. Local files first; sync second. Notes must open offline.
2. Model strokes as data (points/pressure), not screenshots.
3. Dual-layer highlighter compositing is a classic graphics lesson in a product.

## Pitfalls

- Stylus latency is perceptible at ~1 frame.
- File format lock-in will anger users more than missing cloud features.

Study Saber when building **canvas-centric** Flutter tools.
""",
        """App viết tay là vấn đề sâu tới RenderObject: input nét, blend highlighter, export và định dạng file đều quan trọng.

![Kiến trúc Saber](/blog/images/oss-saber-notes.svg)

## Bài học

1. File local trước; sync sau. Note phải mở được offline.
2. Model nét là data (điểm/áp lực), không phải screenshot.
3. Composite highlighter hai lớp là bài học graphics cổ điển trong sản phẩm.

## Cạm bẫy

- Latency stylus cảm nhận được ở ~1 frame.
- Lock-in định dạng file làm user giận hơn thiếu cloud.

Học Saber khi xây công cụ Flutter **lõi canvas**.
""",
    ),
    oss(
        "oss-flutter-deer", "🦌",
        "Flutter Deer: a production-shaped practice project",
        "Flutter Deer: dự án luyện tập dáng production",
        "A Chinese multi-flavor shop template that still teaches clean layering and test discipline.",
        "Template shop đa flavor từng dạy layering sạch và kỷ luật test.",
        "Flutter Deer architecture: Provider, flavors, clean layers, integration tests, production Flutter template lessons.",
        "Flutter Deer kiến trúc: Provider, flavor, layer sạch, integration test, bài học template production.",
        ["flutter deer", "flutter production template", "flutter clean architecture example", "flutter flavor example", "flutter provider architecture"],
        ["Flutter", "OpenSource", "Architecture", "Template"],
        [("flutter_deer GitHub", "https://github.com/simplezhli/flutter_deer")],
        ["oss-bloc-architecture", "oss-forui"],
        """Not every learning repo ages well. Deer remains useful because it shows a **complete app skeleton**: flavors, common components, integration tests, and a shop domain that is boring on purpose.

![Flutter Deer layers](/blog/images/oss-flutter-deer.svg)

## What to copy

- Feature folders over layer-only mega-folders at scale.
- Shared widgets library with design tokens/mockups in-repo.
- Integration tests as part of “done.”

## What to update

State management opinions have moved (Riverpod/bloc/etc.). Keep Deer’s **structure**, refresh the state layer for your team.

## Pitfalls

Do not paste UI without extracting design tokens. Templates rot when they hardcode API hosts.
""",
        """Không phải repo học tập nào cũng sống lâu. Deer vẫn hữu ích vì cho thấy **khung app hoàn chỉnh**: flavor, component dùng chung, integration test và domain shop nhàm chán một cách có chủ đích.

![Layer Flutter Deer](/blog/images/oss-flutter-deer.svg)

## Nên copy

- Folder theo feature thay vì mega-folder chỉ theo layer khi scale.
- Thư viện widget dùng chung kèm token/mockup trong repo.
- Integration test là một phần của “done”.

## Nên cập nhật

Ý kiến state management đã dịch chuyển (Riverpod/bloc…). Giữ **cấu trúc** Deer, làm mới tầng state theo team bạn.

## Cạm bẫy

Đừng paste UI mà không trích design token. Template thối khi hardcode API host.
""",
    ),
    oss(
        "oss-flame-engine", "🎮",
        "Flame: game loops inside Flutter",
        "Flame: vòng lặp game bên trong Flutter",
        "Component trees, game loops, and bridge packages — Flame’s place in a Flutter product.",
        "Cây component, vòng game và package cầu nối — vị trí Flame trong sản phẩm Flutter.",
        "Flame engine Flutter architecture: component tree, game loop, bridge packages for audio bloc tiled rive.",
        "Flame kiến trúc Flutter: cây component, vòng game, package cầu nối audio bloc tiled rive.",
        ["flame engine", "flutter game development", "flame component tree", "flutter 2d game", "flame architecture"],
        ["Flutter", "OpenSource", "Games"],
        [("Flame GitHub", "https://github.com/flame-engine/flame"), ("Flame docs", "https://docs.flame-engine.org/")],
        ["oss-bloc-architecture", "flutter-widget-previews-stable"],
        """Flame is how Flutter does games without abandoning the widget tree for a different engine. A `GameWidget` hosts a component tree updated by a game loop; overlays keep HUD/chat in normal Flutter.

![Flame architecture](/blog/images/oss-flame-engine.svg)

## Steal this

1. Hybrid UI: game canvas + Flutter overlays for menus/monetization.
2. Bridge packages (audio, physics, tiled, bloc) keep the core small.
3. Deterministic updates help tests and replays.

## Pitfalls

- Mixing `setState` UIs into the game loop fights the architecture.
- Mobile thermal budgets matter more than desktop FPS flexes.

Use Flame for 2D product mini-games and interactive canvases, not only toys.
""",
        """Flame là cách Flutter làm game mà không rời widget tree sang engine khác. `GameWidget` host cây component cập nhật bởi game loop; overlay giữ HUD/chat bằng Flutter thường.

![Kiến trúc Flame](/blog/images/oss-flame-engine.svg)

## Học theo

1. UI hybrid: canvas game + overlay Flutter cho menu/monetize.
2. Package cầu nối (audio, physics, tiled, bloc) giữ core nhỏ.
3. Update deterministic giúp test và replay.

## Cạm bẫy

- Trộn UI `setState` vào game loop sẽ đấu với kiến trúc.
- Ngân sách thermal mobile quan trọng hơn FPS desktop.

Dùng Flame cho mini-game 2D và canvas tương tác trong sản phẩm, không chỉ đồ chơi.
""",
    ),
    oss(
        "oss-jaspr-dart-web", "🌐",
        "Jaspr: server-driven Dart for the web",
        "Jaspr: Dart server-driven cho web",
        "The Flutter mental model on the server — including the framework that builds Flutter’s own docs site.",
        "Mental model Flutter trên server — gồm framework dựng docs site chính thức.",
        "Jaspr Dart web framework architecture: server components, hydration, Flutter-like UI on the server.",
        "Jaspr kiến trúc web Dart: component server, hydration, UI kiểu Flutter phía server.",
        ["jaspr dart", "dart web framework", "flutter mental model server", "jaspr architecture", "dart ssr"],
        ["Dart", "OpenSource", "Web"],
        [("Jaspr GitHub", "https://github.com/schultek/jaspr"), ("Jaspr site", "https://jaspr.site")],
        ["oss-serverpod", "oss-bloc-architecture"],
        """Jaspr brings a component mental model to Dart on the server. If you like Flutter’s structure but need HTML/SEO, this is the adjacent ecosystem — notably powering parts of Flutter’s own web presence.

![Jaspr architecture](/blog/images/oss-jaspr-dart-web.svg)

## Lessons

1. Shared Dart models between API, server UI, and Flutter clients reduce DTO drift.
2. SSR/hydration is a packaging problem as much as a UI problem.
3. Server components encourage boring, cacheable pages.

## Pitfalls

Do not assume Flutter widgets work unchanged. Layout constraints and lifecycle differ from mobile.

Consider Jaspr for content sites and dashboards where SEO matters and Dart is already your language.
""",
        """Jaspr mang mental model component lên Dart phía server. Nếu bạn thích cấu trúc Flutter nhưng cần HTML/SEO, đây là hệ sinh thái kề cận — đáng chú ý khi góp phần vào hiện diện web của chính Flutter.

![Kiến trúc Jaspr](/blog/images/oss-jaspr-dart-web.svg)

## Bài học

1. Model Dart dùng chung giữa API, UI server và client Flutter giảm lệch DTO.
2. SSR/hydration là vấn đề đóng gói nhiều như vấn đề UI.
3. Server component khuyến khích trang nhàm chán, cache được.

## Cạm bẫy

Đừng giả định widget Flutter chạy nguyên xi. Constraint layout và lifecycle khác mobile.

Cân nhắc Jaspr cho site nội dung và dashboard nơi SEO quan trọng và Dart đã là ngôn ngữ của bạn.
""",
    ),
    oss(
        "oss-shadcn-flutter", "🎛️",
        "shadcn-flutter: porting a design system, not a theme",
        "shadcn-flutter: port design system, không chỉ theme",
        "Tokens, primitives, and composites — how a design-system port stays maintainable.",
        "Token, primitive và composite — port design system sao cho maintain được.",
        "shadcn-flutter architecture: design tokens, primitives, composites, Flutter design system port patterns.",
        "shadcn-flutter kiến trúc: design token, primitive, composite, pattern port design system Flutter.",
        ["shadcn flutter", "flutter design system", "flutter design tokens", "port shadcn to flutter", "flutter ui primitives"],
        ["Flutter", "OpenSource", "DesignSystem"],
        [("shadcn-flutter GitHub", "https://github.com/nank1ro/shadcn-flutter")],
        ["oss-forui", "flutter-standalone-material-ui-cupertino-ui"],
        """Copying a web design system into Flutter fails when you only copy colors. shadcn-flutter is useful because it forces a layered story: tokens → primitives → composites → your app.

![shadcn-flutter layers](/blog/images/oss-shadcn-flutter.svg)

## Steal this

1. Own the source (copy-in model) so you can edit without fork pain.
2. Keep accessibility and focus rings as first-class primitives.
3. Document variants; do not hide them in one mega-widget.

## Pitfalls

Web CSS assumptions (cascading, :hover) do not map 1:1. Budget for desktop pointer polish separately from mobile touch.

Use this when Material defaults fight your brand.
""",
        """Copy design system web vào Flutter thất bại nếu chỉ copy màu. shadcn-flutter hữu ích vì ép câu chuyện phân lớp: token → primitive → composite → app của bạn.

![Layer shadcn-flutter](/blog/images/oss-shadcn-flutter.svg)

## Học theo

1. Sở hữu source (mô hình copy-in) để sửa không đau fork.
2. Giữ accessibility và focus ring là primitive hạng nhất.
3. Tài liệu hóa variant; đừng giấu trong một mega-widget.

## Cạm bẫy

Giả định CSS web (cascade, :hover) không map 1:1. Ngân sách polish pointer desktop tách khỏi touch mobile.

Dùng khi default Material đấu với brand của bạn.
""",
    ),
    oss(
        "oss-forui", "🧩",
        "Forui: an opinionated Flutter UI system",
        "Forui: hệ thống UI Flutter có chủ kiến",
        "Structure-first widgets and theming — a Material alternative worth evaluating.",
        "Widget ưu tiên cấu trúc và theming — lựa chọn thay Material đáng đánh giá.",
        "Forui Flutter design system architecture: opinionated widgets, theming, accessible components.",
        "Forui kiến trúc design system Flutter: widget có chủ kiến, theming, component accessible.",
        ["forui flutter", "flutter ui library", "material alternative flutter", "forui design system", "flutter accessible widgets"],
        ["Flutter", "OpenSource", "DesignSystem"],
        [("Forui GitHub", "https://github.com/forui-dev/forui"), ("Forui docs", "https://forui.dev/")],
        ["oss-shadcn-flutter", "flutter-standalone-material-ui-cupertino-ui"],
        """Forui takes a different bet than “Material everywhere”: strict structure, strong defaults, and a theme system designed as a system.

![Forui architecture](/blog/images/oss-forui.svg)

## When to evaluate it

- Product wants one coherent look across mobile/desktop.
- You are tired of overriding Material component internals.
- Accessibility is a launch requirement, not a backlog item.

## Pitfalls

Adopting a full UI system is a migration. Pilot one flow (settings + forms) before a full rewrite.

Compare Forui with `material_ui` standalone packages if your team still wants Google Material as the base.
""",
        """Forui đặt cược khác “Material ở khắp nơi”: cấu trúc chặt, default mạnh và theme được thiết kế như một hệ thống.

![Kiến trúc Forui](/blog/images/oss-forui.svg)

## Khi nào nên đánh giá

- Sản phẩm muốn một look nhất quán mobile/desktop.
- Bạn chán override internal component Material.
- Accessibility là yêu cầu launch, không phải backlog.

## Cạm bẫy

Adopt hệ thống UI đầy đủ là migration. Pilot một luồng (settings + form) trước khi rewrite cả app.

So Forui với package `material_ui` độc lập nếu team vẫn muốn Material của Google làm nền.
""",
    ),
    oss(
        "oss-lotti-journal", "📔",
        "Lotti: journaling with audio, habits, and a serious local DB",
        "Lotti: journal với audio, habit và local DB nghiêm túc",
        "Complex local data models in Flutter — beyond todo-app tutorials.",
        "Model data local phức tạp trong Flutter — vượt tutorial todo-app.",
        "Lotti journal Flutter architecture: local database, audio notes, habit tracking, complex offline app.",
        "Lotti kiến trúc journal Flutter: database local, note audio, theo dõi habit, app offline phức tạp.",
        ["lotti flutter", "flutter journaling app", "flutter local database complex", "flutter audio notes", "offline first journal"],
        ["Flutter", "OpenSource", "Productivity"],
        [("Lotti GitHub", "https://github.com/lotti/lotti")],
        ["oss-saber-notes", "oss-cashew-budget"],
        """Most Flutter tutorials stop at CRUD. Lotti is interesting because journaling forces multi-modal entries (text, audio, habits, measurements) and long-term local storage.

![Lotti architecture](/blog/images/oss-lotti-journal.svg)

## Lessons

1. Entry type hierarchies beat one giant nullable row.
2. Audio capture + playback is a platform surface, not a widget.
3. Insights need indexes — design queries before charts.

## Pitfalls

Migrations on personal data are sacred; write them carefully. Background recording permissions vary by OS.

Look at Lotti when your “simple notes app” is no longer simple.
""",
        """Tutorial Flutter hay dừng ở CRUD. Lotti thú vị vì journaling buộc entry đa modal (text, audio, habit, đo lường) và lưu trữ local dài hạn.

![Kiến trúc Lotti](/blog/images/oss-lotti-journal.svg)

## Bài học

1. Kiểu entry phân cấp thắng một row nullable khổng lồ.
2. Capture + playback audio là surface platform, không phải widget.
3. Insight cần index — thiết kế query trước chart.

## Cạm bẫy

Migration trên dữ liệu cá nhân là thiêng; viết cẩn thận. Quyền ghi âm nền khác nhau theo OS.

Nhìn Lotti khi “app note đơn giản” của bạn hết đơn giản.
""",
    ),
    oss(
        "oss-venera-reader", "📚",
        "Venera: custom reader layouts in Flutter",
        "Venera: layout reader tùy chỉnh trong Flutter",
        "Comic/manga readers demand custom layout engines, caching, and library UX.",
        "App đọc comic/manga đòi layout engine tùy chỉnh, cache và UX thư viện.",
        "Venera Flutter comic reader architecture: custom layout, image cache, library management patterns.",
        "Venera kiến trúc đọc comic Flutter: layout tùy chỉnh, image cache, pattern quản lý thư viện.",
        ["venera flutter", "flutter comic reader", "flutter custom layout", "flutter image cache reader", "manga app flutter"],
        ["Flutter", "OpenSource", "Reader"],
        [("Venera GitHub", "https://github.com/venera-app/venera")],
        ["oss-saber-notes", "oss-immich-architecture"],
        """Readers look like “just images” until page modes, RTL, zoom, and pre-cache collide. Venera is a useful study in custom layout + library management.

![Venera architecture](/blog/images/oss-venera-reader.svg)

## Steal this

1. Page model independent of page widget.
2. Aggressive adjacent-page pre-cache with memory caps.
3. Library as local DB + optional remote sources.

## Pitfalls

Pinch-zoom + page turn gestures fight each other; define gesture arenas early. Decode off the UI isolate.

Good reference when building any **long-scroll media** viewer.
""",
        """App đọc trông như “chỉ là ảnh” cho tới khi page mode, RTL, zoom và pre-cache va nhau. Venera là nghiên cứu hay về layout tùy chỉnh + quản lý thư viện.

![Kiến trúc Venera](/blog/images/oss-venera-reader.svg)

## Học theo

1. Page model độc lập với page widget.
2. Pre-cache trang kề mạnh kèm memory cap.
3. Thư viện là local DB + nguồn remote tùy chọn.

## Cạm bẫy

Pinch-zoom và lật trang đấu nhau; định nghĩa gesture arena sớm. Decode off UI isolate.

Tham chiếu tốt khi xây viewer **media scroll dài**.
""",
    ),
    oss(
        "oss-harmony-music", "🎧",
        "Harmony Music: offline-first player patterns",
        "Harmony Music: pattern player offline-first",
        "Library scan, queue, and audio service separation in a Flutter music app.",
        "Quét thư viện, hàng đợi và tách audio service trong app nhạc Flutter.",
        "Harmony Music Flutter architecture: offline library scan, queue management, audio service separation.",
        "Harmony Music kiến trúc Flutter: quét thư viện offline, quản lý queue, tách audio service.",
        ["harmony music flutter", "offline music player flutter", "flutter audio service", "flutter music queue", "flutter local library"],
        ["Flutter", "OpenSource", "Music"],
        [("MediaKit", "https://github.com/media-kit/media-kit")],
        ["oss-spotube-architecture", "oss-bloc-architecture"],
        """Offline music apps are storage, scanning, and service lifecycle problems. Harmony-style players keep a local library index and a playback service that survives UI navigation.

![Harmony Music architecture](/blog/images/oss-harmony-music.svg)

## Patterns

1. Scan once, listen to filesystem events later.
2. Queue lives in a controller/service, not in a screen widget.
3. Platform notification/media sessions are required UX.

## Pitfalls

Large libraries need incremental indexing. Do not block first frame on a full SD card scan.

Compare with Spotube if you also need streaming catalogs.
""",
        """App nhạc offline là vấn đề storage, scan và lifecycle service. Player kiểu Harmony giữ index thư viện local và playback service sống sót khi UI điều hướng.

![Kiến trúc Harmony Music](/blog/images/oss-harmony-music.svg)

## Pattern

1. Scan một lần, nghe filesystem event sau.
2. Queue nằm trong controller/service, không trong widget màn hình.
3. Notification/media session nền tảng là UX bắt buộc.

## Cạm bẫy

Thư viện lớn cần index tăng dần. Đừng chặn frame đầu bằng scan full SD.

So với Spotube nếu bạn còn cần catalog streaming.
""",
    ),
    oss(
        "oss-aegis-authenticator", "🔑",
        "What a secure Flutter authenticator must get right",
        "App authenticator Flutter an toàn cần đúng gì",
        "TOTP apps treat secrets carefully — lessons even if your codebase is not Aegis itself.",
        "App TOTP coi trọng secret — bài học dù codebase của bạn không phải Aegis.",
        "Flutter authenticator app security UX: encrypt secrets at rest, TOTP list UX, backup export patterns.",
        "UX bảo mật app authenticator Flutter: mã hóa secret, danh sách TOTP, pattern backup export.",
        ["flutter authenticator app", "totp flutter", "flutter secure storage otp", "flutter 2fa app", "security ux flutter"],
        ["Flutter", "OpenSource", "Security"],
        [("Aegis GitHub", "https://github.com/beemdevelopment/Aegis"), ("OTP auth spec RFC 6238", "https://datatracker.ietf.org/doc/html/rfc6238")],
        ["oss-ente-photos", "oss-localsend-architecture"],
        """Authenticator apps are small UIs with outsized security consequences. Whether you study Aegis or another TOTP client, the Flutter-relevant lessons are the same.

![Authenticator security flow](/blog/images/oss-aegis-authenticator.svg)

## Non-negotiables

1. Secrets encrypted at rest (platform keystore/keychain when available).
2. Screenshot/clipboard hygiene and auto-lock.
3. Backup export that is encrypted — and tested restore.

## UI notes

Large OTP lists need virtualization and urgency in copy-paste feedback. Accessibility labels should include the account name, not only the code.

## Pitfalls

Storing seeds in plain SharedPreferences is how “security” apps fail reviews and user trust.

Even for a learning project, practice secure defaults.
""",
        """App authenticator là UI nhỏ với hệ quả bảo mật lớn. Dù bạn study Aegis hay client TOTP khác, bài học liên quan Flutter vẫn vậy.

![Luồng bảo mật authenticator](/blog/images/oss-aegis-authenticator.svg)

## Không thể thương lượng

1. Secret mã hóa lúc lưu (platform keystore/keychain khi có).
2. Vệ sinh screenshot/clipboard và auto-lock.
3. Backup export được mã hóa — và restore đã test.

## Ghi chú UI

Danh sách OTP lớn cần virtualization và feedback copy-paste rõ. Nhãn accessibility nên gồm tên tài khoản, không chỉ mã.

## Cạm bẫy

Cất seed trong SharedPreferences thường là cách app “bảo mật” fail review và mất niềm tin.

Kể cả project học tập, hãy tập default an toàn.
""",
    ),
    oss(
        "oss-cashew-budget", "💸",
        "Cashew: finance UI that stays local",
        "Cashew: UI tài chính giữ dữ liệu local",
        "Charts, budgets, and local persistence patterns for a Flutter finance app.",
        "Chart, ngân sách và pattern lưu local cho app tài chính Flutter.",
        "Cashew budget Flutter architecture: charts, local database, budgeting UI patterns offline.",
        "Cashew kiến trúc ngân sách Flutter: chart, database local, pattern UI budget offline.",
        ["cashew flutter", "flutter budget app", "flutter finance charts", "flutter local database finance", "open source budget app"],
        ["Flutter", "OpenSource", "Finance"],
        [("Cashew GitHub", "https://github.com/guysmiley7/cashew")],
        ["oss-lotti-journal", "oss-bloc-architecture"],
        """Budget apps fail on trust and clarity. Cashew-style products keep data local, show honest charts, and make month boundaries explicit.

![Cashew architecture](/blog/images/oss-cashew-budget.svg)

## Lessons

1. Money is integers/minor units — never raw doubles for storage.
2. Recurring transactions need a rule engine, not copied rows.
3. Chart libraries need dark mode and accessibility tables.

## Pitfalls

Timezone and locale break “this month” logic. Export CSV early so users feel ownership.

Useful when building any **local-first personal data** app with charts.
""",
        """App budget fail ở niềm tin và sự rõ ràng. Sản phẩm kiểu Cashew giữ data local, chart trung thực và mốc tháng tường minh.

![Kiến trúc Cashew](/blog/images/oss-cashew-budget.svg)

## Bài học

1. Tiền là integer/đơn vị nhỏ — không lưu double thô.
2. Giao dịch định kỳ cần rule engine, không phải copy row.
3. Chart cần dark mode và bảng accessibility.

## Cạm bẫy

Timezone và locale phá logic “tháng này”. Export CSV sớm để user cảm thấy sở hữu dữ liệu.

Hữu ích khi xây app **dữ liệu cá nhân local-first** có chart.
""",
    ),
    oss(
        "oss-serverpod", "🛠️",
        "Serverpod: full-stack Dart behind Flutter",
        "Serverpod: full-stack Dart phía sau Flutter",
        "Generated clients, database, and auth — one language from SQL to widget.",
        "Client sinh tự động, database và auth — một ngôn ngữ từ SQL tới widget.",
        "Serverpod Flutter full-stack architecture: generated API clients, database, auth, Dart backend.",
        "Serverpod kiến trúc full-stack Flutter: API client sinh tự động, database, auth, backend Dart.",
        ["serverpod flutter", "dart backend flutter", "full stack dart", "serverpod architecture", "flutter dart api client"],
        ["Dart", "OpenSource", "Backend"],
        [("Serverpod GitHub", "https://github.com/serverpod/serverpod"), ("Serverpod docs", "https://docs.serverpod.dev/")],
        ["oss-jaspr-dart-web", "flutter-genkit-dart"],
        """Serverpod is the “no, you may not learn three languages” backend: Dart server, generated Flutter clients, database tooling included.

![Serverpod architecture](/blog/images/oss-serverpod.svg)

## Why teams pick it

1. Shared types end JSON drift.
2. Auth and database scaffolding reduce blank-page anxiety.
3. One toolchain for hiring and CI.

## Pitfalls

Full-stack lock-in is real — keep domain logic portable if you might split later. Do not put secrets in client-generated code paths.

Consider Serverpod when the team is Flutter-first and wants a coherent backend without Node/Go context switching.
""",
        """Serverpod là backend “không, bạn không cần học ba ngôn ngữ”: server Dart, client Flutter sinh tự động, tooling database kèm theo.

![Kiến trúc Serverpod](/blog/images/oss-serverpod.svg)

## Vì sao team chọn

1. Type dùng chung hết lệch JSON.
2. Auth và scaffolding database giảm lo trang trắng.
3. Một toolchain cho hiring và CI.

## Cạm bẫy

Lock-in full-stack là thật — giữ domain logic di động nếu có thể tách sau. Không để secret trong path code client sinh.

Cân nhắc Serverpod khi team Flutter-first và muốn backend mạch lạc không đổi ngữ cảnh Node/Go.
""",
    ),
    oss(
        "oss-bloc-architecture", "🧱",
        "Bloc: the boring architecture that scales",
        "Bloc: kiến trúc nhàm chán nhưng scale được",
        "Events in, states out — why bloc remains a default for large Flutter teams.",
        "Event vào, state ra — vì sao bloc vẫn là mặc định của team Flutter lớn.",
        "Flutter bloc architecture: events states predictability, testing large apps, scalable state management.",
        "Kiến trúc Flutter bloc: event state dự đoán được, test app lớn, state management scale.",
        ["flutter bloc architecture", "bloc state management", "flutter scalable architecture", "flutter event state", "bloc testing"],
        ["Flutter", "OpenSource", "Architecture", "StateManagement"],
        [("Bloc GitHub", "https://github.com/felangel/bloc"), ("Bloc docs", "https://bloclibrary.dev/")],
        ["oss-flutter-deer", "oss-serverpod"],
        """Trends rotate; production teams still ship with Bloc because it is **predictable**. UI sends events; blocs emit states; widgets rebuild from state.

![Bloc architecture](/blog/images/oss-bloc-architecture.svg)

## Why it scales

1. Debuggable event logs.
2. Test blocs without pumping the entire app.
3. Clear ownership boundaries between features.

## Modern usage tips

- Prefer `flutter_bloc` builders/selectors over rebuilding whole pages.
- Keep blocs free of `BuildContext` navigation side effects.
- Pair with a repository layer — bloc is not your data layer.

## Pitfalls

God-blocs that hold the whole app. Split by feature and lifecycle. Also do not map 1:1 every field change into a bloc event.

If your team needs a default architecture in 2026, Bloc is still a defensible answer.
""",
        """Xu hướng xoay vòng; team production vẫn ship với Bloc vì nó **dự đoán được**. UI gửi event; bloc emit state; widget rebuild từ state.

![Kiến trúc Bloc](/blog/images/oss-bloc-architecture.svg)

## Vì sao scale được

1. Event log debug được.
2. Test bloc không cần pump cả app.
3. Biên sở hữu feature rõ ràng.

## Mẹo dùng hiện đại

- Ưu tiên builder/selector của `flutter_bloc` hơn rebuild cả trang.
- Giữ bloc không dính side-effect điều hướng `BuildContext`.
- Ghép tầng repository — bloc không phải data layer.

## Cạm bẫy

God-bloc ôm cả app. Chia theo feature và lifecycle. Cũng đừng map 1:1 mọi thay đổi field thành event.

Nếu team cần architecture mặc định năm 2026, Bloc vẫn là câu trả lời bảo vệ được.
""",
    ),
]
