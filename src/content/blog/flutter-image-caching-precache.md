---
title: "The Flutter image pipeline: from a URL to pixels on screen"
description: "Image.network hides five distinct stages — key, fetch, decode, cache, paint. Every image bug you have (flicker on rebuild, blank on scroll back, memory spikes) is one specific stage misbehaving."
seoDescription: "How Flutter loads images: ImageProvider and cache keys, memory vs disk caching, cacheWidth and ResizeImage, precacheImage, placeholders and fade-in, error and retry handling, and gallery patterns."
keywords:
  - flutter image caching
  - flutter precacheimage usage
  - flutter cached_network_image
  - flutter imageprovider resize
  - flutter image flicker rebuild
  - flutter image error builder
category: "Deep Dive"
topic: "Flutter"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-29"
emoji: "🖼️"
tags: ["Flutter", "Images", "Caching", "Performance", "UI"]
sources:
  - name: "ImageProvider — Flutter API"
    url: "https://api.flutter.dev/flutter/painting/ImageProvider-class.html"
  - name: "ImageCache — Flutter API"
    url: "https://api.flutter.dev/flutter/painting/ImageCache-class.html"
  - name: "precacheImage — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/precacheImage.html"
  - name: "ResizeImage — Flutter API"
    url: "https://api.flutter.dev/flutter/painting/ResizeImage-class.html"
  - name: "Image — Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/Image-class.html"
  - name: "cached_network_image package"
    url: "https://pub.dev/packages/cached_network_image"
related:
  - slug: "flutter-memory-leaks-devtools"
    title: "Finding a Flutter memory leak: the five objects that never get disposed"
  - slug: "flutter-lists-performance-builder"
    title: "Why your ListView is slow, and the four fixes that actually work"
draft: false
---

`Image.network(url)` is one of the friendliest APIs in Flutter and one of the easiest to be defeated by. It works immediately, and then a month later you have images that flash white on every rebuild, a gallery that reloads on scroll-back, and 400 MB of memory on a device with 3 GB.

All three are the same misunderstanding: `Image` is a widget, but the caching and decoding happen in an object it delegates to — the `ImageProvider`. Knowing what that object keys on, and what it caches, explains everything.

## The five stages

1. **Key.** The `ImageProvider` produces a key — for `NetworkImage`, the URL plus scale. Two providers with equal keys are the same image as far as the cache is concerned.
2. **Fetch.** Bytes come from the network, an asset bundle, a file, or memory.
3. **Decode.** Compressed bytes become a `dart:ui.Image`: raw pixels, `width × height × 4` bytes.
4. **Cache.** The decoded image goes into `PaintingBinding.instance.imageCache`, keyed on step 1.
5. **Paint.** The widget draws it, applying `fit`, `alignment`, and any colour filter.

The single most important consequence: **the cache stores decoded pixels, and it is keyed on the provider, not the widget**. A widget that rebuilds does not re-download; a widget whose provider key changes does.

## Why an image flickers on rebuild

```dart
// Rebuilds create an equal NetworkImage — this is fine.
Image.network(user.avatarUrl)

// A new provider identity every build — also usually fine, because
// NetworkImage implements == on (url, scale).
Image(image: NetworkImage(user.avatarUrl))

// Not fine: the key changes when `size` changes, so it re-decodes.
Image(image: ResizeImage(NetworkImage(url), width: size.round()))
```

`NetworkImage` and its siblings implement `==` and `hashCode` over their inputs, so constructing a new one each build hits the same cache entry. The flicker cases are the ones where something in the key genuinely changes: a URL with a cache-busting query parameter, a signed URL whose token rotates, or a `ResizeImage` whose dimensions come from a layout that changes by a pixel.

Fix the key, not the widget. Strip volatile query parameters before building the provider, and round `ResizeImage` dimensions to a stable bucket rather than passing raw layout constraints.

## Decode size is the memory lever

This is worth stating on its own because it dominates every other consideration in a media app:

| Source | Disk | Decoded in memory |
| --- | --- | --- |
| 4000×3000 JPEG | ~2 MB | ~48 MB |
| 1200×900 JPEG | ~300 KB | ~4.3 MB |
| 400×300 thumbnail | ~40 KB | ~0.5 MB |

If you display a 400-pixel-wide thumbnail from a 4000-pixel source, you are paying about a hundred times the memory you need. `cacheWidth` and `cacheHeight` change the decode itself:

```dart
Image.network(url, cacheWidth: 400, width: 200, fit: BoxFit.cover)
```

Note the two numbers. `width: 200` is layout — logical pixels. `cacheWidth: 400` is decode — physical pixels, so roughly logical width × device pixel ratio. Passing the logical width to `cacheWidth` produces a blurry image on a 2x or 3x screen; passing the source width defeats the purpose.

```dart
final dpr = MediaQuery.devicePixelRatioOf(context);
Image.network(url, cacheWidth: (200 * dpr).round(), width: 200)
```

`ResizeImage` is the same mechanism as an explicit provider, useful when you are composing providers rather than using the `Image` constructor.

## Memory cache versus disk cache

Flutter's built-in `ImageCache` is **memory only**. There is no disk layer: kill the app and every network image is fetched again. It is also bounded, and the defaults are modest — a maximum entry count and a maximum byte budget, both of which you can raise or lower:

```dart
PaintingBinding.instance.imageCache
  ..maximumSize = 200
  ..maximumSizeBytes = 100 << 20;
```

Raising these makes a gallery smoother and makes an OOM kill more likely. Lower them on a memory-constrained target rather than raising them everywhere by default.

For persistence across launches, you need a package. `cached_network_image` is the common choice and gives you a disk cache, a `placeholder`, an `errorWidget`, and a `memCacheWidth`/`maxWidthDiskCache` pair that mirrors `cacheWidth`:

```dart
CachedNetworkImage(
  imageUrl: url,
  memCacheWidth: 800,
  placeholder: (context, url) => const _ShimmerBox(),
  errorWidget: (context, url, error) => const Icon(Icons.broken_image),
  fadeInDuration: const Duration(milliseconds: 150),
)
```

The trade-off is honest: a disk cache means a directory that grows, an eviction policy you should configure, and stale images if your URLs are not content-addressed. If your image URLs contain a hash or version, disk caching is nearly free; if they are mutable paths like `/avatars/42.jpg`, you need a cache-busting strategy or users will see old avatars indefinitely.

## `precacheImage`, and when it helps

```dart
@override
void didChangeDependencies() {
  super.didChangeDependencies();
  precacheImage(const AssetImage('assets/hero.webp'), context);
}
```

`precacheImage` resolves and decodes an image into the cache before it is displayed, so the widget that eventually shows it paints immediately instead of fading in. It is genuinely useful in three places:

- The **hero image of the next screen**, precached while the user is still on the current one.
- **Onboarding slides**, precached during the first slide.
- **Assets on the critical path**, precached during a splash — with the caveat from startup profiling that this adds to time-to-first-frame if you await it.

It is not useful, and is actively harmful, when applied to a list: precaching forty images means decoding forty images, which is the memory spike you were trying to avoid. Precache what you are about to show, not what the user might scroll to.

Note that `precacheImage` needs a `BuildContext` and is therefore not callable from `initState` directly — `didChangeDependencies` is the usual place.

## Placeholders, fades, and layout stability

The visible quality of an image-heavy screen is mostly about what happens *before* the image arrives.

**Reserve the space.** An image that arrives and pushes content down is the most noticeable UI defect there is. If you know the aspect ratio, wrap in `AspectRatio`; if you know the size, give it one. If you know neither, ask the API — most media APIs return dimensions, and using them is the difference between a stable and a jumping list.

**Fade, briefly.** `FadeInImage` and the `frameBuilder` on `Image` both let you cross-fade from a placeholder. Keep it short — 100–200 ms. A long fade reads as slowness.

```dart
Image.network(
  url,
  frameBuilder: (context, child, frame, wasSynchronouslyLoaded) {
    if (wasSynchronouslyLoaded) return child;
    return AnimatedOpacity(
      opacity: frame == null ? 0 : 1,
      duration: const Duration(milliseconds: 150),
      child: child,
    );
  },
)
```

`wasSynchronouslyLoaded` is the detail people miss: an image already in the cache paints on the first frame, and fading it in makes cached images look slower than uncached ones on the second visit.

**Handle failure.** `errorBuilder` is not optional in a real app — networks fail, URLs 404, and the default is an exception in the console plus an empty box.

```dart
Image.network(
  url,
  errorBuilder: (context, error, stack) => const _AvatarFallback(),
)
```

Retry is worth thinking about too. The built-in `Image` does not retry; `cached_network_image` and similar packages give you a retry hook, or you can force one by changing the provider key.

## Gallery patterns that hold up

For a grid or a feed, four rules cover most of it:

1. `cacheWidth` sized to the cell, not the source.
2. `GridView.builder` / `ListView.builder`, so off-screen cells are not built.
3. A bounded `imageCache` chosen for the worst device you support.
4. Full-resolution decode **only** on the detail screen, from a separate URL if the API offers one.

The last one is the difference between a gallery that works on a 2 GB device and one that does not. A grid should never decode the image the detail view shows.

## FAQ

**Does `Image.network` cache to disk?**

No. The framework cache is memory-only and does not survive a restart. Use a package for disk caching.

**Why is my asset image still loading slowly?**

Assets are read from the bundle, which is fast, but decode still costs. A huge PNG asset decodes just as slowly as a huge network one — `cacheWidth` applies to assets too.

**What clears the image cache?**

`imageCache.clear()` empties it; `imageCache.evict(provider)` removes one entry, which is the correct way to force a reload of a specific image after an upload.

**Should I raise `maximumSizeBytes`?**

Only after measuring, and only with a device floor in mind. It trades smoothness for OOM risk, and the risk falls on your lowest-end users, who are the least likely to report it.

**`Image.asset` versus `SvgPicture`?**

Vector assets avoid the resolution problem entirely and are tiny on disk, at the cost of runtime rasterisation on every distinct size. For icons and flat illustrations, vectors are usually the better trade; for photographs they are not an option.

---

*The provider, cache, `precacheImage` and `ResizeImage` behaviours described here are documented in the Flutter painting and widget API references linked above. The stage framing, the decode-size table (arithmetic from width × height × 4), the precaching guidance and the gallery rules are my own judgement from building media-heavy screens. Cache defaults and package APIs change between versions — verify against the SDK and packages you ship.*
