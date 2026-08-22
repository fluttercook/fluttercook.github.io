---
title: "Flutter offline-first: database dưới máy mới là nguồn sự thật, không phải API"
description: "Cú lật kiến trúc giúp app chạy được trên tàu điện ngầm: UI chỉ đọc từ SQLite, còn network trở thành một tiến trình nền đi đối soát. Kèm schema Drift cụ thể với bảng outbox, idempotency key, vòng lặp sync thật, và một góc nhìn thẳng thắn về việc vì sao xử lý conflict là quyết định sản phẩm chứ không phải tính năng của thư viện."
seoDescription: "Xây app Flutter offline-first với Drift: bảng outbox, idempotency key, các chiến lược xử lý conflict và vòng lặp sync hoàn chỉnh."
keywords:
  - flutter offline first
  - drift database flutter
  - đồng bộ dữ liệu offline flutter
  - hàng đợi ghi outbox
  - xử lý conflict đồng bộ flutter
  - idempotency key mobile
category: "Chuyên sâu"
topic: "Flutter"
level: "Nâng cao"
author: "Trung Hiếu"
publishDate: "2026-08-22"
emoji: "🗄️"
tags: ["Flutter", "Drift", "SQLite", "Offline", "Kiến trúc"]
sources:
  - name: "drift trên pub.dev"
    url: "https://pub.dev/packages/drift"
  - name: "Tài liệu Drift"
    url: "https://drift.simonbinder.eu/"
  - name: "sqflite trên pub.dev"
    url: "https://pub.dev/packages/sqflite"
  - name: "Flutter cookbook — Persist data with SQLite"
    url: "https://docs.flutter.dev/cookbook/persistence/sqlite"
  - name: "SQLite — Write-Ahead Logging"
    url: "https://sqlite.org/wal.html"
  - name: "connectivity_plus trên pub.dev"
    url: "https://pub.dev/packages/connectivity_plus"
  - name: "Android — WorkManager"
    url: "https://developer.android.com/topic/libraries/architecture/workmanager"
  - name: "Apple — BackgroundTasks"
    url: "https://developer.apple.com/documentation/backgroundtasks"
related:
  - slug: "flutter-introduction-2026"
    title: "Flutter là gì: đọc một game 3D dựng trong 15 phút để hiểu cả framework"
  - slug: "web-tech-to-mobile-app-2026"
    title: "Dùng công nghệ web để làm app mobile: bản đồ kỹ thuật 2026"
draft: false
---

Phần lớn app Flutter được viết như một cái điều khiển từ xa mỏng dính cho REST API. Màn hình hiện lên, bắn một request, quay spinner, response về thì rebuild. Cache được gắn thêm sau, thường là một `Map` trong repository hoặc một cục blob trong `shared_preferences`, và cache bị coi như mẹo tăng tốc chứ không phải dữ liệu.

Rồi app gặp thang máy, gặp hầm, gặp sóng 3G lúc 6 giờ chiều, hoặc gặp Wi‑Fi sân bay có captive portal trả HTTP 200 kèm một trang HTML cho mọi request. Spinner cứ quay. Người dùng bấm "lưu" ba lần. Hai trong ba lần đó rốt cuộc tới được server, và bạn có bản ghi trùng trên production.

Offline-first không phải là một tính năng bạn thêm vào kiến trúc đó. Nó là một kiến trúc khác, và khác biệt gói gọn trong một câu: **UI chỉ đọc và ghi database dưới máy, còn network là một tiến trình nền làm nhiệm vụ đối soát database đó với server.** Không màn hình nào `await` một lời gọi HTTP. Không nút nào bị disable vì đang có request bay. API thôi làm nguồn sự thật và trở thành một bên ngang hàng mà thiết bị của bạn đồng bộ cùng.

Cú lật đó nói thì rẻ, làm cho đúng thì đắt, vì nó ép bạn trả lời ba câu hỏi mà app request/response cho phép né: chuyện gì xảy ra với một lệnh ghi chưa kịp gửi, chuyện gì xảy ra khi một lệnh ghi bị gửi hai lần, và chuyện gì xảy ra khi server với thiết bị không đồng ý với nhau. Bài này đi qua cả ba, kèm schema Drift và vòng lặp sync chạy được — và nói thật về phần mà không package nào giải hộ bạn.

## Cú lật: UI subscribe vào database, không bao giờ subscribe vào network

Trong app request/response, widget tree phụ thuộc vào một `Future`. Trong app offline-first, nó phụ thuộc vào một `Stream` chảy ra từ SQLite. `watch()` của Drift cho bạn đúng thứ đó: một query tự phát lại mỗi khi bất kỳ bảng nào nó đụng tới thay đổi.

```dart
Stream<List<Note>> watchNotes() {
  return (select(notes)
        ..where((t) => t.deletedAt.isNull())
        ..orderBy([(t) => OrderingTerm.desc(t.updatedAt)]))
      .watch();
}
```

Hệ quả lớn hơn vẻ ngoài của nó:

- **Với người dùng, lưu là tức thì.** Một lệnh ghi là một transaction cục bộ. Nó commit trong vài mili-giây và stream đẩy row mới lên UI trước khi tầng network kịp thức dậy.
- **Không có loading state cho dữ liệu bạn đã có.** Phân biệt "rỗng hay đang tải" sụp xuống thành "bảng rỗng" và "bảng có row".
- **Sync engine không tham chiếu tới widget nào.** Nó đọc một bảng hàng đợi, nói chuyện với server, ghi kết quả về. Nó chết thì UI vẫn chạy với dữ liệu cũ-nhưng-có-thật.
- **Lỗi đổi chỗ.** Một request hỏng không còn là lỗi trên màn hình. Nó là một row trong hàng đợi kèm số lần retry, và *đó* mới là thứ UI có thể chọn hiển thị.

Cái giá: bạn giờ phải nuôi một schema trên thiết bị, kèm migration, và bạn sở hữu luôn logic đối soát. Đó là chi phí thật. Đừng trả nó cho một app mà mọi màn hình đều là feed chỉ đọc do server render.

## Chọn kho lưu trữ cục bộ: điểm khác nhau thật sự

Tất cả đều là package có thật, và chúng không thay thế cho nhau được. Câu hỏi không phải "cái nào nhanh nhất" — với lượng row mà một app điện thoại giữ, cái nào cũng đủ nhanh. Câu hỏi là bạn có cần truy vấn quan hệ, stream phản ứng, và migration hay không.

| Package | Thực chất là gì | Reactive query | Chọn khi |
| --- | --- | --- | --- |
| `drift` | Lớp SQL có kiểu đặt trên SQLite, có code generation, migration, transaction | Có — `watch()` trên mọi query | Bạn cần join, cần bảng outbox, và cần migration schema kiểm thử được |
| `sqflite` | Plugin SQLite mỏng. SQL dạng chuỗi, không codegen, không stream | Không — tự dựng cơ chế báo thay đổi | Schema nhỏ, không muốn có `build_runner` trong dự án |
| `hive_ce` / `hive` | Box key–value. Không phải database engine; không query planner, không join | Listener trên box | Settings, token, cache blob — không dùng cho dữ liệu quan hệ |
| `isar` | Database NoSQL nhúng, có index và codegen | Có — watcher | Object graph và tra cứu nặng index. Xem trang pub.dev và mức độ hoạt động của repo trước; bản v4 nhiều biến động và đã có bản fork cộng đồng |
| `objectbox` | Database object NoSQL; nhà phát triển còn bán kèm sản phẩm sync | Có | Bạn muốn mô hình hoá kiểu object, hoặc đang cân nhắc dịch vụ sync thương mại của họ |

Nếu bạn muốn mua sẵn cả sync engine thay vì tự viết, `powersync` là package Flutter có thật, ghép một database SQLite cục bộ với dịch vụ replication được host. Đó là một câu trả lời chính đáng cho cả bài viết này — chỉ là bạn mua luôn cả chính sách conflict kèm engine, nên hãy đọc phần áp chót trước khi kết luận nó hợp. Phần còn lại của bài dùng Drift, vì outbox là một cái bảng, retry là một query có `ORDER BY`, và cả hai đều khổ sở nếu phải tự dựng trên một kho key–value.

## Schema gánh phần nặng: ID sinh ở client, tombstone, và outbox

Ba quyết định về schema gánh gần hết trọng lượng. **Khoá chính được sinh ngay trên thiết bị.** Một UUID tạo phía client nghĩa là row có danh tính ổn định ngay khoảnh khắc người dùng tạo ra nó — trước khi server từng nghe nói tới nó. Nếu để server cấp ID, mỗi row cục bộ cần một ID tạm cộng một lượt ánh xạ lại, và mọi khoá ngoại trỏ tới nó đều phải viết lại khi ID thật về. ID sinh ở client xoá sạch cả lớp bug đó.

**Xoá là tombstone.** Bạn không thể `DELETE` một row mà server vẫn còn giữ, nếu không lần pull kế tiếp sẽ hồi sinh nó. Hãy set `deletedAt`, lọc nó khỏi mọi query đọc, và chỉ dọn row sau khi server xác nhận đã xoá.

**Mỗi row mang theo sync state của chính nó.** Tối thiểu: có thay đổi cục bộ chưa gửi hay không, và server đã cấp cho ta version nào lần cuối.

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

Quy tắc làm cho chuyện này đúng: **ghi row và chèn outbox nằm trong cùng một transaction.** Nếu chúng có thể xảy ra tách rời, sớm muộn bạn sẽ ship một bản mà UI hiển thị một note đã lưu nhưng không có entry hàng đợi nào gửi nó đi, hoặc một entry hàng đợi cho một note chưa từng được ghi.

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

Có một lựa chọn thiết kế đáng cân nhắc có chủ đích: outbox lưu **snapshot** ("row này bây giờ trông như *X*") hay lưu **operation** ("thêm comment này", "tăng counter này")? Snapshot thì gộp được — mười lần sửa cùng một note lúc offline có thể co lại thành một entry chờ, và server không bao giờ thấy các trạng thái trung gian. Operation không gộp được, nhưng nó giữ được ý định, điều quan trọng với mọi thứ mang tính cộng dồn hoặc số học. Một counter đồng bộ kiểu snapshot sẽ mất các lượt tăng đồng thời; cùng counter đó đồng bộ kiểu delta `+1` thì không. Phần lớn app muốn snapshot cho các entity thường và operation cho một nhúm thứ mang tính cộng dồn.

## Idempotency key biến "retry" từ bug thành tính năng

Ca trùng dữ liệu kinh điển của offline đến từ một request *đã thành công* nhưng response bị mất — timeout, socket reset, tiến trình bị kill, người dùng force-quit giữa chừng. Client không có cách nào phân biệt "chưa từng tới nơi" với "đã tới nơi mà tôi không nghe được hồi âm", nên một lần retry ngây thơ tạo ra row thứ hai.

Cách sửa nằm trên đường truyền, không nằm trong client: client gửi một khoá mà nó sinh ra đúng một lần, và server cam kết hai request mang cùng khoá đó chỉ tạo ra một tác động.

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

Hai tính chất làm nó hoạt động, và cả hai đều dễ làm sai:

1. **Khoá được sinh lúc lệnh ghi vào hàng đợi, không phải lúc gửi.** Nếu bạn sinh nó bên trong vòng retry, mỗi lần thử lại có một khoá mới và bạn chẳng được gì. Đó là lý do khoá chính là khoá chính của row outbox — về mặt vật lý nó không thể đổi qua các lần thử.
2. **Server phải lưu lại khoá và response mà nó đã tạo ra**, trong phạm vi người dùng đã xác thực, với thời gian giữ dài hơn backoff tối đa của bạn. Một lần phát lại trả về kết quả đã lưu. Server chỉ kiểm tra "có row nào mang khoá này chưa" thì đang làm cùng công việc nhưng kém tin cậy hơn.

`If-Match` kèm version server biết lần cuối là cơ chế đi kèm: nó biến một lần ghi đè âm thầm thành một `412`/`409` tường minh mà client xử lý được. Không có nó, last-write-wins không phải chiến lược bạn chọn — nó là mặc định bạn bị nhận.

Hãy ánh xạ response thành một quyết định, không phải thành một exception:

| Response | Nghĩa là | Vòng lặp làm gì |
| --- | --- | --- |
| `2xx` | Đã áp dụng | Xoá row outbox, ghi bản của server về máy |
| `409` / `412` | Server có version mới hơn | Chạy xử lý conflict |
| `400`, `403`, `404`, `422` | Lệnh ghi này sẽ không bao giờ thành công | Ngừng retry; bật cờ `needsAttention` |
| `408`, `429`, `5xx`, timeout, lỗi socket | Có thể thành công sau | Backoff rồi thử lại (tôn trọng `Retry-After` với `429`) |

Dòng thứ ba là dòng các đội hay quên. Một lỗi validation bị retry mãi mãi là một hàng đợi không bao giờ cạn và một viên pin không bao giờ được nghỉ.

## Vòng lặp sync, từ đầu tới cuối

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

Bốn chi tiết trong đó là chịu lực:

- **`return` ngay ở lần thất bại có-thể-thử-lại đầu tiên.** Nếu cứ chạy tiếp qua một entry đang kẹt, một lần sửa sau của cùng một row có thể tới đích trước lần sửa trước đó. Nếu các entity của bạn thật sự độc lập, bạn có thể chia hàng đợi theo `entityId` và rút cạn từng phân vùng theo thứ tự — nhưng hãy làm có chủ đích, đừng để nó xảy ra do vô tình.
- **Cờ single-flight `_running`.** Hai lượt rút cạn chạy song song sẽ đan xen request cho cùng một row.
- **Full jitter cho backoff.** Không có jitter, mọi thiết bị mất mạng cùng một khoảnh khắc sẽ retry cùng một khoảnh khắc, và API của bạn ăn nguyên một đợt thundering herd ngay giây mạng trở lại.
- **`_pullChanges()` chạy sau khi push.** Pull trước nghĩa là bạn ghi đè các row cục bộ bằng trạng thái server mà bạn sắp phủ định.

Phía pull cần một cursor, không phải một timestamp. Hỏi server "mọi thứ kể từ token *T*", áp dụng cả trang trong một transaction, lưu token mới trong cùng transaction đó, lặp lại tới khi server nói hết. Tham số `?updated_since=<clock>` trông có vẻ tương đương nhưng không phải: những row được ghi trong cùng giây với mốc cắt của bạn sẽ bị bỏ sót, và nó khiến tính đúng đắn phụ thuộc vào việc hai cái đồng hồ khác máy có khớp nhau hay không.

Về chạy nền: bạn không kiểm soát được thời điểm việc này chạy khi app đã đóng. WorkManager của Android và BackgroundTasks của Apple cho bạn những khung giờ mang tính cơ hội, chịu ràng buộc của Doze, của ngân sách, và của việc người dùng mở app thường xuyên tới đâu. Cứ nối chúng vào nếu bạn muốn, nhưng hãy thiết kế sản phẩm sao cho đồng bộ lúc foreground là đủ, và coi các lượt chạy nền là phần thưởng chứ không phải cam kết.

Có hai thiết lập SQLite đáng xác nhận thay vì mặc định tin: bật WAL, để lệnh ghi của sync engine không chặn lệnh đọc của UI, và cho database chạy ngoài UI isolate. Drift hỗ trợ database đặt trên isolate (`DriftIsolate`) và `drift_flutter` nối sẵn phần lớn chuyện này — hãy đọc tài liệu hiện hành của nó thay vì tin một đoạn snippet, vì mặc định ở đây đã đổi qua các phiên bản.

## Xử lý conflict là quyết định sản phẩm, không phải tính năng thư viện

Đây là phần người ta hay bỏ qua, và là phần quyết định người dùng có tin app của bạn hay không.

Không package nào xử lý conflict thay bạn. Package cho bạn *cơ chế* — một mã 409, một cột version, một hook merge. Còn *chính sách* — bản sửa nào thắng và ai được báo — là câu hỏi sản phẩm, và câu trả lời đúng khác nhau giữa một ghi chú, một giỏ hàng, và một số dư ngân hàng. Nếu một thư viện tuyên bố đã giải xong, hãy đọc xem nó thực sự làm gì; nó đã chọn last-write-wins thay bạn rồi.

| Chiến lược | Luật | Mất gì | Chọn khi |
| --- | --- | --- | --- |
| Last-write-wins | Version/timestamp cao hơn ghi đè | Bản sửa còn lại, một cách âm thầm | Ít tranh chấp, làm lại rẻ. Một người dùng, nhiều thiết bị |
| Server làm chủ | Server tính lại từ trạng thái của chính nó; client bỏ giá trị lạc quan và đọc lại | Phỏng đoán của client | Phải giữ bất biến: tồn kho, số dư, đặt chỗ, mọi thứ dính tiền |
| Merge theo từng field | Field chỉ đổi ở một phía thì merge; chỉ xung đột khi cùng một field | Không mất gì, trừ khi hai người sửa cùng một field | Bản ghi rộng với các field độc lập — hồ sơ, cài đặt, form dài |
| Append-only / log operation | Không tồn tại conflict; server quyết định thứ tự | Không mất gì | Chat, bình luận, feed hoạt động, counter biểu diễn dạng delta |
| Hỏi người dùng | Giữ cả hai bản và hiển thị diff | Sự kiên nhẫn của người dùng | Conflict hiếm, giá trị cao, không thể hoàn tác — ví dụ nội dung một tài liệu dài |

Cách chọn thật sự: hỏi người dùng mất gì khi bản sai thắng. Nếu câu trả lời là "họ gõ lại một câu", last-write-wins là đúng và mọi thứ cầu kỳ hơn đều lãng phí. Nếu câu trả lời là "chúng ta thu tiền họ hai lần" hoặc "chúng ta bán cùng một ghế cho hai người", thì không một phép merge phía client nào chấp nhận được — server sở hữu quyết định, còn việc của client là gửi lên một ý định kèm idempotency key và render lại bất cứ thứ gì server trả về.

Hai cái bẫy. **Last-write-wins dựa trên đồng hồ thiết bị không phải là last-write-wins.** Một máy có đồng hồ nhanh một ngày sẽ thắng mọi conflict cho tới khi thời gian thật đuổi kịp, còn một máy chậm một ngày sẽ âm thầm thua mọi lần sửa mà chủ nhân nó thực hiện. Nếu bạn cần LWW, hãy lấy thứ tự từ thứ server kiểm soát — một số thứ tự tăng đơn điệu, hoặc một hybrid logical clock mang theo bộ đếm bên cạnh giờ tường.

**Merge theo field cần ba bản, không phải hai.** Để biết một field có đổi hay không, bạn cần giá trị cục bộ, giá trị trên server, *và* tổ tiên chung — trạng thái server gần nhất mà thiết bị này từng thấy. Đó chính là việc của `baseJson` trong schema ở trên. Không có nó, bạn không phân biệt được "tôi đã đổi field này" với "tôi chưa hề đụng vào, chỉ là nó trông khác", và phép merge của bạn sẽ vui vẻ dựng lại những giá trị mà phía kia đã cố ý xoá.

CRDT là phiên bản có nền tảng lý thuyết của merge theo field, và với văn bản cộng tác thì nó là công cụ đúng. Trong Dart, hệ sinh thái mỏng hơn trên web, và chọn một CRDT nghĩa là cam kết dùng mô hình dữ liệu của nó ở mọi nơi, chứ không chỉ tại điểm merge. Đó là một cam kết kiến trúc nghiêm túc — đáng cho một trình soạn thảo cộng tác, quá cỡ cho một app to-do.

## Hiển thị trạng thái sync mà không nói dối người dùng

Kiểu hỏng ở đây là một dấu tích xanh có nghĩa "đã ghi vào SQLite" nhưng người dùng đọc thành "đã an toàn trên server". Khi họ reset máy và mất một tuần ghi chú, cái dấu tích đó là thứ họ sẽ nhớ.

Các trạng thái trung thực, và mỗi trạng thái được phép tuyên bố gì:

- **Đã lưu trên máy này** — transaction đã commit. Hãy nói rõ *trên máy này*. Đây là trạng thái người dùng thấy ngay khoảnh khắc họ ngừng gõ, và nó là một tuyên bố mạnh thật sự: nó sống sót qua crash và qua khởi động lại.
- **Đang đồng bộ** — có một entry outbox cho row này đang bay. Thường không đáng làm chỉ báo cho từng row; một chỉ báo toàn cục kín đáo là đủ.
- **Đang chờ đồng bộ** — đã xếp hàng, sẽ đi khi mạng cho phép. Hãy hiện số mục đang chờ, đừng hiện spinner. Một spinner không có điểm kết thúc là một lời nói dối về tiến độ.
- **Cần bạn xử lý** — server đã từ chối và không lần retry nào cứu được. Trạng thái này *bắt buộc* phải tới được từ UI. Một lệnh ghi bị từ chối mà không có chỗ hiển thị là dữ liệu mà người dùng tin đã lưu và sẽ không bao giờ tồn tại ở đâu cả.

Vài quy tắc đi theo. Đừng bao giờ chặn điều hướng hay hiện dialog spinner khi lưu — việc lưu đã xong rồi, và một hộp thoại "đang lưu…" trên một transaction cục bộ dạy người dùng rằng app của bạn chậm, trong khi sự thật là ngược lại.

Cẩn thận với banner offline. `connectivity_plus` báo interface mạng nào đang hoạt động — nó không hứa Internet tới được, và nó sẽ vui vẻ báo Wi‑Fi khoẻ mạnh trong khi một captive portal nuốt sạch mọi request. Hãy suy ra banner từ bằng chứng của chính bạn: lần sync gần nhất có thành công không, và outbox có đang cạn dần không. Dùng sự kiện connectivity làm tín hiệu để thử lại, đừng dùng làm sự thật để hiển thị. Và hãy cho trạng thái pending hiện ra ở nơi nó làm thay đổi hành vi, giấu nó ở nơi không: một badge pending trên mọi row trong danh sách là nhiễu, còn một chip duy nhất "3 thay đổi đang chờ đồng bộ" trên app bar, bấm vào ra màn hình liệt kê chúng và cho người dùng thử lại hoặc bỏ đi, mới là thông tin.

Cuối cùng, khi một conflict được giải theo hướng vứt bỏ bản sửa của người dùng, hãy nói ra. Một snackbar một dòng — "Ghi chú này đã được cập nhật trên thiết bị khác; bản của bạn đã bị thay thế" kèm nút hoàn tác — gần như không tốn gì, và nó là ranh giới giữa một chính sách xử lý conflict và một bug mất dữ liệu.

## FAQ

**Tôi có bắt buộc dùng Drift không, hay làm được bằng sqflite?**

Bạn làm được toàn bộ bằng `sqflite`; outbox chỉ là một cái bảng và vòng lặp sync chỉ là SQL. Thứ bạn đánh đổi là query có kiểu, migration sinh tự động, và `watch()` — bạn sẽ phải tự dựng cơ chế báo thay đổi, và đó là phần dễ sai một cách tinh vi nhất. Chọn `sqflite` khi schema rất nhỏ và việc thêm `build_runner` vào dự án là một chi phí thật.

**Idempotency key phải được thực thi ở đâu — client hay server?**

Server. Việc duy nhất của client là sinh khoá một lần và gửi lại đúng khoá đó ở mọi lần thử. Nếu server không khử trùng lặp theo khoá đó thì cái header chỉ là đồ trang trí, và một response bị mất vẫn tạo ra bản ghi trùng. Nếu bạn không kiểm soát API, đây là thứ đáng yêu cầu nhất từ đội backend.

**Tôi cứ dùng last-write-wins ở mọi nơi rồi đi tiếp có được không?**

Thường là được — với app một người dùng nhiều thiết bị và ít tranh chấp, đó là lựa chọn kỹ thuật đúng chứ không phải đi đường tắt. Thứ bạn không được làm là dùng nó cho các bản ghi có bất biến (tiền, tồn kho, sức chứa), hoặc để đồng hồ thiết bị điều khiển nó. Hãy quyết định tường minh, ghi vào tài liệu thiết kế, và bảo đảm một lần sửa bị vứt đi sẽ tạo ra một thông báo chứ không phải sự im lặng.

**Làm sao để database cục bộ không phình mãi?**

Dọn tombstone khi server đã xác nhận xoá, xoá row outbox khi thành công, và giới hạn lịch sử cho các bảng thay đổi nhiều. Với tập dữ liệu lớn, hãy đồng bộ một cửa sổ thay vì tất cả — N mục gần nhất cộng những gì người dùng đã mở — rồi tải các bản ghi cũ theo yêu cầu, chấp nhận rằng đó chính là những thứ sẽ không có mặt khi bạn ở trên máy bay.

**Chuyện này có chạy trên Flutter web không?**

Drift hỗ trợ web qua bản WASM của SQLite, với phần lưu trữ dựa trên storage của trình duyệt. Nó chạy được, nhưng bảo đảm lưu trữ là của trình duyệt chứ không phải của hệ điều hành — dữ liệu của một origin có thể bị dọn khi máy thiếu chỗ, và các bước cài đặt khác với mobile. Nếu web là nền tảng chính, hãy kiểm tra tình trạng lưu trữ hiện tại trong tài liệu Drift trước khi hứa với người dùng rằng các sửa đổi offline của họ là bền vững.

---

*Phần ý kiến ở đây: việc chọn Drift, kiểu rút cạn FIFO có dừng, và cách diễn đạt cụ thể trên UI. Phần sự kiện: mẫu outbox cộng idempotency key, kiểu hỏng của last-write-wins dựa trên đồng hồ, và việc cần một tổ tiên chung để merge ba chiều theo field. API của package và luật chạy nền của nền tảng thay đổi giữa các phiên bản — hãy đối chiếu mọi thứ phụ thuộc phiên bản với tài liệu được dẫn ở trên trước khi ship.*
