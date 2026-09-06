---
title: "Background work in Flutter: what the OS will actually let you run"
description: "Android and iOS have different, and equally firm, opinions about running code when your app is not in front. Understanding those limits before choosing a package saves you from building a feature the platform will quietly refuse to execute."
seoDescription: "Flutter background execution: WorkManager and BGTaskScheduler through the workmanager package, isolate entry points, constraints, iOS limits, foreground services, and when to move work to a server."
keywords:
  - flutter background task
  - flutter workmanager package
  - flutter background isolate entry point
  - ios bgtaskscheduler flutter
  - flutter foreground service android
  - flutter periodic background sync
category: "Deep Dive"
topic: "Flutter"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-08-19"
emoji: "⏱️"
tags: ["Flutter", "Background", "Android", "iOS", "Architecture"]
sources:
  - name: "workmanager — pub.dev"
    url: "https://pub.dev/packages/workmanager"
  - name: "WorkManager — Android developer documentation"
    url: "https://developer.android.com/topic/libraries/architecture/workmanager"
  - name: "BGTaskScheduler — Apple developer documentation"
    url: "https://developer.apple.com/documentation/backgroundtasks/bgtaskscheduler"
  - name: "Foreground services — Android developer documentation"
    url: "https://developer.android.com/develop/background-work/services/foreground-services"
  - name: "Isolates — Dart documentation"
    url: "https://dart.dev/language/isolates"
  - name: "Background processes — Flutter documentation"
    url: "https://docs.flutter.dev/packages-and-plugins/background-processes"
related:
  - slug: "flutter-isolates-off-main-thread"
    title: "Flutter isolates: what actually goes off the UI thread, and what doesn't"
  - slug: "flutter-push-notifications-fcm"
    title: "Push notifications in Flutter: the four states your app can be in"
draft: false
---

"Sync the user's data every fifteen minutes" sounds like a scheduling problem. It is really a negotiation with two operating systems that have spent a decade getting better at saying no.

Before choosing a package, it is worth being precise about what each platform actually offers, because the gap between them determines what your feature can promise.

## What you are actually allowed

| Capability | Android | iOS |
| --- | --- | --- |
| Periodic background work | Yes, minimum ~15 minutes, subject to Doze | `BGAppRefreshTask` — the system decides when, possibly never |
| One-off deferred work | Yes, with constraints | `BGProcessingTask`, typically overnight while charging |
| Guaranteed execution while app is closed | Only via a foreground service with a visible notification | No |
| Long-running work (minutes) | Foreground service | No — a background task gets seconds, then is suspended |
| Triggered by a server | Yes, high-priority FCM | Limited; silent pushes are throttled |

The row that changes designs is the third. **On iOS there is no way to guarantee that your code runs while the app is closed.** The system learns usage patterns and schedules refresh opportunities around them; a user who opens your app rarely may get none for days. Any feature specified as "must update every hour, regardless" cannot be built on iOS background execution. It can be built on a server that does the work and a push that delivers the result.

## The isolate rule

Whatever package you use, background callbacks run in a **fresh isolate** with no connection to your app's running state.

```dart
@pragma('vm:entry-point')
void callbackDispatcher() {
  Workmanager().executeTask((taskName, inputData) async {
    // A separate isolate: no providers, no singletons, no open connections.
    WidgetsFlutterBinding.ensureInitialized();

    switch (taskName) {
      case 'sync':
        final db = await openDatabase();
        try {
          await SyncService(db).runOnce();
          return true;
        } catch (e, s) {
          await logToDisk(e, s);
          return false; // Ask the platform to retry with backoff.
        } finally {
          await db.close();
        }
      default:
        return true;
    }
  });
}

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Workmanager().initialize(callbackDispatcher);
  runApp(const MyApp());
}
```

Three details that are load-bearing:

**`@pragma('vm:entry-point')`** — without it the function is tree-shaken out of release builds. Works in debug, silently does nothing in release. This is the single most common background-work bug in Flutter.

**`WidgetsFlutterBinding.ensureInitialized()` inside the callback** — the new isolate has no binding, so any plugin channel you touch fails without it.

**The boolean return value is a contract.** Returning `false` tells the platform the task failed and should be retried according to its backoff policy. Returning `true` on failure means the work is silently dropped.

Because the isolate is fresh, everything it needs must come from `inputData` (which must be primitives) or from disk. Passing an object graph is not possible, and any `SharedPreferences` value you read there was written by a different isolate — fine, but be aware writes from background and foreground can race.

## Scheduling with constraints

```dart
await Workmanager().registerPeriodicTask(
  'sync-task-id',
  'sync',
  frequency: const Duration(hours: 1),
  constraints: Constraints(
    networkType: NetworkType.connected,
    requiresBatteryNotLow: true,
  ),
  existingWorkPolicy: ExistingWorkPolicy.keep,
  backoffPolicy: BackoffPolicy.exponential,
  initialDelay: const Duration(minutes: 10),
);
```

Constraints are the part people skip and then wonder why users complain about battery. `requiresBatteryNotLow` and `networkType` let the system batch your work with everyone else's, which is both better for the device and more likely to actually run.

`existingWorkPolicy: keep` matters if you register on every app start — without it, `replace` cancels and reschedules the task each launch, and a task that is always being rescheduled may never reach its first execution.

The requested `frequency` is a *minimum*, not a promise. An hourly task on a device in Doze may run once overnight. Design the work to be correct at any cadence: idempotent, resumable, and reconciling rather than incremental.

## When you genuinely need it to run

If the work is user-visible and must complete — a file upload, a workout tracker, an audio player — the answer on Android is a **foreground service** with a persistent notification, not WorkManager. Packages such as `flutter_foreground_task` wrap this. The visible notification is not optional; it is the deal the platform offers in exchange for reliable execution.

Recent Android versions also require declaring a foreground service *type* in the manifest and requesting a matching permission, and Play reviews the justification. Choose the type honestly — a "data sync" declaration used for something else is a rejection risk.

On iOS the equivalent list is short and specific: audio playback, location updates, VoIP, and a few others, each requiring the matching background mode and each policed at review. If your use case is not on the list, it is not available, and designing around that early is cheaper than discovering it at submission.

## The design that survives both platforms

For anything approaching "keep data fresh", the shape that works everywhere is:

1. **The server does the work.** It knows the schedule and does not sleep.
2. **A push tells the app something changed** — data-only on Android where reliability is better, and accept that iOS may batch it.
3. **The app syncs on resume.** This is the path that actually runs, on both platforms, every time.
4. **Background tasks are an optimisation**, making the app fresher when the OS is feeling generous — never the mechanism the feature depends on.

Written that way, background execution failing is a slightly staler first screen rather than a broken feature. I have not seen a design that assumes reliable background execution on iOS survive contact with real users.

## Debugging

Background code is hard to observe because your debugger is not attached when it runs. Two things help disproportionately:

- **Log to a file, not to the console.** Append a timestamped line at the start and end of every background run and expose it in a debug screen. Without this you cannot distinguish "never scheduled" from "ran and failed".
- **Force execution.** On Android, `adb shell cmd jobscheduler run -f <package> <job-id>` triggers a job immediately. On iOS, Xcode's debugger can trigger a registered `BGTaskScheduler` task via a debugger command. Both are far faster than waiting.

## FAQ

**Why does my task never run on iOS?**

Most likely working as designed. Confirm the background mode is declared, the identifier is registered before launch completes, and then test with the Xcode trigger rather than by waiting.

**Can I run a task every minute?**

No. Android's floor is roughly fifteen minutes for periodic work; iOS does not accept a frequency at all. A foreground service can run continuously, with the notification that requires.

**Does the background isolate share my database connection?**

No. Open your own and close it. Concurrent access from two isolates needs a database that supports it — check your package's guarantees rather than assuming.

**Will background work drain the battery?**

It can, which is why constraints exist. Respect `requiresBatteryNotLow`, keep runs short, and never poll when a push would do.

**Is `Timer.periodic` an option?**

Only while the app is alive in the foreground. It stops when the app is suspended, which is the exact case background execution is for.

---

*The platform capabilities, `workmanager` API, `vm:entry-point` requirement and foreground-service rules described here are documented in the references linked above. The capability table's framing, the four-step design recommendation, the file-logging practice and the assessment that iOS background execution cannot be depended upon are my own judgement from building sync features. Platform background policies tighten with nearly every OS release — verify current limits against the platform documentation before designing around them.*
