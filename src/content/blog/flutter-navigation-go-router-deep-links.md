---
title: "go_router and deep links: the parts the quickstart leaves out"
description: "Declaring routes is the easy half. Redirects that do not loop, nested shells with their own navigation stacks, typed routes, and the platform files that make a real https:// link open your app — that is the other half."
seoDescription: "A practical go_router guide: redirect guards, StatefulShellRoute for bottom navigation, typed routes with go_router_builder, and configuring App Links and Universal Links."
keywords:
  - go_router deep linking
  - statefulshellroute example
  - go_router redirect auth guard
  - flutter app links universal links setup
  - go_router builder typed routes
  - flutter deep link not opening app
category: "Guide"
topic: "Flutter"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-05"
emoji: "🔗"
tags: ["Flutter", "Navigation", "go_router", "Deep Links", "Routing"]
sources:
  - name: "go_router — pub.dev"
    url: "https://pub.dev/packages/go_router"
  - name: "Flutter — Deep linking"
    url: "https://docs.flutter.dev/ui/navigation/deep-linking"
  - name: "Flutter cookbook — Set up app links for Android"
    url: "https://docs.flutter.dev/cookbook/navigation/set-up-app-links"
  - name: "Flutter cookbook — Set up universal links for iOS"
    url: "https://docs.flutter.dev/cookbook/navigation/set-up-universal-links"
  - name: "Router — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/Router-class.html"
  - name: "go_router_builder — pub.dev"
    url: "https://pub.dev/packages/go_router_builder"
related:
  - slug: "flutter-build-context-explained"
    title: "BuildContext is an element: reading the error messages that mention it"
  - slug: "flutter-flavors-build-config"
    title: "Flutter flavors: one codebase, three apps, zero copy-pasted config"
draft: false
---

Every routing tutorial ends at the same place: a `GoRouter` with three routes, a `context.go('/details/42')`, and a screenshot of it working. That part takes ten minutes. The parts that take the rest of the week are the ones nobody demos — an auth redirect that does not fight the login screen, a bottom navigation bar where each tab keeps its own history, and the platform configuration that decides whether `https://yourapp.com/order/7` opens your app or Safari.

## The routing table, and where state actually lives

Start with the shape that scales, which is a top-level router object that is *not* rebuilt:

```dart
final _rootKey = GlobalKey<NavigatorState>();
final _shellKey = GlobalKey<NavigatorState>();

final router = GoRouter(
  navigatorKey: _rootKey,
  initialLocation: '/feed',
  debugLogDiagnostics: true,
  routes: [ /* ... */ ],
  errorBuilder: (context, state) => NotFoundScreen(uri: state.uri),
);

class App extends StatelessWidget {
  @override
  Widget build(BuildContext context) =>
      MaterialApp.router(routerConfig: router);
}
```

Two things in there are load-bearing. `debugLogDiagnostics: true` prints the full match for every navigation, which turns "why did it go there" from a guess into a line of output — leave it on in debug builds permanently. And the router lives outside `build`, because recreating a `GoRouter` throws away the navigation stack; putting one in a `build` method is the source of the "my back button stopped working" bug.

Route parameters come in three flavours and are read from `GoRouterState`:

```dart
GoRoute(
  path: '/order/:id',
  builder: (context, state) {
    final id = state.pathParameters['id']!;             // /order/42
    final tab = state.uri.queryParameters['tab'];       // ?tab=items
    final draft = state.extra as Draft?;                // in-memory only
    return OrderScreen(id: id, tab: tab, draft: draft);
  },
),
```

`extra` deserves a warning. It is a plain Dart object passed in memory — it does not survive a deep link, a browser reload, or process restoration on Android. Anything the screen genuinely needs to render must be in the path or the query string; `extra` is for optimistic hand-offs you can rebuild without.

## Redirects: the part that loops

`redirect` runs before a route is built and can return a new location or `null` for "carry on." It runs on the router as a whole and on individual routes, and both fire on every navigation. The classic auth guard:

```dart
final router = GoRouter(
  refreshListenable: authState,       // a ChangeNotifier
  redirect: (context, state) {
    final loggedIn = authState.isLoggedIn;
    final loggingIn = state.matchedLocation == '/login';

    if (!loggedIn && !loggingIn) {
      return '/login?from=${Uri.encodeComponent(state.uri.toString())}';
    }
    if (loggedIn && loggingIn) {
      final from = state.uri.queryParameters['from'];
      return from ?? '/feed';
    }
    return null;
  },
  routes: [ /* ... */ ],
);
```

Three details make the difference between this working and this hanging:

- **`refreshListenable`.** Without it, the redirect is only re-evaluated when someone navigates. Hand it a `ChangeNotifier` that fires on login and logout and the router re-runs redirects the moment auth state changes — which is what makes logout kick you out of a protected screen immediately.
- **The `loggingIn` escape hatch.** Redirecting to `/login` while already on `/login` is an infinite loop, and go_router will throw a redirect-limit error rather than hang. Always exempt the destination.
- **`matchedLocation` versus `uri`.** `matchedLocation` is the route pattern that matched, without query parameters. Comparing against `state.uri.toString()` breaks the moment you add `?from=...`.

For an async check — a token refresh, a feature flag fetch — do not `await` inside `redirect`. Resolve it into a synchronous `Listenable` before the router asks. A splash route that stays until initialisation completes is the usual shape, with the redirect sending everything to `/splash` while `!authState.isInitialised`.

## Nested navigation that keeps per-tab history

The requirement is familiar: a bottom bar with five tabs, each tab keeping its own stack, the bar staying put while you push detail screens. `StatefulShellRoute.indexedStack` is built for exactly this.

```dart
StatefulShellRoute.indexedStack(
  builder: (context, state, navigationShell) =>
      ScaffoldWithNavBar(navigationShell: navigationShell),
  branches: [
    StatefulShellBranch(routes: [
      GoRoute(
        path: '/feed',
        builder: (c, s) => const FeedScreen(),
        routes: [
          GoRoute(path: 'post/:id', builder: (c, s) =>
              PostScreen(id: s.pathParameters['id']!)),
        ],
      ),
    ]),
    StatefulShellBranch(routes: [
      GoRoute(path: '/search', builder: (c, s) => const SearchScreen()),
    ]),
  ],
)
```

The shell hands you a `navigationShell` that knows the current branch and can switch:

```dart
class ScaffoldWithNavBar extends StatelessWidget {
  const ScaffoldWithNavBar({super.key, required this.navigationShell});

  final StatefulNavigationShell navigationShell;

  @override
  Widget build(BuildContext context) => Scaffold(
        body: navigationShell,
        bottomNavigationBar: NavigationBar(
          selectedIndex: navigationShell.currentIndex,
          onDestinationSelected: (i) => navigationShell.goBranch(
            i,
            // Tapping the active tab returns it to its root.
            initialLocation: i == navigationShell.currentIndex,
          ),
          destinations: const [ /* ... */ ],
        ),
      );
}
```

That `initialLocation: i == currentIndex` line is the platform-conventional behaviour people file bugs about when it is missing: tapping the tab you are already on pops back to the tab's root.

Note the nested `routes:` under `/feed` rather than a sibling `/post/:id`. Child routes are what keep the detail screen *inside* the branch, so the bottom bar stays and back returns to the feed. A top-level route with the same path would cover the whole screen — sometimes what you want for a full-screen media viewer, which is exactly when you pass `parentNavigatorKey: _rootKey` to push above the shell.

## Typed routes remove a whole category of bug

String paths are stringly typed: a rename breaks silently, and a missing parameter is a runtime crash. `go_router_builder` generates the plumbing from annotated classes:

```dart
@TypedGoRoute<OrderRoute>(path: '/order/:id')
class OrderRoute extends GoRouteData with _$OrderRoute {
  const OrderRoute({required this.id, this.tab});

  final String id;
  final String? tab;

  @override
  Widget build(BuildContext context, GoRouterState state) =>
      OrderScreen(id: id, tab: tab);
}

// Navigating is now a constructor call, checked at compile time:
const OrderRoute(id: '42', tab: 'items').go(context);
```

Rename `id` and every call site fails to compile. Forget `tab` and the analyser says so. The cost is a `build_runner` step in your workflow; the benefit shows up the first time you restructure a route hierarchy in an app with two hundred navigation calls.

## Making a real link open the app

This is where most "deep linking doesn't work" issues actually live, and none of it is Flutter code.

**Android — App Links.** Add an intent filter with `android:autoVerify="true"` to your main activity in `AndroidManifest.xml`, then host `https://yourdomain.com/.well-known/assetlinks.json` containing your package name and the SHA-256 fingerprint of the **signing key that ships**. The upload key and the Play-managed signing key are different fingerprints, and using the wrong one produces the single most common symptom: links open the app in debug and the browser in production.

**iOS — Universal Links.** Add the Associated Domains capability with `applinks:yourdomain.com`, and host `https://yourdomain.com/.well-known/apple-app-site-association` — served as `application/json`, with **no** `.json` extension, over HTTPS, with no redirects. iOS caches this file, so during testing delete and reinstall the app rather than assuming your edit took effect.

**Flutter side.** Recent Flutter enables deep linking by default on both platforms; on older versions you may still need `<meta-data android:name="flutter_deeplinking_enabled" android:value="true" />`. go_router then receives the incoming path through the standard `Router` API and matches it against your table — no plugin required for `https://` links.

Verify with the platform tools rather than by tapping links in a chat app, which often route through their own in-app browser:

```bash
adb shell am start -a android.intent.action.VIEW -d "https://yourdomain.com/order/42"
```

```bash
xcrun simctl openurl booted "https://yourdomain.com/order/42"
```

If the app opens but lands on the wrong screen, the problem is your route table. If the browser opens instead, the problem is the association file or the fingerprint — Flutter never got involved.

## Things that will bite you later

- **Web URLs get a `#` by default.** Call `usePathUrlStrategy()` before `runApp` for clean paths, and configure your host to serve `index.html` for unknown paths, or a refresh on `/order/42` returns a 404 from the server.
- **`go` versus `push`.** `go` replaces the stack according to the route hierarchy; `push` adds on top. Using `push` for tab switches builds an unbounded stack that back-button users notice.
- **Deep links that need auth.** A cold-start deep link arrives *before* your token has loaded. This is exactly why the redirect must depend on an initialised flag rather than a nullable user object.
- **`errorBuilder` is your 404.** Without it a mistyped link shows a framework error page. With `state.uri` you can log which links people are actually hitting.

## FAQ

**Do I need a package like `uni_links` or `app_links`?**

Not for `https://` and custom-scheme links that the framework already delivers to `Router`. A package earns its place when you need to observe raw incoming links outside the router, or handle schemes the platform integration does not.

**Why does my redirect run twice?**

It runs for the initial location and again for the redirected one — that is expected. If it runs many times you have a cycle; go_router raises a redirect-limit error rather than looping forever, and `debugLogDiagnostics` shows the chain.

**Can I use `Navigator.push` alongside go_router?**

Yes, and it is right for things that are not addressable — a dialog, a bottom sheet, a photo viewer opened from a gesture. Anything a user could bookmark or receive as a link belongs in the route table.

**How do I keep scroll position when switching tabs?**

`StatefulShellRoute.indexedStack` keeps each branch's widgets alive, so scroll position survives by construction. If it does not, something inside the branch is being rebuilt from scratch — usually a router or a controller created in `build`.

**What is `state.matchedLocation` versus `state.fullPath`?**

`matchedLocation` is the concrete path that matched, with parameters filled in. `fullPath` is the pattern, like `/order/:id`. Use the pattern for analytics grouping and the concrete one for guards.

---

*Route API details are from the go_router documentation and the Flutter deep-linking guides linked above; the platform configuration steps follow the official cookbook recipes. Which patterns are worth adopting — typed routes, the splash-until-initialised shape, `initialLocation` on tab taps — is my own judgement from shipping them. go_router's API has changed across major versions; check the changelog for the version in your `pubspec.yaml`.*
