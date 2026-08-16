---
title: "Migrate sang material_ui và cupertino_ui: design system rời khỏi SDK"
description: "Flutter 3.47 đưa Material và Cupertino thành package 1.0 độc lập. Đây là những gì thay đổi trong import, cách công cụ tự động chạy, và cách sống sót qua giai đoạn dependency pha trộn."
seoDescription: "Hướng dẫn migrate material_ui và cupertino_ui cho Flutter: dart fix --apply --code=migrate_design_widgets, MaterialUiCompatibilityBridge, thay đổi localizations, và mốc deprecate tháng 11."
keywords: ["package material_ui flutter", "package cupertino_ui", "migrate_design_widgets", "MaterialUiCompatibilityBridge", "migrate flutter 3.47", "design system flutter package"]
category: "Flutter"
topic: "Flutter"
author: "FlutterCook Editorial"
publishDate: "2026-08-16"
updatedDate: "2026-08-16"
emoji: "🧱"
tags: ["Flutter 3.47", "Flutter", "Material", "Cupertino", "Migration"]
sources:
  - name: "material_ui 1.0.0 on pub.dev"
    url: "https://pub.dev/packages/material_ui"
  - name: "cupertino_ui on pub.dev"
    url: "https://pub.dev/packages/cupertino_ui"
  - name: "What's new in Flutter 3.47"
    url: "https://flutter.dev/blog/whats-new-in-flutter-3-47"
  - name: "Flutter Q2 2026 survey results"
    url: "https://flutter.dev/blog/flutter-q2-2026-survey"
related:
  - slug: "flutter-3-47-standalone-material-cupertino-impeller-desktop"
    title: "Flutter 3.47: Material và Cupertino rời khỏi SDK, Impeller tiếp quản desktop"
  - slug: "flutter-2026-roadmap-webassembly-platform-parity"
    title: "Lộ trình Flutter 2026: WebAssembly mặc định, TV LG, và cú đẩy cho ngang tầm bản địa"
draft: false
---

Suốt chín năm, `import 'package:flutter/material.dart';` là dòng đầu tiên của gần như mọi file Flutter từng được viết. Flutter 3.47 bắt đầu kết thúc điều đó. **`material_ui` và `cupertino_ui` giờ là package độc lập trên pub.dev**, cả hai ở 1.0, cùng do publisher đã xác minh `flutter.dev` phát hành. Bản trong SDK vẫn chạy — và **đã lên lịch deprecate chính thức ở bản stable tháng 11**.

Đây là thay đổi lớn hơn vẻ ngoài của cái diff, nên hiểu lý do trước khi chạy công cụ migrate là đáng.

## Vì sao phải tách ra

Khảo sát Q2 2026 trả lời điều này rõ hơn mọi bài blog. Ở mọi mảng trọng tâm, mức hài lòng đều cao: **Dart 92%, Android 91%, core framework 90%**. Một con số phá vỡ quy luật — **Cupertino widgets 61%, giảm 6 điểm**, mảng bị chấm thấp nhất khảo sát.

Nguyên nhân cấu trúc là nhịp phát hành. Bị buộc vào SDK, Cupertino chỉ ship sửa lỗi được theo chuyến tàu stable hàng quý. Apple thì đổi thiết kế bất cứ lúc nào họ muốn. Một design system chỉ phản ứng được bốn lần mỗi năm sẽ luôn chạy sau nền tảng mà nó mô phỏng.

Khi tách ra, `material_ui` và `cupertino_ui` có thể phát hành hàng tuần. Đó là toàn bộ chiến lược: không phải refactor cho đẹp, mà là sửa một sự lệch nhịp hiện lên trực tiếp trong mức hài lòng của lập trình viên.

Lợi ích thứ hai là độc lập phiên bản. Hôm nay, nâng Flutter đồng nghĩa chấp nhận mọi thay đổi widget cùng lúc. Khi design system là một dependency bình thường, bạn ghim được nó:

```yaml
dependencies:
  flutter:
    sdk: flutter
  material_ui: ^1.0.0
  cupertino_ui: ^1.0.0
```

Nâng framework để lấy một bản vá engine mà không phải nhận kèm thay đổi layout của `ListTile` trong cùng buổi chiều.

## Thực sự đổi gì trong code

Chủ yếu là đường dẫn import:

| Trước | Sau |
| --- | --- |
| `package:flutter/material.dart` | `package:material_ui/material_ui.dart` |
| `package:flutter/cupertino.dart` | `package:cupertino_ui/cupertino_ui.dart` |
| `GlobalMaterialLocalizations` từ `flutter_localizations` | bản do `material_ui` cung cấp |

API widget không đổi. Đây là chuyện đóng gói, không phải phá vỡ API — và đó chính là lý do nó tự động hoá được.

## Chạy migrate

Thêm package, rồi để `dart fix` viết lại import:

```bash
flutter pub add material_ui cupertino_ui
dart fix --apply --code=migrate_design_widgets
```

Fix `migrate_design_widgets` viết lại import từ vị trí cũ trong framework sang package mới trên toàn project. Hãy đọc diff — gần như toàn bộ phải là dòng import. Thứ gì khác thì đáng nhìn lại lần hai.

Thứ duy nhất công cụ không xử lý trọn cho bạn là **localizations**. Nếu bạn dùng `GlobalMaterialLocalizations`, hãy chuyển sang bản do `material_ui` cung cấp thay vì bản từ `flutter_localizations`. Trộn hai thứ sẽ sinh lỗi "không tìm thấy localizations" khó hiểu lúc chạy chứ không phải lúc biên dịch, nên hãy grep tường minh:

```bash
grep -rn "GlobalMaterialLocalizations" lib/
```

## Sống sót qua giai đoạn dependency pha trộn

Đây là vấn đề thực tế. Bạn migrate app trong hai mươi phút. Rồi bạn phát hiện bốn dependency vẫn import `package:flutter/material.dart`, và cây widget của họ với của bạn giờ đến từ hai thư viện khác nhau.

Đó là lý do **`MaterialUiCompatibilityBridge`** tồn tại. Bọc app — hoặc chỉ nhánh cây chứa widget cũ — và hai thế giới cũ mới vẫn làm việc được với nhau:

```dart
import 'package:material_ui/material_ui.dart';

void main() {
  runApp(
    MaterialUiCompatibilityBridge(
      child: const MyApp(),
    ),
  );
}
```

Hãy coi bridge là giàn giáo có ngày tháo dỡ, không phải kiến trúc. Mỗi nhánh được bọc là một dependency bạn đang chờ. Giữ một danh sách.

## Mốc thời gian deprecate

Hôm nay chưa có gì vỡ. Trình tự cần lên kế hoạch:

- **Bây giờ (3.47):** cả hai đường đều chạy. Package ở 1.0. Migrate là tuỳ chọn.
- **Stable tháng 11:** thư viện Material và Cupertino trong SDK bị **deprecate chính thức**. Hãy chờ cảnh báo analyzer trên mọi import chưa migrate.
- **Về sau:** API bị deprecate cuối cùng sẽ bị gỡ. Chưa có ngày công bố, và bạn không nên chờ ngày đó.

Ước lượng chi phí thành thật: một buổi chiều cho một app, lâu hơn cho một hệ sinh thái plugin bạn không kiểm soát.

## Nếu bạn phát hành package

Tác giả package gánh phần nặng thật, vì lựa chọn của bạn lan tới mọi người dùng. Vài nguyên tắc:

- **Đừng migrate rồi phát hành ngay một major phá vỡ** nếu package của bạn chỉ chạm vài widget — bạn sẽ chia người dùng thành hai thế giới mà chẳng được gì.
- **Hãy migrate sớm** nếu package của bạn *chính là* một thư viện UI. Người dùng không hoàn tất migrate được cho tới khi bạn xong.
- **Nới ràng buộc phiên bản** thay vì ghim chặt, để người dùng nhận được bản vá design system mà không phải chờ bản phát hành của bạn.

## Checklist migrate của bạn

1. **Nâng lên Flutter 3.47** và xác nhận build sạch trước khi đổi bất cứ thứ gì.
2. **Chạy `flutter pub add material_ui cupertino_ui`.**
3. **Chạy `dart fix --apply --code=migrate_design_widgets`** và đọc diff.
4. **Tìm `GlobalMaterialLocalizations`** và đổi sang bản của `material_ui`.
5. **Build và chạy** trên ít nhất một target iOS và một Android. Chú ý riêng các hồi quy về theme và localization.
6. **Xác định dependency còn dùng thư viện trong SDK.** Mở issue cho họ ngay hôm nay.
7. **Bọc `MaterialUiCompatibilityBridge`** chỉ ở nơi buộc phải, và ghi lại lý do.
8. **Đặt nhắc lịch tháng 10** để rà lại danh sách trước khi mốc deprecate tháng 11 tới.

## Kết luận

Cuộc migrate này mang tính cơ học, và tooling làm hộ phần lớn. Phần cần phán đoán là đồ thị dependency: app của bạn thì dễ, dependency thì không, và `MaterialUiCompatibilityBridge` là cây cầu chứ không phải điểm đến. Hãy làm phần cơ học ngay bây giờ khi nó còn tuỳ chọn và analyzer còn im lặng — đó là việc khó chịu hơn nhiều vào tháng 11, với cảnh báo trên mọi file và một chiếc đồng hồ deprecate đang chạy.
