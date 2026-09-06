---
title: "AI chạy trên thiết bị trong Flutter: cái gì vừa với một chiếc điện thoại"
description: "Chạy mô hình ngôn ngữ cục bộ xoá bỏ hoá đơn API, phụ thuộc mạng và câu hỏi riêng tư, đổi lại là dung lượng tải về, trần bộ nhớ và ngân sách nhiệt. Đây là cách nhận ra bạn đang đánh đổi cái gì."
seoDescription: "Nhìn thực tế về AI chạy trên thiết bị trong ứng dụng Flutter: tác vụ nào vừa với model nhỏ cục bộ, lượng tử hoá và giới hạn bộ nhớ, chiến lược tải model, luồng chạy, pin và nhiệt, và thiết kế lai cục bộ cộng đám mây."
keywords:
  - ai trên thiết bị flutter
  - llm cục bộ flutter
  - flutter_gemma
  - model lượng tử hoá di động
  - litert mediapipe flutter
  - ứng dụng ai offline
category: "Chuyên sâu"
topic: "AI"
level: "Nâng cao"
author: "Trung Hiếu"
publishDate: "2026-08-01"
emoji: "📱"
tags: ["AI", "Flutter", "Mobile", "Performance", "Privacy"]
sources:
  - name: "LiteRT — tài liệu Google AI Edge"
    url: "https://ai.google.dev/edge/litert"
  - name: "LLM Inference guide — Google AI Edge"
    url: "https://ai.google.dev/edge/mediapipe/solutions/genai/llm_inference"
  - name: "Gói flutter_gemma — pub.dev"
    url: "https://pub.dev/packages/flutter_gemma"
  - name: "Core ML — tài liệu Apple Developer"
    url: "https://developer.apple.com/documentation/coreml"
  - name: "Tài liệu ONNX Runtime"
    url: "https://onnxruntime.ai/docs/"
  - name: "Viết code riêng theo nền tảng — tài liệu Flutter"
    url: "https://docs.flutter.dev/platform-integration/platform-channels"
related:
  - slug: "ai-model-routing-cascades"
    title: "Định tuyến mô hình và thác bậc: chỉ trả tiền cho mức thông minh bạn cần"
  - slug: "flutter-isolates-off-main-thread"
    title: "Isolate trong Flutter: cái gì thật sự rời khỏi UI thread, cái gì thì không"
draft: false
---

Lời chào mời thật sự hấp dẫn: không API key, không tính tiền theo token, không vòng gọi mạng, và dữ liệu người dùng không bao giờ rời khỏi máy. Với một ứng dụng ghi chú, một bàn phím, hay bất cứ thứ gì đụng tới hồ sơ sức khoẻ hoặc tài chính, riêng điểm cuối cùng đã đủ quyết định kiến trúc.

Rồi bạn nhìn vào những con số. Một mô hình ngôn ngữ nhỏ đã lượng tử hoá là gói tải về một tới ba gigabyte, cần giữ phần lớn chỗ đó trong RAM khi chạy, và sinh token với tốc độ khiến một API năm 2019 phải ngượng. Cả hai bức tranh đều đúng. Vấn đề là bức nào áp dụng cho tính năng của bạn.

## Cái gì thật sự chạy tốt trên điện thoại

Những tác vụ mà một model nhỏ cục bộ thật sự làm tốt hẹp hơn các bản demo gợi ý, và chúng tụ quanh một tính chất: **đầu vào ngắn, đầu ra ngắn, không cần kiến thức về thế giới.**

| Tác vụ | Khả thi trên thiết bị | Vì sao |
| --- | --- | --- |
| Phân loại văn bản, nhận diện ý định | Rất tốt | Model tí hon, thường còn chẳng phải LLM |
| Embedding cho tìm kiếm ngữ nghĩa cục bộ | Rất tốt | Model nhỏ, chạy một lần mỗi tài liệu, không sinh văn bản |
| Gợi ý tự hoàn thành, đoán cụm từ tiếp theo | Tốt | Đầu ra ngắn, nhạy độ trễ, hưởng lợi khi chạy cục bộ |
| Tóm tắt một ghi chú ngắn | Dùng được | Vài trăm token vào và ra |
| Chuyển giọng nói thành chữ | Tốt | Model chuyên dụng đã chín, runtime tối ưu tốt |
| Phân loại ảnh, OCR | Rất tốt | Không phải model ngôn ngữ; đã giải quyết trên thiết bị từ lâu |
| Chat mở | Kém | Người dùng so nó với model tiên tiến và nó thua |
| Bất cứ thứ gì mang tính dữ kiện | Kém | Kiến thức thế giới của model 2B tham số vừa mỏng vừa sai đầy tự tin |
| Phân tích tài liệu dài | Kém | Cả cửa sổ ngữ cảnh lẫn bộ nhớ đều cạn |
| Sinh code | Kém | Khoảng cách chất lượng lớn nhất chính là ở đây |

**Kiểu hỏng phổ biến nhất không nằm ở kỹ thuật mà nằm ở kỳ vọng.** Nếu giao diện trông như một trợ lý chat, người dùng sẽ mang kỳ vọng dành cho model tiên tiến tới một model nhỏ hơn cả nghìn lần. Hãy đóng khung tính năng thật hẹp — "gợi ý thẻ", "viết lại câu này", "tìm trong ghi chú của tôi" — và cũng model đó sẽ được đọc là tốt.

## Ba con số quyết định tính khả thi

Trước khi viết bất kỳ dòng code nào, hãy đối chiếu tính năng của bạn với chúng:

1. **Dung lượng tải về.** Một model 2B tham số lượng tử hoá 4 bit rơi vào tầm vài gigabyte. Bạn không thể đóng gói nó trong bundle ứng dụng: cả hai chợ ứng dụng đều giới hạn thấp hơn nhiều, và một bản cài 2GB giết tỉ lệ chuyển đổi bất kể thế nào. Nó phải là gói tải theo yêu cầu, tức là cần một giao diện cho việc đó, hỗ trợ tải tiếp, và một phương án cho người dùng từ chối tải.
2. **RAM đỉnh.** Trọng số model phải nằm trong bộ nhớ suốt quá trình suy luận, cộng với KV cache lớn dần theo độ dài ngữ cảnh. Trên một máy Android tầm trung 4GB, đây mới là ràng buộc thật sự cắn. Vượt quá nó không suy giảm êm ái — hệ điều hành giết ứng dụng của bạn, và giết đúng trên những máy bạn ít kiểm thử nhất.
3. **Token mỗi giây.** Tốc độ sinh trên chip di động chỉ nhanh hơn tốc độ đọc của người vài lần trên máy tốt, và chậm hơn trên máy tệ. Cộng với thời gian nạp vài giây khi model nguội, điều này loại bỏ mọi thứ cần cảm giác tức thì, trừ khi bạn giữ model luôn nóng — mà làm vậy lại kéo vấn đề bộ nhớ quay lại.

Hãy đo cả ba trên máy *tệ nhất* bạn định hỗ trợ, đừng đo trên điện thoại dùng để phát triển. Khoảng cách giữa một flagship hiện tại và một máy Android tầm trung ba năm tuổi lớn hơn mọi tối ưu bạn sẽ áp dụng.

## Tầng runtime

Flutter không có engine suy luận sẵn, nên mọi hướng tiếp cận đều đi qua code nền tảng:

- **Google AI Edge (LiteRT và tác vụ LLM inference của MediaPipe)** là con đường trực tiếp nhất cho các model họ Gemma trên cả Android và iOS.
- **Gói `flutter_gemma`** trên pub.dev bọc lại stack đó cho Dart, và là đường ngắn nhất tới một bản prototype chạy được. Hãy đọc README của nó để biết nền tảng được hỗ trợ và hình dạng API hiện tại trước khi thiết kế xung quanh nó — các plugin cộng đồng ở mảng này thay đổi rất nhanh.
- **Core ML** trên nền tảng Apple cho hiệu suất phần cứng tốt nhất trên iOS, đổi lại là một nhánh code riêng cho Apple và một bước chuyển đổi model.
- **ONNX Runtime** là lựa chọn di động nhất nếu bạn đã có model ONNX và cần cả desktop lẫn di động.
- **Method channel tới llama.cpp** cho bạn nhiều lựa chọn model nhất và nhiều quyền kiểm soát nhất, kèm nhiều code nền tảng phải bảo trì nhất. Chỉ đáng làm nếu các lựa chọn đóng gói sẵn không hỗ trợ model của bạn.

Chọn cái nào cũng được, nhưng **hãy tách nó sau một interface ngay từ ngày đầu**:

```dart
abstract interface class LocalInference {
  Future<bool> isAvailable();
  Future<void> load({void Function(double progress)? onProgress});
  Stream<String> generate(String prompt, {int maxTokens = 256});
  Future<void> unload();
}
```

Hai bản cài đặt — một bản thật và một bản dự phòng chạy qua đám mây — nằm sau interface đó là thiết kế sống sót được. Mảng này thay đổi đủ nhanh để runtime bạn chọn hôm nay khó là runtime bạn phát hành sau hai năm, và interface chính là thứ ngăn điều đó thành một cuộc viết lại.

## Luồng chạy: phần lập trình viên Flutter hay làm sai

Suy luận là thao tác CPU/GPU chạy dài. Chạy nó trên main thread của nền tảng là bạn đóng băng giao diện; độ giật không hề tinh tế.

- Suy luận native phải chạy trên luồng nền **ở phía native**. Isolate của Dart không giúp gì ở đây — công việc không nằm trong Dart.
- Hãy stream kết quả qua channel theo từng token thay vì trả về một chuỗi hoàn chỉnh, vì đúng những lý do trải nghiệm khiến streaming quan trọng khi gọi API.
- Mọi xử lý trước và sau ở phía Dart mà tốn kém đo được — tách token, parse, định dạng một kết quả dài — nên nằm trong isolate.
- Hãy xử lý việc ứng dụng chạy nền: trên iOS, phải lường trước suy luận bị treo, và thiết kế cho tình huống lần sinh dừng giữa chừng và không bao giờ tiếp tục.

## Pin và nhiệt là ràng buộc có thật

Suy luận kéo dài là một trong những thứ nặng nhất mà ứng dụng có thể bắt điện thoại làm. Sinh văn bản liên tục làm máy nóng lên thấy rõ và rút pin với tốc độ mà người dùng sẽ quy trách nhiệm cho đúng ứng dụng của bạn — một cách chính xác.

Quan trọng hơn, tải kéo dài kích hoạt giảm xung vì nhiệt, và **các con số benchmark của bạn sẽ không còn đúng sau hai phút sử dụng.** Hãy đo một workload kéo dài, đừng đo một lần chạy nguội duy nhất.

Các cách giảm nhẹ thực dụng: đừng bao giờ sinh mang tính đầu cơ, chặn cứng độ dài đầu ra, giải phóng model sau một khoảng không hoạt động, và cân nhắc dời việc nặng theo lô — lập chỉ mục cả kho ghi chú, sinh embedding cho mọi tài liệu — sang lúc máy đang sạc và rảnh.

## Thiết kế lai thường mới là câu trả lời đúng

Chỉ cục bộ và chỉ đám mây đều tệ hơn phương án ở giữa khá hiển nhiên:

- **Cục bộ cho những việc nhỏ, thường xuyên, riêng tư, nhạy độ trễ** — phân loại, embedding, tự hoàn thành, tìm kiếm trên dữ liệu của chính người dùng.
- **Đám mây cho việc khó** — tài liệu dài, suy luận thật sự, mọi thứ cần kiến thức cập nhật về thế giới.
- **Cục bộ làm phương án dự phòng khi offline**, suy giảm nhưng vẫn dùng được, với giao diện nói thẳng rằng nó đang chạy ở chế độ offline.

Đây chính là quyết định định tuyến giống như khi chọn giữa model API nhỏ và lớn, cộng thêm hai số hạng trong phương trình: đường cục bộ có chi phí biên bằng không và quyền riêng tư tuyệt đối, và nó vẫn dùng được khi không có mạng. Hãy cân những điều đó với một khoảng cách chất lượng lớn hơn nhiều so với giữa hai model đám mây.

Dù bạn xây gì, **hãy nói cho người dùng biết chế độ nào đã tạo ra câu trả lời**. "Được tạo ngay trên máy bạn" là một điểm đáng quảng cáo khi nó đúng, còn giấu đi sự phân biệt này sẽ biến lợi thế riêng tư thành vấn đề niềm tin ngay lần đầu có người phát hiện một request mạng.

## Câu hỏi thường gặp

**Tôi có thể đóng gói model trong bundle ứng dụng không?**

Chỉ với model thật sự nhỏ — bộ phân loại, model embedding, model giọng nói. Model ngôn ngữ phải tải theo yêu cầu.

**Model cục bộ có cần cập nhật không?**

Có, và bạn cần một phương án đánh phiên bản cùng di trú cho nó. Hãy tính trước là việc tải về sẽ xảy ra nhiều hơn một lần.

**Chạy trên thiết bị thì tự động riêng tư phải không?**

Phần suy luận thì đúng. Hãy kiểm tra xem ứng dụng có đang ghi prompt và đầu ra lên analytics không, việc đó âm thầm phá vỡ cam kết.

**Còn Flutter web và desktop?**

Desktop dễ hơn — nhiều RAM, cắm điện. Web hiện chưa thực tế với model ngôn ngữ; riêng dung lượng tải đã loại rồi.

**Kiểm thử việc này trong CI thế nào?**

Bạn không thể kiểm thử chất lượng suy luận một cách có ý nghĩa trên máy ảo. Hãy kiểm thử interface bằng bản cài đặt giả, và chạy kiểm tra với model thật trên một dàn nhỏ thiết bị vật lý.

---

*Năng lực runtime, API của các gói và giới hạn nền tảng mô tả ở đây lấy từ tài liệu được liên kết phía trên và thay đổi rất nhanh — hãy kiểm chứng chi tiết hiện hành, nhất là với các gói cộng đồng, trước khi chốt thiết kế. Bảng đánh giá tác vụ, ba con số khả thi, hướng dẫn về luồng chạy và khuyến nghị thiết kế lai là đánh giá của riêng tôi từ việc xây tính năng chạy trên thiết bị bằng Flutter; hãy tự đo trên các máy đích của bạn.*
