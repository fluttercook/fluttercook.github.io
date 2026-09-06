---
title: "Dependency injection in Flutter without the ceremony"
description: "get_it, Provider, Riverpod and plain constructors all solve the same problem: making a class say what it needs instead of reaching for it. Here is what each actually gives you, and the rule that decides between them."
seoDescription: "Flutter dependency injection compared: get_it service locator, InheritedWidget and Provider, Riverpod, constructor injection, lazy singletons, scoped disposal, and testing without global state."
keywords:
  - flutter dependency injection
  - get_it service locator flutter
  - flutter provider vs riverpod di
  - flutter constructor injection
  - flutter lazy singleton
  - flutter testing dependency override
category: "Guide"
topic: "Flutter"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-17"
emoji: "🧩"
tags: ["Flutter", "Architecture", "Testing", "Dart", "Patterns"]
sources:
  - name: "get_it — pub.dev"
    url: "https://pub.dev/packages/get_it"
  - name: "provider — pub.dev"
    url: "https://pub.dev/packages/provider"
  - name: "Riverpod documentation"
    url: "https://riverpod.dev/"
  - name: "InheritedWidget — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/InheritedWidget-class.html"
  - name: "Testing Flutter apps — Flutter documentation"
    url: "https://docs.flutter.dev/testing/overview"
  - name: "injectable — pub.dev"
    url: "https://pub.dev/packages/injectable"
related:
  - slug: "flutter-state-management-decision-guide"
    title: "Choosing Flutter state management without the holy war"
  - slug: "flutter-build-context-explained"
    title: "BuildContext is an element: reading the error messages that mention it"
draft: false
---

Dependency injection has an intimidating name for an unremarkable idea: a class should be handed what it needs rather than constructing or locating it. That is the whole concept. Everything else — containers, locators, providers, generated code — is machinery for delivering it.

The reason to care is testing. `ApiClient()` written inside a repository means every test of that repository makes real network calls. `ApiClient` passed in means every test can pass a fake. That is the entire payoff, and it is enough.

## Constructor injection, which needs no package

```dart
final class UserRepository {
  const UserRepository(this._api, this._cache);

  final ApiClient _api;
  final UserCache _cache;

  Future<User> fetch(String id) async {
    final cached = _cache.get(id);
    if (cached != null) return cached;

    final user = await _api.getUser(id);
    _cache.put(user);
    return user;
  }
}
```

Testing this requires no framework at all:

```dart
test('returns cached user without hitting the network', () async {
  final api = FakeApi()..failIfCalled = true;
  final repo = UserRepository(api, UserCache()..put(knownUser));

  expect(await repo.fetch(knownUser.id), knownUser);
});
```

Every DI package exists to answer one question this does not: **who constructs the object graph, and where does the top of it live?** For a small app the answer can literally be `main()`. It stops scaling when the widget three levels down needs the repository and you are threading it through constructors that do not otherwise care.

## get_it: a service locator

```dart
final getIt = GetIt.instance;

void configureDependencies() {
  getIt
    ..registerLazySingleton<ApiClient>(() => ApiClient(baseUrl: Config.apiBase))
    ..registerLazySingleton<UserCache>(UserCache.new)
    ..registerLazySingleton<UserRepository>(
      () => UserRepository(getIt(), getIt()),
    )
    ..registerFactory<SearchController>(() => SearchController(getIt()));
}
```

The registration types matter and are easy to confuse:

| Registration | Created | Lives |
| --- | --- | --- |
| `registerSingleton` | Immediately at registration | Forever |
| `registerLazySingleton` | On first `get` | Forever |
| `registerFactory` | On every `get` | Until you drop the reference |
| `registerSingletonAsync` | Immediately, awaitable via `allReady()` | Forever |

`registerLazySingleton` should be your default. Eager singletons run their constructors at startup, and a database or analytics client constructed at `main()` is directly measurable in your cold-start time.

Async registration is the answer to "my repository needs `SharedPreferences`, which is a `Future`":

```dart
getIt.registerSingletonAsync<SharedPreferences>(SharedPreferences.getInstance);
getIt.registerSingletonWithDependencies<SettingsStore>(
  () => SettingsStore(getIt<SharedPreferences>()),
  dependsOn: [SharedPreferences],
);

await getIt.allReady();
```

This is much better than the common alternative of making everything downstream async, or of a global `late` variable initialised in `main()` that throws confusingly when something reads it early.

**The honest downside**: `getIt<Thing>()` called from inside a class hides a dependency. The class's constructor no longer tells you what it needs, and a test must configure the global container. The discipline that keeps it manageable is to **call `getIt` only at composition points** — in `main()`, in a route builder, in a widget's `initState` — and pass the result down as a constructor argument. Used that way it is a locator at the edges and constructor injection everywhere else.

## Provider and Riverpod: scoped to the tree

`Provider` puts dependencies in the widget tree, which gives you something get_it structurally cannot: **scope**.

```dart
MultiProvider(
  providers: [
    Provider<ApiClient>(create: (_) => ApiClient(), dispose: (_, c) => c.close()),
    ProxyProvider<ApiClient, UserRepository>(
      update: (_, api, __) => UserRepository(api, UserCache()),
    ),
  ],
  child: const MyApp(),
)
```

A provider placed above a subtree is disposed when that subtree leaves the tree. For anything with a lifecycle tied to a screen — a WebSocket for a chat room, an editing session, a scoped cache — this is exactly right, and doing it with a global locator means manual registration and unregistration that someone will eventually get wrong.

Riverpod's version drops the `BuildContext` requirement, which is its main practical advantage:

```dart
final apiClientProvider = Provider<ApiClient>((ref) {
  final client = ApiClient();
  ref.onDispose(client.close);
  return client;
});

final userRepositoryProvider = Provider<UserRepository>((ref) {
  return UserRepository(ref.watch(apiClientProvider), UserCache());
});
```

And overriding for tests is first-class rather than a global mutation:

```dart
ProviderScope(
  overrides: [apiClientProvider.overrideWithValue(FakeApi())],
  child: const MyApp(),
)
```

## The rule I use

| Situation | Approach |
| --- | --- |
| App-lifetime services (http client, database, logger) | `get_it` lazy singletons, or a Riverpod provider |
| Anything scoped to a screen or flow | Tree-scoped: Provider or Riverpod with `autoDispose` |
| Anything a class needs to do its job | Constructor parameter, always |
| A widget that needs a service three levels down | Locate at the screen, pass down |

The consistent thread: **locate at the edge, inject in the middle.** Business logic classes should be constructible with `new` and no framework present. If a repository cannot be instantiated in a plain Dart test without initialising a container, the dependency is in the wrong place.

## Testing

Whichever you pick, tests need a reset between cases or state leaks across them:

```dart
setUp(() async {
  await getIt.reset();
  getIt.registerLazySingleton<ApiClient>(() => FakeApi());
});
```

Forgetting `reset()` produces the worst test failure mode: passes alone, fails in the suite, or vice versa, depending on order. If you find yourself debugging that, check container lifetime before anything else.

## Do you need code generation?

`injectable` generates the registration code from annotations. It removes boilerplate and adds a build step, a generated file to keep current, and one more thing to explain to a new contributor.

For a large app with dozens of services, the trade is often worth it. For a typical app with fifteen, a hand-written `configureDependencies()` is thirty lines you can read top to bottom, and reading it is how people learn the architecture. I would start hand-written and adopt generation when the file genuinely becomes a burden — which, for most apps, is never.

## FAQ

**Is a service locator an anti-pattern?**

Used inside business logic, it hides dependencies and complicates tests. Used at composition points only, it is a reasonable way to build the object graph. The pattern is not the problem; unrestricted use is.

**get_it or Riverpod, if I must pick one?**

If you already use Riverpod for state, use it for dependencies too — one mental model beats two. If you use BLoC or setState, get_it plus constructor injection stays out of your way.

**How do I inject something that needs `BuildContext`?**

You usually should not. Pass the value derived from context (a theme colour, a locale) rather than context itself. A service holding a `BuildContext` outlives it and crashes later.

**Can I register different implementations per flavor?**

Yes — branch in `configureDependencies()` on your flavor config. This is one of the clearest wins of having a single composition point.

**What about circular dependencies?**

They are a design signal, not a container problem. A lazy singleton lets you postpone the crash rather than avoid it; splitting the shared concern into a third class is the actual fix.

---

*The `get_it` registration types, Provider and Riverpod scoping and override APIs, and the testing facilities described here are documented in the references linked above. The locate-at-the-edge rule, the recommendation to default to lazy singletons, the situation table and the position on code generation are my own judgement from maintaining apps with each of these. Package APIs change between major versions — check the changelog for the version you depend on.*
