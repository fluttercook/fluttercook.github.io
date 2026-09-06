---
title: "Flutter on desktop: the window is part of your app now"
description: "On mobile the OS owns the window. On desktop you own it — size, position, minimum bounds, multiple windows, the close button that must not close. Here is what changes when your Flutter app grows a title bar."
seoDescription: "Flutter desktop window management: window_manager, minimum sizes, preventing close, tray icons, keyboard shortcuts, menus, multi-window considerations, and desktop-specific layout and input differences."
keywords:
  - flutter desktop window manager
  - flutter window size position
  - flutter prevent window close
  - flutter desktop keyboard shortcuts
  - flutter system tray
  - flutter desktop menu bar
category: "Guide"
topic: "Flutter"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-18"
emoji: "🖥️"
tags: ["Flutter", "Desktop", "macOS", "Windows", "UI"]
sources:
  - name: "Desktop support for Flutter — Flutter documentation"
    url: "https://docs.flutter.dev/platform-integration/desktop"
  - name: "window_manager — pub.dev"
    url: "https://pub.dev/packages/window_manager"
  - name: "Shortcuts and Actions — Flutter documentation"
    url: "https://docs.flutter.dev/ui/interactivity/actions-and-shortcuts"
  - name: "PlatformMenuBar — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/PlatformMenuBar-class.html"
  - name: "MenuAnchor — Flutter API"
    url: "https://api.flutter.dev/flutter/material/MenuAnchor-class.html"
  - name: "ScrollBehavior — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/ScrollBehavior-class.html"
related:
  - slug: "flutter-custom-scroll-physics"
    title: "Custom scroll physics: making a list stop where you want it to"
  - slug: "flutter-accessibility-semantics"
    title: "Flutter accessibility: what the semantics tree actually reports"
draft: false
---

A Flutter app that runs on desktop and a Flutter app that *belongs* on desktop are different pieces of software. The first is a phone layout stretched to 1920 pixels wide. The second knows its window can be resized to something absurd, that the user expects Cmd+W to close a tab, that a right-click should produce a context menu, and that scrolling with a trackpad is not the same gesture as dragging with a finger.

None of this is hard. It is just a list of things mobile never made you think about.

## The window has a lifecycle you control

```dart
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await windowManager.ensureInitialized();

  const options = WindowOptions(
    size: Size(1200, 800),
    minimumSize: Size(720, 480),
    center: true,
    titleBarStyle: TitleBarStyle.normal,
  );

  await windowManager.waitUntilReadyToShow(options, () async {
    await windowManager.show();
    await windowManager.focus();
  });

  runApp(const MyApp());
}
```

`waitUntilReadyToShow` exists to avoid the flash of an unstyled, wrongly-sized window before your first frame. Showing the window only once it is configured is the difference between an app that feels native and one that visibly assembles itself on launch.

**`minimumSize` is the single highest-value line here.** Without it, a user can drag the window to 200×100 and your carefully built layout throws overflow errors. Pick a size below which the app genuinely does not work, and enforce it at the window rather than with defensive layout code everywhere.

Restoring the previous size and position is expected behaviour on desktop:

```dart
Future<void> restoreWindowState() async {
  final prefs = await SharedPreferences.getInstance();
  final w = prefs.getDouble('win_w');
  final h = prefs.getDouble('win_h');
  if (w != null && h != null) {
    await windowManager.setSize(Size(w, h));
  }
  // Deliberately not restoring position: a saved position can land the
  // window off-screen when a monitor is disconnected.
}
```

The comment there is the real advice. Restoring position without validating it against the current display arrangement is how an app becomes invisible on a laptop that was previously docked to two monitors.

## Intercepting close

Desktop users expect to be warned about unsaved work, and expect some apps to keep running when the window closes.

```dart
class _AppState extends State<App> with WindowListener {
  @override
  void initState() {
    super.initState();
    windowManager.addListener(this);
    windowManager.setPreventClose(true);
  }

  @override
  void dispose() {
    windowManager.removeListener(this);
    super.dispose();
  }

  @override
  Future<void> onWindowClose() async {
    if (!context.mounted) return;

    final hasUnsaved = context.read<DocumentModel>().isDirty;
    if (!hasUnsaved) {
      await windowManager.destroy();
      return;
    }

    final shouldClose = await showDialog<bool>(
      context: context,
      builder: (_) => const UnsavedChangesDialog(),
    );
    if (shouldClose ?? false) await windowManager.destroy();
  }
}
```

`setPreventClose(true)` plus `destroy()` is the pattern: you take responsibility for closing, so every path that should close must call `destroy()`. Forgetting one branch produces an app that cannot be quit, which users resolve with force-quit and a bad review.

For a menu-bar or tray app, `onWindowClose` hides instead of destroying — and then you must provide an obvious way to quit from the tray menu, or you have built the same trap in a different shape.

## Keyboard is a first-class input

On mobile, shortcuts are a nicety. On desktop, their absence is a defect.

```dart
Shortcuts(
  shortcuts: <ShortcutActivator, Intent>{
    SingleActivator(LogicalKeyboardKey.keyS, meta: true): const SaveIntent(),
    SingleActivator(LogicalKeyboardKey.keyS, control: true): const SaveIntent(),
    SingleActivator(LogicalKeyboardKey.keyF, meta: true): const FindIntent(),
  },
  child: Actions(
    actions: <Type, Action<Intent>>{
      SaveIntent: CallbackAction<SaveIntent>(onInvoke: (_) => _save()),
      FindIntent: CallbackAction<FindIntent>(onInvoke: (_) => _openFind()),
    },
    child: Focus(autofocus: true, child: child),
  ),
)
```

Registering both `meta` and `control` variants covers macOS and Windows/Linux without a platform check. It is slightly redundant and considerably simpler than branching.

Two things that are easy to forget: **something must have focus** for shortcuts to fire, hence the `Focus(autofocus: true)`; and tab order must be sensible, because keyboard users navigate your form with Tab, not by tapping. Test the whole app once using only the keyboard — it takes ten minutes and finds real problems.

For a native application menu on macOS, `PlatformMenuBar` renders into the actual system menu bar rather than drawing an in-window imitation, which is what users expect.

## Input differences that surprise people

| Behaviour | Mobile | Desktop |
| --- | --- | --- |
| Scroll | Finger drag on content | Wheel or trackpad; dragging content is not standard |
| Long-press menu | Standard | Right-click is expected instead |
| Hover | Does not exist | Users expect visual feedback on hover |
| Text selection | Handles and a toolbar | Click-drag, double-click for word, Cmd+A |
| Scrollbars | Transient overlay | Expected to be visible and draggable |

The first row causes a specific bug: a `ListView` on desktop cannot be scrolled by dragging with the mouse unless you extend `ScrollBehavior` with `dragDevices` including `PointerDeviceKind.mouse`. It is correct default behaviour — desktop apps scroll with the wheel — but if you have a drag-to-scroll carousel it will appear broken.

Hover states need real attention. `MouseRegion` and the `WidgetStateProperty` hover states exist for this; an app where nothing responds to the cursor feels dead in a way that is hard to name but easy to notice.

## Multiple windows

Flutter's desktop story has historically been one Flutter view per window, with multi-window support evolving. Before designing around several windows, check what your target Flutter version actually supports rather than assuming, because the answer has been changing and the packages that fill the gap vary in maturity.

A pragmatic alternative that works today: an in-app tabbed or split layout that gives users the same capability without the platform complexity. Not as good as real windows for a document editor — perfectly adequate for most apps.

## Distribution reality check

Building the binary is the easy part. Shipping it means code signing on macOS plus notarisation, an installer and ideally a signing certificate on Windows, and choosing among several formats on Linux. Sandboxing on macOS also restricts file access in ways your development build does not, so test file pickers and any path you write to under the sandboxed build, not just under `flutter run`.

## FAQ

**Should I build one app for mobile and desktop or two?**

One codebase, with layout that adapts at breakpoints and separate widgets where the interaction genuinely differs. Sharing models and data layers is the win; sharing a navigation structure across a phone and a 27-inch display usually is not.

**Why does my app open at the wrong size on second launch?**

Restored state from a previous session, or the OS remembering. Set the size explicitly in `WindowOptions` and only restore what you validated.

**How do I show a tray icon?**

The `tray_manager` package pairs with `window_manager`. Always include a Quit item — a tray app with no visible way to exit is a support burden.

**Does `MediaQuery` work on desktop?**

Yes, and it reports the window size, which changes as the user resizes. Layout that reads it live is exactly what you want; layout that reads it once and caches is not.

**Is `Platform.isMacOS` the right way to branch?**

For platform conventions, yes. For capability, prefer feature checks. And remember `Platform` throws on web — guard with `kIsWeb` first if the code is shared.

---

*The `window_manager` API, `Shortcuts`/`Actions`, `PlatformMenuBar`, and desktop platform support described here are documented in the references linked above. The advice not to restore window position, the both-modifiers shortcut registration, the input-differences table and the multi-window pragmatism are my own judgement from shipping desktop builds. Flutter's desktop support and its multi-window capabilities are actively evolving — verify against your Flutter version before designing around them.*
