# fluttercook.github.io — AdSense and Search Console

_Recorded 2026-08-21. Publisher `pub-5091408807979195`._

## Why the generated recipe pages were pulled out of ads and the index

The 1000 `/recipes/<slug>/` pages (500 EN + 500 VI) are mail-merged from the
GitHub API and pub.dev into one template. That is exactly the shape Google's
Publisher Policies call **low value content**, and it is the single most common
reason a site is rejected. It is not a hypothetical here: **flutter9.blogspot.com**,
in this same AdSense account, is already flagged _Needs attention — Low value
content_ on the same material.

So the monetised surface and the indexed surface were made identical — the
hand-written pages, nothing else:

| | Before | After |
|---|---|---|
| URLs in the sitemap | 1096 | **96** |
| Pages with `noindex, follow` | 0 | **1000** (all recipe details) |
| Pages loading `adsbygoogle.js` | 1096 | **96** — exactly the sitemap set |
| Recipe pages loading ads | 1000 | **0** |

`follow` is deliberate: link equity still flows to the source repos and to our
own hand-written pages. The `/recipes/` and `/vi/recipes/` **index** pages stay
indexed and monetised — those are hubs, not templated detail pages.

**To reverse it:** delete the `ads={false}` and `robots="noindex, follow"` props
from `src/pages/recipes/[...id].astro` and `src/pages/vi/recipes/[...id].astro`,
and drop the `filter` in `astro.config.mjs`. All three must move together — a
sitemap that lists a noindexed URL is a contradictory signal to crawlers.

## Other things the reviewer looks for

- **`src/pages/404.astro`** — GitHub Pages serves one `404.html` for both
  language trees, so it is bilingual. `noindex`, no ads.
- **`about.astro` / `vi/about.astro`** — rewritten to name a real publisher
  (Trung Hieu), state that it is a personal project, that nobody pays to appear,
  and that paid posts and link exchanges are declined. It also says out loud
  which pages are hand-written and which are compiled, and that the compiled ones
  carry `noindex` and no ads. The link to flutter9.blogspot.com was removed —
  that site is the one flagged for low value content.
- **`<meta name="google-adsense-account">`** in `BaseLayout` keeps ownership
  verified even on the pages that do not load the ad script.

## Consent (GDPR)

AdSense → Privacy & messaging → European regulations → **"FlutterCook — EEA/UK
consent"**, site `fluttercook.github.io`, status **Published** (2026-08-21).
Privacy policy `https://fluttercook.github.io/privacy/`, logo `public/logo.png`.

**"Do not consent" is On for every EEA country** — several EEA regulators require
a reject as prominent as accept. English only; the additional-language list is
EEA languages, so Vietnamese is not on offer.

Not attached to the message: trunghieu-it.blogspot.com and flutter9.blogspot.com.
Neither has a privacy policy URL, and a half-configured message is worse than a
missing one. **trunghieu-it serves ads to EEA visitors with no consent message
today** — that is an open gap, not a decision.

Still unset: the US state regulations (CCPA) message.

## Search Console

The property is a **URL prefix** property for `https://fluttercook.github.io/`,
verified 2026-08-21 by **HTML tag**.

A *Domain* property for `fluttercook.github.io` was started first. It cannot be
finished: a Domain property only verifies through a DNS TXT record, and the
`github.io` zone belongs to GitHub. Its token (`w5g-9sSX…`) is therefore useless
to us and is **not** the one in the page head. Google Analytics verification also
fails — the GA property behind `G-B299VQ6G9N` lives in a different Google account
("The tracking code used by your site is not associated with your Google
Analytics account"). The dead Domain property is still listed and can be removed
from the property picker.

The live token is `2ycDQu9CC…`, in `src/layouts/BaseLayout.astro`. **Do not remove
it** — Search Console re-checks periodically and unverifies the property if the
tag disappears.

`sitemap-index.xml` was submitted 2026-08-21. It still reads _Couldn't fetch_
from the failed Jul 17 attempt (made before the property was verified); the file
itself returns `200 application/xml` and Google refetches on its own schedule.

## Social cards

`og:image` used to be `/og-default.svg`. Facebook, LinkedIn, Slack and X all
refuse to render an SVG card, so every share looked like a bare link. It is now
`/og-default.png` (1200×630) with `og:image:width/height/alt`. The JSON-LD
`publisher.logo` on 1054 pages moved from that SVG banner to `/logo.png`
(600×120) — Google's structured-data docs accept png/jpg/gif only, and want a
logo rather than a hero image. Both PNGs are rendered from SVG with
`rsvg-convert`; the sources are inline in this repo's history.
