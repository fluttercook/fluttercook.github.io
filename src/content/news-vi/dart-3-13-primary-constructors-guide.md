---
title: "Primary constructor trong Dart 3.13: bớt boilerplate, một thay đổi phá vỡ thật sự"
description: "Primary constructor đã stable ở Dart 3.13. Đây là cú pháp đầy đủ, cách declaring parameter hoạt động, dạng const và named, và thay đổi phá vỡ với final/var trên tham số hàm."
seoDescription: "Hướng dẫn primary constructor Dart 3.13: declaring parameter với var và final, primary constructor named và const, super parameter, quy tắc scope, và lint parameter_assignments."
keywords: ["dart 3.13", "primary constructor dart", "declaring parameter dart", "cú pháp const constructor dart", "lint parameter_assignments", "thay đổi phá vỡ dart 3.13"]
category: "Flutter"
topic: "Flutter"
author: "FlutterCook Editorial"
publishDate: "2026-08-16"
updatedDate: "2026-08-16"
emoji: "🎯"
tags: ["Dart 3.13", "Dart", "Ngôn ngữ", "Flutter 3.47", "Refactoring"]
sources:
  - name: "Announcing Dart 3.13 — Dart Blog"
    url: "https://dart.dev/blog/announcing-dart-3-13"
  - name: "Primary constructors — Dart language docs"
    url: "https://dart.dev/language/primary-constructors"
  - name: "Constructors — Dart language docs"
    url: "https://dart.dev/language/constructors"
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
related:
  - slug: "flutter-3-47-standalone-material-cupertino-impeller-desktop"
    title: "Flutter 3.47: Material và Cupertino rời khỏi SDK, Impeller tiếp quản desktop"
  - slug: "flutter-2026-roadmap-webassembly-platform-parity"
    title: "Lộ trình Flutter 2026: WebAssembly mặc định, TV LG, và cú đẩy cho ngang tầm bản địa"
draft: false
---

Dart 3.13 ra cùng Flutter 3.47, và tính năng tiêu điểm là thứ lập trình viên Dart đòi từ hồi ngôn ngữ có null safety: **primary constructor đã stable**. Khai báo field và constructor ngay trên header của class, và xoá đi ba dòng nghi thức mà mọi class model trong codebase của bạn đang lặp lại.

Trong bản phát hành cũng có một thay đổi phá vỡ ẩn mình, và nó không phải thứ phần lớn mọi người đoán.

## Hình dạng cơ bản

Dạng truyền thống:

```dart
class Point {
  int x;
  int y;
  Point(this.x, this.y);
}
```

Dạng primary constructor:

```dart
class Point(var int x, var int y);
```

Đó là toàn bộ class. Chú ý thứ tự — modifier đứng trước, rồi tới kiểu, rồi tới tên: `var int x`, không phải `int var x`.

## Declaring parameter mới là tính năng thật

Đây là phần đáng hiểu cho kỹ, vì thiết kế ở đây tinh tế hơn câu "cú pháp ngắn hơn".

Một tham số có tiền tố `var` hoặc `final` là **declaring parameter**: nó sinh ra một instance field. Tham số không có modifier nào hành xử như một đối số constructor thông thường và không tạo field nào cả.

```dart
// Tạo field x và y
class Point(var int x, var int y);

// Không tạo field — `name` chỉ là đối số
class User(String name);
```

Sự phân biệt đó cho bạn miễn phí một constructor chỉ để validate, mà không cần mẹo tạo một field private chẳng bao giờ đọc.

Với model bất biến — tức là phần lớn model trong một codebase Flutter — hãy dùng `final`:

```dart
class ConstPoint(final int x, final int y);
```

## Named parameter, và mẹo dấu gạch dưới

Named parameter hoạt động như bạn nghĩ, kèm một chi tiết hay: một named parameter private tự động phơi ra một tên public cho phía gọi.

```dart
class User({required var String _name});
// Gọi bằng: User(name: 'John Doe')
```

Field là `_name`, private trong thư viện. Nhãn đối số là `name`, public. Bạn có đóng gói mà không phải viết một constructor để ánh xạ cái này sang cái kia.

## Primary constructor có tên và private

Thêm dấu chấm và một cái tên sau định danh class:

```dart
class Point.custom(var int x, var int y);

// Private — hạn chế khởi tạo trực tiếp từ ngoài thư viện
class Point._(var int x, var int y);
```

Dạng private chính là mẫu "gần như sealed" mà nhiều package đang tự cài đặt bằng tay hôm nay.

## Primary constructor const

Đặt `const` trước danh sách tham số:

```dart
class ConstPoint const (final int x, final int y) {
  final int z;
  this : z = x + y;
}
```

Các ràng buộc đúng như bạn đoán từ ngữ nghĩa `const`:

- không có khối thân
- mọi field phải `final` và chắc chắn được khởi tạo
- biểu thức khởi tạo phải có khả năng là hằng

Với Flutter điều này quan trọng hơn vẻ ngoài. Constructor widget const là một đòn bẩy hiệu năng thật, và bất cứ thứ gì làm chúng rẻ hơn để viết đều khiến chúng được viết nhiều hơn.

## Thêm thân mà không phải bỏ header

Bạn không phải chọn giữa primary constructor và logic constructor. `this :` mở ra một initializer list, một thân, hoặc cả hai:

```dart
class Point(var int x, var int y) {
  this : assert(x >= 0 && y >= 0) {
    print('Point initialized at ($x, $y)');
  }
}
```

Super parameter chuyển tiếp gọn gàng:

```dart
class Person(final String name, final int age);

class Employee(super.name, super.age, final String role) extends Person;
```

## Quy tắc scope sẽ làm bạn vấp

Có hai scope, và chúng phân giải cùng một định danh theo cách khác nhau:

| Scope | Ở đâu | `x` trỏ tới |
| --- | --- | --- |
| Primary initializer scope | Khởi tạo field, initializer list | **tham số** |
| Primary parameter scope | Thân constructor | **field** (với declaring parameter) |

Cụ thể:

```dart
class ScopingDemo(var String x, String suffix) {
  final String field = x;  // 'x' là tham số

  this : {
    x = x.toUpperCase();   // 'x' giờ trỏ tới field
    print('$x$suffix');    // 'suffix' vẫn là tham số
  }
}
```

Hãy đọc hai lần trước khi refactor một class có initializer list không tầm thường. Nó nhất quán, nhưng không hiển nhiên.

## Ràng buộc

Các ràng buộc lúc biên dịch đáng biết trước khi bạn bắt đầu chuyển đổi class:

- declaring parameter không được dùng `late` hay `external`
- tên tham số không được trùng method hoặc field đã có
- tham số là chỉ đọc bên trong primary initializer scope
- không được khởi tạo một field ở cả chỗ khai báo lẫn trong primary constructor
- class mixin chỉ được khai báo primary constructor tầm thường — không tham số, không initializer list, không thân
- `covariant` chỉ hoạt động với declaring parameter khả biến (`var`)

## Thay đổi phá vỡ

Đây là phần cần lên kế hoạch. **`final` và `var` trên tham số hàm thông thường giờ dành riêng cho declaring parameter của primary constructor.** Code hiện có viết `void f(final int x)` trở thành không hợp lệ.

Câu chuyện lint đổi theo: `parameter_assignments` (Dart 3.13+) thay cho `avoid_final_parameters` và `var_with_no_type_annotation` cũ từ 3.12 trở về trước.

Còn một cạm bẫy thứ hai, âm thầm hơn: một method tên `factory` không có kiểu trả về tường minh giờ có thể bị phân tích nhầm thành factory constructor. Nếu bạn có, hãy thêm chú thích kiểu trả về.

## Còn gì nữa trong 3.13

Ngoài thay đổi ngôn ngữ:

- **dart2wasm deferred loading (preview)** — `dart compile wasm -O2 --enable-deferred-loading`, cải thiện đáng kể thời gian tải trang lần đầu so với `dart2js` cho app lớn
- **`@RecordUse()`** trong `package:meta`, cho phép tree-shake thư viện native song song với code Dart
- **tinh chỉnh formatter** — sửa lỗi định dạng sai quanh các collection literal lớn, cải thiện heuristic ngắt chuỗi method, và thêm dòng trống giữa các nhóm import theo Effective Dart
- **sửa tính đúng đắn của type promotion** cho hàm lồng nhau
- **dartdoc render nhanh hơn** trên pub.dev nhờ chỉ mục băm hai tầng

## Áp dụng mà không gây xáo trộn

1. **Nâng cấp và build.** Sửa mọi tham số kiểu `void f(final int x)` mà analyzer giờ từ chối.
2. **Thêm kiểu trả về tường minh** cho mọi method tên `factory`.
3. **Bật `parameter_assignments`** và gỡ `avoid_final_parameters` / `var_with_no_type_annotation` khỏi `analysis_options.yaml`.
4. **Bắt đầu với class dữ liệu thuần** — DTO, value object, model kiểu `freezed`. Giảm boilerplate nhiều nhất, rủi ro thấp nhất.
5. **Dùng bốn refactoring trong IDE** để chuyển qua lại giữa primary constructor và constructor trong thân, thay vì sửa tay.
6. **Chuyển constructor widget const tiếp theo**, khi bạn đã quen với ràng buộc của dạng const.
7. **Để dành class có initializer list phức tạp sau cùng**, và đọc lại bảng scope trước khi động vào.

## Kết luận

Primary constructor là loại tính năng ngôn ngữ hiếm hoi mang tính thuần trừ đi: cùng ngữ nghĩa, gõ ít hơn, không thêm khái niệm mới một khi bạn hiểu declaring parameter. Ràng buộc `var`/`final` trên tham số hàm là thay đổi phá vỡ thật, nhưng mang tính cơ học và analyzer sẽ tìm ra hết trong một lần build. Hãy chuyển các class dữ liệu ngay tuần này; để dành mấy class rắc rối cho tới khi bạn đã thuộc quy tắc hai scope.
