---
title: "Secrets in a Flutter app: what you can store, and what you cannot"
description: "Every string compiled into your app is readable by anyone who downloads it. That single fact decides which secrets belong on the device, which belong on a server, and what flutter_secure_storage is actually for."
seoDescription: "Flutter secrets handling: why dart-define is not secret, Keychain and Keystore via flutter_secure_storage, token refresh patterns, certificate pinning, and a threat model that holds up."
keywords:
  - flutter secure storage
  - flutter api key security
  - flutter keychain keystore
  - flutter token refresh storage
  - flutter certificate pinning
  - flutter dart-define not secret
category: "Guide"
topic: "Flutter"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-22"
emoji: "🔐"
tags: ["Flutter", "Security", "Storage", "Authentication", "Mobile"]
sources:
  - name: "flutter_secure_storage — pub.dev"
    url: "https://pub.dev/packages/flutter_secure_storage"
  - name: "Keychain Services — Apple developer documentation"
    url: "https://developer.apple.com/documentation/security/keychain_services"
  - name: "Android Keystore system — Android developer documentation"
    url: "https://developer.android.com/privacy-and-security/keystore"
  - name: "OAuth 2.0 for Native Apps (RFC 8252)"
    url: "https://datatracker.ietf.org/doc/html/rfc8252"
  - name: "SecurityContext — Dart API"
    url: "https://api.dart.dev/stable/dart-io/SecurityContext-class.html"
  - name: "App security best practices — Android developer documentation"
    url: "https://developer.android.com/privacy-and-security/security-tips"
related:
  - slug: "flutter-flavors-build-config"
    title: "Flutter flavors: one codebase, three apps, zero copy-pasted config"
  - slug: "flutter-error-handling-crash-reporting"
    title: "Flutter error handling: catching what actually reaches users"
draft: false
---

Start with the uncomfortable part, because everything else follows from it.

**Any string compiled into your app is public.** Not "hard to find" — public. An APK is a zip file; `strings` on the extracted binary takes seconds. `--dart-define` values, constants, obfuscated names, base64-encoded blobs: all of it is recoverable by anyone motivated enough to download your app once.

This is not a Flutter weakness. It is true of every client application on every platform. What it changes is where you draw the line between "the app knows this" and "the app can ask for this".

## The line

| Kind of secret | Where it belongs |
| --- | --- |
| Third-party API key with billing attached | Server only. The app calls your backend, your backend calls them |
| Public/publishable keys (Stripe publishable, Firebase config, Maps key) | In the app — they are designed for it, and restricted server-side |
| User session token | Device secure storage, short-lived, refreshable |
| Refresh token | Device secure storage, revocable server-side |
| Encryption key for local data | Derived or generated on-device, stored in Keychain/Keystore |
| Signing keys, service accounts | Never in the repository, never in the app |

The Firebase row surprises people. `google-services.json` is not a secret — its contents are visible in any app that ships it, and Firebase's security model is built on server-side Security Rules, not on hiding the config. If your Firestore is protected only by the config file being "hidden", it is not protected.

The general test: if leaking the value lets an attacker do something *as you* rather than *as themselves*, it cannot live on the device.

## Using platform secure storage

`flutter_secure_storage` wraps iOS Keychain and Android's `EncryptedSharedPreferences` behind one API:

```dart
final class TokenStore {
  TokenStore(this._storage);

  final FlutterSecureStorage _storage;

  static const _accessKey = 'access_token';
  static const _refreshKey = 'refresh_token';

  Future<void> save({
    required String access,
    required String refresh,
  }) async {
    await Future.wait([
      _storage.write(key: _accessKey, value: access),
      _storage.write(key: _refreshKey, value: refresh),
    ]);
  }

  Future<String?> readAccess() => _storage.read(key: _accessKey);
  Future<String?> readRefresh() => _storage.read(key: _refreshKey);

  Future<void> clear() => _storage.deleteAll();
}
```

Configure the platform options explicitly rather than accepting defaults:

```dart
final storage = FlutterSecureStorage(
  aOptions: const AndroidOptions(encryptedSharedPreferences: true),
  iOptions: const IOSOptions(
    accessibility: KeychainAccessibility.first_unlock_this_device,
  ),
);
```

Two choices worth understanding.

**`first_unlock_this_device`** means the value is readable after the first unlock following a reboot, and — the important half — is *not* included in iCloud Keychain or device backups. A token that syncs to a second device is a token that outlives the device the user thinks they revoked.

**`encryptedSharedPreferences: true`** on Android uses the Keystore-backed implementation rather than plain shared preferences. Without it, "secure" storage on some configurations is considerably less secure than the name implies.

## The uninstall asymmetry

A behaviour that produces confusing bug reports: on Android, uninstalling clears app storage. On iOS, **Keychain items can survive an app uninstall and reinstall**. A user who deletes the app to "sign out and start fresh" may reinstall and find themselves still logged in, or worse, holding a token for an account they no longer own on a resold device.

The fix is a first-run marker in ordinary preferences, which *do* get cleared:

```dart
Future<void> clearSecureStorageOnFirstRun() async {
  final prefs = await SharedPreferences.getInstance();
  if (prefs.getBool('has_run_before') ?? false) return;

  await storage.deleteAll();
  await prefs.setBool('has_run_before', true);
}
```

Call it before reading any token. It costs one read on every launch and removes an entire class of "impossible" session bugs.

## Tokens: short-lived, refreshed, revocable

The storage is the easy half. The design that makes storage survivable is short access-token lifetimes plus server-side revocation:

```dart
final class AuthInterceptor extends Interceptor {
  AuthInterceptor(this._store, this._api);

  final TokenStore _store;
  final AuthApi _api;

  Future<void>? _refreshInFlight;

  @override
  Future<void> onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode != 401) return handler.next(err);

    // Collapse concurrent refreshes into one.
    _refreshInFlight ??= _doRefresh();
    try {
      await _refreshInFlight;
    } finally {
      _refreshInFlight = null;
    }

    final token = await _store.readAccess();
    if (token == null) return handler.next(err);

    final retried = await _api.retry(err.requestOptions, token);
    handler.resolve(retried);
  }

  Future<void> _doRefresh() async {
    final refresh = await _store.readRefresh();
    if (refresh == null) return;
    final tokens = await _api.refresh(refresh);
    await _store.save(access: tokens.access, refresh: tokens.refresh);
  }
}
```

The `_refreshInFlight` collapsing is not an optimisation. Without it, five parallel requests hitting a 401 trigger five refreshes; if the server rotates refresh tokens on use, four of them fail and the user is logged out. This is one of the most common real-world auth bugs in mobile apps.

For login itself, RFC 8252 is unambiguous: use the system browser with PKCE, not an embedded webview. An embedded webview can read the user's credentials, which is exactly why identity providers increasingly refuse to render in one.

## What pinning does and does not buy

Certificate pinning stops an attacker with a trusted-CA-installed device from reading your traffic. It does not stop an attacker who controls the device — they can patch the check out.

```dart
final client = HttpClient(
  context: SecurityContext(withTrustedRoots: false)
    ..setTrustedCertificatesBytes(pemBytes),
);
```

If you pin, pin to an intermediate or a public key rather than a leaf certificate, ship at least one backup pin, and have a remote kill switch. A pinned app whose certificate rotates unexpectedly is an app that stops working for every user simultaneously, and the fix requires a store review. I have seen that outage; it is worse than the threat pinning addressed.

## FAQ

**Does obfuscation (`--obfuscate --split-debug-info`) protect my keys?**

It renames identifiers. String literals remain string literals. It raises reverse-engineering cost slightly and protects nothing on its own.

**Is `flutter_secure_storage` enough for offline-first apps with sensitive local data?**

Store the *encryption key* there, and encrypt the database with it — for example SQLCipher via `sqflite_sqlcipher`. Putting megabytes of records into Keychain is not what it is for.

**How do I keep a third-party key out of the app but still call the service?**

Proxy through your backend. The app authenticates to you; you authenticate to them. This also gives you rate limiting and the ability to rotate the key without a release.

**Can I detect a rooted or jailbroken device?**

Partially, and it is an arms race. Treat it as a signal for risk scoring on your server, never as a client-side gate you rely on.

**What about biometric-gated storage?**

`IOSOptions` and `AndroidOptions` support requiring user presence. It is a real improvement for high-value actions, and a real friction cost — apply it to the payment confirmation, not to every app launch.

---

*The Keychain and Keystore behaviours, `flutter_secure_storage` options, RFC 8252's guidance on native-app OAuth, and `SecurityContext` API described here are documented in the references linked above. The where-secrets-belong table, the first-run cleanup pattern, the refresh-collapsing interceptor and the caution about pinning outages are my own judgement from shipping and debugging these systems. Security defaults change between package and OS versions — verify the options against the versions you actually depend on.*
