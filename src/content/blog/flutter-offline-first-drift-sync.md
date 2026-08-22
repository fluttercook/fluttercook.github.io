---
title: "Offline-first Flutter: the local database is the source of truth, not the API"
description: "The architectural flip that makes an app work on a train: the UI reads only from SQLite, and the network becomes a background reconciler. A concrete Drift schema with an outbox table, idempotency keys, a real sync loop, and an honest look at why conflict resolution is a product decision no package can make for you."
seoDescription: "Build offline-first Flutter apps with Drift: outbox table, idempotency keys, conflict resolution strategies, and a complete sync loop."
keywords:
  - flutter offline first
  - drift database flutter
  - flutter sync local database
  - offline write queue outbox
  - flutter conflict resolution sync
  - idempotency key mobile app
category: "Deep Dive"
topic: "Flutter"
level: "Advanced"
author: "Trung Hieu"
publishDate: "2026-08-22"
emoji: "🗄️"
tags: ["Flutter", "Drift", "SQLite", "Offline", "Architecture"]
sources:
  - name: "drift on pub.dev"
    url: "https://pub.dev/packages/drift"
  - name: "Drift documentation"
    url: "https://drift.simonbinder.eu/"
  - name: "sqflite on pub.dev"
    url: "https://pub.dev/packages/sqflite"
  - name: "Flutter cookbook — Persist data with SQLite"
    url: "https://docs.flutter.dev/cookbook/persistence/sqlite"
  - name: "SQLite — Write-Ahead Logging"
    url: "https://sqlite.org/wal.html"
  - name: "connectivity_plus on pub.dev"
    url: "https://pub.dev/packages/connectivity_plus"
  - name: "Android — WorkManager"
    url: "https://developer.android.com/topic/libraries/architecture/workmanager"
  - name: "Apple — BackgroundTasks"
    url: "https://developer.apple.com/documentation/backgroundtasks"
related:
  - slug: "flutter-introduction-2026"
    title: "What Flutter is: reading a 3D game built in 15 minutes to understand the whole framework"
  - slug: "web-tech-to-mobile-app-2026"
    title: "Using web technology to build mobile apps: the 2026 technical map"
draft: false
---

Most Flutter apps are written as thin remote controls for a REST API. A screen appears, it fires a request, it shows a spinner, and when the response lands it rebuilds. Caching gets bolted on later, usually as a `Map` in a repository class or a `shared_preferences` blob, and the cache is treated as a performance trick rather than as data.

Then the app meets a lift, a tunnel, a Vietnamese 3G cell at 6pm, or an airport Wi‑Fi captive portal that answers every request with an HTTP 200 full of HTML. The spinner spins. The user taps "save" three times. Two of those taps eventually reach the server and you get duplicate rows in production.

Offline-first is not a feature you add to that architecture. It is a different architecture, and the difference is one sentence: **the UI reads and writes only the local database, and the network is a background process that reconciles that database with the server.** No screen ever awaits an HTTP call. No button is disabled because a request is in flight. The API stops being the source of truth and becomes a peer that your device syncs with.

That flip is cheap to describe and expensive to get right, because it forces you to answer three questions that a request/response app lets you avoid: what happens to a write that hasn't been sent yet, what happens when a write is sent twice, and what happens when the server and the device disagree. This post covers all three, with a working Drift schema and sync loop — and it is honest about the part no package will solve for you.

## The flip: the UI subscribes to the database, never to the network

In a request/response app, the widget tree depends on a `Future`. In an offline-first app, it depends on a `Stream` coming out of SQLite. Drift's `watch()` gives you exactly that: a query that re-emits whenever any table it touches changes.

```dart
Stream<List<Note>> watchNotes() {
  return (select(notes)
        ..where((t) => t.deletedAt.isNull())
        ..orderBy([(t) => OrderingTerm.desc(t.updatedAt)]))
      .watch();
}
```

The consequences are larger than they look:

- **Saving is synchronous from the user's point of view.** A write is a local transaction. It commits in a millisecond and the stream pushes the new row into the UI before the network layer has even woken up.
- **There is no loading state for data you already have.** The "empty vs. loading" distinction collapses into "the table is empty" and "the table has rows".
- **The sync engine has no reference to any widget.** It reads a queue table, talks to the server, writes results back. If it crashes, the UI keeps working with stale-but-real data.
- **Errors move.** A failed request is no longer an error on a screen. It is a row in a queue with a retry count, and *that* is what the UI may choose to display.

The cost: you now maintain a schema on the device, with migrations, and you own the reconciliation logic. That is a real cost. Do not pay it for an app whose screens are all read-only feeds of server-rendered content.

## Choosing the local store: what actually differs

All of these are real packages, and they are not interchangeable. The question is not "which is fastest" — for the row counts a phone app holds, they are all fast enough. The question is whether you need relational queries, reactive streams, and migrations.

| Package | What it actually is | Reactive queries | Reach for it when |
| --- | --- | --- | --- |
| `drift` | Typed SQL layer over SQLite with code generation, migrations, transactions | Yes — `watch()` on any query | You want joins, an outbox table, and schema migrations you can test |
| `sqflite` | A thin SQLite plugin. Raw SQL strings, no codegen, no streams | No — you build your own change notification | Small schema, you want no `build_runner` in the project |
| `hive_ce` / `hive` | Key–value boxes. Not a database engine; no query planner, no joins | Box listeners | Settings, tokens, a cache of blobs — not relational data |
| `isar` | NoSQL embedded database with indexes and codegen | Yes — watchers | Object graphs and index-heavy lookups. Check the pub.dev page and repo activity first; v4 has been in flux and a community fork exists |
| `objectbox` | NoSQL object database; the vendor also sells a sync product | Yes | You want object-style modelling, or are evaluating their commercial sync |

If you want the sync engine itself off the shelf rather than hand-written, `powersync` is a real Flutter package that pairs a local SQLite database with a hosted replication service. That is a legitimate answer to this whole article — it just means you buy the conflict policy along with the engine, so read the next-to-last section before you decide it fits. The rest of this post uses Drift, because an outbox is a table, retries are a query with an `ORDER BY`, and both are miserable to hand-roll on a key–value store.

## The schema does the hard work: client IDs, tombstones, and an outbox

Three schema decisions carry most of the weight. **Primary keys are generated on the device.** A UUID created client-side means a row has a stable identity the instant the user creates it — before the server has ever heard of it. If you let the server assign IDs, every local row needs a temporary ID plus a remapping pass, and every foreign key pointing at it needs rewriting when the real ID arrives. Client-generated IDs delete that entire class of bug.

**Deletes are tombstones.** You cannot `DELETE` a row that the server still has, or the next pull will resurrect it. Set `deletedAt`, filter it out of every read query, and purge the row only after the server has confirmed the delete.

**Every row carries its sync state.** At minimum: is there an unsent local change, and what version did the server last give us.

```dart
import 'package:drift/drift.dart';

enum OutboxOp { create, update, delete }

class Notes extends Table {
  TextColumn get id => text()();                    // client-generated UUID
  TextColumn get body => text().withDefault(const Constant(''))();
  DateTimeColumn get updatedAt => dateTime()();     // local edit time
  DateTimeColumn get deletedAt => dateTime().nullable()();   // tombstone

  /// Opaque version the server gave us (ETag, rev, seq). Null = never synced.
  TextColumn get serverVersion => text().nullable()();

  /// The server's copy as of [serverVersion], as JSON. Only needed for
  /// per-field merges — see the conflict section.
  TextColumn get baseJson => text().nullable()();

  BoolColumn get hasLocalChanges =>
      boolean().withDefault(const Constant(false))();

  @override
  Set<Column> get primaryKey => {id};
}

class OutboxEntries extends Table {
  /// This value IS the idempotency key. Generated once, never regenerated.
  TextColumn get id => text()();
  TextColumn get entity => text()();                // 'notes'
  TextColumn get entityId => text()();              // Notes.id
  TextColumn get op => textEnum<OutboxOp>()();
  TextColumn get payload => text()();               // JSON body to send
  DateTimeColumn get createdAt => dateTime()();
  DateTimeColumn get nextAttemptAt => dateTime()();
  IntColumn get attempts => integer().withDefault(const Constant(0))();
  TextColumn get lastError => text().nullable()();
  BoolColumn get needsAttention =>
      boolean().withDefault(const Constant(false))();

  @override
  Set<Column> get primaryKey => {id};
}
```

The rule that makes this correct: **the row write and the outbox insert happen in the same transaction.** If they can happen separately, you will eventually ship a build where the UI shows a saved note that no queue entry will ever send, or a queue entry for a note that was never written.

```dart
Future<void> saveNote({required String id, required String body}) async {
  final now = DateTime.now().toUtc();

  await _db.transaction(() async {
    await _db.into(_db.notes).insertOnConflictUpdate(
          NotesCompanion.insert(
            id: id,
            body: Value(body),
            updatedAt: now,
            hasLocalChanges: const Value(true),
          ),
        );

    await _db.into(_db.outboxEntries).insert(
          OutboxEntriesCompanion.insert(
            id: _uuid.v4(),
            entity: 'notes',
            entityId: id,
            op: OutboxOp.update,
            payload: jsonEncode({'id': id, 'body': body}),
            createdAt: now,
            nextAttemptAt: now,
          ),
        );
  });

  unawaited(_sync.kick());   // fire and forget; the UI is already updated
}
```

One design choice worth making deliberately: does the outbox store **snapshots** ("this row now looks like *X*") or **operations** ("append this comment", "increment this counter")? Snapshots coalesce — ten edits to the same note while offline can collapse into one pending entry, and the server never sees the intermediate states. Operations cannot coalesce, but they preserve intent, which matters for anything additive or numeric. A counter synced as a snapshot loses concurrent increments; the same counter synced as `+1` deltas does not. Most apps want snapshots for entity edits and operations for the handful of additive things.

## Idempotency keys turn "retry" from a bug into a feature

The classic offline duplicate comes from a request that *succeeded* and whose response was lost — timeout, socket reset, process kill, the user force-quitting mid-flight. The client has no way to distinguish "never arrived" from "arrived and I didn't hear back", so a naive retry creates a second row.

The fix is on the wire, not in the client: the client sends a key it generated once, and the server promises that two requests carrying the same key produce one effect.

```dart
final response = await _client.post(
  Uri.parse('$base/notes'),
  headers: {
    'Content-Type': 'application/json',
    'Idempotency-Key': entry.id,       // the outbox row's primary key
    if (row.serverVersion != null) 'If-Match': row.serverVersion!,
  },
  body: entry.payload,
);
```

Two properties make this work, and both are easy to get wrong:

1. **The key is generated when the write is queued, not when it is sent.** If you generate it inside the retry loop, every attempt gets a new key and you have gained nothing. This is why the key is the outbox row's primary key — it physically cannot change across attempts.
2. **The server must persist the key and the response it produced**, keyed within the authenticated user, for a retention window longer than your maximum backoff. A replay returns the stored result. A server that merely checks "does a row with this key exist" is doing the same job less reliably.

`If-Match` with the last-known server version is the companion mechanism: it converts a silent overwrite into an explicit `412`/`409` that your client can handle. Without it, last-write-wins isn't a strategy you chose — it's the default you got.

Map the response to a decision, not to an exception:

| Response | Meaning | What the loop does |
| --- | --- | --- |
| `2xx` | Applied | Delete the outbox row, write the server's copy back |
| `409` / `412` | Server has a newer version | Run conflict resolution |
| `400`, `403`, `404`, `422` | This write will never succeed | Stop retrying; flag `needsAttention` |
| `408`, `429`, `5xx`, timeouts, socket errors | Might succeed later | Backoff and retry (honour `Retry-After` on `429`) |

The third row is the one teams forget. A validation failure retried forever is a queue that never drains and a battery that never rests.

## The sync loop, end to end

```dart
sealed class SendResult {}

class Sent extends SendResult { Sent(this.row); final Map<String, Object?> row; }
class Conflicted extends SendResult { Conflicted(this.row); final Map<String, Object?> row; }
class Retryable extends SendResult { Retryable(this.error); final Object error; }
class Rejected extends SendResult { Rejected(this.reason); final String reason; }

class SyncEngine {
  SyncEngine(this._db, this._api);

  final AppDatabase _db;
  final Api _api;

  bool _running = false;
  StreamSubscription<Object?>? _connSub;

  void start() {
    // A connectivity change is a hint to try again, not proof of reachability.
    _connSub = Connectivity().onConnectivityChanged.listen((_) => kick());
    kick();
  }

  /// Single-flight: overlapping runs would reorder writes.
  Future<void> kick() async {
    if (_running) return;
    _running = true;
    try {
      await _drainOutbox();
      await _pullChanges();
    } finally {
      _running = false;
    }
  }

  Future<void> _drainOutbox() async {
    final now = DateTime.now().toUtc();
    final due = await (_db.select(_db.outboxEntries)
          ..where((t) => t.needsAttention.equals(false))
          ..where((t) => t.nextAttemptAt.isSmallerOrEqualValue(now))
          ..orderBy([(t) => OrderingTerm.asc(t.createdAt)])
          ..limit(50))
        .get();

    for (final entry in due) {
      final result = await _api.send(entry);

      switch (result) {
        case Sent(:final row):
          await _db.transaction(() async {
            await _db.applyServerRow(entry.entity, row);
            await _db.deleteOutboxEntry(entry.id);
          });
        case Conflicted(:final row):
          await _db.resolveConflict(entry, row);
        case Rejected(:final reason):
          await _db.flagForAttention(entry, reason);
        case Retryable(:final error):
          final delay = _backoff(entry.attempts + 1);
          await _db.scheduleRetry(entry, error.toString(), delay);
          return; // Stop here. Later writes must not overtake this one.
      }
    }
  }

  Duration _backoff(int attempt) {
    const capSeconds = 60 * 60;
    final window = math.min(1 << attempt.clamp(0, 12), capSeconds);
    return Duration(seconds: 1 + Random().nextInt(window)); // full jitter
  }
}
```

Four details in there are load-bearing:

- **`return` on the first retryable failure.** Draining past a stuck entry lets a later edit of the same row land before an earlier one. If your entities are genuinely independent you can partition the queue by `entityId` and drain each partition in order — but do it deliberately, not by accident.
- **Single-flight `_running` guard.** Two concurrent drains will interleave requests for the same row.
- **Full jitter on backoff.** Without jitter, every device that lost connectivity at the same moment retries at the same moment, and your API gets a thundering herd the second the network returns.
- **`_pullChanges()` runs after the push.** Pulling first means you overwrite local rows with server state you are about to contradict.

The pull side wants a cursor, not a timestamp. Ask the server for "everything since token *T*", apply the page inside one transaction, store the new token in the same transaction, repeat until the server says there is no more. A `?updated_since=<clock>` parameter looks equivalent and isn't: rows written during the same second as your cutoff get skipped, and it makes your correctness depend on two machines' clocks agreeing.

On background execution: you do not control when this runs while the app is closed. Android's WorkManager and Apple's BackgroundTasks give you opportunistic windows subject to Doze, budgets, and how often the user opens your app. Wire them up if you like, but design the product so that syncing on foreground is sufficient, and treat background runs as a bonus rather than a guarantee.

Two SQLite settings are worth confirming rather than assuming: WAL mode, so the sync engine's writes don't block the UI's reads, and running the database off the UI isolate. Drift supports isolate-hosted databases (`DriftIsolate`) and `drift_flutter` wires much of this up for you — check its current docs rather than trusting a snippet, defaults here have changed across versions.

## Conflict resolution is a product decision, not a library feature

This is the section people skip, and it is the one that decides whether users trust the app.

No package resolves conflicts for you. Packages give you the *mechanism* — a 409, a version column, a merge hook. The *policy* — which edit wins and who gets told — is a product question, and the right answer is different for a note, a shopping cart, and a bank balance. If a library claims to solve it, read what it actually does; it has picked last-write-wins on your behalf.

| Strategy | The rule | What is lost | Pick it when |
| --- | --- | --- | --- |
| Last-write-wins | Highest version/timestamp overwrites | The other edit, silently | Low contention, cheap to redo. One user, several devices |
| Server-authoritative | Server recomputes from its own state; client discards its optimistic value and re-reads | The client's guess | Invariants must hold: stock, balances, seat booking, anything monetary |
| Per-field merge | Fields changed on only one side merge; only same-field edits conflict | Nothing, unless two people edited the same field | Wide records with independent fields — profiles, settings, long forms |
| Append-only / operation log | No conflicts exist; the server assigns an order | Nothing | Chat, comments, activity feeds, counters expressed as deltas |
| Ask the user | Keep both versions and show a diff | The user's patience | Rare, high-value, irreversible conflicts — a long document body |

How to actually choose: ask what a user loses when the wrong version wins. If the answer is "they retype a sentence", last-write-wins is correct and anything fancier is waste. If the answer is "we charge them twice" or "we sell the same seat to two people", no client-side merge is acceptable — the server owns the decision and the client's job is to submit an intent with an idempotency key and render whatever comes back.

Two traps. **Last-write-wins on device clocks is not last-write-wins.** A phone whose clock is a day fast will win every conflict until the real time catches up, and a phone a day slow will silently lose every edit its user makes. If you need LWW, derive the ordering from something the server controls — a monotonic sequence number, or a hybrid logical clock that carries a counter alongside the wall clock.

**Per-field merge needs three versions, not two.** To know whether a field changed you need the local value, the server value, *and* the common ancestor — the last server state this device saw. That is what `baseJson` in the schema above is for. Without it you cannot distinguish "I changed this field" from "I never touched it and it just looks different", and your merge will happily reintroduce values the other side deliberately cleared.

CRDTs are the principled version of per-field merge, and for collaborative text they are the right tool. In Dart the ecosystem is thinner than on the web, and adopting one means committing to its data model everywhere, not just at the merge point. That is a serious architectural commitment — worth it for a collaborative editor, oversized for a to-do list.

## Showing sync state without lying to the user

The failure mode here is a green checkmark that means "written to SQLite" but reads, to the user, as "safe on the server". When they wipe their phone and lose a week of notes, the checkmark is what they will remember.

Honest states, and what each is allowed to claim:

- **Saved on this device** — the transaction committed. Say *on this device*. This is the state the user sees the instant they stop typing, and it is a genuinely strong claim: it survives an app crash and a reboot.
- **Syncing** — an outbox entry for this row is in flight right now. Usually not worth a per-row indicator; a subtle global one is enough.
- **Waiting to sync** — queued, will go when the network allows. Show the count of pending items, not a spinner. A spinner with no end is a lie about progress.
- **Needs your attention** — the server rejected it and no retry will help. This *must* be reachable in the UI. A rejected write with no surface is data the user believes is saved and which will never exist anywhere else.

A few rules follow. Never block navigation or show a modal spinner on save — the save already happened, and a "saving…" dialog on a local transaction teaches users that your app is slow when it is the opposite.

Be careful with the offline banner. `connectivity_plus` reports which network interface is active — it does not promise the internet is reachable, and it will happily report a healthy Wi‑Fi connection while a captive portal eats every request. Derive the banner from your own evidence: did the last sync attempt succeed, and is the outbox draining. Use connectivity events as a trigger to retry, not as the truth you display. And make pending state visible where it changes behaviour, invisible where it doesn't: a pending badge on every row in a list is noise, while a single "3 changes waiting to sync" chip in the app bar, tappable to a screen that lists them and lets the user retry or discard, is information.

Finally, when a conflict is resolved in a way that discards the user's edit, say so. A one-line snackbar — "This note was updated on another device; your version was replaced" with an undo — costs almost nothing and is the difference between a resolution policy and a data-loss bug.

## FAQ

**Do I need Drift, or can I do this with sqflite?**

You can do all of it with `sqflite`; the outbox is just a table and the sync loop is just SQL. What you give up is typed queries, generated migrations, and `watch()` — you would build change notification yourself, which is the part most likely to go subtly wrong. Pick `sqflite` when the schema is tiny and adding `build_runner` to the project is a real cost.

**Where does the idempotency key have to be enforced — client or server?**

The server. The client's only job is to generate the key once and resend the same one on every attempt. If the server does not deduplicate on that key, the header is decoration and a lost response still creates a duplicate. If you do not control the API, this is the single most valuable thing to ask the backend team for.

**Can I just use last-write-wins everywhere and move on?**

Often yes — for single-user, multi-device apps with low contention it is the correct engineering call, not a shortcut. What you cannot do is use it for records with invariants (money, stock, capacity) or drive it from device clocks. Decide it explicitly, write it in the design doc, and make sure a discarded edit produces a message rather than silence.

**How do I keep the local database from growing forever?**

Purge tombstones once the server has confirmed the delete, delete outbox rows on success, and cap history for high-churn tables. For large collections, sync a window rather than everything — the most recent N items plus anything the user has opened — and fetch older records on demand, accepting that those are the ones that will not be there on a plane.

**Does this work on Flutter web?**

Drift supports the web via a WASM build of SQLite, with persistence backed by browser storage. It works, but the storage guarantees are the browser's, not the OS's — an origin's data can be evicted under pressure, and the setup steps differ from mobile. If web is a primary target, verify the current storage story in the Drift docs before you promise users that their offline edits are durable.

---

*Opinion here: the choice of Drift, the FIFO-with-stop drain, and the specific UI wording. Fact: the outbox-plus-idempotency-key pattern, the failure mode of clock-based last-write-wins, and the need for a common ancestor to do a three-way field merge. Package APIs and platform background-execution rules change between versions — verify anything version-dependent against the linked documentation before you ship it.*
