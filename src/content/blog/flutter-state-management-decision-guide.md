---
title: "Riverpod, Bloc, signals or setState: choosing Flutter state management and living with it"
description: "One list screen with loading, error, data and pull-to-refresh, written four ways — setState, ValueNotifier, Riverpod and Bloc — so you compare real code instead of adjectives. Plus the point where setState genuinely stops being enough."
seoDescription: "The same Flutter screen built in setState, ValueNotifier, Riverpod and Bloc, plus a decision table keyed on team size, testing and async load."
keywords:
  - flutter state management
  - riverpod vs bloc
  - flutter setstate vs provider
  - valuenotifier flutter
  - flutter_bloc tutorial
  - flutter signals package
category: "Guide"
topic: "Flutter"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-22"
emoji: "🧩"
tags: ["Flutter", "State Management", "Riverpod", "Bloc", "Architecture"]
sources:
  - name: "Flutter — List of state management approaches"
    url: "https://docs.flutter.dev/data-and-backend/state-mgmt/options"
  - name: "Flutter — Differentiate between ephemeral state and app state"
    url: "https://docs.flutter.dev/data-and-backend/state-mgmt/ephemeral-vs-app"
  - name: "Flutter — App architecture"
    url: "https://docs.flutter.dev/app-architecture"
  - name: "ValueNotifier class — Flutter API docs"
    url: "https://api.flutter.dev/flutter/foundation/ValueNotifier-class.html"
  - name: "ValueListenableBuilder class — Flutter API docs"
    url: "https://api.flutter.dev/flutter/widgets/ValueListenableBuilder-class.html"
  - name: "RefreshIndicator class — Flutter API docs"
    url: "https://api.flutter.dev/flutter/material/RefreshIndicator-class.html"
  - name: "Dart — Patterns"
    url: "https://dart.dev/language/patterns"
  - name: "Dart — Class modifiers"
    url: "https://dart.dev/language/class-modifiers"
  - name: "flutter_riverpod on pub.dev"
    url: "https://pub.dev/packages/flutter_riverpod"
  - name: "flutter_bloc on pub.dev"
    url: "https://pub.dev/packages/flutter_bloc"
  - name: "provider on pub.dev"
    url: "https://pub.dev/packages/provider"
  - name: "signals on pub.dev"
    url: "https://pub.dev/packages/signals"
related:
  - slug: "flutter-introduction-2026"
    title: "What Flutter is: reading a 3D game built in 15 minutes to understand the whole framework"
  - slug: "creating-a-custom-progress-indicator"
    title: "Creating a custom progress indicator in Flutter with CustomPaint"
draft: false
---

Every Flutter state management comparison is a feature checklist. Riverpod has compile-safe providers. Bloc has a unidirectional event log. signals has fine-grained reactivity. All true, all useless — a checklist tells you what a library *has* and never what it *costs* when the person maintaining that code is not you.

The more useful framing is that each of these libraries answers a different question. If the question it answers is not one your app is asking, its features are overhead you pay for in review time and onboarding. So instead of tabulating adjectives, this article writes **the same feature four times** — one screen that loads a list, shows loading, error and data states, and supports pull-to-refresh — and then reads the diff.

I will say the unpopular part up front: `setState` plus `ValueNotifier` and `InheritedWidget` is enough for a lot of production apps, and Flutter's own documentation draws that line too. There is a real point where it stops being enough. That point is not "the app got big." It is much more specific, and it is named at the end.

## Each library is answering a different question

Read these as design questions, not marketing:

- **`setState`** answers *"which widget should rebuild?"* — nothing else. It has no opinion on where state lives, how long it lives, or who else can see it.
- **`ValueNotifier` + `InheritedWidget`** answer *"how does a value get from where it lives to where it's read, and how do readers find out it changed?"* This is Flutter's built-in answer to propagation. It has no answer for lifetime.
- **`provider`** answers *"how do I put an object above the widget that needs it, and dispose it at the right moment?"* It is `InheritedWidget` plumbing with disposal attached.
- **Riverpod** answers *"who owns this state, when is it created, when is it thrown away, and what recomputes when it changes?"* It is a dependency graph with lifetimes. Caching and invalidation are the product; dependency injection is a side effect.
- **Bloc** answers *"what happened, and what did that produce?"* Its product is an auditable, uniform, greppable shape that every feature follows regardless of who wrote it.
- **signals** answers *"which exact leaf of the widget tree needs to rebuild when this one value changes?"* Dependencies are recorded when you read them, so you never declare them.

Only two of those are really about state. Riverpod is about *lifetime*. Bloc is about *convention*. If your pain is neither lifetime nor convention, you are shopping in the wrong aisle.

## The feature, written four times

One screen, four states: loading, failure, data, refreshing. Shared types for every version:

```dart
class Recipe {
  const Recipe({required this.id, required this.title});
  final String id;
  final String title;
}

abstract interface class RecipeRepository {
  Future<List<Recipe>> fetchRecipes();
}
```

Every version below also uses two trivial presentational widgets that hold no state logic: `RecipeList(recipes)`, a `ListView.builder` of `ListTile`s, and `ErrorView(message, onRetry:)`, a message with a retry button. They are identical in all four and left out to keep the diffs honest.

And, for the three versions that model state explicitly, one sealed hierarchy. This is the part people skip, and it matters most — **the state model is identical across libraries.** What changes is only who is allowed to move it.

```dart
sealed class RecipeListState { const RecipeListState(); }

final class RecipeListLoading extends RecipeListState { const RecipeListLoading(); }

final class RecipeListFailure extends RecipeListState {
  const RecipeListFailure(this.error);
  final Object error;
}

final class RecipeListSuccess extends RecipeListState {
  const RecipeListSuccess(this.recipes);
  final List<Recipe> recipes;
}
```

Because the class is `sealed`, a `switch` over it is exhaustive: add a fourth state and every screen that renders it stops compiling until you handle it. That one Dart 3 feature removes a large share of what people historically bought a state library to get.

### Version 1 — `setState`, with the bugs visible

```dart
class _RecipeListPageState extends State<RecipeListPage> {
  RecipeListState _state = const RecipeListLoading();

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _state = const RecipeListLoading());
    try {
      final recipes = await widget.repository.fetchRecipes();
      if (!mounted) return;
      setState(() => _state = RecipeListSuccess(recipes));
    } catch (error) {
      if (!mounted) return;
      setState(() => _state = RecipeListFailure(error));
    }
  }

  @override
  Widget build(BuildContext context) => switch (_state) {
        RecipeListLoading() => const Center(child: CircularProgressIndicator()),
        RecipeListFailure(error: final e) => ErrorView('$e', onRetry: _load),
        RecipeListSuccess(recipes: final recipes) =>
          RefreshIndicator(onRefresh: _load, child: RecipeList(recipes)),
      };
}
```

Around thirty lines, and genuinely correct — more than a lot of Bloc code manages. Three things are worth naming.

`if (!mounted) return;` is not optional. Without it, a user who backs out mid-request gets `setState() called after dispose()`. Every async state solution has to solve this; here you solve it by hand, twice, in every method that awaits.

`RefreshIndicator.onRefresh` wants a `Future` that completes when the refresh is done, and `_load` happens to be exactly that. Remember this — it is the one place `setState` is *easier* than Bloc.

And the real limitation: **`_load` cannot be unit tested.** The logic is welded to a `State` object, so testing it needs `pumpWidget` and a full widget tree. Fine for one screen. Not fine for forty.

### Version 2 — `ValueNotifier`, the same logic lifted out

```dart
class RecipeListController extends ValueNotifier<RecipeListState> {
  RecipeListController(this._repository) : super(const RecipeListLoading());

  final RecipeRepository _repository;

  Future<void> load() async {
    value = const RecipeListLoading();
    try {
      value = RecipeListSuccess(await _repository.fetchRecipes());
    } catch (error) {
      value = RecipeListFailure(error);
    }
  }
}
```

```dart
class _RecipeListPageState extends State<RecipeListPage> {
  late final _controller = RecipeListController(widget.repository)..load();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<RecipeListState>(
      valueListenable: _controller,
      builder: (context, state, _) => switch (state) {
        RecipeListLoading() => const Center(child: CircularProgressIndicator()),
        RecipeListFailure(error: final e) =>
          ErrorView('$e', onRetry: _controller.load),
        RecipeListSuccess(recipes: final recipes) => RefreshIndicator(
            onRefresh: _controller.load,
            child: RecipeList(recipes),
          ),
      },
    );
  }
}
```

Nothing was added. Something was *removed*: the logic no longer touches `BuildContext`, so it is a plain Dart object you can test with a plain `test()` and a fake repository. No `pumpWidget`, no pumping frames.

Two traps nobody warns you about. **Setting `value` after `dispose()` throws.** The `mounted` problem did not disappear, it moved — if the route is popped while `fetchRecipes()` is in flight, `load()` resumes and assigns to a disposed notifier. Guard it with a `bool _disposed` you set in an overridden `dispose()`, or hold the controller somewhere that outlives the route.

**`ValueNotifier` skips the notification when the new value `==` the old one.** With `const RecipeListLoading()` on both sides, Dart canonicalises them to the same instance, so Loading → Loading emits nothing. Harmless here. Not harmless the day you add `Equatable` to a state class and wonder why an identical-looking state stops re-rendering a list you mutated in place.

For a screen this size, version 2 is where a lot of apps should stop. No packages, testable, and every Flutter developer alive can read it.

## Riverpod: the state gets an owner and a lifetime

Riverpod's pitch is not "less boilerplate." It is that a piece of state is declared once, at top level, with an explicit lifetime, and anything reading it recomputes automatically when it changes.

These snippets target **Riverpod 3.x with `flutter_riverpod`, no code generation**, because that syntax has been stable across major versions. The `riverpod_generator` `@riverpod` annotation style produces the same providers with less typing.

```dart
final recipeRepositoryProvider = Provider<RecipeRepository>((ref) {
  return HttpRecipeRepository();
});

final recipeListProvider = FutureProvider<List<Recipe>>((ref) async {
  return ref.watch(recipeRepositoryProvider).fetchRecipes();
});
```

That is the whole feature. There is no `RecipeListState` — `FutureProvider` exposes an `AsyncValue`, the same three-state sealed union written for you, plus the two cases hand-rolled code usually forgets: *data present but a refresh is in flight*, and *error present but stale data still available*.

```dart
class RecipeListPage extends ConsumerWidget {
  const RecipeListPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ref.watch(recipeListProvider).when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, stack) => ErrorView(
            '$error',
            onRetry: () => ref.invalidate(recipeListProvider),
          ),
          data: (list) => RefreshIndicator(
            onRefresh: () => ref.refresh(recipeListProvider.future),
            child: RecipeList(list),
          ),
        );
  }
}
```

`ref.refresh(recipeListProvider.future)` returns a `Future`, exactly what `RefreshIndicator` wants — the awkwardness you are about to see in the Bloc version does not exist here. The app is wrapped once in `ProviderScope`.

The cancellation and mounted problems are gone, not because Riverpod is clever about `async` but because *the widget no longer owns the request*. The provider does, and the provider's lifetime belongs to the scope. When the last listener goes away an auto-disposing provider tears down; without auto-dispose the result stays cached, and the next screen that watches it gets the cached list rather than a second network call. **That caching behaviour is the actual reason to adopt Riverpod**, and it is the thing that takes real effort to replicate by hand.

Testing needs no widget at all:

```dart
test('recipeListProvider resolves from the repository', () async {
  final container = ProviderContainer(
    overrides: [recipeRepositoryProvider.overrideWithValue(FakeRepository())],
  );
  addTearDown(container.dispose);

  expect(await container.read(recipeListProvider.future), hasLength(3));
});
```

When you need methods on the state rather than a bare future — an optimistic delete, say — you graduate to an `AsyncNotifier`, where `AsyncValue.guard` collapses the whole try/catch from version 1 into one call:

```dart
class RecipeListNotifier extends AsyncNotifier<List<Recipe>> {
  @override
  Future<List<Recipe>> build() =>
      ref.watch(recipeRepositoryProvider).fetchRecipes();

  Future<void> reload() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ref.read(recipeRepositoryProvider).fetchRecipes(),
    );
  }
}

final recipeListProvider =
    AsyncNotifierProvider<RecipeListNotifier, List<Recipe>>(RecipeListNotifier.new);
```

If you are on a different major version, check the notifier base-class names against the current docs before copying — that part of the API has moved between releases, while `FutureProvider` and `ref.watch` have not.

## Bloc: every change has a name you can log

Bloc reuses the exact `RecipeListState` hierarchy from earlier and adds a second one for inputs. That doubling is the trade, and it buys something specific. These snippets target `flutter_bloc` 9.x.

```dart
sealed class RecipeListEvent { const RecipeListEvent(); }

final class RecipeListRequested extends RecipeListEvent { const RecipeListRequested(); }

final class RecipeListRefreshed extends RecipeListEvent { const RecipeListRefreshed(); }

class RecipeListBloc extends Bloc<RecipeListEvent, RecipeListState> {
  RecipeListBloc(this._repository) : super(const RecipeListLoading()) {
    on<RecipeListRequested>(_onLoad);
    on<RecipeListRefreshed>(_onLoad);
  }

  final RecipeRepository _repository;

  Future<void> _onLoad(
    RecipeListEvent event,
    Emitter<RecipeListState> emit,
  ) async {
    emit(const RecipeListLoading());
    try {
      emit(RecipeListSuccess(await _repository.fetchRecipes()));
    } catch (error) {
      emit(RecipeListFailure(error));
    }
  }
}
```

The widget side splits in two, deliberately — the provider half creates the bloc, the view half only reads it:

```dart
BlocProvider(
  create: (_) => RecipeListBloc(context.read<RecipeRepository>())
    ..add(const RecipeListRequested()),
  child: const RecipeListView(),
);
```

```dart
class RecipeListView extends StatelessWidget {
  const RecipeListView({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<RecipeListBloc, RecipeListState>(
      builder: (context, state) => switch (state) {
        RecipeListLoading() => const Center(child: CircularProgressIndicator()),
        RecipeListFailure(error: final e) => ErrorView(
            '$e',
            onRetry: () =>
                context.read<RecipeListBloc>().add(const RecipeListRequested()),
          ),
        RecipeListSuccess(recipes: final recipes) => RefreshIndicator(
            onRefresh: () {
              final bloc = context.read<RecipeListBloc>()
                ..add(const RecipeListRefreshed());
              return bloc.stream.firstWhere((s) => s is! RecipeListLoading);
            },
            child: RecipeList(recipes),
          ),
      },
    );
  }
}
```

That `onRefresh` body is the honest cost of unidirectional data flow. `add()` is fire-and-forget by design, but `RefreshIndicator` needs a `Future` that completes when the work finishes, so you reconstruct it by listening to the output stream. Every Bloc codebase has some version of this; most hide it in a helper and stop noticing.

Note also `emit(const RecipeListLoading())` when the initial state is already `const RecipeListLoading()`: `emit` drops a state that `==` the current one, so that first emit does nothing. Invisible here, a genuine bug source once your states carry `Equatable` and you re-emit a list you mutated in place instead of replacing.

What you get back is `bloc_test`, which reads like a specification:

```dart
blocTest<RecipeListBloc, RecipeListState>(
  'emits a success state when the repository returns',
  build: () => RecipeListBloc(FakeRepository()),
  act: (bloc) => bloc.add(const RecipeListRequested()),
  expect: () => [isA<RecipeListSuccess>()],
);
```

And you get something nothing else on this list provides: **a uniform shape.** Forty features by twelve developers all look the same. That is worth real money at a certain headcount, and worth nothing at all below it.

## signals: rebuild the smallest thing that changed

The `signals` package brings the reactive-primitive model — the idea behind SolidJS and Preact signals — to Dart. You do not declare dependencies; they are recorded when you read them.

```dart
final counter = signal(0);
final doubled = computed(() => counter.value * 2);

// In build():
Watch((context) => Text('${doubled.value}'));
```

`doubled` knows it depends on `counter` because it read it. Only the `Watch` that read `doubled` rebuilds — not the enclosing widget, not the route. For a screen with many independent small values (a form, a canvas editor, a live dashboard) that is a real reduction in rebuild scope compared with one `setState` at the top.

I am deliberately not showing a full async list implementation, because the async surface of `signals` has changed more between releases than the core primitives have, and a version-specific snippet would age badly. Read the package docs before adopting.

The strategic caveat matters more than the API anyway: signals is a smaller ecosystem than Riverpod or Bloc, and Flutter's own architecture guidance is written around `Listenable`/`ChangeNotifier`. That is not an argument against it — it is an argument that you will write more of your own conventions and field more "why is this different from the tutorial?" questions.

## What actually differs once the app is real

Line counts for one screen are a bad proxy. These are the differences that surface at month six:

| | setState + ValueNotifier | provider | Riverpod | Bloc |
| --- | --- | --- | --- | --- |
| Test logic without a widget | Only once extracted to a controller | Yes | Yes, via `ProviderContainer` | Yes, via `bloc_test` |
| Cache server state across screens | Hand-rolled | Hand-rolled | Built in | In a repository layer |
| Dispose correctly on route pop | Yours to get right | Handled | Handled | Handled |
| Missing dependency fails at | — | Runtime lookup | Compile time | Runtime lookup |
| Swap a dependency in tests | Constructor argument | Provider override | Provider override | Constructor argument |
| Trace "why did this change?" | Read the code | Read the code | Provider observer | Event log, by design |
| `RefreshIndicator` integration | Natural | Natural | Natural | Needs a stream round-trip |
| New hire productive in | Hours | Hours | A day or two | A day, then mechanical |

The last row is the one teams underweight. Bloc's learning curve is front-loaded and then flat — once you have written two blocs you have written all of them. Riverpod's curve is gentler at the start and has a second climb later, when you meet auto-dispose, families, and the difference between `ref.watch` and `ref.read` inside a callback. Plain Flutter has no curve and no ceiling either; you simply keep paying in hand-written plumbing.

## A decision table you can argue with

Pick your row by the strongest signal, not by adding up points.

| If this is true of your app | Then |
| --- | --- |
| Solo or two devs, mostly local/UI state, a handful of network calls | `setState` + `ValueNotifier`. Extract controllers, skip the package. |
| Solo dev, but the same object is needed on unrelated screens | `provider` with `ChangeNotifier`, or Riverpod if you want the caching. |
| Most screens are server-backed, with caching and invalidation | Riverpod. This is precisely the question it answers. |
| Six or more devs, several squads, a long-lived product | Bloc. You are buying uniformity, and uniformity scales with headcount. |
| Compliance or support needs a replayable trail of what happened | Bloc. Nothing else gives you this without building it. |
| A few screens with many small independent values | signals, scoped to those screens. |
| You are migrating a large existing codebase | Whatever it already uses. A half-migration is worse than either endpoint. |

Two things that table will not tell you. First, mixing is normal and healthy: a Riverpod app still uses `setState` for whether a card is expanded, and Flutter's docs draw exactly that line between *ephemeral* state and *app* state. Second, whichever you pick, **the sealed state class and the repository interface stay the same**, which is why migrating hurts less than the internet suggests. You are swapping the delivery mechanism, not rewriting the feature.

## Where setState stops being enough

Not "when the app gets big." Four concrete triggers, and you usually hit them in this order:

1. **The same server data is read by two widgets with no ancestor–descendant relationship.** You now need either a lift-and-drill through unrelated constructors, or a real propagation mechanism. This is the `InheritedWidget`/`provider` threshold, and it arrives early.
2. **State has to outlive the widget that created it.** The user navigates away and back, and you refetch a list that has not changed. Every fix inside a `State` object is a cache you now maintain by hand — with invalidation, which is the hard half.
3. **You are counting `if (!mounted)` guards.** When a file has more mounted checks and `_disposed` flags than actual business branches, the framework is telling you the request should not be owned by the widget.
4. **Two people disagree in review about where a feature's state should live, more than once.** This is the convention threshold, and the only one that is purely social. It is also the only argument for Bloc that holds up on its own.

Triggers 1 and 2 point at Riverpod. Trigger 3 points at anything that owns lifetime for you. Trigger 4 points at Bloc. If none of the four is true of your codebase today, adding a state management package makes your app harder to read in exchange for nothing.

## FAQ

**Can I use more than one of these in the same app?**
Yes, and most healthy codebases do. `setState` for ephemeral widget state — expanded, focused, hovering — and one shared solution for app state. Where it goes wrong is having two *shared* solutions for the same kind of state, so a new developer cannot predict which one a given feature uses.

**Is `provider` dead now that Riverpod exists?**
No. It is still maintained and still shipped, and remains the lowest-ceremony way to get an object above the widgets that need it. Riverpod was written by the same author to fix specific problems — runtime provider-not-found errors, awkward combination of providers, testability outside the widget tree. If you are not hitting those problems, `provider` is not costing you anything.

**Do I need code generation to use Riverpod?**
No. Every example here is plain Dart with no build step. The `riverpod_generator` package removes the type parameters and infers provider kinds from your function signature, which is pleasant on a large codebase and pure overhead on a small one. You can adopt it later without rewriting your widgets.

**Is Bloc's boilerplate worth it for a solo developer?**
Usually not. An event class per interaction pays for itself when many people touch the same code and need a shared pattern, or when you need a replayable log of what happened. Alone, you pay the full cost of a convention and capture very little of its benefit — and you can add it later, because the state classes carry over unchanged.

**What does Flutter's own team recommend?**
The docs are deliberately unopinionated about packages and very opinionated about structure: separate ephemeral from app state, and follow an MVVM-shaped layering with a repository between your view models and your data sources. That layering is what makes the choice on this page reversible. Get the layers right and the state library becomes an implementation detail of one of them.

---

*The code targets Flutter 3.x with Dart 3 sealed classes and pattern matching; the Riverpod snippets target the 3.x non-generated syntax and the Bloc snippets `flutter_bloc` 9.x. The API surfaces flagged as version-sensitive — notifier base classes in Riverpod, the async helpers in `signals` — are exactly the ones to verify against the current package docs before you copy them. Everything in the decision table is my judgement from shipped apps, not a measurement; the trade-offs are real but your team's numbers will differ from mine.*
