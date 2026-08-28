---
title: "tapflow: stream simulator tự host cho cả nhóm"
package: "tapflow"
repo: "jo-duchan/tapflow"
githubUrl: "https://github.com/jo-duchan/tapflow"
category: "Library/Tooling"
stars: 530
forks: 65
lastUpdate: "2026-08-28"
pubDev: ""
youtube: "https://www.youtube.com/results?search_query=tapflow+simulator+streaming+qa"
priority: "High"
phase: "P1"
trendRank: 0
description: "tapflow stream iOS Simulator và Android emulator từ chính máy Mac của bạn lên trình duyệt, để designer, PM và lập trình viên backend cùng QA được bản build Flutter mà không cần Xcode."
seoDescription: "tapflow là lựa chọn tự host, giấy phép MIT, thay cho Appetize và BrowserStack. Stream simulator lên trình duyệt qua H.264, không cần WebDriverAgent, bản build không rời hạ tầng của bạn."
keywords:
  - tapflow
  - thay thế appetize tự host
  - thay thế browserstack mã nguồn mở
  - công cụ qa flutter
  - stream ios simulator
  - android emulator trên trình duyệt
topics:
  - qa
  - devtools
  - self-hosted
summary:
  - "**tapflow** stream iOS Simulator và Android emulator từ chiếc Mac bạn đang có lên trình duyệt của bất kỳ đồng nghiệp nào."
  - "Ba thành phần: một relay tự host, một agent macOS kết nối ra ngoài, và một dashboard chạy trên trình duyệt."
  - "`npm install -g tapflow`, rồi `tapflow setup` và `tapflow start` — không cần WebDriverAgent, không upload lên cloud."
  - "**530★**, giấy phép MIT, vẫn ở v0.x, và phía agent chỉ chạy trên macOS."
related:
  - slug: simvyn
    title: "simvyn: một bảng điều khiển cho mọi simulator, emulator và thiết bị"
  - slug: flutter-skill
    title: "flutter-skill: cho AI agent điều khiển ứng dụng đang chạy"
  - slug: maidkit
    title: "MaidKit: bộ công cụ SSH viết bằng Flutter để quản trị server"
faq:
  - q: tapflow có phải device farm không?
    a: "Không. Nó stream simulator và emulator chạy trên chính những chiếc Mac bạn đang sở hữu, chứ không quản lý một dàn điện thoại thật. Dự án nói rõ điều đó — nó chỉ làm cho simulator đang chạy trở nên truy cập được từ trình duyệt, không hơn."
  - q: Bản build Flutter của tôi có bị upload đi đâu không?
    a: "Không. tapflow được thiết kế để tự host. File binary, luồng stream thiết bị và bản ghi phiên đều nằm trên relay do bạn vận hành. Đó chính là lý do chính để chọn nó thay vì Appetize hay BrowserStack."
  - q: Cả nhóm có cần máy Mac không?
    a: "Chỉ những máy chạy agent. Relay chạy trên hệ điều hành nào có Node 22+ cũng được, còn người QA chỉ cần một trình duyệt hiện đại — không Xcode, không Android Studio, không Flutter SDK."
  - q: AI agent có điều khiển được tapflow không?
    a: "Có. `@tapflowio/mcp-server` phơi bày khả năng điều khiển simulator dưới dạng công cụ MCP cho Claude Code và các agent khác, và có endpoint REST chụp ảnh tại `/api/v1/sessions/:sessionId/screenshot` dùng cho CI."
datePublished: "2026-08-28"
dateModified: "2026-08-28"
draft: false
---

[`tapflow`](https://github.com/jo-duchan/tapflow) là lựa chọn tự host thay cho Appetize và BrowserStack: nó stream iOS Simulator và Android emulator đang chạy trên máy Mac của bạn lên bất kỳ trình duyệt nào. **530★**, giấy phép MIT, cập nhật lần cuối **2026-08-28**.

## tapflow là gì?

Nhóm Flutter nào rồi cũng đụng cùng một bức tường. Lập trình viên mobile muốn chạy app lúc nào cũng được. Còn tất cả những người khác — designer đang kiểm tra bố cục, PM muốn so hai bản build, lập trình viên backend muốn xem cái gì thật sự đã lên sandbox — đều phải đi nhờ, lần nào cũng vậy.

Các cách giải quyết thông thường đều có giá của nó. Máy thật tốn tiền, tốn độ phủ phiên bản hệ điều hành và tốn cả một buổi chiều của ai đó. Appetize và BrowserStack tốn phí thuê bao *và* buộc phải upload bản build nội bộ lên bên thứ ba. Phát Xcode cho cả nhóm thì tốn một chiếc Mac và cả bộ toolchain cho mỗi người.

Câu trả lời của tapflow là tận dụng lại những chiếc Mac bạn đã có. Nó gồm ba phần:

1. một **relay** (Linux hoặc macOS) đồng thời phục vụ dashboard trên cùng một cổng
2. một **agent macOS** điều khiển simulator hoặc emulator, kết nối *ra ngoài* tới relay — không cần mở firewall vào trong, và không cần WebDriverAgent vì nó tiêm sự kiện chạm iOS trực tiếp
3. một **dashboard trên trình duyệt** cho tất cả những người còn lại

## Vì sao điều này quan trọng với nhóm Flutter

Lời hứa của Flutter là một nhóm phát hành cho cả hai nền tảng. Trên thực tế, khâu QA vẫn kẹt ở người sở hữu máy Mac. tapflow dời nút thắt đó đi mà không đưa bản build ra khỏi hạ tầng của bạn.

Phần stream được suy tính kỹ hơn mức bạn chờ đợi ở một dự án v0.x. Cả hai nền tảng đều stream H.264 qua bộ giải mã hai tầng — WebCodecs khi ở ngữ cảnh bảo mật, bộ giải mã WASM khi chạy HTTP thường — cố tình bỏ qua Media Source Extensions để bộ đệm của thẻ media không nằm trên đường giải mã. Dự án công bố số đo độ trễ của chính mình: p50 khoảng 11–17 ms từ lúc giải mã đến lúc hiển thị với bộ giải mã phần mềm, cộng thêm thời gian đi về của mạng. Trình duyệt cũ thì lùi về JPEG thay vì báo lỗi.

Xung quanh luồng stream là những thứ một quy trình QA thật sự cần: chạm, vuốt và pinch được chuyển tiếp trực tiếp; thanh công cụ deeplink; App Center nhận file `.app.zip` và `.apk` rồi theo dõi bản build qua các trạng thái Backlog / In Progress / Done / Rejected; bản ghi phiên giữ khoảng 72 giờ rồi tự xóa; chỉ số CPU và RAM theo từng agent để biết máy Mac nào đang quá tải; và phân quyền Admin, Developer, QA, Viewer kèm link mời và personal access token.

## Bắt đầu

```bash
npm install -g tapflow
```

Trên chiếc Mac sẽ chạy agent, cài các thành phần cần thiết cho simulator:

```bash
tapflow setup
```

Rồi khởi động relay và agent cùng lúc:

```bash
tapflow start
```

Lệnh đó in ra URL của relay (mặc định `http://localhost:4000`). Mở lên, tapflow sẽ chuyển bạn tới `/setup` để tạo tài khoản admin đầu tiên — hoặc dùng `tapflow admin init` trên server không có giao diện. `tapflow doctor` kiểm tra lại các điều kiện tiên quyết khi có gì đó bất thường.

Bỏ qua `tapflow setup` trên máy Linux chỉ chạy relay; nó chỉ cần Node 22+ và khoảng 512 MB RAM.

## Khi nào nên dùng tapflow?

- những người không phải lập trình viên trong nhóm cần thử bản build Flutter mà hiện tại thì không thể
- bạn đang trả tiền cho Appetize hay BrowserStack chủ yếu để dùng simulator, chứ không phải máy thật
- chính sách công ty hoặc hợp đồng với khách nói rằng bản build nội bộ không được upload lên cloud của bên thứ ba
- bạn muốn một LLM agent hoặc một job CI điều khiển simulator qua MCP hoặc REST

## Điểm còn hạn chế

Agent chỉ chạy trên macOS, và mãi sẽ như vậy — nó điều khiển simulator của Xcode và Android emulator trên máy Mac. Relay chạy ở đâu cũng được; máy làm việc thật thì không.

Dự án đang ở v0.x và nói thẳng điều đó. Nhóm bảo trì hứa mặc định giữ tương thích ngược và ghi chú các thay đổi phá vỡ trong changelog, nhưng đó là một lời hứa, chưa phải một bề dày thành tích.

Và nó nói rõ mình không phải device farm, cũng không thay thế Appium. Nó chỉ kèm một trình chạy flow tối giản; việc ghép WebDriverAgent hay Appium nằm ngoài phạm vi theo chủ ý. Nếu kế hoạch QA của bạn phụ thuộc vào những đặc thù của phần cứng thật — camera của một hãng cụ thể, modem thật, hiện tượng giảm xung do nóng — thì luồng stream simulator sẽ không tìm ra các lỗi đó, dù độ trễ có tốt đến đâu.

## Các lựa chọn đáng so sánh

- [simvyn: một bảng điều khiển cho mọi simulator, emulator và thiết bị](/vi/recipes/simvyn/) — điều khiển cục bộ cho một người thay vì stream cho cả nhóm
- [flutter-skill: cho AI agent điều khiển ứng dụng đang chạy](/vi/recipes/flutter-skill/) — cho agent truy cập ứng dụng thay vì thiết bị
- Appetize và BrowserStack — bản dịch vụ gốc, nếu bạn thà trả tiền còn hơn tự vận hành một relay

## Câu hỏi thường gặp

### tapflow có phải device farm không?

Không. Nó stream simulator và emulator chạy trên chính những chiếc Mac bạn đang sở hữu, chứ không quản lý một dàn điện thoại thật. Dự án nói rõ điều đó — nó chỉ làm cho simulator đang chạy trở nên truy cập được từ trình duyệt, không hơn.

### Bản build Flutter của tôi có bị upload đi đâu không?

Không. tapflow được thiết kế để tự host. File binary, luồng stream thiết bị và bản ghi phiên đều nằm trên relay do bạn vận hành. Đó chính là lý do chính để chọn nó thay vì Appetize hay BrowserStack.

### Cả nhóm có cần máy Mac không?

Chỉ những máy chạy agent. Relay chạy trên hệ điều hành nào có Node 22+ cũng được, còn người QA chỉ cần một trình duyệt hiện đại — không Xcode, không Android Studio, không Flutter SDK.

### AI agent có điều khiển được tapflow không?

Có. `@tapflowio/mcp-server` phơi bày khả năng điều khiển simulator dưới dạng công cụ MCP cho Claude Code và các agent khác, và có endpoint REST chụp ảnh tại `/api/v1/sessions/:sessionId/screenshot` dùng cho CI.

## Tài nguyên & liên kết

- **GitHub:** [jo-duchan/tapflow](https://github.com/jo-duchan/tapflow)
- **Tài liệu:** [tapflow.dev](https://www.tapflow.dev)
- **npm:** [tapflow](https://www.npmjs.com/package/tapflow)

---

*Thuộc [FlutterCook](/vi/recipes/) — hướng dẫn thực hành về các thư viện, UI kit và ứng dụng Flutter mã nguồn mở tốt nhất. Xem [xu hướng GitHub](/vi/trends/) hoặc [hướng dẫn YouTube](/vi/youtube/).*
