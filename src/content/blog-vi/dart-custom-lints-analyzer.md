---
title: "Viết một lint tuỳ chỉnh cho codebase Dart của bạn"
description: "Quy ước của nhóm nằm trong wiki thì sẽ bị phá vỡ. Quy ước nằm trong bộ phân tích thì được sửa trước cả khi pull request mở ra. Đây là cách đường ống phân tích tĩnh của Dart hoạt động và một luật tuỳ chỉnh nằm ở đâu trong đó."
seoDescription: "Cách thực thi quy ước nhóm trong Dart: analysis_options.yaml, chọn luật lint, ghi đè mức nghiêm trọng, loại trừ file, và viết một lint tuỳ chỉnh với AST của analyzer kèm quick fix."
keywords:
  - luat lint tuy chinh dart
  - huong dan analysis_options.yaml
  - luat lint flutter cho nhom
  - plugin analyzer dart
  - ast visitor dart
  - dart analyze fatal infos
category: "Hướng dẫn"
topic: "Dart"
level: "Nâng cao"
author: "Trung Hiếu"
publishDate: "2026-08-11"
emoji: "🔍"
tags: ["Dart", "Công cụ", "Lint", "Chất lượng mã", "CI"]
sources:
  - name: "Customizing static analysis — tài liệu Dart"
    url: "https://dart.dev/tools/analysis"
  - name: "Linter rules — tài liệu Dart"
    url: "https://dart.dev/tools/linter-rules"
  - name: "dart analyze — tài liệu công cụ Dart"
    url: "https://dart.dev/tools/dart-analyze"
  - name: "analyzer package — pub.dev"
    url: "https://pub.dev/packages/analyzer"
  - name: "flutter_lints package — pub.dev"
    url: "https://pub.dev/packages/flutter_lints"
  - name: "Diagnostic messages — tài liệu Dart"
    url: "https://dart.dev/tools/diagnostic-messages"
related:
  - slug: "dart-build-runner-codegen"
    title: "Sinh mã trong Dart: build_runner mà không bực mình"
  - slug: "dart-records-and-patterns"
    title: "Record và pattern trong Dart: chúng thay thế những gì"
draft: false
---

Nhóm nào cũng có một quy tắc cứ bị phá vỡ hoài. "Đừng dùng `context` sau một await." "Repository trả về `Result`, không bao giờ ném lỗi." "Không `print` trong `lib/`." Chúng sống trong một bình luận review, được giải thích lại cho từng người mới, rồi tuần sau lại bị vi phạm.

Một luật của analyzer thì không bao giờ mệt khi phải nhắc đi nhắc lại.

## Trước hết, dùng cạn các luật có sẵn

Trước khi viết bất cứ thứ gì, hãy kiểm tra xem luật đó đã tồn tại chưa. Linter đi kèm hơn hai trăm luật, và phần lớn quy ước của nhóm nằm trong số đó. Một cấu hình đáng để bắt đầu:

```yaml
# analysis_options.yaml
include: package:flutter_lints/flutter.yaml

analyzer:
  language:
    strict-casts: true
    strict-raw-types: true
  errors:
    invalid_annotation_target: ignore
    unused_import: error
    dead_code: error
  exclude:
    - "**/*.g.dart"
    - "**/*.freezed.dart"

linter:
  rules:
    - always_declare_return_types
    - avoid_print
    - prefer_final_locals
    - unawaited_futures
    - use_build_context_synchronously
    - cancel_subscriptions
    - close_sinks
```

Ba phần đáng được bình luận.

**`strict-casts` và `strict-raw-types`** là hai thiết lập giá trị nhất trên trang này và không được bật mặc định. `strict-casts` chặn `dynamic` âm thầm chảy vào những vị trí có kiểu — đúng chỗ mà lỗi phân tích JSON ẩn nấp. Bật nó lên trong một codebase sẵn có sẽ sinh ra rất nhiều cảnh báo; đó là thông tin, không phải nhiễu.

**Khối `errors:` thay đổi mức nghiêm trọng.** Một lint ở mức warning là một lint mà cả nhóm học cách lướt qua. Hãy nâng những cái bạn thật sự nghiêm túc lên `error`, và hạ hoặc bỏ qua những cái bạn đã quyết định không quan tâm — một `ignore` tường minh tốt hơn nhiều so với một luật mà ai cũng tắt bằng bình luận nội dòng.

**`exclude` phải bao phủ file sinh ra.** Lint một file `.g.dart` là báo lỗi trong mã không ai viết và không ai sửa được.

Sau đó bắt CI thực thi nó:

```bash
dart analyze --fatal-infos --fatal-warnings
```

Không có những cờ này, `dart analyze` thoát với mã 0 khi chỉ có info và warning, và những luật bạn chọn lựa kỹ càng trở thành đồ trang trí.

## Khi không có luật sẵn nào phù hợp

Những quy ước còn lại là những cái đặc thù với kiến trúc của bạn, và chúng cần một luật tuỳ chỉnh. Cơ chế là một plugin của analyzer: một package nhận AST đã phân giải và báo cáo chẩn đoán, rồi IDE và `dart analyze` hiển thị chúng như mọi lint khác.

Hình dạng của một luật luôn giống nhau: đăng ký quan tâm tới một cấu trúc cú pháp, xem xét nó, báo cáo nếu nó vi phạm quy ước.

```dart
class AvoidRepositoryThrows extends DartLintRule {
  const AvoidRepositoryThrows() : super(code: _code);

  static const _code = LintCode(
    name: 'avoid_repository_throws',
    problemMessage: 'Phương thức repository phải trả về Result, không ném lỗi.',
    correctionMessage: 'Trả về Err(...) thay vì ném lỗi.',
    errorSeverity: ErrorSeverity.WARNING,
  );

  @override
  void run(CustomLintResolver resolver, ErrorReporter reporter,
      CustomLintContext context) {
    context.registry.addThrowExpression((node) {
      final unit = resolver.path;
      if (!unit.contains('/repositories/')) return;
      reporter.atNode(node, _code);
    });
  }
}
```

Các callback `context.registry.addX` là bề mặt API bạn sẽ dành thời gian ở đó — có một callback cho mỗi loại nút AST, và chọn đúng cái nào chiếm phần lớn công việc. `addMethodInvocation`, `addClassDeclaration`, `addInstanceCreationExpression` và `addAwaitExpression` bao phủ phần lớn các luật thực tế.

**Việc kiểm tra đường dẫn ở trên là phiên bản thô sơ.** Một luật tốt hơn sẽ xem xét element đã phân giải — phương thức này có được khai báo trên một class triển khai `Repository` không? — việc này tốn công hơn nhưng không gãy khi có người sắp xếp lại thư mục. Sự phân biệt đó, giữa luật *cú pháp* (nhanh, dễ, mong manh) và luật *ngữ nghĩa* (chậm hơn, khó hơn, đúng đắn), là quyết định thiết kế chính trong bất kỳ lint nào bạn viết.

## Thêm một bản sửa tự động

Một lint biết báo cáo thì hữu ích. Một lint biết tự sửa thì được cả nhóm đón nhận.

```dart
class _UseResultFix extends DartFix {
  @override
  void run(CustomLintResolver resolver, ChangeReporter reporter,
      CustomLintContext context, AnalysisError analysisError,
      List<AnalysisError> others) {
    context.registry.addThrowExpression((node) {
      if (!analysisError.sourceRange.intersects(node.sourceRange)) return;

      final builder = reporter.createChangeBuilder(
        message: 'Chuyển thành Err(...)',
        priority: 80,
      );
      builder.addDartFileEdit((b) {
        b.addSimpleReplacement(
          node.sourceRange,
          'return Err(${node.expression.toSource()})',
        );
      });
    });
  }
}
```

Chốt chặn `intersects` rất quan trọng: callback sửa lỗi chạy cho mọi nút cùng loại trong file, và thiếu nó thì bạn sẽ đề nghị sửa ở mọi biểu thức throw thay vì đúng cái mà con trỏ người dùng đang đứng.

## Cái gì đáng có luật tuỳ chỉnh, cái gì không

| Quy ước | Lint tuỳ chỉnh? |
| --- | --- |
| Phân tầng — UI không được import `data/` | Có. Giá trị cao, thuần cú pháp, dễ viết. |
| Không dùng `DateTime.now()` ngoài lớp trừu tượng đồng hồ | Có. Bắt mã không kiểm thử được ngay tại nguồn. |
| Quy ước đặt tên file hoặc class | Thường là có, và dễ — nhưng hãy cân nhắc nó có bù được chi phí bảo trì không. |
| Định dạng mã | Không. `dart format` lo việc này. |
| "Hàm phải ngắn" | Không. Ngưỡng tuỳ tiện sinh ra tranh cãi, không sinh ra chất lượng. |
| Bất cứ thứ gì đòi hiểu ý định | Không. Bạn sẽ viết ra một luật hay báo nhầm và cả nhóm sẽ tắt nó. |

**Kiểu hỏng cần tránh là một luật hay báo nhầm.** Chỉ một lần báo sai là các lập trình viên bắt đầu thêm bình luận `// ignore:`, và một khi thói quen đó hình thành thì luật ấy còn tệ hơn không có, vì giờ nó là thứ nhiễu mà cả nhóm đã tự huấn luyện để đi vòng qua. Nếu bạn không làm cho luật chính xác được, hãy làm nó hẹp lại — kiểm tra một trường hợp nhỏ hơn và chắc chắn hơn — thay vì chấp nhận báo nhầm.

## Triển khai mà không gây nổi loạn

Một luật mới trên codebase sẵn có sẽ phơi bày hàng trăm vi phạm. Đừng mở pull request đó.

1. Thêm luật ở mức `info` trước. Nó xuất hiện trong IDE, không làm hỏng gì cả.
2. Sửa vi phạm theo từng thư mục, trong các commit tách bạch và review được.
3. Khi số vi phạm về 0, nâng lên `warning` hoặc `error` trong `analysis_options.yaml`.
4. Chỉ tới lúc này mới bắt CI chết vì nó.

Khối `errors:` cũng chấp nhận ghi đè theo thư mục qua các file `analysis_options.yaml` lồng nhau, nên một thư mục cũ có thể giữ mức nghiêm trọng cũ trong khi mã mới chịu mức nghiêm ngặt. Đó thường là con đường thực tế duy nhất trong một codebase lớn.

## Câu hỏi thường gặp

**Lint tuỳ chỉnh có làm IDE chậm không?**

Chúng chạy trong một tiến trình phân tích riêng nên ảnh hưởng ở mức vừa phải, nhưng một luật ngữ nghĩa phải phân giải element sau mỗi lần gõ phím thì nặng hơn rõ rệt so với luật cú pháp. Hãy ưu tiên kiểm tra cú pháp khi nó đủ dùng.

**Tôi chia sẻ luật cho nhóm khác được không?**

Được — xuất bản package lint và bên dùng thêm nó vào `dev_dependencies` cùng với analysis options của họ.

**`dart analyze` có chạy lint tuỳ chỉnh không?**

Thông qua cơ chế plugin thì có, miễn là plugin được cấu hình trong `analysis_options.yaml`. Hãy kiểm chứng điều này tường minh trước khi trông cậy vào CI để thực thi một luật tuỳ chỉnh.

**Còn `// ignore_for_file:` thì sao?**

Nó cũng có tác dụng với lint tuỳ chỉnh. Hãy cân nhắc grep tìm nó trong CI và báo lỗi khi có lần xuất hiện mới với những luật quan trọng nhất của bạn.

**`avoid_print` có đủ để chặn ghi log trong bản phát hành không?**

Không — nó bắt `print`, không bắt được một logger mà ai đó cấu hình để ghi ra stdout. Luật bắt được khuôn mẫu, không bắt được ý định.

---

*Cấu trúc `analysis_options.yaml`, `strict-casts`/`strict-raw-types`, ghi đè mức nghiêm trọng, loại trừ file và các cờ của `dart analyze` đều nằm trong tài liệu Dart liên kết bên trên. Mã lint tuỳ chỉnh minh hoạ hình dạng chuẩn của một plugin analyzer; bề mặt API chính xác phụ thuộc vào package framework lint và phiên bản bạn dùng, nên hãy đọc tài liệu của nó trước khi sao chép. Bảng chọn luật, cảnh báo về báo nhầm và lộ trình triển khai theo giai đoạn là đánh giá riêng của tôi từ việc đưa luật lint vào các nhóm đang làm việc.*
