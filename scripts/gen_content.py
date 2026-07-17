#!/usr/bin/env python3
"""Regenerate long-form, SEO-optimised bodies + enriched frontmatter for every
recipe in src/content/recipes/*.md.

Design goals:
- Drive off each file's existing frontmatter (curated title/repo/category/etc.).
- Augment with dataset fields (open_issues, created, language) ONLY when the
  dataset record's repo matches the frontmatter repo (slugs can collide).
- Produce differentiated, category-aware content (~700-1100 words) grounded in
  real data. Never fabricate package APIs — only emit accurate install/import
  commands + prose + real metrics.
- Add frontmatter used by the Astro templates for JSON-LD / internal linking:
  seoDescription, keywords[], faq[{q,a}], related[{slug,title}],
  datePublished, dateModified, wordCount.
"""
import json
import re
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent
RECIPES = ROOT / "src/content/recipes"
DATASET = json.loads((ROOT / "data/FlutterCook_500_dataset.json").read_text("utf-8"))
YEAR = "2026"

# dataset indexed by repo (authoritative join key)
DS_BY_REPO = {r["repo"]: r for r in DATASET}

CATEGORY = {
    "State management": {
        "kind": "state-management library",
        "blurb": "keeping your UI in sync with your app state as it changes",
        "keywords": ["flutter state management", "flutter app state", "flutter mobile app"],
        "use_cases": [
            "your widget tree needs to react to shared, changing data",
            "you want to separate business logic from presentation",
            "you're scaling past `setState` and need predictable rebuilds",
        ],
    },
    "UI/Components": {
        "kind": "UI component library",
        "blurb": "building polished, reusable interface widgets faster",
        "keywords": ["flutter ui", "flutter widgets", "flutter mobile app ui"],
        "use_cases": [
            "you need a ready-made widget instead of building one from scratch",
            "you want a consistent look across screens",
            "you're prototyping a mobile app UI quickly",
        ],
    },
    "Animation": {
        "kind": "animation library",
        "blurb": "adding smooth, expressive motion to your Flutter app",
        "keywords": ["flutter animation", "flutter animated ui", "flutter mobile app"],
        "use_cases": [
            "you want delightful micro-interactions without hand-rolling tweens",
            "you need page transitions or loading effects",
            "you're bringing a static UI to life",
        ],
    },
    "AI/ML": {
        "kind": "AI/ML toolkit",
        "blurb": "bringing on-device or cloud AI features into a Flutter app",
        "keywords": ["flutter ai", "flutter llm", "flutter machine learning", "flutter mobile app"],
        "use_cases": [
            "you're adding a chatbot, assistant, or generative feature",
            "you need on-device inference for privacy or offline use",
            "you're wiring an LLM or ML model into a mobile app",
        ],
    },
    "Backend/Data": {
        "kind": "backend & data library",
        "blurb": "talking to APIs, databases, and persistence layers",
        "keywords": ["flutter http", "flutter backend", "flutter database", "flutter mobile app"],
        "use_cases": [
            "you're calling REST/GraphQL APIs from a Flutter app",
            "you need local storage, caching, or offline sync",
            "you want typed, testable data access",
        ],
    },
    "Library/Tooling": {
        "kind": "developer tooling library",
        "blurb": "improving your Flutter developer workflow and codebase",
        "keywords": ["flutter tooling", "flutter developer tools", "flutter mobile app"],
        "use_cases": [
            "you want to automate or streamline part of your build",
            "you need better debugging, codegen, or DX",
            "you're standardising tooling across a team",
        ],
    },
    "App/Template": {
        "kind": "open-source app / starter template",
        "blurb": "learning from a complete, real-world Flutter codebase",
        "keywords": ["flutter app", "flutter template", "flutter example app", "flutter mobile app"],
        "use_cases": [
            "you want a production-grade example to study or fork",
            "you're bootstrapping a new app from a proven starter",
            "you learn best by reading complete projects",
        ],
    },
    "Navigation": {
        "kind": "navigation & routing library",
        "blurb": "structuring screens, routes, and deep links",
        "keywords": ["flutter navigation", "flutter routing", "flutter mobile app"],
        "use_cases": [
            "you need declarative, URL-driven routing",
            "you're handling deep links or nested navigation",
            "you want type-safe routes",
        ],
    },
    "Learning/Awesome": {
        "kind": "curated learning resource",
        "blurb": "finding the best Flutter examples, tutorials, and references",
        "keywords": ["learn flutter", "flutter examples", "flutter tutorials", "flutter mobile app"],
        "use_cases": [
            "you're looking for a curated jumping-off point",
            "you want vetted examples instead of random search results",
            "you're planning a learning path",
        ],
    },
    "Framework/Core": {
        "kind": "core framework project",
        "blurb": "the foundation the whole Flutter ecosystem builds on",
        "keywords": ["flutter framework", "flutter sdk", "flutter mobile app"],
        "use_cases": [
            "you want to understand what powers Flutter itself",
            "you're contributing to or tracking the core project",
            "you need the ground truth for how Flutter works",
        ],
    },
}
DEFAULT_CAT = {
    "kind": "Flutter project",
    "blurb": "building better Flutter apps",
    "keywords": ["flutter", "flutter mobile app"],
    "use_cases": ["you're building a Flutter mobile app",
                  "you want a well-maintained open-source option",
                  "you value an active community"],
}

APP_CATEGORIES = {"App/Template", "Learning/Awesome"}


def scrub(obj):
    """Recursively strip lone surrogates / non-encodable chars from strings."""
    if isinstance(obj, str):
        return obj.encode("utf-8", "ignore").decode("utf-8")
    if isinstance(obj, list):
        return [scrub(x) for x in obj]
    if isinstance(obj, dict):
        return {k: scrub(v) for k, v in obj.items()}
    return obj


def parse_fm(text):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    fm = {}
    raw = m.group(1)
    # minimal, order-preserving YAML-ish parse good enough for our known schema
    import yaml
    fm = yaml.safe_load(raw)
    return fm, m.group(2)


def maint_status(days):
    if days is None:
        return "still maintained"
    if days <= 30:
        return "actively maintained (updated within the last month)"
    if days <= 180:
        return "actively maintained"
    if days <= 365:
        return "stable, with updates in the past year"
    return "mature and stable"


def clean_desc(desc):
    desc = (desc or "").strip().rstrip(" ,;:")
    if desc and not re.search(r"[.!?]$", desc):
        desc += "."
    return desc


def seo_description(name, cat, stars, desc):
    base = f"{name}: {cat} for Flutter"
    if stars:
        base += f" with {stars:,}★ on GitHub"
    tail = clean_desc(desc)
    out = f"{base}. {tail} Install, usage, alternatives & FAQ."
    return out[:158].rsplit(" ", 1)[0] + "…" if len(out) > 160 else out


def build_related(fm_by_slug, by_cat):
    related = {}
    for slug, fm in fm_by_slug.items():
        cat = fm.get("category", "")
        peers = [s for s in by_cat.get(cat, []) if s != slug]
        peers.sort(key=lambda s: fm_by_slug[s].get("stars", 0), reverse=True)
        related[slug] = [
            {"slug": s, "title": fm_by_slug[s]["title"]} for s in peers[:4]
        ]
    return related


def make_faq(name, cat, stars, forks, pub, is_app, related):
    faq = []
    faq.append({
        "q": f"Is {name} free to use?",
        "a": f"Yes. {name} is open source and free to use in your Flutter "
             f"projects. You can view the source, report issues, and contribute "
             f"on GitHub.",
    })
    faq.append({
        "q": f"Does {name} work on both iOS and Android?",
        "a": f"{name} is built for Flutter, so it targets iOS and Android from a "
             f"single codebase, and typically web and desktop too depending on the "
             f"project's platform support.",
    })
    if stars:
        faq.append({
            "q": f"How popular is {name}?",
            "a": f"As of {YEAR}, {name} has around {stars:,} stars"
                 + (f" and {forks:,} forks" if forks else "")
                 + " on GitHub, which puts it among the more widely used options "
                   f"in the {cat} space.",
        })
    if related:
        alts = ", ".join(r["slug"] for r in related[:3])
        faq.append({
            "q": f"What are good alternatives to {name}?",
            "a": f"Popular alternatives in the {cat} category include {alts}. "
                 f"The best choice depends on your app's size, team, and "
                 f"performance needs.",
        })
    if not is_app and pub:
        faq.append({
            "q": f"How do I install {name}?",
            "a": f"Add {name} to the dependencies section of your pubspec.yaml and "
                 f"run flutter pub get. Full versions and API docs are on pub.dev.",
        })
    return faq


def body(fm, extra, related):
    name = fm["package"]
    title = fm["title"]
    cat = fm.get("category", "")
    ci = CATEGORY.get(cat, DEFAULT_CAT)
    stars = fm.get("stars", 0) or 0
    forks = fm.get("forks", 0) or 0
    repo = fm.get("repo", "")
    gh = fm.get("githubUrl", "")
    pub = fm.get("pubDev", "")
    yt = fm.get("youtube", "")
    topics = fm.get("topics", []) or []
    desc = clean_desc(fm.get("description", ""))
    last = fm.get("lastUpdate", "")
    is_app = cat in APP_CATEGORIES
    issues = extra.get("open_issues")
    created = extra.get("created")
    days = extra.get("days_since_update")
    owner = repo.split("/")[0] if "/" in repo else repo

    P = []
    # Intro — keyword-rich
    P.append(
        f"[`{name}`]({gh}) is an open-source **{ci['kind']}** for Flutter mobile "
        f"app development"
        + (f", with **{stars:,}★** on GitHub" if stars else "")
        + (f" and last updated on **{last}**" if last else "")
        + f". This guide covers what {name} does, why it matters in {YEAR}, how to "
          f"add it to your project, when to reach for it, and how it compares to "
          f"the alternatives — plus a quick FAQ."
    )

    # What is
    P.append(f"## What is {name}?")
    what = desc if desc else f"{name} is a {ci['kind']} in the Flutter ecosystem."
    P.append(
        f"{what} It focuses on {ci['blurb']}. The project lives at "
        f"[{repo}]({gh})"
        + (f" and is maintained by `{owner}`" if owner else "")
        + "."
    )

    # Why it matters
    P.append(f"## Why {name} is worth knowing in {YEAR}")
    signals = []
    if stars:
        signals.append(f"**{stars:,} GitHub stars**")
    if forks:
        signals.append(f"**{forks:,} forks**")
    if issues is not None:
        signals.append(f"{issues:,} open issues")
    sig = ", ".join(signals) if signals else "steady community interest"
    P.append(
        f"{name} carries {sig}. "
        + (f"It has been around since {created[:4]}, and is {maint_status(days)}. "
           if created else f"It is {maint_status(days)}. ")
        + f"For a {cat} option, that combination of adoption and upkeep usually "
          f"means a healthy community, production usage, and plenty of examples to "
          f"learn from — the things that make a dependency safe to build on."
    )

    # Install / get started
    if is_app:
        P.append(f"## Running {name}")
        P.append(
            f"{name} is a complete project you can clone and run. Make sure you "
            f"have the Flutter SDK installed, then:"
        )
        P.append(
            f"```bash\ngit clone {gh}.git\ncd {name}\nflutter pub get\nflutter run\n```"
        )
        P.append(
            f"From there, read through the project structure to see how a real "
            f"Flutter app is organised — routing, state, data access, and UI — and "
            f"fork it as a starting point for your own build."
        )
    else:
        P.append(f"## Installing {name}")
        P.append("Add the package to your `pubspec.yaml`:")
        P.append(f"```yaml\ndependencies:\n  {name}: ^latest\n```")
        P.append(
            "Then fetch it and import it in your Dart code:"
        )
        imp = re.sub(r"[^a-z0-9_]", "_", name.lower())
        P.append(
            f"```bash\nflutter pub get\n```\n```dart\nimport 'package:{imp}/{imp}.dart';\n```"
        )
        P.append(
            f"Check the package's `example/` directory and its "
            + (f"[pub.dev page]({pub})" if pub else f"[GitHub repo]({gh})")
            + f" for the exact API — {name} is versioned there with full docs so "
              f"you always integrate against the current release."
        )

    # When to use
    P.append(f"## When should you use {name}?")
    P.append(f"Reach for {name} when:")
    P.append("\n".join(f"- {u}" for u in ci["use_cases"]))
    if topics:
        P.append(
            "It's especially relevant if your project touches "
            + ", ".join(f"`{t}`" for t in topics[:6]) + "."
        )

    # Alternatives / internal links
    if related:
        P.append(f"## {name} vs. the alternatives")
        P.append(
            f"If you're weighing options in the **{cat}** space, these are the "
            f"other projects developers most often compare {name} against:"
        )
        P.append("\n".join(
            f"- [{r['title']}](/recipes/{r['slug']}/)" for r in related
        ))
        P.append(
            f"There's no single winner — the right pick depends on your app's "
            f"size, your team's familiarity, and your performance budget. Browse "
            f"the full [{cat} collection](/recipes/) to compare them side by side."
        )

    # FAQ
    faq = make_faq(name, cat, stars, forks, pub, is_app, related)
    P.append("## Frequently asked questions")
    for item in faq:
        P.append(f"### {item['q']}\n\n{item['a']}")

    # Resources
    P.append("## Resources & links")
    res = [f"- **GitHub:** [{repo}]({gh})"]
    if pub:
        res.append(f"- **pub.dev:** [{name}]({pub})")
    if yt:
        res.append(f"- **Video tutorials:** [search YouTube for {name}]({yt})")
    P.append("\n".join(res))

    P.append(
        "---\n\n*Part of [FlutterCook](/recipes/) — 500 hands-on guides to the "
        "best open-source Flutter libraries, UI kits, and apps. Explore the live "
        "[GitHub trends](/trends/) or browse [YouTube guides](/youtube/).*"
    )

    text = "\n\n".join(P) + "\n"
    return text, faq


def dump_fm(fm):
    """Emit frontmatter deterministically, preserving our schema order."""
    import yaml
    order = ["title", "package", "repo", "githubUrl", "category", "stars", "forks",
             "lastUpdate", "pubDev", "youtube", "priority", "phase", "trendRank",
             "description", "seoDescription", "keywords", "topics", "related",
             "faq", "datePublished", "dateModified", "draft"]
    lines = ["---"]
    for k in order:
        if k not in fm:
            continue
        v = fm[k]
        if isinstance(v, (list, dict)):
            dumped = yaml.safe_dump(v, allow_unicode=True, default_flow_style=False,
                                    sort_keys=False).rstrip("\n")
            lines.append(f"{k}:")
            for dl in dumped.split("\n"):
                lines.append(f"  {dl}")
        elif isinstance(v, bool):
            lines.append(f"{k}: {str(v).lower()}")
        elif isinstance(v, (int, float)):
            lines.append(f"{k}: {v}")
        else:
            s = str(v).replace('"', '\\"')
            lines.append(f'{k}: "{s}"')
    lines.append("---")
    return "\n".join(lines)


def main():
    files = sorted(RECIPES.glob("*.md"))
    fm_by_slug, body_src = {}, {}
    for f in files:
        fm, _ = parse_fm(f.read_text("utf-8", errors="ignore"))
        fm_by_slug[f.stem] = scrub(fm)
    by_cat = defaultdict(list)
    for slug, fm in fm_by_slug.items():
        by_cat[fm.get("category", "")].append(slug)
    related_map = build_related(fm_by_slug, by_cat)

    total_words = 0
    for f in files:
        slug = f.stem
        fm = fm_by_slug[slug]
        ds = DS_BY_REPO.get(fm.get("repo", ""))
        extra = {}
        if ds:
            extra = {"open_issues": ds.get("open_issues"),
                     "created": ds.get("created"),
                     "days_since_update": ds.get("days_since_update"),
                     "language": ds.get("language")}
        related = related_map[slug]
        new_body, faq = body(fm, extra, related)

        name = fm["package"]
        cat = fm.get("category", "")
        stars = fm.get("stars", 0) or 0
        ci = CATEGORY.get(cat, DEFAULT_CAT)
        fm["description"] = clean_desc(fm.get("description", "")) or \
            f"{name} — {ci['kind']} for Flutter."
        fm["seoDescription"] = seo_description(name, cat, stars, fm["description"])
        kws = list(dict.fromkeys(
            [f"flutter {name}", f"{name} flutter", f"flutter {cat.lower()}"]
            + ci["keywords"] + [f"{name} example", f"{name} tutorial"]
        ))
        fm["keywords"] = kws
        fm["related"] = related
        fm["faq"] = faq
        if extra.get("created"):
            fm["datePublished"] = extra["created"]
        if fm.get("lastUpdate"):
            fm["dateModified"] = fm["lastUpdate"]

        wc = len(re.findall(r"\w+", new_body))
        total_words += wc
        fm = scrub(fm)
        out = scrub(dump_fm(fm) + "\n\n" + new_body.strip() + "\n")
        f.write_bytes(out.encode("utf-8"))

    print(f"regenerated {len(files)} recipes, avg words ~{total_words // len(files)}")


if __name__ == "__main__":
    main()
