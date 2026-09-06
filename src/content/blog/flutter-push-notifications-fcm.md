---
title: "Push notifications in Flutter: the four states your app can be in"
description: "Foreground, background, terminated, and 'the user tapped the notification to open the app' each deliver the message through a different code path. Most notification bugs are one of those four being unhandled."
seoDescription: "Flutter push notifications with FCM: the four app states, background handlers as top-level functions, notification vs data messages, iOS APNs setup, deep-link routing from a tap, and testing."
keywords:
  - flutter push notifications fcm
  - firebase messaging background handler
  - flutter notification tap deep link
  - flutter data message vs notification
  - flutter apns setup ios
  - flutter local notifications foreground
category: "Guide"
topic: "Flutter"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-21"
emoji: "🔔"
tags: ["Flutter", "Firebase", "Notifications", "Mobile", "Backend"]
sources:
  - name: "firebase_messaging — pub.dev"
    url: "https://pub.dev/packages/firebase_messaging"
  - name: "FCM message types — Firebase documentation"
    url: "https://firebase.google.com/docs/cloud-messaging/concept-options"
  - name: "Receive messages in a Flutter app — Firebase documentation"
    url: "https://firebase.google.com/docs/cloud-messaging/flutter/receive"
  - name: "flutter_local_notifications — pub.dev"
    url: "https://pub.dev/packages/flutter_local_notifications"
  - name: "Notification channels — Android developer documentation"
    url: "https://developer.android.com/develop/ui/views/notifications/channels"
  - name: "UNUserNotificationCenter — Apple developer documentation"
    url: "https://developer.apple.com/documentation/usernotifications"
related:
  - slug: "flutter-navigation-go-router-deep-links"
    title: "go_router and deep links: the parts the quickstart leaves out"
  - slug: "flutter-background-tasks-workmanager"
    title: "Background work in Flutter: what the OS will actually let you run"
draft: false
---

The notification arrives. Sometimes the app shows it, sometimes the system does, sometimes tapping it opens the right screen and sometimes it dumps the user on the home page. The behaviour feels random until you see the structure underneath: **the same message takes four different paths depending on what the app was doing.**

| App state | Who displays it | Which handler runs |
| --- | --- | --- |
| Foreground | Nobody, by default | `onMessage` |
| Background | The OS | `onBackgroundMessage` (separate isolate) |
| Terminated | The OS | `onBackgroundMessage` (separate isolate) |
| Opened by tapping | — | `onMessageOpenedApp`, or `getInitialMessage` if it was terminated |

Every notification bug I have debugged was one of those rows being unhandled. Wire all four and most of the mystery disappears.

## Notification messages versus data messages

Before the code, the distinction that determines everything: an FCM payload can contain a `notification` block, a `data` block, or both.

- **`notification` present** — the OS displays it automatically when the app is backgrounded or terminated. Your handler may not run at all on iOS unless you also opt into it.
- **`data` only** — nothing is displayed automatically. Your handler always gets a chance to run, and you display something yourself.

Data-only messages give control and cost reliability: the OS is free to delay or drop them under battery restrictions. Notification messages are reliable and rigid. For most apps the right answer is **both** — a `notification` block so the user reliably sees something, plus a `data` block carrying the routing information for the tap.

```json
{
  "notification": { "title": "New reply", "body": "Alex replied to your post" },
  "data": { "type": "post", "id": "1234" }
}
```

## Setup, and the part that must be top-level

```dart
@pragma('vm:entry-point')
Future<void> _firebaseBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  // Runs in its own isolate: no access to your app's state or providers.
  debugPrint('Background message: ${message.messageId}');
}

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();

  FirebaseMessaging.onBackgroundMessage(_firebaseBackgroundHandler);

  runApp(const MyApp());
}
```

Two annotations-worth of detail hide a lot of pain.

**The handler must be a top-level or static function**, not a closure and not an instance method. It is looked up by name and invoked in a fresh isolate.

**`@pragma('vm:entry-point')`** stops tree-shaking from removing it in release builds. Without it, background messages work perfectly in debug and silently do nothing in release — which is the kind of bug that reaches production.

Because the handler runs in a **separate isolate**, it shares nothing with your running app: no providers, no singletons, no open database handles you opened elsewhere. It can write to disk or call a network endpoint; it cannot call `setState` or read your Riverpod container.

## Permissions and tokens

```dart
final class PushService {
  PushService(this._messaging);

  final FirebaseMessaging _messaging;

  Future<bool> requestPermission() async {
    final settings = await _messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );
    return settings.authorizationStatus == AuthorizationStatus.authorized ||
        settings.authorizationStatus == AuthorizationStatus.provisional;
  }

  Future<void> syncToken() async {
    final token = await _messaging.getToken();
    if (token != null) await _api.registerDevice(token);

    _messaging.onTokenRefresh.listen(_api.registerDevice);
  }
}
```

Subscribe to `onTokenRefresh` and treat it as the primary path, not a fallback. Tokens rotate — on reinstall, on restore to a new device, occasionally for no visible reason — and an app that only registers the token at first launch accumulates users who silently stop receiving anything.

Ask for permission at a moment where the value is obvious, not on first launch. On iOS the prompt is one-shot: a user who declines cannot be asked again from inside the app, only via Settings.

## Displaying in the foreground

By default, a foreground app shows nothing. You choose:

```dart
FirebaseMessaging.onMessage.listen((message) {
  final notification = message.notification;
  if (notification == null) return;

  _localNotifications.show(
    notification.hashCode,
    notification.title,
    notification.body,
    const NotificationDetails(
      android: AndroidNotificationDetails(
        'messages',
        'Messages',
        importance: Importance.high,
      ),
      iOS: DarwinNotificationDetails(),
    ),
    payload: jsonEncode(message.data),
  );
});
```

The Android channel id here must match a channel you created at startup, and **channel settings are fixed at creation time** — changing importance in code after the channel exists does nothing until the app is reinstalled. Create channels deliberately, and use a new id if you genuinely need different behaviour.

Alternatively, show nothing and update in-app UI instead. For a chat app where the user is already looking at the conversation, an in-place update beats a banner.

## Routing a tap

This is the row most often missed — the terminated case needs a separate call:

```dart
Future<void> setupTapRouting(GoRouter router) async {
  void handle(RemoteMessage message) {
    final type = message.data['type'];
    final id = message.data['id'];
    if (type == 'post' && id != null) router.go('/posts/$id');
  }

  // App was terminated and launched by the notification.
  final initial = await FirebaseMessaging.instance.getInitialMessage();
  if (initial != null) handle(initial);

  // App was backgrounded and resumed by the notification.
  FirebaseMessaging.onMessageOpenedApp.listen(handle);
}
```

`getInitialMessage` returns non-null exactly once, on the launch caused by the tap. Call it after your router exists but before the first frame settles, or the navigation happens against a router that is not ready.

Treat the payload as untrusted input. `router.go(message.data['route'])` with a server-supplied path is a route-injection primitive; map from a small set of known types instead, as above.

## Testing it honestly

Four checks, all worth doing manually at least once per release:

1. Foreground with the app open.
2. Backgrounded with the home button, then tap.
3. **Force-quit** the app (swipe away), then send and tap. This is the case that breaks.
4. Release build, not debug — the `vm:entry-point` failure only shows here.

On iOS, remember that a notification requires a real device with a valid APNs key, uploaded to the Firebase project, plus the Push Notifications and Background Modes capabilities in Xcode. The simulator will not deliver remote pushes.

## FAQ

**Why do notifications work on Android but not iOS?**

Almost always APNs configuration: a missing or wrong key in the Firebase console, or missing Xcode capabilities. The Dart code is rarely at fault.

**Why does my background handler not run in release?**

Missing `@pragma('vm:entry-point')`, or the handler is not top-level. Both work in debug and fail in release.

**Can I run heavy work in the background handler?**

You get a short window and the OS decides. Do the minimum — store the payload, schedule real work for next launch. Long work will be killed.

**Should I use data-only messages for silent updates?**

Only if the update is genuinely optional. Both platforms throttle silent pushes aggressively, and neither guarantees delivery.

**How do I stop duplicate notifications?**

Usually caused by both showing the OS notification and posting a local one for the same message. Show a local notification only in `onMessage`, where the OS shows nothing.

---

*The four delivery paths, the `@pragma('vm:entry-point')` requirement, message-type semantics and Android channel behaviour described here are documented in the Firebase and platform references linked above. The recommendation to send both blocks, the untrusted-payload routing caution, and the four-case manual test list are my own judgement from shipping notification features. FCM's Flutter APIs change between major versions — check the package changelog against your version.*
