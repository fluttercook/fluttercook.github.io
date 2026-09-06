---
title: "Record và pattern trong Dart: chúng thay thế những gì"
description: "Record cho bạn nhiều giá trị trả về mà không cần class. Pattern cho bạn phá cấu trúc và switch vét cạn. Kết hợp lại, chúng xoá bỏ cả một nhóm mã lặp — và hình thành vài thói quen nên rèn sớm."
seoDescription: "Giải thích record và pattern matching trong Dart: trường vị trí và trường có tên, destructuring, switch expression, tính vét cạn với sealed class, guard, và khi nào record là lựa chọn sai."
keywords:
  - record dart huong dan
  - pattern matching dart switch
  - destructuring dart
  - sealed class dart vet can
  - switch expression dart
  - dart tra ve nhieu gia tri
category: "Chuyên sâu"
topic: "Dart"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-15"
emoji: "🎯"
tags: ["Dart", "Ngôn ngữ", "Pattern", "Record", "Kiểu dữ liệu"]
sources:
  - name: "Records — tài liệu Dart"
    url: "https://dart.dev/language/records"
  - name: "Patterns — tài liệu Dart"
    url: "https://dart.dev/language/patterns"
  - name: "Pattern types — tài liệu Dart"
    url: "https://dart.dev/language/pattern-types"
  - name: "Branches — tài liệu Dart"
    url: "https://dart.dev/language/branches"
  - name: "Class modifiers — tài liệu Dart"
    url: "https://dart.dev/language/class-modifiers"
  - name: "Destructuring — tài liệu ngôn ngữ Dart"
    url: "https://dart.dev/language/patterns#destructuring"
related:
  - slug: "dart-extension-types-zero-cost"
    title: "Extension type trong Dart: một cái tên mới cho giá trị cũ"
  - slug: "flutter-state-management-decision-guide"
    title: "Riverpod, Bloc, signals hay setState: chọn cách quản lý state Flutter và sống chung với nó"
draft: false
---

Trước khi có record, trả về hai giá trị từ một hàm nghĩa là chọn một trong ba lựa chọn đều không hấp dẫn: một class chỉ dùng một lần, một `List<Object>` mà bạn phải truy cập theo chỉ số, hoặc hai tham số ra thông qua một lớp bọc. Record biến nó thành một dòng.

```dart
({int width, int height}) measure(String text) {
  // ...
  return (width: 120, height: 40);
}

final size = measure('hello');
print(size.width);
```

Đó là tính năng nổi bật nhất, và nó là phần nhỏ nhất trong những gì record cùng pattern đã thay đổi.

## Record: theo cấu trúc, không theo tên

Kiểu của một record chính là hình dạng của nó. `(int, String)` và `(int, String)` là cùng một kiểu bất kể chúng được tạo ở đâu, và đó là điểm phân biệt record với class.

```dart
// Theo vị trí
(String, int) parseEntry(String line) {
  final parts = line.split(':');
  return (parts[0], int.parse(parts[1]));
}

// Có tên — rõ ràng hơn ở nơi gọi
({String name, int score}) parseNamed(String line) {
  final parts = line.split(':');
  return (name: parts[0], score: int.parse(parts[1]));
}

// Trộn cả hai
(String, {bool valid}) check(String input) => (input.trim(), valid: true);
```

Record **bất biến và so sánh bằng theo cấu trúc**, điều này hữu ích hơn vẻ ngoài của nó:

```dart
final a = (1, 'x');
final b = (1, 'x');
print(a == b); // true — không cần viết operator==
```

Nhờ vậy chúng là khoá map ghép cực tốt:

```dart
final cache = <(int, int), Tile>{};
cache[(3, 7)] = tile;
```

Trước khi có record, việc này đòi hỏi một class khoá với `==` và `hashCode`, hoặc một chuỗi kiểu `'3,7'`. Cả hai đều chạy được; không cái nào tốt bằng.

## Pattern: phá cấu trúc

Một pattern nằm bên trái dấu `=` sẽ tháo rời một giá trị:

```dart
final (name, score) = parseEntry(line);
final (:width, :height) = measure(text);   // rút gọn cho trường có tên

// Trong vòng lặp for trên một map
for (final MapEntry(key: id, value: user) in users.entries) {
  print('$id → ${user.name}');
}
```

Cách viết tắt `:width` khai báo một biến trùng tên với trường, và đây là dạng bạn sẽ dùng nhiều nhất.

Pattern cũng dùng được trong `if-case`, cách gọn nhất để gộp kiểm tra kiểu với phá cấu trúc:

```dart
if (response case {'data': {'items': List<Map<String, Object?>> items}}) {
  return items.map(Item.fromJson).toList();
}
```

Một dòng đó kiểm tra rằng `response` là map, rằng nó có khoá `data` chứa một map, rằng map ấy có khoá `items`, và rằng giá trị của khoá này là danh sách các map — chỉ gán `items` khi tất cả đều đúng. Cách thay thế là năm tầng kiểm tra null và kiểm tra kiểu lồng nhau.

**Đây là tính năng pattern hữu dụng nhất trên thực tế với bất kỳ ai phải phân tích JSON.** Nó không thay thế một model class thật, nhưng nó khiến đoạn mã ở biên — nơi bạn xác thực dữ liệu không có kiểu — ngắn hơn hẳn và khó sai một cách âm thầm hơn nhiều.

## Switch expression và tính vét cạn

Switch đã trở thành một biểu thức, và điều đó thay đổi cách bạn viết mã ánh xạ:

```dart
String describe(Shape shape) => switch (shape) {
  Circle(radius: final r) when r > 100 => 'hình tròn rất lớn',
  Circle(radius: final r) => 'hình tròn bán kính $r',
  Rectangle(width: final w, height: final h) when w == h => 'hình vuông cạnh $w',
  Rectangle() => 'hình chữ nhật',
};
```

Ba việc đang diễn ra cùng lúc: kiểm tra kiểu, phá cấu trúc, và một guard `when`, tất cả nằm trong pattern của case.

Tính năng khiến điều này thật sự an toàn hơn là **kiểm tra vét cạn trên cây sealed**:

```dart
sealed class Result<T> {}
final class Ok<T> extends Result<T> {
  const Ok(this.value);
  final T value;
}
final class Err<T> extends Result<T> {
  const Err(this.message);
  final String message;
}

String render(Result<int> r) => switch (r) {
  Ok(value: final v) => 'Nhận được $v',
  Err(message: final m) => 'Thất bại: $m',
};
```

Không có nhánh mặc định. Thêm một lớp con thứ ba và **mọi** switch trên `Result` sẽ thành lỗi biên dịch, liệt kê chính xác những file cần cập nhật. Trải nghiệm đó khác hẳn về bản chất so với việc phát hiện lỗ hổng lúc chạy, và nó là lập luận mạnh nhất cho việc mô hình hoá trạng thái bằng cây sealed thay vì bằng một class với các trường nullable.

Chú ý sự vắng mặt có chủ ý của `default:` — thêm nó vào sẽ tắt kiểm tra vét cạn và trả lại đúng thứ bảo đảm mà bạn tìm đến.

## Khi record là công cụ sai

Record là vô danh, và sự vô danh có cái giá của nó:

- **Chúng không có phương thức.** `(double lat, double lng)` không mang theo được `distanceTo`. Một class thì có.
- **Chúng không ép được bất biến logic.** Không có constructor nghĩa là không có kiểm tra. Record không đảm bảo được `lat` nằm trong khoảng hợp lệ.
- **Tên trường chính là API.** Đổi `width` thành `w` là mọi nơi gọi đều hỏng, không có lộ trình deprecate nào.
- **Chúng là tài liệu tồi.** `({String, String})` ở biên API công khai không cho người đọc biết cái nào là cái nào.

Quy tắc của tôi: **record cho đường ống nội bộ, class cho khái niệm.** Một hàm trả về "giá trị đã phân tích và nó có từ cache hay không" là đường ống. `User` là khái niệm. Bất cứ thứ gì vượt biên giới package hoặc xuất hiện trong API công khai nên là kiểu có tên.

## Chuyển đổi dần dần

Không phần nào ở đây đòi hỏi viết lại thứ gì. Ba thay đổi mang lại lợi ích ngay trong mã hiện có:

1. Thay các hàm trợ giúp riêng tư trả về `Map<String, dynamic>` bằng record — cùng hình dạng, an toàn kiểu thật sự.
2. Thay các chuỗi `if/else if` kiểm tra kiểu dài dòng bằng một switch expression.
3. Biến các class trạng thái có trường `isLoading`/`error`/`data` thành cây sealed, để những trạng thái bất khả thi ngừng biên dịch được.

Điều thứ ba là điều làm thay đổi cảm giác khi viết mã. Một class trạng thái với ba trường nullable có tám tổ hợp biểu diễn được và thường chỉ ba tổ hợp hợp lệ; một cây sealed chỉ có đúng những tổ hợp hợp lệ.

## Câu hỏi thường gặp

**Record có chi phí lúc chạy không?**

Chúng là đối tượng nên có một lần cấp phát, nhưng chúng nhẹ và trình biên dịch tối ưu các trường hợp phổ biến. Đây không phải lý do để tránh dùng chúng trong mã thông thường.

**Tôi dùng record trong ngữ cảnh `const` được không?**

Được, nếu mọi trường đều là hằng: `const point = (x: 1, y: 2);`.

**Pattern tương tác với null safety thế nào?**

Rất tốt. `case final String s?` khớp chuỗi khác null; `case null` khớp null. Tính vét cạn có tính đến nullable, nên switch trên `String?` cần một case null hoặc một case bắt tất cả.

**Sealed class có nên thay thế enum không?**

Chỉ khi các biến thể mang theo dữ liệu. Một enum không có dữ liệu kèm theo vẫn đơn giản hơn, và enum cũng hỗ trợ switch vét cạn.

**`when` có giống một `if` lồng bên trong không?**

Về mặt chức năng thì có, nhưng guard tham gia vào chính case nên thứ tự và độ dễ đọc đều tốt hơn. Lưu ý guard không được tính vào tính vét cạn — trình biên dịch không thể chứng minh một case có guard luôn khớp.

---

*Cú pháp record, so sánh bằng theo cấu trúc, các dạng pattern và quy tắc vét cạn cho cây sealed mô tả ở đây đều nằm trong tài liệu tham chiếu Dart liên kết bên trên. Quy tắc record-cho-đường-ống, khuyến nghị dùng ở biên JSON, danh sách chuyển đổi và cảnh báo `default:` phá vỡ tính vét cạn là đánh giá riêng của tôi từ việc dùng những tính năng này trong mã sản phẩm. Tính năng ngôn ngữ luôn tiến hoá — hãy kiểm tra phiên bản Dart SDK mà dự án bạn nhắm tới.*
