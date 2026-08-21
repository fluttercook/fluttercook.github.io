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

A second message, **"trunghieu-it — EEA/UK consent"**, covers
`trunghieu-it.blogspot.com` and is **Published** (2026-08-21). Same "Do not
consent" On for every EEA country, privacy policy
`https://trunghieu-it.blogspot.com/p/privacy-policy.html` (the English one — the
message only ever shows to EEA/UK/CH readers), logo
`blogger/assets/trunghieu-it-logo.png`. AdSense *requires* a logo per site, and
the blog ships no wordmark, so that PNG is generated from
`trunghieu-it-logo.svg` using the blog theme's own colours (`#25a186` on
`#292929`); regenerate it with the `rsvg-convert` line in the SVG's comment.
This one carries English plus **23 EEA languages** — a consent has to be
understood to be valid, and the default-language-only setup leaves a French or
Polish reader with an English dialog.

Still not attached to any message: flutter9.blogspot.com. It has no privacy
policy URL, and it is also the site flagged for low value content.

Still unset: the US state regulations (CCPA) message.

## Site approval and ads.txt

`fluttercook.github.io` is **Getting ready** in AdSense → Sites, not yet Ready.
Ownership is verified and the review was requested **21 Aug 2026 13:48**; Google
says a few days, up to 2-4 weeks. Until it flips to Ready, ads do not serve: the
Auto ads script loads, injects an `<ins class="adsbygoogle">` and calls
doubleclick, and the slot comes back `data-ad-status="unfilled"` at 0x0. That is
the expected pre-approval state, not a bug — nothing needs redeploying when the
review passes.

Auto ads and Auto optimize are **On** for the site. There are no hand-placed
`<ins>` units anywhere in `src/`; every placement comes from Auto ads, which only
runs where `BaseLayout` loads the script — so the 1000 `/recipes/` detail pages
and 404 stay ad-free by construction.

`public/ads.txt` carries the one DIRECT line for `pub-5091408807979195` plus
`OWNERDOMAIN` and `CONTACT` variable records (IAB Tech Lab v1.1). Two things to
know:

- Crawlers fetch **lowercase** `/ads.txt` only. GitHub Pages is case-sensitive,
  so `/Ads.txt` returns 404. That is correct; do not add a second copy.
- The Sites list read _ads.txt: Not found_ on 2026-08-21 because the crawl ran at
  13:48 and the file first went live at 14:37 (commit `0f03734`). Stale, not
  broken — `trunghieu-it.blogspot.com` already reads _Authorized_, which proves
  the crawler reads these fine.

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
