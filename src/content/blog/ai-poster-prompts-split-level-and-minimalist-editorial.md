---
title: "Two layout systems that make AI posters look designed, not generated"
description: "Split-level composition and photo-to-abstract editorial: two reusable layout frameworks, with fill-in prompt templates and the zone ratios that make them work."
seoDescription: "AI poster design prompts: the split-level layout for exhibition posters and the photo-to-abstract editorial split. Includes zone percentages, colour limits, typography hierarchy and copy-paste templates."
keywords:
  - ai poster prompt
  - split level layout poster
  - editorial design ai prompt
  - minimalist poster prompt
  - exhibition poster ai
  - nano banana poster prompt
  - ai image composition template
category: "Guide"
topic: "AI Design"
level: "Beginner"
author: "Trung Hieu"
publishDate: "2026-08-20"
emoji: "🖼️"
tags: ["AI", "Design", "Prompt Engineering", "Image Generation", "Typography"]
sources:
  - name: "ZzzLc0405/photo-abstract-editorial — skill and prompt for photo-to-abstract posters"
    url: "https://github.com/ZzzLc0405/photo-abstract-editorial"
  - name: "Müller-Brockmann, Grid Systems in Graphic Design"
    url: "https://en.wikipedia.org/wiki/Grid_(graphic_design)"
draft: false
---

Ask an image model for "a poster" and you get a poster-shaped image: picture on top, text at the bottom, both fighting for the same attention, nothing holding them together. It reads as generated because the *composition* is generic, not because the rendering is bad.

The fix isn't a better model. It's giving the model a layout system instead of a subject.

Below are two systems that reliably produce work that looks art-directed. Both come with fill-in templates. Both work in any current image model that accepts long prompts — Nano Banana, Midjourney, Seedream, GPT Image, Flux.

## Why layout instructions beat style adjectives

Most poster prompts are a pile of adjectives: *minimalist, elegant, high-end, professional, award-winning*. Those words push the model toward the average of everything tagged that way in training. Average is exactly what you're trying to escape.

Layout instructions are different. **"The bottom information zone occupies 25–40% of the height"** is a constraint the model can actually satisfy or fail, and it constrains the composition rather than the surface. Say four specific things about structure and you get a specific structure.

The three levers that do the most work:

| Lever | Why it matters |
| --- | --- |
| **Zone proportions** | Unequal splits read as designed; 50/50 reads as a template |
| **Colour count** | An explicit cap (3–5) is the single biggest quality lever |
| **Type hierarchy** | Naming 3–4 distinct text sizes stops the model from making everything medium |

Everything below is built on those three.

## System 1 — Split-level composition

**Good for:** exhibition posters, book covers, cultural and event graphics, anything that needs to feel curated.

The idea sounds obvious — divide the canvas into an upper and lower region — but the version that works has a specific twist. It isn't *"image on top, text below."* It's **two or three unequal zones with different jobs, reconnected by elements that cross the boundary.**

That crossing is the whole trick. A flower stem running through the divide, a title set large enough to straddle it, the subject's shoulder breaking past the line. Without it you have two stacked rectangles. With it you have depth.

### The zone recipe

```text
┌─────────────────────────┐
│                         │
│   MAIN VISUAL ZONE      │  50–65%
│   one hero subject      │
│                         │
├─────────────────────────┤
│  TRANSITIONAL BAND      │  8–15%
├─────────────────────────┤
│  INFORMATION ZONE       │
│  title / date / venue   │  25–40%
│  institution (tiny)     │
└─────────────────────────┘
```

Three things make this work rather than just look tidy:

**The transitional band is not decoration.** It's a narrow strip — a desaturated colour block, a thin band, a row of small info modules — whose job is to be a *third thing* that neither zone owns. Without it, the two zones read as unrelated. It's the visual equivalent of a comma.

**One hero, several whispers.** Keep exactly one primary subject. Then scatter a few low-weight details into the negative space: line drawings, partial sketches, a diagram fragment, vertical text, small annotation marks. These give the empty areas density without competing. This is the difference between "spacious" and "empty."

**The title participates in the composition.** Not a caption sitting under the image — the title is a compositional element. Scale it up, set it vertically, misalign it deliberately, or run it across the zone boundary.

### Template

Fill the brackets, delete the rest of this sentence, paste the whole thing:

```text
[Subject]: ___
[Hero visual]: ___
[Primary title]: ___
[Secondary title / translation]: ___
[Supporting motifs]: ___
[Dominant colour]: ___
[Accent colour]: ___
[Date and venue]: ___
[Aspect ratio]: 9:16

Design a poster in a high-end editorial and cultural-exhibition
idiom, built on a split-level composition.

STRUCTURE — do not produce a plain "image above, text below" layout.
Divide the canvas into three unequal horizontal zones:
- a main visual zone occupying 50-65% of the height
- a narrow transitional band of 8-15%
- an information zone of 25-40%

MAIN ZONE — one hero subject only: [Hero visual]. Add two or three
low-weight secondary marks in the negative space (fine line work, a
partial sketch, a small diagram, vertical lettering) so the empty
areas carry density without competing with the hero.

TRANSITIONAL BAND — connect the two zones using a desaturated colour
block, a thin rule, or a row of small information modules. This band
must belong to neither zone.

TYPE — the primary title is a compositional element, not a caption.
Scale it up, set it vertically, offset it, or let it cross the zone
boundary. Allow part of the hero subject to break past the boundary
as well, so foreground and background separate.

HIERARCHY — four clearly distinct text sizes: large primary title,
then secondary title and date, then a small subtitle, then very small
institutional text. Group the small text tightly; never scatter it.

COLOUR — no more than 5 colours total. [Dominant colour] leads,
[Accent colour] appears in under 10% of the area.

INTENT — each zone has a distinct role, and the zones are reconnected
through the hero subject and the typography. Rich but not cluttered,
open but not empty; the finish of a real museum poster or art catalogue.
```

### Getting it right

- **Nothing crosses the boundary.** Say so explicitly: *"the hero subject must overlap the zone boundary by 10–15% of its height."* Models default to tidy separation.
- **Small text scattered everywhere.** Add: *"all text below the secondary title must sit in a single tight block."*
- **Too many colours.** Lower the cap to 3 and name them.
- **Zones came out equal.** Restate the percentages at the end of the prompt — position bias is real, and the last instruction tends to survive.

## System 2 — Photo to abstract editorial

**Good for:** turning an existing photo into a gallery-style piece. Portraits, architecture, landscape, product shots.

Different structure, same philosophy. The canvas is split into two halves: one keeps the **real photograph**, the other holds an **abstract reduction** of the same subject. Side by side, the pairing reads as intentional in a way either half alone doesn't.

The orientation rule is what makes it robust:

| Source photo | Split |
| --- | --- |
| Landscape | Horizontal — top / bottom, roughly 50:50 |
| Portrait | Vertical — left / right, roughly 50:50 |

This one exception to "avoid 50/50" earns itself: the halves aren't competing, they're the same subject in two registers, so equality reads as a deliberate comparison.

There's an open-source skill implementing this approach at [ZzzLc0405/photo-abstract-editorial](https://github.com/ZzzLc0405/photo-abstract-editorial) if you'd rather have it as a reusable tool than a pasted prompt.

### What each half must do

**The photo half — preserve, don't reinterpret.** This is where most attempts fail. The model wants to stylise, and the moment it does, the pairing collapses. Be blunt: keep the subject's form, proportions, real textures, natural light and shadow, original colour. Grading only — the light touch of contemporary art photography, nothing more. If the frame needs extending to fit, extend only sky, ground or surrounding environment, never the subject.

**The graphic half — reduce to silhouette.** Take the subject's most recognisable outline and rebuild it from clean geometry, flat colour fields, fine lines and generous empty space. No realistic illustration, no fussy detail. The target is *abstract but instantly recognisable*.

**Pull the palette from the photo.** This is the instruction that ties the halves together, and it's the one people forget. Colours sampled from the original image are what make the two halves look like one poster instead of two files.

### Template

```text
Create a high-end minimalist editorial poster from the uploaded photo.
Vertical 3:4 format.

SPLIT — if the source photo is landscape, divide the canvas
horizontally into two roughly equal halves (photo above, graphic
below). If it is portrait, divide vertically into two roughly equal
halves (photo one side, graphic the other).

PHOTO HALF — preserve the original image faithfully: the subject's
form, proportions, real textures, natural lighting and shadow, and
original colours. Apply only restrained professional colour grading,
in the register of contemporary art photography. If the frame must be
extended, extend only sky, ground or surrounding environment. Do not
distort, restyle or alter the subject in any way.

GRAPHIC HALF — reinterpret the subject's most recognisable silhouette
and structure as a simplified abstract composition: clean geometric
forms, flat colour fields, fine lines, generous negative space. No
realistic illustration, no intricate detail. The result must read as
abstract yet remain instantly recognisable as the same subject. Draw
the entire palette from colours sampled in the original photograph.

GROUND — a light neutral background (bone, ivory, warm grey), with
generous margins and a balanced central composition.

TYPE — minimal or none. At most a short title and a year, set small.

DIRECTION — high-end minimalist editorial design, contemporary art
exhibition poster, architectural graphic language, understated luxury,
museum-quality art direction, generous negative space.

AVOID — template layouts, stock-commercial design, cartoon styling,
3D rendering, heavy ornament, gradients, neon, busy illustration, and
any distortion of the photographed subject.
```

### Getting it right

- **Feed it a photo with a clear silhouette.** Reduction needs something to reduce. Busy scenes with no dominant shape produce mush.
- **The abstract half looks like a bad tracing.** Push harder on reduction: *"no more than 5 distinct shapes."*
- **The photo half got stylised.** Move the preservation clause to the end of the prompt and add: *"the photograph must remain photographic."*
- **The halves look unrelated.** Restate the palette instruction, and name two or three colours you can see in the source.

## What transfers to any poster prompt

Strip both systems down and the same four moves are underneath:

**Specify structure before style.** Percentages, zones and counts constrain the model in ways adjectives can't. *"25–40% of the height"* is checkable; *"balanced"* is not.

**Cap the palette.** If you change one thing about how you write image prompts, make it this. Three to five colours, stated as a number, is the highest-leverage instruction in the whole prompt.

**Name the hierarchy explicitly.** Models flatten hierarchy by default because averaged training data is flat. Listing four distinct type sizes forces separation.

**Make elements cross their boundaries.** Depth in a layout comes from things that refuse to stay in their box. It's the single instruction most likely to be missing from a prompt that produced something flat.

## FAQ

**Which image models do these work with?**
Any model that accepts long structured prompts — Nano Banana, Midjourney, Seedream, GPT Image, Flux. Models with stronger text rendering handle the typography hierarchy better; for weaker ones, generate the layout and set the type yourself afterwards.

**Can I use these commercially?**
The layout systems are design conventions, not property — split-level composition predates AI by decades. Check your model's own commercial terms, and check the licence on any code or skill you use.

**How do I get readable text in the poster?**
Keep the wording short, specify the exact string in quotes, and expect to fix it. For anything client-facing, generate the composition and typeset the real text in a design tool over the top.

**Which system for a book cover?**
Split-level. The information zone maps naturally onto title, author and imprint.

**Why does the 50/50 rule flip for system 2?**
Because the halves aren't competing for attention — they're the same subject shown twice. Equality reads as comparison rather than indecision.

---

*The split-level framework here is adapted from a composition breakdown credited to Larus Canus, and the photo-to-abstract approach from one credited to VibeEverything, both circulating in Vietnamese AI design communities. The prompt templates above are rewritten in my own words with the reasoning added; the open-source skill implementing the second system is linked in the sources.*
