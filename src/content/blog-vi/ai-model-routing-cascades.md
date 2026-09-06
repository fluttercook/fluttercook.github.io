---
title: "Định tuyến mô hình và thác bậc: chỉ trả tiền cho mức thông minh bạn cần"
description: "Gửi mọi yêu cầu tới model lớn nhất là kiến trúc đơn giản nhất và thường là sai. Định tuyến và thác bậc cắt giảm đáng kể chi phí lẫn độ trễ — nếu bạn nhận ra được yêu cầu nào khó trước khi trả lời."
seoDescription: "Cách định tuyến yêu cầu LLM giữa nhiều model: định tuyến tĩnh theo tác vụ, định tuyến bằng bộ phân loại, thác bậc và tín hiệu leo thang, tương tác với prompt cache, cách đo lường, và khi nào một model duy nhất mới đúng."
keywords:
  - định tuyến model llm
  - cascade model llm
  - giảm chi phí api llm
  - model nhỏ và model lớn
  - phân loại yêu cầu llm
  - tối ưu độ trễ llm
category: "Chuyên sâu"
topic: "AI"
level: "Nâng cao"
author: "Trung Hiếu"
publishDate: "2026-08-02"
emoji: "🔀"
tags: ["AI", "Architecture", "Cost", "LLM", "Performance"]
sources:
  - name: "Models overview — tài liệu Anthropic"
    url: "https://docs.anthropic.com/en/docs/about-claude/models"
  - name: "Prompt caching — tài liệu Anthropic"
    url: "https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching"
  - name: "Models — tài liệu OpenAI"
    url: "https://platform.openai.com/docs/models"
  - name: "Building effective agents — Anthropic engineering"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
  - name: "FrugalGPT — arXiv"
    url: "https://arxiv.org/abs/2305.05176"
  - name: "Quy ước ngữ nghĩa GenAI của OpenTelemetry"
    url: "https://opentelemetry.io/docs/specs/semconv/gen-ai/"
related:
  - slug: "ai-streaming-ux-token-by-token"
    title: "Trải nghiệm streaming: thiết kế cho token đến từng cái một"
  - slug: "ai-on-device-flutter-gemma"
    title: "AI chạy trên thiết bị trong Flutter: cái gì vừa với một chiếc điện thoại"
draft: false
---

Hoá đơn về, và 90% trong đó là những yêu cầu kiểu "tóm tắt cái này trong một câu" hay "tin nhắn này có phải spam không?" — được gửi tới đúng cái model tiên tiến bạn dùng cho suy luận nhiều bước, chỉ vì đó là model bạn nối dây đầu tiên.

Cách sửa nghe hiển nhiên: dùng model nhỏ ở chỗ model nhỏ là *đủ*. Cái khó nằm trọn trong chữ *đủ*, và trong việc biết yêu cầu nào là như vậy trước khi bạn có câu trả lời.

## Ba kiến trúc, không phải một

Người ta nói "định tuyến" cho ba thứ khác nhau, và chúng có hồ sơ rủi ro khác nhau.

| Cách tiếp cận | Quyết định thế nào | Chi phí | Rủi ro |
| --- | --- | --- | --- |
| **Định tuyến tĩnh** | Nhánh code quyết định model | Ít phức tạp nhất | Gán sai không lộ ra cho tới khi có phàn nàn chất lượng |
| **Định tuyến bằng phân loại** | Một model nhỏ hoặc heuristic chọn theo từng yêu cầu | Thêm một lời gọi | Phân loại sai đẩy việc khó cho model yếu |
| **Thác bậc** | Thử nhỏ trước, leo thang khi hỏng | Đôi khi hai lời gọi đầy đủ | Tiêu chí leo thang là toàn bộ bài toán |

**Hãy bắt đầu bằng định tuyến tĩnh.** Nó gom được phần lớn khoản tiết kiệm khả dĩ mà gần như không thêm phức tạp, và đây lại là thứ người ta bỏ qua vì thấy nó quá đơn giản.

## Định tuyến tĩnh: khoản lợi cho không

Bạn vốn đã biết tính năng nào của mình là dễ. Trong một ứng dụng điển hình:

- Phân loại, gắn nhãn, đẩy email vào hàng đợi, trích một ngày tháng, nhận diện ngôn ngữ — model nhỏ.
- Tóm tắt tài liệu ngắn, viết lại một câu, sinh tiêu đề, định dạng phản hồi — model nhỏ.
- Suy luận nhiều bước, sinh code, phân tích tài liệu dài, mọi việc mà trả lời sai là có giá — model lớn.
- Mọi việc gọi công cụ trong vòng lặp — model lớn, vì lỗi chọn công cụ dồn tích qua từng lượt.

Hãy gắn lựa chọn model vào chính tính năng, đừng gắn vào một cấu hình toàn cục. Rồi đo theo từng tính năng. Tính năng nào hạ cấp mà chất lượng không đổi thì để hạ cấp vĩnh viễn; tính năng nào tệ đi thấy rõ thì trả về như cũ, và bạn đã học được một điều cụ thể.

Hãy làm việc này trước mọi thứ tinh vi. Ở phần lớn ứng dụng nó xoá đi phần lớn hoá đơn, và các quyết định còn lại khi đó chỉ xoay quanh một nhóm nhỏ hơn nhiều những yêu cầu thật sự mập mờ.

## Định tuyến bằng phân loại: trả một lời gọi nhỏ để né một lời gọi lớn

Khi yêu cầu đến dưới dạng văn bản tự do không có ranh giới tính năng — một giao diện chat tổng quát, một hộp thư, một hàng đợi hỗ trợ — bạn không định tuyến tĩnh được. Bạn cần quyết định theo từng yêu cầu.

Bài toán kinh tế đơn giản và đáng kiểm tra rành mạch: lời gọi phân loại phải rẻ hơn đáng kể so với chênh lệch giữa hai model mà nó đang chọn. Một bộ phân loại tốn một phần năm model lớn mà chỉ chuyển hướng được một phần ba lưu lượng thì không đủ bù chính nó.

Hai lưu ý thực dụng:

- **Định tuyến theo năng lực cần thiết, không theo chủ đề.** "Đây có phải câu hỏi lập trình không?" là câu hỏi sai; "việc này cần suy luận nhiều bước hay chỉ là tra cứu?" mới là câu hỏi đúng.
- **Heuristic thắng bộ phân loại nhiều hơn ta tưởng.** Độ dài đầu vào, có khối code hay không, số lượt hội thoại, có công cụ khả dụng không, người dùng có trả phí không — những tín hiệu này tính ra miễn phí và nắm được phần lớn thông tin. Chỉ dùng tới model khi các tín hiệu rẻ thật sự không tách được các trường hợp.

Và hãy lệch ngưỡng định tuyến một cách bất đối xứng. Gửi yêu cầu dễ tới model lớn thì tốn tiền; gửi yêu cầu khó tới model nhỏ thì tạo ra câu trả lời sai mà người dùng nhìn thấy. Hai cái giá đó không cân bằng, nên ngưỡng không nên đặt ở mức tự tin 50%.

## Thác bậc: thử rẻ trước, leo thang khi hỏng

Thác bậc chạy model nhỏ trước rồi leo thang khi kết quả không đạt. Nó hấp dẫn vì quyết định được đưa ra *sau* khi đã nhìn thấy một lần thử, chứ không phải đoán trước.

Toàn bộ bài toán thiết kế nằm ở tín hiệu leo thang. Xếp theo độ tin cậy giảm dần:

1. **Kiểm tra tất định.** Đầu ra phải parse được thành JSON, thoả schema, chứa trường bắt buộc, trích dẫn một ID tài liệu có thật, cho ra phép tính khớp. Hỏng thì leo thang. Đây là tín hiệu duy nhất tôi tin trọn vẹn, và đó là lý do thác bậc hợp với tác vụ có cấu trúc hơn nhiều so với văn xuôi.
2. **Cho phép từ chối tường minh.** Hãy nói rõ với model nhỏ rằng trả về `{"insufficient": true}` là câu trả lời chấp nhận được và được mong đợi, và làm cho việc từ chối trở nên nhẹ nhàng. Model sẽ dùng nó nếu bạn cho phép; sẽ không dùng nếu prompt ngụ ý bắt buộc phải trả lời.
3. **Kiểm chứng ở hạ nguồn.** Đoạn văn được truy hồi không chứa dữ kiện đang được khẳng định; code sinh ra không biên dịch được; tổng tiền trích xuất không khớp các dòng chi tiết. Đây là kiểm tra thật với thế giới.
4. **Độ tự tin do model tự khai.** Hỏi model xem nó tự tin đến đâu. Yếu, hiệu chuẩn kém, và lại là thứ mà phần lớn bài hướng dẫn về thác bậc xây lên. Cùng lắm chỉ dùng để phá thế hoà.

Nếu tác vụ của bạn không áp dụng được ba tín hiệu đầu, thác bậc sẽ chạy không tốt và định tuyến bằng phân loại là cấu trúc phù hợp hơn.

Mô hình chi phí đáng nói chính xác. Nếu leo thang xảy ra với xác suất *p*, chi phí kỳ vọng mỗi yêu cầu là chi phí model nhỏ cộng *p* lần chi phí model lớn. **Khi *p* vượt khoảng 30-40%, bạn trả tiền cho hai lời gọi đủ thường xuyên tới mức lẽ ra cứ đi thẳng tới model lớn** — và còn cộng thêm độ trễ. Hãy đo *p* và cảnh báo khi nó trôi; nó sẽ trôi khi lưu lượng của bạn thay đổi.

## Định tuyến ảnh hưởng tới độ trễ ra sao

Định tuyến có một hồ sơ độ trễ mà người ta hay quên tính:

- **Định tuyến tĩnh** cải thiện độ trễ một cách chắc chắn. Model nhỏ chạy nhanh hơn.
- **Định tuyến bằng phân loại** cộng độ trễ của bộ phân loại vào mọi yêu cầu, kể cả những yêu cầu rốt cuộc chạy trên model nhỏ. Hãy giữ nó thật nhỏ, hoặc dùng heuristic cục bộ rẻ tiền.
- **Thác bậc** cộng trọn độ trễ của model nhỏ vào mọi yêu cầu bị leo thang. Với giao diện streaming, chuyện này tệ hơn nghe tưởng: người dùng không thấy gì trong lần thử đầu, rồi lại không thấy gì khi lần thứ hai bắt đầu.

Với bất cứ thứ gì hướng tới người dùng và có streaming, điểm cuối cùng đó thường loại thẳng thác bậc. Chúng hợp nhất với việc chạy nền và xử lý theo lô, nơi thêm một giây không thành vấn đề.

## Đừng định tuyến làm mất prompt cache

Đây là tương tác khiến nhiều người bất ngờ. Prompt caching giảm giá đáng kể cho phần tiền tố lặp lại — một system prompt dài, một tập định nghĩa công cụ cố định, một tài liệu bạn hỏi nhiều câu về nó. **Cache là theo từng model.** Chia lưu lượng cho hai model là chia tỉ lệ trúng cache cho hai cache.

Nếu workload của bạn có tiền tố chung lớn và tỉ lệ trúng cache cao, model lớn có cache hoàn toàn có thể rẻ hơn model nhỏ không cache. Hãy đo hoá đơn thật ở cả hai cách bố trí thay vì suy luận từ bảng giá niêm yết. Đây là cách phổ biến nhất khiến một dự án định tuyến kết thúc mà chẳng tiết kiệm được gì.

## Đo xem nó có hiệu quả không

Một thay đổi định tuyến làm biến đổi đồng thời chi phí, độ trễ và chất lượng; bạn phải theo dõi cả ba, nếu không thì đang mù ở đúng cái quan trọng nhất.

- Ghi log **model được chọn và lý do** trên mọi yêu cầu. Thiếu nó bạn không debug được một phàn nàn chất lượng, vì bạn không biết model nào đã tạo ra câu trả lời tệ.
- Theo dõi tỉ lệ leo thang và phân bố của bộ phân loại theo thời gian. Cả hai đều trôi.
- Chạy bộ eval trên từng nhánh định tuyến riêng biệt. Một con số chất lượng tổng hợp che mất trường hợp lưu lượng model nhỏ tệ đi 15% trong khi model lớn vẫn giữ nguyên.
- Giữ một **công tắc ngắt** ép mọi yêu cầu về model lớn. Khi có phàn nàn chất lượng, bật nó lên là cách nhanh nhất để xác nhận hay loại trừ định tuyến là nguyên nhân.

## Khi một model duy nhất mới là câu trả lời đúng

Định tuyến là một tối ưu, và tối ưu nào cũng có điểm hoà vốn:

- **Lưu lượng thấp.** Nếu hoá đơn hàng tháng nhỏ, sự phức tạp của định tuyến tốn thời gian kỹ sư nhiều hơn khoản tiết kiệm. Hãy xem lại khi quy mô lớn hơn.
- **Workload khó đồng đều.** Nếu mọi yêu cầu đều thật sự cần model tiên tiến, định tuyến chỉ thêm kiểu hỏng.
- **Sản phẩm còn sớm.** Prompt và tính năng vẫn đang thay đổi. Quyết định định tuyến hôm nay sẽ sai sau một tháng, và bạn sẽ không nhận ra.
- **Rủi ro cao trên mỗi yêu cầu.** Y tế, pháp lý, tài chính. Khoản tiết kiệm không đáng để đánh đổi một lớp lỗi mà model rẻ đã trả lời thứ lẽ ra không nên trả lời.

Prompt gọn hơn, prompt caching, và đơn giản là yêu cầu đầu ra ngắn hơn thường mang lại khoản tiết kiệm lớn hơn định tuyến mà không kèm rủi ro chất lượng. Hãy vắt kiệt những thứ đó trước.

## Câu hỏi thường gặp

**Định tuyến tiết kiệm được bao nhiêu trên thực tế?**

Phụ thuộc hoàn toàn vào cơ cấu lưu lượng của bạn. Định tuyến tĩnh trên workload có tỉ lệ việc dễ lớn là đòn bẩy đơn lẻ mạnh nhất; workload khó đồng đều thì không tiết kiệm được gì.

**Bộ định tuyến có nên là một LLM không?**

Chỉ khi các tín hiệu rẻ không đủ. Độ dài, cấu trúc và ngữ cảnh tính năng giải quyết được phần lớn trường hợp mà không tốn gì.

**Tôi có thể làm thác bậc nhiều hơn hai tầng không?**

Được, và hiếm khi đáng. Mỗi tầng thêm độ trễ và thêm một tiêu chí leo thang có thể sai.

**Chọn model nhỏ nào?**

Bằng cách đánh giá các ứng viên trên bộ eval của chính bạn, không phải theo bảng xếp hạng benchmark. Những khác biệt quan trọng với bạn là đặc thù theo tác vụ.

**Định tuyến có phá vỡ tính liền mạch của hội thoại không?**

Có thể. Đổi model giữa hội thoại làm giọng văn và định dạng thay đổi thấy rõ. Hãy ghim model trong suốt một cuộc hội thoại.

---

*Năng lực model, giá và hành vi caching lấy từ tài liệu nhà cung cấp được liên kết phía trên và thay đổi thường xuyên — hãy kiểm chứng chi tiết hiện hành trước khi thiết kế dựa trên chúng. Cách phân loại các kiểu định tuyến, thứ tự xếp hạng tín hiệu leo thang, lập luận về điểm hoà vốn và khuyến nghị bắt đầu bằng định tuyến tĩnh là đánh giá của riêng tôi từ việc xây các hệ thống LLM nhạy chi phí.*
