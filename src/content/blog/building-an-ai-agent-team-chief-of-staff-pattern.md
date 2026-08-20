---
title: "The chief-of-staff pattern: turning scattered AI chats into an agent team"
description: "Nine habits that turn a pile of one-off AI conversations into a system with a single front door, shared memory, logged work, and routines that run while you sleep."
seoDescription: "How to build an AI agent team: the chief-of-staff routing pattern, shared vs private memory, tool bridges, work logging, teach-by-demonstration, and scheduled routines. Platform-agnostic guide."
keywords:
  - ai agent team
  - chief of staff ai agent
  - orchestrator agent pattern
  - ai agent memory shared private
  - grok bot tips
  - custom gpt routing
  - ai automation routines
category: "Guide"
topic: "AI Agents"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-08-20"
emoji: "🧑‍✈️"
tags: ["AI", "AI Agents", "Automation", "Productivity", "Grok", "Claude"]
sources:
  - name: "Composio — integration platform for AI agents"
    url: "https://composio.dev/"
  - name: "Anthropic — Building effective agents"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
  - name: "Anthropic — Agent Skills"
    url: "https://www.anthropic.com/news/skills"
draft: false
---

Most people's AI setup looks the same after six months: eleven half-remembered custom assistants, a browser tab graveyard, and a nagging sense that the thing you figured out in March is buried in a chat you'll never find again.

Creating agents is the easy part. Every platform — Grok Bot, custom GPTs, Claude Projects — makes it a two-minute job. What separates a useful setup from a cluttered one is not how many agents you have. It's whether they share context, report their work, and can run without you sitting there.

Nine habits get you there. They're written platform-agnostically, because the pattern outlives whichever tool you're using this year.

## Part 1 — Teach the system who you are

### 1. Interview yourself first

An agent team is only as good as its understanding of your situation. And most people never write that down, because it's tedious and they already know it.

Make the AI extract it instead. Create a skill or saved prompt whose only job is to interrogate you — one question at a time, no answers offered, until it can state your work, goals and constraints back to you accurately.

```text
You are interviewing me to build a context document about my work.

Rules:
- Ask ONE question at a time and wait for my answer.
- Never suggest an answer or offer multiple choice.
- When an answer is vague, ask a follow-up instead of moving on.
- Cover: what I actually do day to day, what I'm measured on, who
  depends on me, what's currently blocked, what I'm avoiding, and
  what I want to be true in 90 days.
- Stop when you can summarise my situation in 10 bullets I'd agree
  with. Show me those bullets and ask what's wrong with them.
```

That last rule matters more than the rest. "Show me the summary and ask what's wrong with it" is what turns an interview into a correction loop.

Run this before quarterly planning, before starting a project, before building any automation. Save the output. It becomes the shared context every other agent reads.

**Why it works:** you're not writing documentation, which you'd never finish. You're answering questions, which is much easier, and something else does the writing.

### 2. One front door

You might have agents for content, research, planning and admin. What you don't want is to remember which one handles what, every single time.

Pick one agent to be the front door. Give it a name — it genuinely helps to talk to *Klaus* rather than *Assistant 4*. Everything goes through it.

Its operating rule is short:

```text
You are my chief of staff. You are the only agent I talk to directly.

Before doing any task yourself:
1. Check whether a specialist agent covers it. Here is the roster:
   - Motion — images, video, animation
   - Eyes — research and fact-checking
   - Miner — content research, sourcing, competitor scans
   - Coffee — morning planning and daily priorities
   - Views — content strategy and distribution
2. If one fits, delegate to it and bring the result back here.
3. Only handle it yourself if no specialist fits.
4. If you delegated, say which agent you used and why.

Never make me open another conversation.
```

That last line is the whole point. The cost of a multi-agent setup isn't tokens, it's the mental overhead of routing. Move the routing into the system.

**Give each specialist a sharp description.** "General assistant" is useless to a router. "Handles image generation, video editing prompts, and motion graphics briefs" is routable. The chief of staff reads these descriptions to decide — vague descriptions produce bad routing.

### 3. Let the front door design the rest of the team

Once you've done the interview from habit #1, you no longer have to guess which agent to build next. Ask:

```text
Here is my context document and my current agent roster.

Given the goals in the context document, what roles are missing?
Rules:
- Do not propose a second chief of staff or a general assistant.
- Do not propose a role that overlaps an existing one — say which
  existing agent already covers it instead.
- For each proposal: the specific recurring problem it solves, what
  it should be able to do, and what it should never touch.
- Rank by how much time it saves me per month. Show your estimate.
```

The two "do not" rules are load-bearing. Left alone, models propose a generic helper and a duplicate coordinator, because those are the most common shapes in their training data. Ban them and you get proposals shaped by your actual problems.

When priorities shift, tell the chief of staff what changed and let it redesign the roster. Teams should be disposable.

## Part 2 — Control who knows what

### 4. Split shared memory from private memory

Most platforms now offer persistent memory. The mistake is dumping everything into one pile.

Two tiers:

| Shared memory — every agent reads | Private memory — one agent only |
| --- | --- |
| Company, role, location, timezone | Working notes for that agent's task |
| Team names and who owns what | Style preferences specific to its output |
| Products, channels, funnels | Its own running to-do state |
| Which tools you use and how they connect | Feedback you gave *it* about *its* work |

The test is simple: **would another agent make a worse decision without knowing this?** If yes, it's shared. If it only matters to one agent's job, keep it private.

This matters more as the roster grows. Several agents may use your calendar — but the context about *why* Tuesday mornings are protected belongs in shared memory, or every one of them will book over it.

Be explicit when you tell an agent to remember something:

```text
Save to shared memory: we ship on Thursdays, never Fridays.
Save to your own memory: I prefer your drafts at 400 words, not 800.
```

**One more habit:** most tools let you branch an important message into its own thread. Use it. Explore a tangent in a branch, keep the main conversation clean. The main thread is your system's spine — don't clutter it with exploration.

## Part 3 — Connect the tools, log the work

### 5. Bridge to the apps your platform doesn't support

Every AI platform ships plugins. None ships all of them. When you need YouTube, Reddit, LinkedIn, a CRM, or a search API that isn't natively supported, an integration platform like [Composio](https://composio.dev/) sits in between — hundreds of integrations behind one connection your agents can call.

Then record the bridge in **shared** memory, so every agent knows the capability exists:

```text
Save to shared memory: YouTube, LinkedIn, Reddit and Perplexity are
reachable through Composio. Check Composio before telling me
something isn't possible.
```

Without that line, agents will keep telling you they can't do things they can do. Capabilities that aren't written down don't exist.

**Security note, and it's not optional:** an integration bridge holds live credentials to your accounts. Grant the narrowest scopes that work, review what each connection can actually do, and never give a scheduled, unattended agent write access to something you'd hate to have wrongly rewritten. The convenience is real; so is the blast radius.

### 6. Log agent work somewhere outside the chat

The moment you start delegating from both phone and laptop, you lose track. Work disappears into conversations nobody reopens.

Fix it by making logging part of the task, not an afterthought. A skill like *"log this work to the tracker"* that fires **before** the work starts:

```text
When I assign research or a multi-step task:
1. Create a project in the tracker FIRST, before doing anything.
2. Add a task per subtask, with: owner agent, start time, what it's
   waiting on, and a link field for the output.
3. Delegate the work.
4. Update the task with progress notes and the output link when done.
5. Give me the project link in your reply.
```

Ask for five voice-agent vendors compared, and the tracker gets a project before any research happens. Later you can see what ran, what finished, who did it, and where the output went — without archaeology through chat history.

The value isn't project management theatre. It's that **work stops evaporating.**

## Part 4 — Teach once, then automate

### 7. Demonstrate the workflows you can't describe

Some processes are visual and genuinely painful to write down. Where to click, which of four similar buttons, what to do when the layout shifts.

If your platform gives agents a shared cloud computer with a "teach a task" recording mode, use it for exactly these. Start recording, do the process at normal speed, stop. The agent analyses what you did and turns it into a reusable skill.

Good candidates: sourcing images and saving them with a specific naming convention; navigating an interface with no API; anything where the next step depends on what's currently on screen.

Bad candidates: anything with a clean API. Recording clicks over a supported API is slower and far more brittle. Demonstration is for the gaps.

### 8. Routines are what make it run without you

Chat apps are for when you're thinking. Routines are for when you're not.

A routine is a recurring task the agent runs on a schedule or a trigger. Give it a name, the instruction, and which skill or agent it should invoke.

Two trigger types, and they solve different problems:

- **Schedule** — hourly, daily, custom interval. Good for digests, reviews, recurring reports.
- **Event** — Slack message, Git activity, Teams message, and similar. Good for reacting to things you don't control the timing of.

Because routines run in the cloud, they keep running with your laptop shut and your phone in a drawer. That's the difference between an assistant and a system.

Start with the boring ones. A daily 7am brief that reads your calendar and inbox and tells you the three things that actually matter is worth more than any clever automation you'll build later and never trust.

**Set a guardrail on anything unattended:** unattended agents should default to producing drafts and notifications, not sending, publishing, or deleting. Move an individual routine to fully automatic only after you've watched its output for a couple of weeks and it's been right every time.

### 9. Save logged-in browser profiles

An agent's computer becomes far more useful when it can reuse a browser profile that's already signed in.

Log the agent into a service once, in its saved profile. Teach it the task. Attach the task to a routine. The session persists — so you're not pasting a password into a conversation on every run.

That's the real security argument for this feature, and it's worth stating plainly: **credentials in a saved profile are better than credentials in your chat history.** Chat history gets summarised, exported, and fed back into other contexts. A stored browser session doesn't.

Two rules if you do this:

1. Use a dedicated account for agent work where the service allows it — not your primary account.
2. Never paste a password, API key or 2FA code into a conversation, including "just this once to set it up." Sign in interactively in the profile instead.

## Putting it together

A weekend's worth of setup, in order:

1. **Run the self-interview.** Save the output as your context document.
2. **Create the chief of staff.** Paste in the routing rule. Give it the context document.
3. **Ask it what agents are missing.** Build the top two. Not eight.
4. **Split memory.** Shared facts up top, per-agent notes below.
5. **Connect one bridge** for the tool you keep wishing worked, and record it in shared memory.
6. **Add logging** to the chief of staff's instructions.
7. **Build one routine** — a morning brief is the standard first one.
8. **Only then** consider demonstrations and saved profiles.

Steps 1–3 deliver most of the value. The rest is compounding.

## What actually makes it work

The best setup is not the one with the most agents. It's the one where each agent knows its role, has the context it needs, reports what it did, and can turn a process you've already done well into something reusable.

Three failure modes to watch for:

**Too many agents.** Every agent is a routing decision. Five sharp ones beat fifteen fuzzy ones — and a fuzzy roster degrades the chief of staff's routing, because it's choosing from descriptions.

**Memory that's never pruned.** Stale shared memory is worse than no shared memory, because agents act on it confidently. Review it monthly and delete what's no longer true.

**Routines nobody reads.** An automation producing output you skim past is pure cost. If you've ignored a routine's output twice in a row, either fix it or delete it.

## FAQ

**Do I need a specific platform for this?**
No. The pattern works on any system with persistent custom assistants and memory — Grok Bot, custom GPTs, Claude Projects. Only habits 7 and 8 need platform-specific features (agent computer, scheduled routines).

**How many agents should I start with?**
Two: the chief of staff, and one specialist for your most repetitive task. Add more only when routing to an existing agent visibly produces worse output than a dedicated one would.

**What goes in shared memory vs private?**
Shared if another agent would make a worse decision without it. Private if it only affects one agent's own work.

**Is it safe to let agents run unattended?**
With scope discipline, yes. Give unattended routines read access and draft-only output by default. Anything that sends, publishes, spends or deletes should require you to approve it, until you've watched it behave correctly for weeks.

**What's the single highest-value habit here?**
The self-interview. Every other habit gets better when the system actually knows your situation, and every one of them degrades when it doesn't.

---

*This piece expands on a set of nine tips circulating in Vietnamese AI communities, originally written up after a week of daily use with Grok Bot. The prompts and framing here are my own; the underlying habits are worth stealing regardless of which platform you're on.*
