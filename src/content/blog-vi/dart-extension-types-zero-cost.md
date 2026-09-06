---
title: "Extension type trong Dart: một cái tên mới cho giá trị cũ"
description: "Extension type cho một kiểu nguyên thuỷ một kiểu tĩnh riêng biệt mà không cấp phát lúc chạy. Đó là công cụ thật sự hữu ích cho lỗi nhầm ID và nhầm đơn vị — và là cái bẫy nếu bạn mong chúng hành xử như class."
seoDescription: "Giải thích extension type trong Dart: lớp bọc không chi phí trên kiểu biểu diễn, vì sao chúng không tồn tại lúc chạy, khác gì extension method và class bọc, và chúng gãy ở đâu."
keywords:
  - extension type dart
  - dart lop boc khong chi phi
  - typedef va extension type dart
  - dart primitive obsession
  - kieu bieu dien dart
  - khac biet extension method dart
category: "Chuyên sâu"
topic: "Dart"
level: "Nâng cao"
author: "Trung Hiếu"
publishDate: "2026-08-14"
emoji: "🧬"
tags: ["Dart", "Ngôn ngữ", "Kiểu dữ liệu", "Hiệu năng", "Thiết kế API"]
sources:
  - name: "Extension types — tài liệu Dart"
    url: "https://dart.dev/language/extension-types"
  - name: "Extension methods — tài liệu Dart"
    url: "https://dart.dev/language/extension-methods"
  - name: "Typedefs — tài liệu Dart"
    url: "https://dart.dev/language/typedefs"
  - name: "Class modifiers — tài liệu Dart"
    url: "https://dart.dev/language/class-modifiers"
  - name: "dart:js_interop — tài liệu Dart API"
    url: "https://api.dart.dev/stable/dart-js_interop/dart-js_interop-library.html"
  - name: "Type system — tài liệu Dart"
    url: "https://dart.dev/language/type-system"
related:
  - slug: "dart-records-and-patterns"
    title: "Record và pattern trong Dart: chúng thay thế những gì"
  - slug: "dart-streams-in-depth"
    title: "Stream trong Dart chuyên sâu: backpressure, broadcast và những rò rỉ ở giữa"
draft: false
---

Mọi codebase vượt qua một kích thước nhất định đều dính lỗi này ít nhất một lần:

```dart
void transfer(String fromUserId, String toAccountId, int cents) { ... }

transfer(accountId, userId, 500); // biên dịch ngon lành, sai lúc chạy
```

Cả hai đều là `String`, nên hệ thống kiểu không có gì để nói. Cách sửa thường thấy là một class bọc, và nó tốn một lần cấp phát cho mỗi ID bạn chạm vào. Extension type là đúng cách sửa đó nhưng không cấp phát.

```dart
extension type UserId(String value) {}
extension type AccountId(String value) {}

void transfer(UserId from, AccountId to, int cents) { ... }

transfer(accountId, userId, 500); // lỗi biên dịch
```

Lúc chạy, `UserId` **chính là** một `String`. Không có đối tượng bọc, không có truy cập trường gián tiếp, không cấp phát gì cả. Sự phân biệt chỉ tồn tại trong hệ thống kiểu tĩnh, và bị xoá đi trước khi chương trình chạy.

## "Bị xoá" thật sự nghĩa là gì

Đây là phần quyết định extension type có hợp với bài toán của bạn hay không. Trình biên dịch thay extension type bằng kiểu biểu diễn của nó. Các hệ quả theo sau trực tiếp:

```dart
extension type UserId(String value) {}

final id = UserId('u_123');

print(id is String);       // true
print(id.runtimeType);     // String
print(id is UserId);       // đây là kiểm tra lúc biên dịch, không phải lúc chạy

// Và quan trọng nhất:
final list = <Object>[UserId('a'), 'a'];
print(list[0] == list[1]); // true — cả hai đều là chuỗi 'a'
```

Vậy nên extension type chỉ cho bạn sự phân biệt **lúc biên dịch**. Nếu mã của bạn rẽ nhánh theo `runtimeType`, lưu giá trị vào một danh sách hỗn tạp rồi switch theo kiểu của chúng, hoặc dựa vào kiểm tra `is` lúc chạy để phân biệt các ID, thì extension type sẽ không làm được. Một class bọc thì làm được.

Hệ quả thứ hai: extension type không phải kiểu con theo nghĩa thông thường, và bạn không thể bắt một extension type triển khai một interface trừ khi kiểu biểu diễn của nó đã triển khai. `extension type UserId(String value) implements Comparable<UserId>` sẽ không biên dịch được chỉ vì bạn muốn thế.

## Kiểm soát bề mặt API

Mặc định, một extension type không lộ ra **bất cứ gì** từ kiểu biểu diễn:

```dart
extension type UserId(String value) {}

final id = UserId('u_123');
id.length;        // lỗi biên dịch — thành viên của String không được kế thừa
id.value.length;  // được
```

Đó thường là điều bạn muốn với một ID: `UserId` không phải chuỗi để bạn viết hoa. Khi bạn thật sự cần API bên dưới, hãy khai báo tường minh:

```dart
extension type Meters(double value) implements Comparable<num> {
  Meters operator +(Meters other) => Meters(value + other.value);
  Meters operator *(double k) => Meters(value * k);
  double get inFeet => value * 3.28084;

  @override
  int compareTo(num other) => value.compareTo(other);
}

final total = Meters(4.5) + Meters(2.0);
print(total.inFeet);
```

`implements` ở đây không có nghĩa kế thừa — nó có nghĩa "cho phép những thành viên này đi qua, và coi kiểu này gán được cho kiểu kia". Lưu ý `implements num` sẽ khiến `Meters` gán tự do được cho `num`, tức là vứt đi chính sự an toàn bạn vừa thêm vào; hãy dè sẻn với những gì bạn cho lộ ra.

So sánh với các lựa chọn khác:

| Cách làm | Chi phí lúc chạy | Phân biệt lúc biên dịch | Phân biệt lúc chạy | Thêm được phương thức |
| --- | --- | --- | --- | --- |
| `typedef UserId = String` | không | không | không | không |
| `extension on String` | không | không | không | có (trên mọi String) |
| `extension type UserId(String)` | không | có | không | có |
| `class UserId { final String v; }` | cấp phát | có | có | có |

Dòng đáng nhìn kỹ là dòng thứ hai: một extension method thêm hành vi "kiểu UserId" vào **mọi** `String` trong chương trình của bạn. Extension type chỉ thêm vào một kiểu có tên.

## Trường hợp interop

Extension type được thiết kế song song với `dart:js_interop`, và đó là nơi chúng ít mang tính tuỳ chọn nhất. Một đối tượng JavaScript đi vào Dart không có class Dart nào; mô hình hoá nó thành extension type trên `JSObject` cho bạn một API có kiểu mà không tốn chi phí chuyển đổi:

```dart
extension type DomRect._(JSObject _) implements JSObject {
  external double get width;
  external double get height;
}
```

Dấu `._` đặt tên cho một constructor riêng tư, đây là quy ước cho ý "giá trị này đến từ nơi khác, đừng tự tay tạo ra nó".

## Tôi dùng chúng ở đâu, và không dùng ở đâu

Dùng cho:

- **ID và handle mờ.** `UserId`, `SessionToken`, `Sku`. Trường hợp kinh điển.
- **Đơn vị đo.** `Meters`, `Cents`, `Milliseconds`. Nhầm đơn vị là một nhóm lỗi có thật, và một lần cấp phát cho mỗi giá trị là chi phí có thật trong đường nóng.
- **Chuỗi đã xác thực** khi việc xác thực chỉ diễn ra một lần ở biên — `Email`, `Slug` — thông qua một factory ném lỗi hoặc trả về null.
- **Lớp bọc interop**, như trên.

Không dùng cho:

- Bất cứ thứ gì bạn cần kiểm tra bằng `is` lúc chạy.
- Bất cứ thứ gì lưu hỗn tạp rồi phân phối theo kiểu.
- Model nghiệp vụ. `User` nên là một class; nó có những bất biến mà extension type không ép được và ngữ nghĩa định danh mà extension type không cho được.
- Giá trị bạn tuần tự hoá bằng bộ sinh mã dựa trên kiểu lúc chạy — bộ sinh mã nhìn thấy `String`, không phải `UserId`.

**Tóm tắt thành thật là extension type giải quyết trọn vẹn một bài toán hẹp.** Chúng không phải class nhẹ hơn; chúng là một lớp đặt tên chỉ có ở mức tĩnh kèm một cửa thoát. Với tới chúng ở nơi mà bạn thật ra cần một class sẽ tạo ra mã biên dịch rất đẹp và hành xử rất bất ngờ.

Một ví dụ có xác thực, vì đây là mẫu đáng chép lại nhất:

```dart
extension type const Email._(String value) {
  static final _re = RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$');

  factory Email(String raw) {
    final trimmed = raw.trim();
    if (!_re.hasMatch(trimmed)) {
      throw FormatException('Không phải email: $raw');
    }
    return Email._(trimmed);
  }

  static Email? tryParse(String raw) =>
      _re.hasMatch(raw.trim()) ? Email._(raw.trim()) : null;
}
```

Giờ một hàm nhận `Email` có bảo đảm tĩnh rằng việc xác thực đã chạy rồi, với chi phí lúc chạy bằng không, và trong codebase chỉ có đúng một nơi chứa logic xác thực đó.

## Câu hỏi thường gặp

**Extension type có giống value class của Kotlin không?**

Ý đồ giống nhau, cơ chế khác nhau. Inline class của Kotlin vẫn có thể bị đóng hộp trong một số tình huống; extension type của Dart hoàn toàn không tồn tại lúc chạy.

**Tôi dùng nó làm khoá map được không?**

Được, và nó hành xử đúng như kiểu biểu diễn — `UserId('a')` và chuỗi thường `'a'` là cùng một khoá. Điều đó đôi khi tiện và đôi khi là lỗi.

**Chúng có dùng được với `const` không?**

Có: `extension type const Email._(String value)` cho phép tạo const khi biểu diễn là const.

**Hai extension type trên cùng một kiểu biểu diễn có gán cho nhau được không?**

Không trực tiếp — đó chính là toàn bộ mục đích. Hãy chuyển đổi tường minh qua `.value`.

**Tôi có nên thêm `implements` để lấy các phương thức bên dưới không?**

Chỉ với những phương thức bạn thật sự cần. Mỗi thành viên bạn cho lộ ra là một đường để sự phân biệt rò rỉ mất.

---

*Ngữ nghĩa xoá kiểu, bề mặt thành viên mặc định, hành vi của `implements` và cách dùng với `dart:js_interop` mô tả ở đây đều nằm trong tài liệu Dart liên kết bên trên. Danh sách nên/không nên dùng, cách đọc thực tế bảng so sánh và mẫu `Email` có xác thực là đánh giá riêng của tôi từ việc áp dụng extension type trong mã sản phẩm. Hãy kiểm chứng hành vi với phiên bản Dart SDK mà dự án bạn nhắm tới.*
