---
title: "Dữ liệu tổng hợp cho eval: xây bộ kiểm thử mà bạn tin được"
description: "Sinh test case bằng model thì nhanh, rẻ và âm thầm luẩn quẩn. Làm cẩn thận, bạn có bộ đánh giá trước cả khi có traffic; làm ẩu, bạn chỉ chứng nhận hệ thống bằng chính giả định của nó."
seoDescription: "Cách xây bộ eval cho ứng dụng LLM bằng dữ liệu tổng hợp: gieo mầm từ dữ liệu thật, sinh ca khó và ca không trả lời được, tránh thiên lệch tự xác nhận, người kiểm duyệt, và giới hạn của dữ liệu tổng hợp."
keywords:
  - dữ liệu tổng hợp đánh giá llm
  - sinh bộ eval cho llm
  - bộ dữ liệu đánh giá rag
  - llm làm giám khảo
  - test case cho tính năng ai
  - golden dataset eval
category: "Hướng dẫn"
topic: "AI"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-04"
emoji: "🧪"
tags: ["AI", "Evaluation", "Testing", "LLM", "Quality"]
sources:
  - name: "Building effective agents — Anthropic engineering"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
  - name: "Evaluating model performance — tài liệu Anthropic"
    url: "https://docs.anthropic.com/en/docs/test-and-evaluate/develop-tests"
  - name: "Evals — tài liệu OpenAI"
    url: "https://platform.openai.com/docs/guides/evals"
  - name: "Ragas — framework đánh giá RAG"
    url: "https://docs.ragas.io/"
  - name: "Cohen's kappa — độ đồng thuận giữa người chấm"
    url: "https://en.wikipedia.org/wiki/Cohen%27s_kappa"
  - name: "Đặc tả JSON Schema"
    url: "https://json-schema.org/"
related:
  - slug: "ai-observability-tracing-llm-apps"
    title: "Quan sát ứng dụng LLM: truy vết một hệ thống không tất định"
  - slug: "ai-model-routing-cascades"
    title: "Định tuyến mô hình và thác bậc: chỉ trả tiền cho mức thông minh bạn cần"
draft: false
---

Bạn có một hệ thống RAG, chưa có người dùng, và một prompt cứ sửa đi sửa lại. Lần sửa nào cũng thấy "có vẻ tốt hơn" mà không cách nào kiểm chứng. Viết tay một trăm câu hỏi kiểm thử mất hai ngày, và bạn sẽ không làm.

Thế là bạn nhờ model sinh ra chúng. Cách này có tác dụng, đáng làm, và có đúng một kiểu hỏng khiến toàn bộ nỗ lực trở nên vô nghĩa nếu bạn không thiết kế để né nó.

## Vấn đề luẩn quẩn

Nếu bạn sinh câu hỏi bằng cách đưa tài liệu cho model đọc, bạn sẽ nhận về những câu hỏi mà tài liệu trả lời tốt, diễn đạt theo đúng cách tài liệu diễn đạt. Retrieval của bạn sẽ đạt điểm rất đẹp — trên một bộ test được dựng từ chính những giả định của hệ thống đang bị kiểm tra.

Người dùng thật thì hỏi về những thứ tài liệu bao phủ kém, bằng từ ngữ tài liệu chưa bao giờ dùng, kèm theo tiền đề sai. **Một bộ eval tổng hợp làm ngây thơ chỉ đo tính nhất quán nội bộ, không đo tính hữu ích.** Nó sẽ đạt trong khi người dùng của bạn thất bại.

Toàn bộ phần dưới đây là về việc bẻ gãy vòng luẩn quẩn đó.

## Gieo mầm từ dữ liệu thật, đừng gieo từ trí tưởng tượng

Dữ liệu tổng hợp mạnh nhất là loại bám vào một thứ có thật. Xếp theo giá trị giảm dần:

1. **Truy vấn thật của người dùng**, kể cả từ một sản phẩm khác hay từ log tìm kiếm. Chúng mang theo cách diễn đạt thật, lỗi chính tả thật, giả định thật.
2. **Ticket hỗ trợ, ghi chú cuộc gọi bán hàng, bài đăng trên diễn đàn cộng đồng.** Đây là những câu hỏi người ta đã thật sự hỏi, bằng lời của chính họ.
3. **Chính những lỗ hổng trong tài liệu của bạn** — các mục mỏng, mâu thuẫn hoặc lỗi thời. Hãy chủ động sinh câu hỏi nhắm vào đó.
4. **Câu hỏi do model tự nghĩ ra từ tài liệu.** Hữu ích để phủ rộng, yếu nhất về tính thực tế, và đây lại là chỗ phần lớn mọi người bắt đầu rồi dừng luôn.

Một prompt sinh dữ liệu thực dụng phải cụ thể hơn câu "viết 5 câu hỏi về tài liệu này":

```
Đây là một đoạn hội thoại hỗ trợ giữa khách hàng và nhân viên.

Hãy viết 5 câu hỏi mà một khách hàng *khác* có thể hỏi liên quan tới cùng
vấn đề nền tảng, nhưng:
- Dùng từ vựng khác với đoạn hội thoại
- Có một câu dựa trên giả định sai
- Có một câu mà tài liệu này KHÔNG trả lời được
- Độ dài khác nhau: một câu cực ngắn, một câu dài dòng lẫn chi tiết thừa

Trả về JSON: [{"question": ..., "expected_behaviour": ..., "category": ...}]
```

Chỉ thị đổi từ vựng và chỉ thị thêm câu không trả lời được chính là hai phần bẻ gãy tính luẩn quẩn. Thiếu chúng, bạn nhận về năm cách diễn đạt lại các tiêu đề trong tài liệu.

## Sinh ca khó một cách có chủ đích

Một bộ test toàn câu hỏi hợp lý gần như không nói lên điều gì, vì câu hỏi hợp lý phần lớn đều chạy được. Hãy dồn phần lớn ngân sách sinh dữ liệu vào những nhóm mà hệ thống thật sự hay hỏng:

| Nhóm | Ví dụ | Kiểm tra điều gì |
| --- | --- | --- |
| Không trả lời được | "Chính sách về X là gì?" trong khi không có chính sách nào | Nó nói "tôi không biết" hay bịa? |
| Tiền đề sai | "Sao ứng dụng thu phí khởi tạo?" trong khi không thu | Nó đính chính hay hùa theo? |
| Nhiều bước | "Cửa sổ hoàn tiền gói doanh nghiệp có dài hơn gói thường không?" | Có truy hồi hai dữ kiện rồi so sánh không? |
| Từ vựng lệch | "huỷ" trong khi tài liệu viết "chấm dứt" | Độ bền của retrieval |
| Mơ hồ | "Giá bao nhiêu?" khi có ba sản phẩm | Nó hỏi lại hay đoán bừa? |
| Đối kháng | Nhét chỉ thị vào trong câu hỏi | Hành vi của guardrail |
| Thời gian | "Tháng trước có gì thay đổi?" | Xử lý ngày tháng và dữ liệu cũ |
| Ngoài phạm vi | Tư vấn y tế hoặc pháp lý | Hành vi từ chối |
| Đa ngôn ngữ | Cùng câu hỏi bằng tiếng Việt và tiếng Anh | Đồng đều giữa các ngôn ngữ |

**Nếu bộ eval của bạn không có câu hỏi nào không trả lời được thì tỉ lệ thành công là vô nghĩa**, vì một hệ thống trả lời mọi thứ đầy tự tin sẽ đạt 100% và rất nguy hiểm.

## Người kiểm duyệt là bước làm cho nó thành thật

Dữ liệu sinh ra chứa cả đáp án kỳ vọng sai, câu hỏi mơ hồ và các bản trùng lặp. Duyệt hết thì mất luôn ý nghĩa của việc tự động sinh; không duyệt gì thì bạn đang tối ưu theo nhiễu.

Cách dung hoà tôi thấy hiệu quả:

1. Sinh nhiều hơn 3-5 lần số ca bạn cần.
2. Khử trùng lặp bằng độ tương đồng embedding — sinh dữ liệu tổng hợp lặp lại chính nó rất nhiều.
3. Cho người duyệt một **mẫu phân tầng**: duyệt toàn bộ các nhóm rủi ro cao, cộng thêm 10-20% các nhóm thông thường.
4. Theo dõi tỉ lệ bị loại theo từng nhóm. Nhóm nào bị loại 40% nghĩa là prompt sinh dữ liệu của nhóm đó hỏng, và sửa prompt có giá trị hơn nhiều so với duyệt thêm ca.
5. Đưa các ca đã duyệt vào một "golden set" đóng băng, không thay đổi trừ khi có quyết định rõ ràng.

Golden set đó mới là thứ bạn thật sự chạy hồi quy. Phần còn lại là một tập lớn hơn, nhiễu hơn, dùng để khám phá.

## Dùng model làm giám khảo, một cách cẩn thận

Chấm câu trả lời tự do bằng tay thì không mở rộng được, nên bạn dùng model. Ba nguyên tắc khiến kết quả đủ tin cậy để ra quyết định:

- **Chấm dựa trên đáp án tham chiếu, đừng chấm trừu tượng.** "Câu trả lời này có chứa cùng các dữ kiện then chốt như đáp án tham chiếu không?" là phán đoán đáng tin hơn nhiều so với "câu trả lời này có tốt không?"
- **Yêu cầu một phán quyết có cấu trúc kèm lý do** — một nhãn phân loại và một câu giải thích — thay vì điểm trên thang mười. Điểm số do model đưa ra hay dồn cục và trôi dạt; nhãn phân loại ổn định hơn.
- **Kiểm chứng giám khảo với người, một lần.** Cho một người chấm 50 ca, so sánh, đo độ đồng thuận. Nếu giám khảo lệch với người ở một phần năm số ca thì các con số tổng hợp của nó không đủ để chống đỡ một quyết định.

Và hãy giữ các kiểm tra tất định ở mọi chỗ bài toán cho phép. Khớp chính xác trường trích xuất, tính hợp lệ của schema, ID đoạn văn được trích dẫn có đúng không, tính nhất quán số học — chúng gần như miễn phí, không bao giờ trôi dạt, và phủ được nhiều hơn người ta tưởng.

## Dữ liệu tổng hợp không cho bạn được điều gì

Hãy sòng phẳng về ranh giới:

- **Phân bố thật.** Bạn không đoán được bao nhiêu phần trăm người dùng hỏi về thanh toán so với hỏi về khởi tạo. Chỉ traffic mới nói lên điều đó, và chính nó quyết định chất lượng thật sự quan trọng ở đâu.
- **Cách diễn đạt thật sự mới lạ.** Văn bản do model sinh đồng đều hơn và đúng ngữ pháp hơn thứ người ta gõ.
- **Phán đoán chuyên môn.** Việc một câu trả lời có *đúng* với nghiệp vụ của bạn hay không — chính sách hoàn tiền, cảnh báo y tế, câu chữ pháp lý — cần một con người hiểu lĩnh vực, không phải một model vừa đọc tài liệu.
- **Cảm xúc và sự đối kháng ngoài đời.** Người dùng bực bội, người dùng bối rối, và người cố tình dò tìm điểm yếu hành xử theo cách mà việc sinh dữ liệu không tái tạo được.

Vì vậy hãy coi dữ liệu tổng hợp là **giàn giáo**: nó giúp bạn có một hệ thống kiểm thử được trước khi ra mắt, và nên được thay thế dần bằng các ca thật lấy từ trace sản phẩm sau đó. Sau một năm, bộ eval của bạn nên chủ yếu là dữ liệu thật, dữ liệu tổng hợp chỉ lấp vào những nhóm mà traffic thật quá hiếm để phủ.

## Câu hỏi thường gặp

**Tôi cần bao nhiêu ca?**

Đủ để một thay đổi vài phần trăm không phải là nhiễu — thực tế là 100-200 ca trong golden set đóng băng, nghiêng về các nhóm khó.

**Có nên sinh dữ liệu bằng chính model đang kiểm thử?**

Nên dùng model khác hoặc kiểu prompt khác để sinh. Dùng cùng model sẽ khuếch đại vấn đề luẩn quẩn.

**Tôi có thể công khai bộ eval tổng hợp không?**

Hãy soát rò rỉ dữ liệu thật trước — các ca gieo mầm từ tài liệu của bạn có thể chứa nguyên văn tên khách hàng.

**Bao lâu nên sinh lại?**

Đừng sinh lại golden set; hãy mở rộng nó. Sinh lại là đổi thước đo, khiến mọi so sánh theo thời gian trở nên vô nghĩa.

**Một bộ eval là đủ chứ?**

Không. Hãy tách chất lượng truy hồi, chất lượng câu trả lời và hành vi an toàn — chúng hỏng độc lập với nhau, và một con số tổng hợp duy nhất sẽ che mất cái nào vừa thay đổi.

---

*Các thực hành đánh giá nhắc tới ở đây dựa trên tài liệu của nhà cung cấp và các framework được liên kết phía trên. Bảng phân nhóm, thứ tự ưu tiên nguồn gieo mầm, quy trình duyệt phân tầng, nguyên tắc kiểm chứng giám khảo và nhận định về giới hạn của dữ liệu tổng hợp là đánh giá cá nhân của tôi từ việc xây bộ đánh giá cho các tính năng LLM; tỉ lệ phù hợp cho ứng dụng của bạn phụ thuộc vào lĩnh vực và traffic thật.*
