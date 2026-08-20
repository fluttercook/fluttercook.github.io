# trunghieu-it.blogspot.com — theme and page audit

_Measured 2026-08-20 against the live Screenshot Studio page
(`/p/app-store-screenshot-generator-free-in.html`, theme: Notable / rockpool)._

Everything in this file needs the **Blogger UI**. The Blogger v3 API exposes a
page's `title` and `content` and nothing else: `customMetaData` and
`metaDescription` are accepted and silently dropped (probed, confirmed), and
there is no theme API and no layout API at all. Whatever we *can* do from code
is already done by `scripts/publish_page_to_blogger.py` — see the list at the
bottom.

## What the page ships today

| | Measured |
|---|---|
| HTML | 193 KB (~41 KB over the wire) |
| Inline `<style>` blocks | 8, 69,669 bytes total — one is 56 KB (the theme skin) |
| External scripts | 6, including **`adsbygoogle.js` twice** |
| `preconnect` / `dns-prefetch` | **0** |
| Fonts | 5 TTFs from fonts.gstatic.com (4 Open Sans weights + Lora) |
| `<meta name="description">` | absent |
| `og:description` | present but **empty** |
| `og:image`, Twitter card | absent |
| `<h1>` | the blog name, on every page; the page's own title is an `<h3>` |

## Fixes, most value first

### 1. Turn on search descriptions (Settings, 2 minutes)

**Settings → Meta tags → Enable search description → On**, then write the blog
description. Only after that does the per-page **Search description** box appear
(page editor → right sidebar → Search description). Fill it with:

*EN page:*

> Free browser-based App Store and Google Play screenshot generator: pick one of 24 templates, drop in your app screens, write captions and export PNGs at the exact store sizes. Nothing is uploaded.

*VI page:*

> Công cụ tạo ảnh chụp màn hình App Store và Google Play miễn phí, chạy ngay trong trình duyệt: chọn 1 trong 24 mẫu, thả ảnh màn hình ứng dụng, viết caption và xuất PNG đúng kích thước store. Không tải ảnh lên máy chủ.

This is what fills both `<meta name="description">` and the empty
`og:description` — it is the single highest-value change on this list, and it is
the one thing the API cannot do for us.

### 2. Resource hints (Theme → Edit HTML)

There are none today, and the first font request cannot start until the CSS that
references it has parsed. Paste immediately after `<head>`:

```html
<link crossorigin='crossorigin' href='https://fonts.gstatic.com' rel='preconnect'/>
<link href='https://resources.blogblog.com' rel='preconnect'/>
<link href='https://pagead2.googlesyndication.com' rel='preconnect'/>
```

### 3. Drop the duplicate AdSense loader (Theme → Edit HTML)

The page loads the same script twice, once protocol-relative and once over
https:

```
//pagead2.googlesyndication.com/pagead/js/adsbygoogle.js      <- delete this one
https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js
```

Search the theme for `pagead2` and delete the `<script>` whose `src` starts with
`//`. Keep the `https://` one and make sure it carries `async`.

### 4. Cut the font payload (Theme → Customize → Advanced)

Five TTF files load on every page. Open Sans is used at four weights and Lora
appears to be used only for the drop cap. Reduce to two Open Sans weights
(400/700), and drop Lora if you are happy losing the serif accent. Blogger
serves these as `@font-face` inside the theme skin; if you edit the skin
directly, add `font-display: swap` so text paints before the font arrives.

### 5. Give the page its own `<h1>` (Theme → Edit HTML)

Right now every URL on the blog has the same `<h1>` — *Hola, I'm Hieu, a
Software Engineer* — while the actual page title sits in `<h3 class='post-title'>`.
Search the theme for `post-title` and for the header title widget, then:

- make the post/page title an `<h1>` on item views,
- demote the header title to a `<div>` (or `<h1>` only on the homepage):

```html
<b:if cond='data:view.isHomepage'>
  <h1 class='title'><data:title/></h1>
<b:else/>
  <div class='title'><data:title/></div>
</b:if>
```

### 6. Decide on the duplicate with fluttercook.github.io

Both pages exist twice: here, and at
`https://fluttercook.github.io/tools/screenshot-studio/` (which has canonical,
hreflang, OG, Twitter and JSON-LD). Blogger writes its own
`<link rel='canonical'>` to the Blogger URL and gives no way to point it at
another domain, so there are only two honest options:

- **Keep both indexed** (recommended). The blog has its own audience, the text
  is genuinely ours on both, and the body already links to the canonical copy.
  Worst case Google prefers one of them.
- **Mirror without competing**: page editor → Custom robots tags →
  `noindex, follow`. Traffic then goes only to fluttercook.github.io.

### 7. Optional: trim the theme skin

56 KB of the 69 KB of inline CSS is one block, most of it for widgets this blog
does not use. Worth doing only with a copy of the theme saved first — the
savings are ~10 KB gzipped, well behind items 1–4.

## Already handled from code

`scripts/publish_page_to_blogger.py` writes into the page body, which is the
only surface the API gives us:

- JSON-LD: `SoftwareApplication`, `FAQPage`, `BreadcrumbList` (~2.9 KB, ~1.3 KB
  gzipped). The FAQ is parsed out of the page's own visible Q/A markup, so the
  two cannot drift apart.
- A cross-language link carrying `hreflang` on the `<a>` — the closest thing to
  hreflang available without head access.
- A footer pointing at the canonical copy on fluttercook.github.io.

The studio widget itself was also made cheaper on this page: it now stacks on
the *container* width (the 740 px post column, previously squeezing the stage to
402 px), sizes thumbnail bitmaps from the measured cell, and paints only the
thumbnails near the gallery viewport.
