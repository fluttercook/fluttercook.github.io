---
title: "Sinh mã trong Dart: build_runner mà không bực mình"
description: "build_runner chậm, khó hiểu và thỉnh thoảng sai — cho tới khi bạn hiểu nó cache cái gì, vì sao nó xung đột, và bộ sinh mã nào thật sự xứng đáng với thời gian build. Hướng dẫn thực tế cho toàn bộ đường ống."
seoDescription: "Hướng dẫn thực tế về build_runner trong Dart và Flutter: file part, cấu hình build.yaml, xung đột generator, chế độ watch, làm mới cache, thiết lập CI, và khi nào sinh mã là xứng đáng."
keywords:
  - build_runner dart huong dan
  - sinh ma flutter
  - cau hinh build.yaml
  - build_runner cham sua the nao
  - json_serializable freezed
  - file part sinh ra dart
category: "Hướng dẫn"
topic: "Dart"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-12"
emoji: "⚙️"
tags: ["Dart", "Công cụ", "Build", "Sinh mã", "CI"]
sources:
  - name: "build_runner package — pub.dev"
    url: "https://pub.dev/packages/build_runner"
  - name: "build_config — tài liệu build.yaml"
    url: "https://pub.dev/packages/build_config"
  - name: "json_serializable package — pub.dev"
    url: "https://pub.dev/packages/json_serializable"
  - name: "source_gen package — pub.dev"
    url: "https://pub.dev/packages/source_gen"
  - name: "Libraries and parts — tài liệu Dart"
    url: "https://dart.dev/language/libraries"
  - name: "dart run — tài liệu công cụ Dart"
    url: "https://dart.dev/tools/dart-run"
related:
  - slug: "dart-streams-in-depth"
    title: "Stream trong Dart chuyên sâu: backpressure, broadcast và những rò rỉ ở giữa"
  - slug: "dart-custom-lints-analyzer"
    title: "Viết một lint tuỳ chỉnh cho codebase Dart của bạn"
draft: false
---

Bạn thêm `json_serializable`, chạy `dart run build_runner build`, và nhận được:

```
Conflicting outputs were detected and the build will be terminated.
```

Bạn chạy lại với `--delete-conflicting-outputs`, nó chạy được, và từ đó bạn gõ cờ này mãi mãi mà không biết nó đã xoá gì. Đó là mối quan hệ điển hình giữa lập trình viên và build_runner, và nó đáng được sửa, vì công cụ này dễ đoán hơn vẻ ngoài của nó.

## Mô hình: một asset vào, một asset ra

build_runner không phải bộ chạy script. Nó là một hệ thống build trên *asset* — những file được định danh theo dạng `package:name|path`. Mỗi builder khai báo nó tiêu thụ phần mở rộng nào và sinh ra phần mở rộng nào, và build_runner dựng một đồ thị từ đó.

`json_serializable` nói: với mỗi `.dart`, có thể sinh ra một `.g.dart`. `freezed` nói: với mỗi `.dart`, có thể sinh ra một `.freezed.dart`. Vì đầu ra được đánh khoá theo đường dẫn, **hai builder cùng nhận một đường dẫn đầu ra sẽ xung đột** — và một builder cũng xung đột với chính đầu ra cũ của nó còn nằm trên đĩa từ lần chạy với cấu hình khác.

Đó chính là việc `--delete-conflicting-outputs` làm: nó xoá các file sinh ra mà lần build hiện tại muốn ghi nhưng không phải do chính nó tạo trong cache của lần chạy này. Nó an toàn với file thật sự được sinh ra, và đó là lý do bạn không bao giờ được sửa tay một file `.g.dart`.

Cache nằm ở `.dart_tool/build/`. Khi build hành xử một cách bất khả thi, đó là thư mục cần xoá:

```bash
rm -rf .dart_tool/build && dart run build_runner build --delete-conflicting-outputs
```

## File part, và lỗi ai cũng gặp đầu tiên

Hầu hết generator phát ra file *part*, nghĩa là mã sinh ra dùng chung một library với mã nguồn của bạn:

```dart
import 'package:json_annotation/json_annotation.dart';

part 'user.g.dart';   // bắt buộc, và tên phải khớp chính xác với file

@JsonSerializable()
class User {
  const User({required this.id, required this.name});
  final String id;
  final String name;

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
  Map<String, dynamic> toJson() => _$UserToJson(this);
}
```

`Target of URI hasn't been generated` trước lần build đầu tiên là chuyện bình thường — bộ phân tích đang báo về một file chưa tồn tại. Chạy build đi; nó sẽ hết.

Vì là part, mã sinh ra nhìn thấy các thành viên riêng tư của bạn, và file của bạn nhìn thấy các hàm `_$…` được sinh ra. Nó cũng có nghĩa mỗi file nguồn sinh ra một file, và đó là lý do một package có 200 model sẽ có 200 file `.g.dart`.

## Làm cho nó nhanh lên

Thời gian build là lời than phiền chính, và phần lớn có thể sửa được bằng cấu hình. `build.yaml` ở gốc package:

```yaml
targets:
  $default:
    builders:
      json_serializable:
        generate_for:
          - lib/models/**.dart
        options:
          explicit_to_json: true
          field_rename: snake
      freezed:
        generate_for:
          - lib/models/**.dart
```

`generate_for` là thiết lập có đòn bẩy lớn nhất trong file này. Mặc định, một builder được đưa cho **mọi** file Dart trong package của bạn, và tối thiểu nó phải phân tích từng file để quyết định rằng chẳng có gì phải làm. Giới hạn nó vào đúng thư mục thật sự chứa các class có annotation thường xuyên cắt hơn một nửa thời gian build trên package lớn.

Vài biện pháp thực tế khác:

- **Dùng `watch` khi phát triển**, không phải chạy `build` lặp đi lặp lại. Nó giữ đồ thị asset còn nóng và chỉ dựng lại phần đã đổi.
  ```bash
  dart run build_runner watch --delete-conflicting-outputs
  ```
- **Chẻ nhỏ package lớn.** build_runner làm việc theo từng package; một monorepo năm package chỉ dựng lại cái bạn vừa chạm vào.
- **Rà soát các generator của bạn.** Mỗi phụ thuộc sinh mã đánh thuế lên mọi lần build. Một generator giúp bạn tiết kiệm ba mươi dòng mã lặp trong hai file thì không đáng giá.

## Generator nào xứng đáng

Xếp hạng thành thật của tôi, nhìn từ góc độ bảo trì codebase chứ không phải đếm tính năng:

| Generator | Kết luận |
| --- | --- |
| `json_serializable` | Đáng dùng từ khoảng 10 model trở lên. `fromJson` viết tay là nơi trú ngụ của những lỗi gõ nhầm tên trường một cách âm thầm. |
| `freezed` | Đáng dùng nếu bạn dùng nhiều union kiểu sealed và `copyWith`. Record và sealed class trong Dart hiện đại đã bao phủ một phần lý do trước đây cần tới nó. |
| `retrofit` / client API | Đáng với API lớn và ổn định. Là gánh nặng với năm endpoint. |
| Sinh mã `mockito` | Hãy ưu tiên fake viết tay cho bất cứ thứ gì có hành vi đáng kể; mock sinh ra hợp nhất với những interface rộng mà bạn hiếm khi dùng. |
| Generator asset/đa ngôn ngữ | Gần như luôn đáng — chúng biến lỗi gõ chuỗi lúc chạy thành lỗi biên dịch. |

Câu hỏi tôi tự đặt trước khi thêm một cái: **nó ngăn được nhóm lỗi nào?** "Gõ ít hơn" là câu trả lời yếu; "gõ sai một khoá JSON giờ là lỗi biên dịch" là câu trả lời mạnh.

## CI và quản lý phiên bản

Hai chính sách đều bảo vệ được, và bạn nên chọn một cách có chủ ý:

**Không commit file sinh ra** (mặc định của tôi). `.gitignore` nhận `*.g.dart`, `*.freezed.dart`, và CI chạy build trước khi phân tích và kiểm thử:

```yaml
- run: dart pub get
- run: dart run build_runner build --delete-conflicting-outputs
- run: dart analyze --fatal-infos
- run: dart test
```

Ưu: không có diff của file sinh ra khi review, không có khả năng commit nhầm đầu ra cũ. Nhược: mọi lần checkout sạch đều phải trả chi phí build, và việc nâng phiên bản generator có thể làm hỏng CI mà không hề có thay đổi mã nguồn nào.

**Commit chúng.** Checkout là build được ngay và diff cho thấy chính xác một lần đổi phiên bản generator đã làm gì. Nhược: pull request ồn ào, và xung đột merge trong những file không ai nên sửa.

Nếu bạn xuất bản package lên pub.dev thì bạn phải commit file sinh ra, vì bên dùng không chạy builder của bạn.

Dù chọn cách nào, **hãy ghim phiên bản generator**. `json_serializable: ^6.0.0` sẽ vui vẻ nhận một bản phát hành nhỏ làm đổi định dạng đầu ra và tạo ra một diff cả nghìn dòng trong một PR chẳng liên quan.

## Gỡ lỗi khi build chẳng làm gì

Khi build báo thành công nhưng file `.g.dart` của bạn thiếu hoặc cũ, hãy đi theo thứ tự sau:

1. Chỉ thị `part` đã có và viết đúng chính xác chưa?
2. Annotation đã đặt trên class chưa, và có import từ đúng package không?
3. `generate_for` trong `build.yaml` có thật sự bao gồm đường dẫn của file này không?
4. Builder có nằm trong `dev_dependencies` không? Một generator trong `dependencies` vẫn chạy nhưng làm phình bên dùng.
5. Chạy với `--verbose` và tìm tên builder gắn với file của bạn.
6. Xoá `.dart_tool/build` rồi dựng lại.

Bước 3 bắt được nhiều trường hợp hơn bạn tưởng, vì việc thêm `generate_for` cho nhanh rồi sau đó tạo model trong một thư mục mới là chuỗi hành động cực kỳ dễ rơi vào.

## Câu hỏi thường gặp

**Vì sao lần build đầu tiên sau `pub get` lại chậm thế?**

build_runner biên dịch chính script build, bao gồm mọi builder. Kernel đó sau đó được cache — các lần build sau bỏ qua nó trừ khi phụ thuộc thay đổi.

**Tôi chạy build_runner từ dự án Flutter được không?**

Được: `dart run build_runner build`. `flutter pub run build_runner` là dạng cũ và vẫn chạy, nhưng `dart run` là cách viết hiện hành.

**`part` có bắt buộc không?**

Không — một số generator phát ra library độc lập để bạn import. File part là trường hợp phổ biến vì chúng truy cập được thành viên riêng tư.

**Sinh mã có ảnh hưởng kích thước ứng dụng không?**

Mã sinh ra là mã thật và bị cắt tỉa như mọi mã khác. Mã tuần tự hoá cho model bạn không dùng sẽ bị loại bỏ nếu không có gì tham chiếu tới nó.

**Tôi có nên tự viết builder không?**

Chỉ cho thứ đặc thù của codebase mà không package nào bao phủ, và hãy chuẩn bị mất một ngày để học `source_gen`. Đó là khoản đầu tư hợp lý cho, ví dụ, việc sinh bảng route từ annotation trong một ứng dụng lớn.

---

*Ngữ nghĩa đồ thị asset, các tuỳ chọn `build.yaml` bao gồm `generate_for`, yêu cầu về file part, và hành vi của `--delete-conflicting-outputs` đều nằm trong tài liệu build_runner và build_config liên kết bên trên. Bảng xếp hạng generator, đánh đổi commit-hay-không, thứ tự gỡ lỗi và bài kiểm tra "nó ngăn được nhóm lỗi nào" là đánh giá riêng của tôi từ việc bảo trì các codebase Dart dùng nhiều sinh mã.*
