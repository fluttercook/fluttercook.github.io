---
title: "Trải nghiệm streaming: thiết kế cho token đến từng cái một"
description: "Streaming khiến một model chậm cảm giác nhanh, và kéo theo một loạt vấn đề giao diện mà phản hồi trọn gói không hề có: layout nhảy, markdown dở dang, huỷ giữa chừng, và lỗi đến sau khi bạn đã hiển thị nội dung."
seoDescription: "Hướng dẫn thực dụng để stream phản hồi LLM trên giao diện: đường ống SSE, render markdown tăng dần, neo cuộn, huỷ yêu cầu, lỗi giữa luồng, tiến trình tool call, và mạng di động."
keywords:
  - streaming llm giao diện
  - server sent events ai
  - flutter stream phản hồi llm
  - render markdown tăng dần
  - huỷ yêu cầu llm
  - thiết kế ux streaming
category: "Hướng dẫn"
topic: "AI"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-03"
emoji: "🌊"
tags: ["AI", "UX", "Streaming", "Flutter", "Frontend"]
sources:
  - name: "Streaming Messages — tài liệu Anthropic"
    url: "https://docs.anthropic.com/en/api/messages-streaming"
  - name: "Streaming API responses — tài liệu OpenAI"
    url: "https://platform.openai.com/docs/api-reference/streaming"
  - name: "Server-sent events — MDN"
    url: "https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events"
  - name: "Lớp Stream — tài liệu Dart API"
    url: "https://api.dart.dev/stable/dart-async/Stream-class.html"
  - name: "Lớp ScrollController — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/ScrollController-class.html"
  - name: "Giới hạn thời gian phản hồi — Nielsen Norman Group"
    url: "https://www.nngroup.com/articles/response-times-3-important-limits/"
related:
  - slug: "ai-model-routing-cascades"
    title: "Định tuyến mô hình và thác bậc: chỉ trả tiền cho mức thông minh bạn cần"
  - slug: "ai-guardrails-prompt-injection-defense"
    title: "Prompt injection: cái gì thật sự phòng thủ được"
draft: false
---

Một phản hồi mười hai giây kèm vòng xoay chờ thì cảm giác như hỏng. Cũng mười hai giây đó nhưng chữ bắt đầu hiện sau 400ms thì cảm giác nhanh. Model không thay đổi gì — chỉ thay đổi thứ người dùng nhìn thấy trong lúc chờ.

Đó là toàn bộ lý lẽ ủng hộ streaming, và nó là lý lẽ tốt. Phần dưới đây là những vấn đề bạn thừa hưởng kèm theo.

## Phần đường ống, nói ngắn gọn

Cả hai nhà cung cấp lớn đều stream qua server-sent events: một phản hồi HTTP giữ mở lâu gồm các dòng `data:`, mỗi dòng mang một sự kiện JSON. Những sự kiện quan trọng là loại nối thêm văn bản, loại báo một khối nội dung bắt đầu hoặc kết thúc, và sự kiện cuối mang lý do dừng cùng số token cuối cùng.

Hai nguyên tắc mang tính cấu trúc:

- **Đừng bao giờ stream trực tiếp từ trình duyệt hay ứng dụng di động tới nhà cung cấp.** Làm vậy là đặt API key lên thiết bị. Hãy đi qua endpoint của chính bạn, chỗ đó cũng là nơi để ghi log, giới hạn tần suất và áp guardrail.
- **Proxy của bạn phải stream ra trong khi stream vào**, không được gom lại. Nếu bạn `await` toàn bộ phản hồi thượng nguồn trước khi ghi xuống hạ nguồn, bạn đã trả giá cho sự phức tạp của streaming mà không giữ lại lợi ích nào.

Phía Dart, hình dạng tự nhiên là một `Stream<String>` các delta:

```dart
Stream<String> streamCompletion(String prompt, {CancelToken? cancel}) async* {
  final request = http.Request('POST', _endpoint)
    ..headers.addAll(_headers)
    ..body = jsonEncode({'prompt': prompt, 'stream': true});

  final response = await _client.send(request);
  if (response.statusCode != 200) {
    throw ApiException(response.statusCode);
  }

  await for (final line in response.stream
      .transform(utf8.decoder)
      .transform(const LineSplitter())) {
    if (!line.startsWith('data: ')) continue;
    final payload = line.substring(6);
    if (payload == '[DONE]') return;
    final delta = _extractDelta(jsonDecode(payload));
    if (delta != null) yield delta;
  }
}
```

`LineSplitter` là chi tiết quan trọng: các chunk SSE không đến đúng theo ranh giới dòng, và cắt ngây thơ theo `\n` trên từng chunk sẽ làm hỏng JSON ở chỗ nối.

## Đừng dựng lại cả thế giới sau mỗi token

Cách làm ngây thơ trong Flutter là gọi `setState` cho mỗi delta với một `Text(fullBuffer)` bên dưới. Với ba mươi token mỗi giây trên một câu trả lời dài, cách này rebuild và layout lại một đoạn văn đang phình ra ba mươi lần mỗi giây, và ngân sách frame biến mất.

Ba cách sửa, xếp theo mức hiệu quả:

1. **Cô lập vùng rebuild.** Đặt phần văn bản đang tích luỹ vào một `ValueNotifier<String>` và chỉ bọc widget văn bản trong `ValueListenableBuilder`. Phần còn lại của trang — header, sidebar, lịch sử hội thoại — ngừng rebuild hoàn toàn.
2. **Gộp các delta lại.** Đệm token đến rồi xả theo timer khoảng 60ms. Cảm giác mượt không đổi; số lần rebuild giảm hai tới ba lần. Người dùng không phân biệt được từng token một với mười sáu token một lượt.
3. **Đóng băng các tin nhắn đã xong.** Trong một khung chat, chỉ tin nhắn cuối đang stream. Hãy render mọi thứ phía trên nó thành một cây con riêng, thân thiện với `const`, để nó không tham gia vào các lần rebuild của streaming.

## Markdown lúc nào cũng dở dang

Nếu bạn render markdown tăng dần, mỗi frame đều là một tài liệu có cấu trúc chưa đóng. Luồng vừa phát ra `**import` sẽ hiển thị `**import` dưới dạng chữ thường, rồi hai token sau lật thành in đậm. Khối code còn tệ hơn: dấu ``` mở đến trước dấu đóng rất lâu, nên bộ render ngây thơ hiển thị code như một đoạn văn cho tới khi khối kết thúc, rồi bố cục lại toàn bộ tin nhắn.

Cách hiệu quả:

- **Phát hiện code fence chưa đóng và tự đóng nó khi render.** Đếm số fence trong buffer; nếu lẻ, nối thêm một fence đóng giả trước khi parse. Khối hiển thị như code ngay từ dòng đầu và lớn dần tại chỗ.
- **Làm tương tự với các cấu trúc inline ở ngay cuối buffer.** Một `**` hoặc một `` ` `` lẻ ở cuối nên bị ẩn thay vì hiện thô.
- **Đừng bao giờ animate layout trong lúc stream.** Không animate kích thước ngầm cho khung tin nhắn, không fade-in theo từng token. Bố cục lại cộng với animation đọc ra thành nhấp nháy.

Một số sản phẩm chọn cách render chữ thường trong lúc stream rồi đổi sang markdown đã định dạng khi xong. Cách đó đơn giản hơn và trông như một cú giật tại thời điểm đổi. Tôi thích cách tăng dần kèm tự đóng fence hơn.

## Hành vi cuộn là chi tiết hay bị làm sai

Tự cuộn xuống đáy sau mỗi token là đúng, cho tới khi người dùng cuộn lên đọc lại một đoạn, lúc đó nó thành một cuộc giằng co mà họ luôn thua.

Nguyên tắc: **chỉ tự cuộn khi khung nhìn vốn đã ở gần đáy.**

```dart
void _maybeStickToBottom() {
  if (!_controller.hasClients) return;
  final position = _controller.position;
  final distanceFromBottom = position.maxScrollExtent - position.pixels;
  if (distanceFromBottom > 80) return; // người dùng đã cuộn đi; để yên cho họ
  _controller.jumpTo(position.maxScrollExtent);
}
```

Hãy dùng `jumpTo`, không dùng `animateTo` — một animation bị khởi động ba mươi lần mỗi giây thì không bao giờ hoàn tất và tạo ra giật thấy rõ. Và hãy hiện nút "xuống mới nhất" khi người dùng đã cuộn đi, để việc để yên cho họ không đồng nghĩa với bỏ rơi họ.

## Huỷ giữa chừng, và vì sao nó là một tính năng sản phẩm

Người dùng đổi ý giữa câu trả lời. Nút dừng không phải thứ trang trí:

- Nó tiết kiệm output token mà lẽ ra bạn phải trả tiền.
- Nó giải phóng kết nối và sự chú ý của người dùng.
- Nó cho thấy hệ thống nằm trong tầm kiểm soát của họ, điều này quan trọng hơn cả khoản tiết kiệm token.

Hãy làm cho đúng: huỷ luôn request HTTP bên dưới để phía thượng nguồn thật sự dừng sinh, chứ không chỉ huỷ subscription trên giao diện. Huỷ Dart stream trong khi socket vẫn mở thì bạn vẫn bị tính tiền cho toàn bộ phản hồi. Và hãy giữ lại phần văn bản dở dang trên màn hình kèm dấu hiệu "đã dừng" rõ ràng thay vì xoá đi — người dùng thường dừng vì họ đã có thứ họ cần.

## Lỗi đến sau khi bạn đã hiển thị nội dung

Đây là tình huống mà phản hồi trọn gói không có. Bạn đang ở token thứ 200 của một câu trả lời đang hiện thì kết nối rớt, hoặc nhà cung cấp trả về một sự kiện lỗi giữa luồng, hoặc bộ lọc nội dung kích hoạt.

Bạn không thể "gỡ hiện" chữ đã hiện. Vậy nên:

- **Đánh dấu tin nhắn là chưa hoàn tất** bằng dấu hiệu thấy được và một hành động thử lại. Đừng bao giờ âm thầm để một câu trả lời cụt trông như đã xong.
- **Kiểm tra lý do dừng ở sự kiện cuối.** Một phản hồi kết thúc vì chạm giới hạn token khác với một phản hồi kết thúc tự nhiên, và giao diện nên phân biệt chúng — thường bằng một hành động "tiếp tục".
- **Thử lại từ đầu, đừng nối vào giữa.** Nối một lần sinh thứ hai vào phần dở dang tạo ra văn bản rời rạc ngay chỗ nối. Hãy sinh lại và thay thế.
- **Xử lý luồng rỗng.** Một phản hồi kết thúc mà không có chữ nào là chuyện có thật; giao diện hiện một bong bóng rỗng mãi mãi là một báo lỗi.

## Tool call làm luồng gồ ghề

Khi model có thể gọi công cụ, luồng không còn là dòng chữ trôi đều nữa. Nó phát ra một ít chữ, dừng hai giây trong lúc công cụ chạy, rồi tiếp tục. Khoảng dừng đó trông y hệt bị treo.

Hãy lấp nó bằng một trạng thái cụ thể, không phải vòng xoay: "Đang tìm trong tài liệu…", "Đang đọc ba tệp…". Việc gọi tên thao tác biến thời gian chết thành tiến trình thấy được, và cho người dùng cơ sở để huỷ nếu model đang làm thứ họ không muốn. Nếu tham số công cụ cũng stream về dưới dạng JSON dở dang, đừng cố parse và hiển thị tăng dần — hãy chờ tham số đầy đủ rồi mới hiện tên thao tác.

## Mạng di động

Streaming giả định một kết nối giữ mở hàng chục giây, mà đó đúng là giả định mạng di động hay phá vỡ.

- Đặt read timeout theo **khoảng cách giữa hai sự kiện**, không theo tổng thời lượng. Một luồng chạy cả phút là chuyện hợp lệ; im lặng mười lăm giây ở giữa là kết nối đã chết.
- Xử lý trường hợp ứng dụng chạy nền — trên iOS đặc biệt phải lường trước socket bị giết. Hãy quyết định dứt khoát là bỏ luôn lần sinh đó, hay đẩy nó về phía máy chủ và cho client gắn lại theo một job ID.
- Cân nhắc xem streaming có đáng không với đầu ra ngắn. Với một tác vụ phân loại trả về đúng một từ, streaming thêm phức tạp kết nối mà không tiết kiệm được gì cảm nhận được.

## Câu hỏi thường gặp

**Streaming có tốn tiền hơn không?**

Không. Bạn vẫn bị tính đúng số token đó; chỉ cách giao nhận thay đổi.

**Tôi có stream được JSON có cấu trúc không?**

Được, nhưng đừng render tăng dần — JSON dở dang không parse được. Hãy hiện chỉ báo tiến trình rồi render khi xong.

**Token phải hiện nhanh cỡ nào thì mới thấy đã?**

Thời gian tới token đầu tiên mới là thứ chi phối cảm nhận. Dưới khoảng một giây là thấy nhạy; sau đó tốc độ stream ít quan trọng hơn người ta tưởng.

**Có nên thêm con trỏ nhấp nháy?**

Một khối nhấp nháy ở cuối văn bản thật sự hữu ích — nó phân biệt "vẫn đang sinh" với "đã xong và ngắn thôi".

**Còn trợ năng thì sao?**

Trình đọc màn hình xử lý các vùng thay đổi liên tục rất tệ. Hãy thông báo rằng phản hồi đang được tạo, rồi đọc văn bản hoàn chỉnh đúng một lần, thay vì biến vùng đang stream thành live region.

---

*Giao thức streaming và hành vi API mô tả ở đây lấy từ tài liệu nhà cung cấp được liên kết phía trên; hãy đối chiếu tên sự kiện và hình dạng trường với tài liệu hiện hành vì chúng thay đổi theo thời gian. Các chiến lược render, quy tắc cuộn, khuyến nghị xử lý lỗi và nhận định về lúc streaming không đáng làm là ý kiến của riêng tôi, rút ra từ việc xây giao diện streaming trên Flutter và web.*
