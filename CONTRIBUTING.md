# Contributing to FlutterCook

FlutterCook is a growing library of **runnable demos** for open-source Flutter
packages. Adding one is a single small Pull Request — here's the standard.

## The 3-step recipe

1. **Create your demo folder**
   ```
   demos/<package_name>/index.html
   ```
   One self-contained HTML file. Inline all CSS/JS — no build step. Copy
   `demos/flutter_gemma/index.html` as a starting template to match the style
   (dark background `#0b0b0c`, teal accent `#57e3cf`, serif headings).

2. **Make it a real, minimal demo**
   - Show the smallest useful thing the package does.
   - Add a `<title>` and `<meta name="description">` for SEO.
   - Link back to the package on **pub.dev** and to its GitHub repo.
   - If the package needs a device/native feature the web can't do, simulate
     the UI and clearly label it as a UI demo (see flutter_gemma).

3. **Open a Pull Request**
   - The PR template opens automatically — fill in the checklist.
   - The **Validate PR** check runs automatically (see below).
   - When it's green, a maintainer merges it — and the site redeploys itself.

## What the automation does

| Trigger | Workflow | Result |
|--------|----------|--------|
| You open/update a PR | `pr-validate.yml` | Checks your `demos/<name>/index.html` exists, is non-empty, has `<title>` + meta description, links to pub.dev, and contains no obvious secrets. This is a **required status check**. |
| A maintainer merges the PR | — | GitHub records the merge to `main`. |
| Commit lands on `main` | `deploy.yml` | Builds the Pages artifact and deploys → **https://fluttercook.github.io** updates automatically. |

### Want hands-off auto-merge? (maintainers)
For safety we don't auto-merge arbitrary PRs. To enable **native GitHub
auto-merge** the safe way:
1. **Settings → General →** enable *Allow auto-merge*.
2. **Settings → Branches →** add a protection rule for `main`:
   require the **Validate PR** status check and (recommended) **1 approving review**.
3. On any green PR, click **Enable auto-merge** — GitHub merges it the moment
   the required checks pass, then `deploy.yml` ships it. A human still approves,
   so nothing merges unreviewed.

## Local preview

```bash
open demos/<package_name>/index.html      # macOS
xdg-open demos/<package_name>/index.html  # Linux
```

## Style reference

- Colors: bg `#0b0b0c`, ink `#f3efe8`, muted `#9b968c`, accent `#57e3cf`, line `#2a2a2c`
- Headings: serif (`Iowan Old Style, Palatino, Georgia`), italic accent words in teal
- System fonts only (no web-font requests) — keeps it fast

Questions? Open an issue. Happy cooking! 🍳
