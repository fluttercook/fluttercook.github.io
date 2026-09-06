---
title: "In-app purchases in Flutter: the parts that are not about the button"
description: "Wiring up in_app_purchase takes an afternoon. Handling restores, interrupted purchases, refunds, and the receipt validation that stops a modified client from unlocking everything takes considerably longer — and that is the part that matters."
seoDescription: "Flutter in-app purchases with in_app_purchase: the purchase stream, completePurchase, server-side receipt validation, restoring purchases, subscription state, and the failure cases stores test for."
keywords:
  - flutter in app purchase
  - in_app_purchase flutter tutorial
  - flutter receipt validation server
  - flutter restore purchases
  - flutter subscription state
  - flutter completepurchase pending
category: "Guide"
topic: "Flutter"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-08-20"
emoji: "💳"
tags: ["Flutter", "Monetization", "IAP", "Backend", "Mobile"]
sources:
  - name: "in_app_purchase — pub.dev"
    url: "https://pub.dev/packages/in_app_purchase"
  - name: "In-app purchases — Flutter documentation"
    url: "https://docs.flutter.dev/cookbook/in-app-purchases"
  - name: "App Store Server API — Apple developer documentation"
    url: "https://developer.apple.com/documentation/appstoreserverapi"
  - name: "Google Play Developer API — Android developer documentation"
    url: "https://developers.google.com/android-publisher"
  - name: "Real-time developer notifications — Google Play documentation"
    url: "https://developer.android.com/google/play/billing/getting-ready#configure-rtdn"
  - name: "App Store server notifications — Apple developer documentation"
    url: "https://developer.apple.com/documentation/appstoreservernotifications"
related:
  - slug: "flutter-secure-storage-secrets"
    title: "Secrets in a Flutter app: what you can store, and what you cannot"
  - slug: "flutter-error-handling-crash-reporting"
    title: "Flutter error handling: catching what actually reaches users"
draft: false
---

The tutorial version of in-app purchases is a button, a call to `buyNonConsumable`, and a success callback that sets `isPremium = true`. Ship that and you will find out, in order: that users who reinstall lose everything, that a purchase interrupted by a phone call never completes, that a refunded user keeps their access forever, and that anyone with a modified build unlocks the app for free.

None of those are edge cases. They are the normal operating conditions of a payments system.

## The stream is the API

`in_app_purchase` does not work as request-response. Purchases arrive on a stream, including purchases you did not initiate in this session — restores, purchases completed while the app was closed, and purchases from a different device on the same account.

```dart
final class PurchaseService {
  PurchaseService(this._iap, this._backend);

  final InAppPurchase _iap;
  final BackendApi _backend;

  StreamSubscription<List<PurchaseDetails>>? _sub;

  void start() {
    _sub = _iap.purchaseStream.listen(
      _onPurchases,
      onError: (Object e, StackTrace s) => reportError(e, s),
    );
  }

  Future<void> _onPurchases(List<PurchaseDetails> purchases) async {
    for (final purchase in purchases) {
      switch (purchase.status) {
        case PurchaseStatus.pending:
          _showPendingUi();

        case PurchaseStatus.error:
          _showError(purchase.error);
          await _iap.completePurchase(purchase);

        case PurchaseStatus.purchased:
        case PurchaseStatus.restored:
          final valid = await _backend.verify(
            productId: purchase.productID,
            source: purchase.verificationData.source,
            token: purchase.verificationData.serverVerificationData,
          );
          if (valid) await _grantEntitlement(purchase.productID);
          await _iap.completePurchase(purchase);

        case PurchaseStatus.canceled:
          await _iap.completePurchase(purchase);
      }
    }
  }

  void dispose() => _sub?.cancel();
}
```

Two things in there are non-negotiable.

**Start listening before showing any purchase UI**, ideally at app startup. A purchase that completes while nothing is listening is delivered on the next listen — but if you subscribe only when the paywall opens, a purchase completed and then interrupted goes unhandled until the user happens to open the paywall again.

**`completePurchase` must be called for every terminal state**, including errors and cancellations. On iOS, an uncompleted transaction stays in the queue and is redelivered on every launch, forever. Users see the purchase dialog reappear each time they open the app, which generates support tickets and one-star reviews in roughly equal measure.

`PurchaseStatus.pending` is not an error — on Android it covers deferred payment methods where the user pays in cash at a store. The purchase may complete hours later, through the stream, with the app closed in between.

## Validation belongs on your server

The client cannot decide whether a purchase is real. `serverVerificationData` is a token you send to your backend, which then calls Apple's or Google's server API and gets an authoritative answer.

```
App → purchase token → Your backend → App Store / Play API
                            ↓
                     entitlement record
                            ↓
App ← entitlement state ← Your backend
```

Entitlement lives in your database keyed by *your* user id, not by device and not in local storage. That single design choice fixes three problems at once: reinstall works, multi-device works, and a modified client cannot grant itself anything because the server never asked it to.

The reason to do this even for a small app is refunds and cancellations. A user who refunds keeps a valid-looking local receipt indefinitely. Only the store's server knows, and only if you ask — or if you subscribe to **server notifications** (App Store Server Notifications, Play Real-time Developer Notifications), which push refund, cancellation and billing-issue events to you as they happen. For subscriptions these are effectively mandatory; polling every receipt on a schedule is the alternative and it does not scale.

## Restoring

```dart
Future<void> restore() async {
  await _iap.restorePurchases();
  // Results arrive on purchaseStream with status == restored.
}
```

Apple requires a visible restore control for non-consumable products, and reviewers do check. Beyond compliance, it is the escape hatch when your own entitlement sync fails.

Note that restore delivers *every* past non-consumable purchase, so `_grantEntitlement` must be idempotent. Granting twice should be a no-op, not a double credit.

## Consumables need a different shape

For consumables — coins, credits, one-shot boosts — the sequence must be:

1. Receive the purchase.
2. Verify server-side.
3. **Credit the user's balance on the server.**
4. Only then call `completePurchase`.

Complete first and crash before crediting, and the purchase is gone: the store considers it delivered and will not redeliver it. The user paid and received nothing, and the only remedy is manual support.

On Android, also note that a consumable is not repurchasable until it has been consumed, so a bug in this sequence surfaces as "the user cannot buy more coins" rather than as an error.

## Testing without spending money

| Platform | Mechanism | Gotcha |
| --- | --- | --- |
| iOS | StoreKit configuration file in Xcode | Works in simulator; does not exercise the real receipt path |
| iOS | Sandbox account | Subscription durations are compressed — a month may be five minutes |
| Android | License testers in Play Console | Requires an uploaded build on a test track; the app must be installed from Play |
| Both | Server notifications | Test them explicitly; a broken webhook is invisible until a refund happens |

The compressed sandbox durations are useful and misleading in equal measure: renewal logic you tested in five-minute cycles has never been exercised against a real clock or a real timezone boundary.

## Things reviewers reject for

Worth knowing before submission rather than after:

- A paywall with no visible restore option.
- Prices hard-coded in the UI instead of read from `ProductDetails` — stores show local currency, and hard-coded strings will be wrong for most of the world.
- Any mention of an alternative external payment method inside the app, in regions where that is not permitted.
- A subscription without clearly stated duration, price and renewal terms adjacent to the purchase button.

Read prices from `queryProductDetails` and render `product.price`, which is already formatted for the user's storefront.

## FAQ

**Should I use RevenueCat or similar instead?**

If you do not want to build and operate receipt validation and server notifications, yes — that is precisely what they sell. The architecture above is what you are buying.

**Why does a purchase succeed but never reach my listener?**

Usually the subscription was created after the purchase completed, or an exception in the handler killed the stream. Add `onError` and never let the handler throw.

**Can I check subscription status offline?**

Cache the server's answer with an expiry and a grace period. Trust the cache briefly; re-verify on launch and after any resume from background.

**How do I handle a user who subscribes on iOS and opens the Android app?**

Entitlement keyed to your account, not the store. This is one of the strongest arguments for server-side entitlement even in a small app.

**Do I need to handle upgrades and downgrades between subscription tiers?**

Yes, and the platforms model proration differently. Design your entitlement as "which tier is active right now, per the server" rather than as a history of purchases.

---

*The `in_app_purchase` stream model, `completePurchase` semantics, restore behaviour and the existence of store server notifications described here are documented in the references linked above. The server-side entitlement architecture, the consumable ordering rule, the review-rejection list and the caution about compressed sandbox durations are my own judgement from shipping paid apps. Store policies and APIs change frequently — verify current requirements with the platform documentation before submission.*
