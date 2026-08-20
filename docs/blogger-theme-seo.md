# trunghieu-it.blogspot.com — theme and page audit

_Audited 2026-08-20 against the live Screenshot Studio page
(`/p/app-store-screenshot-generator-free-in.html`, theme: Notable Light /
rockpool 1.3.3). Everything marked **done** below was applied on 2026-08-20
through the Blogger UI and verified against the live HTML._

None of this is reachable from the Blogger v3 API: it exposes a page's `title`
and `content` and nothing else — `customMetaData` and `metaDescription` are
accepted and silently dropped (probed, confirmed), and there is no theme API and
no layout API at all. What we *can* do from code is already done by
`scripts/publish_page_to_blogger.py` — see the last section.

## What the page shipped before

| | Measured |
|---|---|
| HTML | 193 KB (~41 KB over the wire) |
| Inline `<style>` blocks | 8, 69,669 bytes total — one is 56 KB (the theme skin) |
| External scripts | 6, including **`adsbygoogle.js` twice** |
| `preconnect` / `dns-prefetch` | **0** |
| `<meta name="description">` | absent |
| `og:description` | present but **empty** |
| `<h1>` | the blog name, on every URL; the page's own title was an `<h3>` |

## Done

### 1. Search descriptions ✅

**Settings → Meta tags → Enable search description** was already on but every
description was empty, so `<meta name="description">` never rendered.

- Blog-level (Settings → Meta tags → Search description), 126/150 chars:
  > Flutter, iOS and Android notes from Hieu — release digests, practical guides, and free browser-based tools for app developers.
- EN page (page editor → Page settings → Search Description), 138/150:
  > Free App Store & Google Play screenshot generator: 24 templates, drop in your screens, export PNGs at exact store sizes. Nothing uploaded.
- VI page, 144/150:
  > Tạo ảnh chụp màn hình App Store & Google Play miễn phí ngay trên trình duyệt: 24 mẫu, xuất PNG đúng kích thước store. Không tải ảnh lên máy chủ.

The box is capped at **150 characters**, which is why these are shorter than the
`META[lang]["description"]` strings in `scripts/publish_page_to_blogger.py` —
those feed JSON-LD, which has no such limit.

Verified: both pages and the homepage now emit `<meta name='description'>` and a
non-empty `og:description`. Saving from the page editor left the body byte-identical
(the studio region diffed to the byte before and after), so the compose-view editor
does not rewrite our markup.

### 2. Resource hints ✅ (Theme → Edit HTML)

Inserted immediately after `<head>`:

```html
<link crossorigin='crossorigin' href='https://fonts.gstatic.com' rel='preconnect'/>
<link href='https://resources.blogblog.com' rel='preconnect'/>
<link href='https://pagead2.googlesyndication.com' rel='preconnect'/>
```

_To revert: delete those three lines._

### 3. Duplicate AdSense loader ✅ (Theme → Edit HTML)

The theme's `<head>` loaded the script protocol-relative while the sidebar
`AdSense1` widget loads it over https in the body. Deleted the theme copy — this
block:

```html
    <b:if cond='(data:widgets.AdSense.any or data:blog.adsenseClientId) and not data:blog.adsenseAutoAds'>
      <script async='async' src='//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js'/>
    </b:if>
```

_To revert: paste that block back just above `<b:include data='blog' name='google-analytics'/>`._
Verified: `adsbygoogle.js` now appears once, and ads still render.

### 4. The page's own `<h1>` ✅ (Theme → Edit HTML)

Only the `Blog1` widget's own `postTitle` includable was touched — not the
`<b:defaultmarkups>` copy, which Popular Posts and Featured Post also use, and
which would otherwise turn every sidebar teaser on an item page into an `<h1>`.
Its body is now wrapped:

```xml
<b:if cond='data:view.isSingleItem'>
  …the original body with <h3 …> → <h1 …>…
<b:else/>
  …the original body, untouched…
</b:if>
```

_To revert: replace the whole includable body with the `<b:else/>` branch._

Verified: item views (both studio pages and a regular post) render
`<h1 class='post-title entry-title'>`; the homepage list is still `<h3>`; the
title still computes to 48px/600 Open Sans, because the theme styles
`.post-title`, not the tag.

The header title is **still** an `<h1>` on every view. Demoting it to a `<div>`
off the homepage would leave the header unstyled — the skin targets the tag
there — and two `<h1>`s on a page is valid HTML5 and explicitly fine with Google,
so it was left alone.

### 5. WebP image serving ✅ (Settings → Posts)

Was off. Turned on — Blogger now serves post images as WebP to browsers that
accept it. `Lazy load images` and `Image lightbox` were already on.

## Not done, and why

### Fonts — the audit's premise was wrong

Blogger already emits `font-display:swap` on all 13 generated `@font-face`
rules, so there is nothing to add. What actually downloads on the studio page is
**7 files, 132 KB**: Lora (4 files, 47 KB) and Open Sans (3 files, 85 KB).

Cutting that means changing which fonts the design uses:

- Lora is the **post body font** (`loraNormal20`, and the source of the drop
  cap). Dropping it changes how every post reads.
- Open Sans loads three weights because the theme uses 400/600/700/800.
  Consolidating to 400/700 would save roughly 30 KB, at the cost of headings
  and buttons rendering bold instead of semibold.

Both are design decisions, not clean wins — say the word and either is a
five-minute change in Theme → Customize → Advanced.

For scale: the page pulls **500 KB** total, of which **284 KB is AdSense**
(three scripts from `pagead2`, the largest 162 KB). Fonts are the second line
item, and everything else is noise. The preconnect added in §2 is the only
lever on the AdSense cost that does not involve removing the ad.

### Duplicate content with fluttercook.github.io — no action (recommended)

Both pages exist twice: here, and at
`https://fluttercook.github.io/tools/screenshot-studio/` (which has canonical,
hreflang, OG, Twitter and JSON-LD). Blogger writes its own
`<link rel='canonical'>` to the Blogger URL and gives no way to point it
elsewhere, so the only two honest options are:

- **Keep both indexed** (recommended, and what is in place). The blog has its
  own audience, the text is genuinely ours on both, and the body already links
  to the canonical copy.
- **Mirror without competing**: page editor → Options → Custom robots tags →
  `noindex, follow`. Traffic then goes only to fluttercook.github.io.

### Trimming the theme skin — skipped

56 KB of the 69 KB of inline CSS is one block, most of it for widgets this blog
does not use. Worth ~10 KB gzipped, and it is the one change here that is hard
to undo by hand, so it wants a theme backup first (Theme → ⋮ → Backup) — which
only you can click.

## Note on backups

The theme edits above were made in place, in the Theme → Edit HTML editor,
without a downloaded backup: the editor's contents cannot be pulled out through
the browser tooling in one piece. Each change is instead recorded above with the
exact string to restore, and Blogger validates theme XML on save, so a malformed
edit is rejected rather than persisted. Before any larger theme work, take a
real backup: **Theme → ⋮ → Backup**.

## Already handled from code

`scripts/publish_page_to_blogger.py` writes into the page body, which is the
only surface the API gives us:

- JSON-LD: `SoftwareApplication`, `FAQPage`, `BreadcrumbList` (~2.9 KB, ~1.3 KB
  gzipped). The FAQ is parsed out of the page's own visible Q/A markup, so the
  two cannot drift apart.
- A cross-language link carrying `hreflang` on the `<a>` — the closest thing to
  hreflang available without head access.
- A footer pointing at the canonical copy on fluttercook.github.io.

The studio widget itself was also made cheaper on this page: it stacks on the
*container* width (the 740 px post column, previously squeezing the stage to
402 px), sizes thumbnail bitmaps from the measured cell, and paints only the
thumbnails near the gallery viewport.
