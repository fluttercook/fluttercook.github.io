---
title: "AI coding agent miễn phí: dùng model free của OpenCode sao cho khỏi hối hận"
description: "OpenCode cho dùng model hosted miễn phí, không cần API key. Bài này nói rõ cái giá thật của tier free, việc nào nên để nó làm, và bậc thang nâng cấp hợp lý."
seoDescription: "Hướng dẫn thực dụng về model miễn phí của OpenCode Zen: giới hạn request, chính sách dùng dữ liệu để train, thứ tuyệt đối không được dán vào tier free, và khi nào nên chuyển sang model trả phí."
keywords:
  - opencode model miễn phí
  - ai coding agent free
  - opencode zen
  - llm miễn phí cho lập trình
  - bảo mật dữ liệu ai agent
  - opencode so với claude code
  - giới hạn tier free ai
category: "Hướng dẫn"
topic: "AI Coding"
level: "Cơ bản"
author: "Trung Hiếu"
publishDate: "2026-08-20"
emoji: "🆓"
tags: ["AI", "AI Agents", "OpenCode", "Công cụ lập trình", "Bảo mật"]
sources:
  - name: "OpenCode — AI coding agent mã nguồn mở"
    url: "https://opencode.ai/"
  - name: "OpenCode Zen — danh sách model, bảng giá và các model miễn phí"
    url: "https://opencode.ai/zen"
  - name: "Tài liệu OpenCode — hướng dẫn về AI coding agent miễn phí"
    url: "https://open-code.ai/en/guides/free-ai-coding-agents"
draft: false
---

Rào cản để thử một AI coding agent trước đây là một cái API key và một cái thẻ tín dụng. [OpenCode](https://opencode.ai/) gỡ cả hai: gateway Zen của nó cho bạn chọn model hosted và dùng ngay, không mất tiền, không cần key.

Nghĩa là lý do cuối cùng để chưa học cách làm việc với agentic coding đã biến mất. Nhưng cũng nghĩa là sắp có rất nhiều người chĩa một model miễn phí vào repo riêng tư mà chưa kịp nghĩ chuyện đó kéo theo cái gì.

Cả hai điều đều đáng coi trọng. Dưới đây là tier free thật sự tốt cho việc gì, nó lấy của bạn cái gì bằng một loại tiền tệ không phải tiền, và cách sắp xếp công việc để bạn không phải trả tiền cho một model frontier chỉ để đổi tên biến.

## "Miễn phí" ở đây nghĩa là gì

Có ba thứ khác nhau bị gộp chung dưới một chữ, và giới hạn của chúng khác nhau:

**Công cụ thì miễn phí.** Bản thân OpenCode là mã nguồn mở. Không giới hạn ở phía client, không license theo ghế, không đo đếm. Cắm API key riêng của bạn từ bất kỳ nhà cung cấp nào thì nó hoạt động như mọi agent harness khác.

**Model hosted miễn phí nhưng có quota.** [OpenCode Zen](https://opencode.ai/zen) là gateway tích hợp sẵn. Tier free của nó chạy ở mức **0đ/tháng với khoảng 100 request mỗi ngày**, không cần thẻ, được dùng dàn model Zen. Các model được nhóm theo tier chứ không bán lẻ từng con — một tier mặc định với context lớn, một tier nâng cao với cửa sổ context lớn nhất, và một tier fast với context nhỏ nhưng độ trễ thấp hơn hẳn.

**Free không có nghĩa là unlimited, và cũng không có nghĩa là riêng tư.** Đó là hai điều mọi người hay bỏ qua, và cũng là hai điều quan trọng nhất.

### Quota nhỏ hơn bạn tưởng

100 request mỗi ngày nghe rộng rãi cho tới khi bạn ngồi nhìn một agent làm việc. Một câu "sửa cái test đang fail này" có thể đốt năm tới mười lăm request, vì agent đọc file, chạy test, sửa, chạy lại, rồi đọc lỗi lần nữa. Vòng lặp agentic ngốn request theo cụm.

Thực tế: hãy trông đợi vài task thật mỗi ngày, chứ không phải một ngày làm việc dùng agent liên tục. Để học thì ổn. Nhưng đó không phải workflow bạn dám cam kết với một deadline.

### Cái giá còn lại là source code của bạn

Đây là phần đáng nói thẳng chứ không phải ghi chú cuối trang: **ở tier free, prompt và output nhìn chung được lưu lại và dùng để cải thiện model về sau.** Đó là mô hình kinh doanh. Có một model trong dàn được ghi rõ là không bao giờ lưu hay dùng dữ liệu của bạn để train — nếu bảo mật là yêu cầu bắt buộc, đó là con cần tìm và cần kiểm chứng lại với tài liệu hiện hành, vì mấy chính sách này thay đổi.

Có một câu hay được nhắc ở đây — nếu bạn không trả tiền cho sản phẩm thì chính bạn là sản phẩm — và trong trường hợp này nó không phải phép ẩn dụ. Cái được trả chính là code của bạn.

Cũng lưu ý rằng tên model và thành phần tier free **thay đổi rất nhanh**. Danh sách đã đổi hai lần chỉ trong mấy tháng trước khi bài này được viết. Hãy coi mọi tên model cụ thể bạn đọc trong một bài blog, kể cả bài này, là ảnh chụp tại một thời điểm. Xem [danh sách model Zen](https://opencode.ai/zen) để biết hôm nay cái gì đang miễn phí, và xem luôn chính sách dữ liệu ở cùng chỗ đó.

## Thứ tuyệt đối không được đưa vào model tier free

Không phải kiểu "cẩn thận nhé" chung chung. Đây là danh sách:

- **Mọi loại credential** — API key, token, mật khẩu, connection string, nội dung `.env`, private key
- **Source riêng tư mà bạn không có quyền tiết lộ** — code của công ty, code của khách hàng, mọi thứ đang trong NDA
- **Dữ liệu khách hàng** — bản ghi người dùng thật, thông tin cá nhân, bất cứ thứ gì lấy từ database production
- **Tài liệu nội bộ** — tài liệu kiến trúc, hợp đồng, roadmap, biên bản sự cố
- **Bất cứ thứ gì thuộc diện tuân thủ quy định** — dữ liệu y tế, tài chính, hoặc bị quản lý bởi luật chuyên ngành

Nguyên tắc nằm dưới: **nếu bạn cần xin phép mới dám email nó cho một người lạ, thì đừng dán nó vào một model mà bạn chưa đọc chính sách lưu trữ.**

Có một cái bẫy riêng của agent mà chat không có: **agent đọc cả những file bạn không đưa cho nó.** Chĩa nó vào thư mục gốc của repo là nó có thể đọc `.env`, `config/secrets.yml`, hay một file fixture đầy dữ liệu khách hàng thật — không cái nào bạn cố ý gửi đi. Model chat chỉ thấy thứ bạn dán vào; agent thấy thứ nó tự mở ra.

Nên trước khi chạy bất kỳ agent nào, free hay trả phí, trên một repo bạn không tạo ra riêng cho mục đích đó:

```bash
git ls-files | grep -Ei '\.env|secret|credential|\.pem$|\.key$|token'
```

Cái gì hiện ra thì phải nằm trong `.gitignore`, nằm trong file ignore mà agent tôn trọng, hoặc bị dời hẳn ra khỏi cây thư mục.

## Bậc thang nâng cấp

Mô hình tư duy hữu ích không phải là free-hay-trả-phí. Mà là ba bậc, khớp với thứ mà task thật sự cần:

| Bậc | Dùng cho | Vì sao |
| --- | --- | --- |
| **Free** | Học công cụ, dự án cá nhân, script dùng một lần, khám phá codebase lạ, sửa hàng loạt kiểu cơ học | Không tốn tiền, và hỏng thì chỉ mất một lần thử lại |
| **Trả phí tầm trung** | Công việc thật — làm feature hằng ngày, sửa bug, refactor, review | Độ tin cậy và rate limit đủ để lên kế hoạch; chính sách dữ liệu có thể chỉ ra bằng văn bản |
| **Frontier** | Bài toán thật sự khó — bug concurrency tinh vi, quyết định kiến trúc, refactor lớn nhiều file, mọi thứ mà sai thì đắt | Tốn tiền thật cho mỗi task; đáng đúng lúc câu trả lời sai còn tốn hơn |

Phần lớn mọi người làm ngược ở cả hai đầu. Họ chạy model frontier cho code boilerplate, và chạy model free cho con bug hiểm đã ăn mất hai ngày. Cả hai đều lãng phí — một bên phí token, một bên phí thời gian của chính bạn.

**Dấu hiệu cần nâng bậc:** nếu bạn đã prompt lại ba lần mà câu trả lời vẫn sai theo đúng một kiểu, thì model không phải nút thắt như bạn nghĩ. Hoặc nâng một bậc, hoặc — thường gặp hơn — prompt của bạn đang thiếu bối cảnh mà model không thể tự suy ra. Thử bổ sung bối cảnh trước; cái đó miễn phí.

## Cách moi được việc thật sự hữu ích từ tier free

Model free nhỏ hơn và kém kiên nhẫn hơn. Hãy điều chỉnh công việc cho vừa, thay vì kỳ vọng nó hành xử như model frontier.

**Giao việc nhỏ hơn.** "Refactor module auth" là task của model frontier. "Trong `auth/session.py`, tách logic refresh token ra thành hàm riêng và cập nhật hai chỗ đang gọi" là task của model free. Phạm vi nhỏ cũng đốt ít request hơn, chuyện này rất đáng khi bạn chỉ có một trăm.

**Chỉ đích danh file.** Để agent tự mò xem file nào quan trọng vừa tốn request vừa hay sai với model nhỏ. Nêu thẳng ba file nó cần thì tiết kiệm cả hai.

**Gom việc cơ học lại làm một lượt.** Đổi tên, thêm type hint, chuyển bộ test từ kiểu assertion này sang kiểu khác, viết docstring từ signature có sẵn — đây đúng là thứ model free làm tốt, và kết quả thì kiểm tra rất rẻ.

**Dùng nó để đọc codebase.** Một trong những cách dùng tier free hay nhất là nhờ một model nhanh giải thích một repo lạ. "Trace xem chuyện gì xảy ra khi một request tới `/api/orders`" là việc rủi ro thấp, giá trị cao, và không cần khả năng suy luận của frontier.

**Dùng tier fast cho việc nhanh.** Tier fast context nhỏ thật sự tốt hơn tier context lớn cho việc tra cứu nhanh và sửa một file — độ trễ thấp hơn, và context bạn không dùng tới là context có thể gây nhiễu.

## Lựa chọn miễn phí còn lại

Đáng biết: **Hermes Agent** cũng miễn phí và hoạt động qua nền tảng nhắn tin — bạn điều khiển agent từ Telegram hoặc Discord thay vì từ terminal. Trải nghiệm hoàn toàn khác. Nếu điều hấp dẫn bạn là bấm điện thoại giao việc rồi lát nữa đọc kết quả, thì cái này hợp hơn một công cụ CLI. Mọi lưu ý về dữ liệu vẫn giữ nguyên, cộng thêm một điểm: nền tảng chat còn giữ bản sao của mọi thứ bạn gửi.

## Setup khởi đầu không khiến bạn trả giá

1. **Cài OpenCode.** Setup đúng là chỉ vài phút.
2. **Bắt đầu trên repo của chính bạn** và không chứa gì bảo mật. Không phải cái monorepo của công ty. Một dự án cá nhân.
3. **Xem dàn model free hiện tại và chính sách dữ liệu** tại [opencode.ai/zen](https://opencode.ai/zen) *trước* task thật đầu tiên, không phải sau.
4. **Chạy lệnh quét secret** ở trên trên bất kỳ repo nào trước khi chĩa agent vào.
5. **Làm ba task thật** — một lần sửa bug, một lần refactor nhỏ, một buổi nhờ giải thích code. Bấy nhiêu là đủ để biết công cụ có hợp với cách bạn làm việc không.
6. **Khi thấy mình bắt đầu phụ thuộc vào nó**, chuyển sang model trả phí tầm trung. Ngay khi output của agent đi vào công việc có người trả tiền, thì cả rate limit lẫn chính sách lưu trữ đều không còn chấp nhận được.

Bước 6 là bước mọi người hay hoãn, thường là hoãn tới lúc dính rate limit giữa sprint. Hãy chuyển trước lúc đó, đừng đợi sau.

## Tóm lại cho thẳng thắn

Tier free là cách rất tốt để học và là cách rất tệ để ship hàng. Đó không phải lời chê — tier free sinh ra để làm đúng việc đó, và OpenCode còn khá sòng phẳng khi nói ra sự đánh đổi.

Học trên free. Làm việc trên trả phí. Chỉ nâng lên frontier khi task thật sự khó. Và đọc chính sách lưu trữ trước prompt đầu tiên, chứ không phải sau khi đã dán vào thứ không rút lại được.

## Câu hỏi thường gặp

**OpenCode miễn phí bản thân công cụ hay chỉ miễn phí model?**
Công cụ là mã nguồn mở và không đo đếm. Tier free của Zen là phần model hosted, có giới hạn request mỗi ngày. Bạn cũng có thể cắm API key riêng từ bất kỳ nhà cung cấp nào.

**Thật sự được bao nhiêu request?**
Tier free được ghi ở mức khoảng 100 request mỗi ngày. Vòng lặp agent tiêu vài request cho mỗi task, nên hãy tính là vài task đáng kể mỗi ngày chứ không phải dùng liên tục.

**Code của tôi có bị dùng để train không?**
Ở tier free thì nhìn chung là có — prompt và output được lưu lại và dùng để cải thiện model. Có ít nhất một model trong dàn được ghi rõ là không nằm trong diện này. Hãy kiểm chứng lại với tài liệu hiện hành, vì điều khoản có thay đổi.

**Dùng cho việc của khách hàng được không?**
Không, nếu đó là tier free có chính sách giữ dữ liệu để train, trừ khi khách hàng đã đồng ý rõ ràng bằng văn bản. Hãy dùng tier trả phí có cam kết xử lý dữ liệu trong hợp đồng.

**Nên bắt đầu với model free nào?**
Bắt đầu ở tier mặc định cho việc code nói chung, chuyển sang tier nâng cao khi task cần nhiều context hoặc nhiều suy luận hơn, và dùng tier fast cho việc nhanh trên một file. Tên model cụ thể thay đổi liên tục — hãy xem danh sách hiện tại thay vì tin bất kỳ bài blog nào, kể cả bài này.

**Model miễn phí có đủ tốt để học agentic coding không?**
Có, và đó là lập luận mạnh nhất ủng hộ nó. Kỹ năng chia nhỏ task, cung cấp bối cảnh và kiểm chứng output chuyển sang model trả phí gần như nguyên vẹn. Kỹ năng mới là phần bền, không phải model.

---

*Bài này khai triển từ một ghi chú đang lan truyền trong cộng đồng lập trình viên Việt Nam về các model miễn phí của OpenCode, mà những cảnh báo cốt lõi trong đó — free không phải unlimited, dữ liệu của bạn dùng để train model kế tiếp, tuyệt đối đừng dán secret — đều là những cảnh báo đúng. Tên model và quota trong bài phản ánh thời điểm viết và thay đổi thường xuyên; các link dẫn tới nguồn chuẩn hiện hành.*
