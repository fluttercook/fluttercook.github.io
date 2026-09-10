#!/usr/bin/env python3
"""Generate consistent editorial SVG heroes for the 2026 content batch."""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "public" / "blog" / "images"

# slug -> (title, subtitle, boxes left-to-right)
TOPICS = {
    # Features
    "flutter-standalone-material-ui-cupertino-ui": (
        "Standalone design packages",
        "material_ui & cupertino_ui 1.0 leave the core SDK",
        ["Core SDK", "material_ui 1.0", "cupertino_ui 1.0", "Weekly releases"],
    ),
    "flutter-impeller-default-desktop": (
        "Impeller on desktop",
        "Default renderer for macOS, Windows, Linux in 3.47",
        ["Build time", "Precompiled shaders", "Metal / Vulkan", "No runtime jank"],
    ),
    "flutter-swift-package-manager-default": (
        "Swift Package Manager",
        "Replaces CocoaPods as the iOS/macOS default",
        ["pubspec", "SwiftPM resolve", "Xcode build", "No Ruby"],
    ),
    "flutter-hybrid-composition-plus-plus": (
        "Hybrid Composition++",
        "Native Android views composited by the OS via Vulkan",
        ["Flutter UI", "SurfaceControl", "Native view", "Synced frames"],
    ),
    "flutter-agentic-hot-reload": (
        "Agentic Hot Reload",
        "Coding agents auto-connect and hot-reload your app",
        ["Prompt agent", "Edit Dart", "MCP reload", "See UI"],
    ),
    "flutter-agent-skills-mcp": (
        "Agent Skills + MCP",
        "Task skills and lean MCP tools for coding agents",
        ["Skill pack", "MCP server", "Fewer tokens", "Best practices"],
    ),
    "flutter-genui-a2ui": (
        "GenUI + A2UI",
        "Agents compose real UI instead of markdown walls",
        ["User intent", "A2UI protocol", "Widget tree", "Live UI"],
    ),
    "flutter-firebase-ai-logic": (
        "Firebase AI Logic",
        "Call Gemini from Flutter without a custom backend",
        ["Flutter app", "firebase_ai", "Server prompts", "Gemini"],
    ),
    "flutter-genkit-dart": (
        "Genkit Dart",
        "Full-stack AI apps in Dart, client or server",
        ["Genkit()", "Model plugins", "Tools + flows", "Production"],
    ),
    "flutter-widget-previews-stable": (
        "Widget Previews",
        "Stable isolated UI iteration without full app runs",
        ["@Preview", "Local cache", "Theme matrix", "Fast loop"],
    ),
    "flutter-multi-window-desktop": (
        "Desktop multi-window",
        "Popups, dialogs, windowHandle with Canonical",
        ["Main window", "Popup", "Dialog", "Native HWND"],
    ),
    "flutter-desktop-flavors": (
        "Desktop flavors",
        "Windows and Linux product flavors in 3.47",
        ["flavor_a", "flavor_b", "Assets", "Build flag"],
    ),
    "flutter-wasm-deferred-loading": (
        "Wasm + deferred loading",
        "Split Flutter web modules for faster first paint",
        ["Main wasm", "Deferred module", "Lazy fetch", "Small boot"],
    ),
    "flutter-platform-specific-assets": (
        "Platform-specific assets",
        "Bundle only what each platform needs",
        ["pubspec", "platforms:", "Mobile APK", "Desktop bin"],
    ),
    "flutter-uiscene-ios-lifecycle": (
        "UIScene lifecycle",
        "Required for iOS 27 / Xcode 27 launches",
        ["AppDelegate", "UIScene", "SceneDelegate", "Launch OK"],
    ),
    "flutter-fragment-shader-api": (
        "Fragment shader API",
        "Uniforms by name, sync textures, high-bit LUTs",
        [".frag file", "getUniformFloat", "Sync image", "128-bit"],
    ),
    "flutter-cupertino-menu-anchor": (
        "CupertinoMenuAnchor",
        "Native-feeling iOS menus on RawMenuAnchor",
        ["Trigger", "RawMenuAnchor", "CupertinoMenu", "Actions"],
    ),
    "flutter-content-sized-views": (
        "Content-sized views",
        "Add-to-App Flutter views that size to content",
        ["Native parent", "content_wrap", "Intrinsic size", "Scroll OK"],
    ),
    "flutter-public-release-windows": (
        "Public release windows",
        "Know when your PR lands in stable",
        ["3.41 Feb", "3.44 May", "3.47 Aug", "3.50 Nov"],
    ),
    "flutter-gemma-litert-ondevice": (
        "On-device Gemma",
        "flutter_gemma + LiteRT-LM across 6 platforms",
        ["Gemma 4", "LiteRT-LM", "NPU/GPU", "Flutter UI"],
    ),
    # OSS
    "oss-immich-architecture": (
        "Immich architecture",
        "Self-hosted photo backup at production scale",
        ["Mobile UI", "Background sync", "ML pipeline", "Server API"],
    ),
    "oss-spotube-architecture": (
        "Spotube architecture",
        "Privacy-friendly music client patterns",
        ["Flutter UI", "Audio engine", "Platform channels", "Local cache"],
    ),
    "oss-fluffychat-architecture": (
        "FluffyChat architecture",
        "Matrix chat with E2EE across platforms",
        ["Matrix SDK", "Rooms UI", "E2EE store", "Multi-platform"],
    ),
    "oss-localsend-architecture": (
        "LocalSend architecture",
        "AirDrop-style transfer with zero backend",
        ["Device A", "LAN HTTPS", "Device B", "No cloud"],
    ),
    "oss-rustdesk-flutter": (
        "RustDesk hybrid",
        "Rust core performance with a Flutter shell",
        ["Rust core", "FFI / bridge", "Flutter UI", "Desktop+Mobile"],
    ),
    "oss-hiddify-next": (
        "Hiddify Next",
        "Cross-platform VPN client engineering",
        ["Config UI", "Tunnel core", "System VPN", "Status feed"],
    ),
    "oss-ente-photos": (
        "Ente Photos",
        "End-to-end encrypted gallery UX",
        ["Encrypt local", "Upload blob", "Key never leaves", "Decrypt UI"],
    ),
    "oss-saber-notes": (
        "Saber notes",
        "Handwriting canvas and local-first files",
        ["Stylus input", "Canvas scene", "Local store", "Sync optional"],
    ),
    "oss-flutter-deer": (
        "Flutter Deer",
        "Production template with flavors + clean layers",
        ["UI layer", "Bloc/Rx", "Repo layer", "Flavors"],
    ),
    "oss-flame-engine": (
        "Flame engine",
        "Game loop and component tree on Flutter",
        ["GameWidget", "Component tree", "Game loop", "Flutter overlay"],
    ),
    "oss-jaspr-dart-web": (
        "Jaspr on the web",
        "Server-driven Dart UI with Flutter mental model",
        ["Dart server", "HTML components", "Hydration", "Deploy"],
    ),
    "oss-shadcn-flutter": (
        "shadcn-flutter",
        "Porting a design system, not just a theme",
        ["Tokens", "Primitives", "Composites", "Your app"],
    ),
    "oss-forui": (
        "Forui design system",
        "Opinionated widgets with strict structure",
        ["Theme", "Base widgets", "Patterns", "Accessible"],
    ),
    "oss-lotti-journal": (
        "Lotti journal",
        "Complex local DB + audio + habits",
        ["Capture UI", "Local DB", "Audio notes", "Insights"],
    ),
    "oss-venera-reader": (
        "Venera reader",
        "Custom layout engines for comics",
        ["Page model", "Reader layout", "Image cache", "Library"],
    ),
    "oss-harmony-music": (
        "Harmony Music",
        "Offline-first music player patterns",
        ["Library scan", "Queue", "Audio service", "Offline UI"],
    ),
    "oss-aegis-authenticator": (
        "Secure authenticator UX",
        "TOTP apps that treat secrets carefully",
        ["Add secret", "Encrypt at rest", "OTP list", "Export"],
    ),
    "oss-cashew-budget": (
        "Cashew budget",
        "Finance charts and local persistence",
        ["Transactions", "Charts", "Budgets", "Local DB"],
    ),
    "oss-serverpod": (
        "Serverpod",
        "Full-stack Dart with generated clients",
        ["Server methods", "Codegen", "Flutter client", "DB"],
    ),
    "oss-bloc-architecture": (
        "Bloc architecture",
        "Predictable state with events and states",
        ["UI event", "Bloc", "State emit", "Rebuild"],
    ),
}

W, H = 1600, 900


def svg_for(slug: str, title: str, subtitle: str, boxes: list[str]) -> str:
    n = len(boxes)
    gap = 36
    margin = 80
    usable = W - 2 * margin - gap * (n - 1)
    bw = usable / n
    bh = 140
    y = 420
    # connectors
    arrows = []
    for i in range(n - 1):
        x1 = margin + (i + 1) * bw + i * gap + 4
        x2 = x1 + gap - 8
        cy = y + bh / 2
        arrows.append(
            f'<line x1="{x1}" y1="{cy}" x2="{x2}" y2="{cy}" stroke="#22D3EE" stroke-width="2" marker-end="url(#arrow)"/>'
        )
    box_svg = []
    for i, label in enumerate(boxes):
        x = margin + i * (bw + gap)
        fill = "#152238" if i % 2 == 0 else "#1A2A44"
        stroke = "#22D3EE" if i == 0 else "#3B5B85"
        box_svg.append(
            f'''<g>
  <rect x="{x}" y="{y}" width="{bw}" height="{bh}" rx="12" fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>
  <text x="{x + bw/2}" y="{y + bh/2}" text-anchor="middle" dominant-baseline="central"
        font-family="-apple-system, PingFang SC, Microsoft YaHei, sans-serif"
        font-size="28" fill="#E5EEF8">{label}</text>
</g>'''
        )
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto">
      <path d="M0,0 L8,3 L0,6 Z" fill="#22D3EE"/>
    </marker>
  </defs>
  <rect width="{W}" height="{H}" fill="#0B1220"/>
  <rect x="0" y="0" width="{W}" height="8" fill="#22D3EE"/>
  <text x="80" y="120" font-family="-apple-system, PingFang SC, Microsoft YaHei, sans-serif"
        font-size="22" fill="#22D3EE" letter-spacing="4">FLUTTERCOOK · 2026</text>
  <text x="80" y="220" font-family="-apple-system, PingFang SC, Microsoft YaHei, sans-serif"
        font-size="64" font-weight="600" fill="#E5EEF8">{title}</text>
  <text x="80" y="290" font-family="-apple-system, PingFang SC, Microsoft YaHei, sans-serif"
        font-size="30" fill="#9BB3CC">{subtitle}</text>
  <line x1="80" y1="340" x2="{W-80}" y2="340" stroke="#243B55" stroke-width="1"/>
  {''.join(arrows)}
  {''.join(box_svg)}
  <text x="80" y="{H-60}" font-family="-apple-system, PingFang SC, Microsoft YaHei, sans-serif"
        font-size="20" fill="#5C7A99">fluttercook.github.io</text>
</svg>
'''


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    missing = []
    for slug, (title, subtitle, boxes) in TOPICS.items():
        path = OUT / f"{slug}.svg"
        path.write_text(svg_for(slug, title, subtitle, boxes), encoding="utf-8")
        print(f"wrote {path.name}")
    print(f"done: {len(TOPICS)} images → {OUT}")
    if missing:
        print("missing:", missing)


if __name__ == "__main__":
    main()
