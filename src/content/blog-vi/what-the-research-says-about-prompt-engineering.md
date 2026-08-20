---
title: "Nghiên cứu thật sự nói gì về prompt engineering — kiểm chứng 5 tuyên bố đang lan truyền"
description: "Năm tuyên bố về prompt engineering đang được chia sẻ khắp nơi, đem đối chiếu với chính các paper được viện dẫn. Hai cái đúng, ba cái không — và sự thật còn hữu ích hơn lời đồn."
seoDescription: "Kiểm chứng 5 tuyên bố phổ biến về prompt engineering: câu hỏi mớm đáp án, chain-of-thought so với persona, trích dẫn bịa đặt tại NeurIPS 2025, prompt nhiều ràng buộc và few-shot examples."
keywords:
  - prompt engineering là gì
  - nghiên cứu prompt engineering
  - cách viết prompt hiệu quả
  - chain of thought còn hiệu quả không
  - prompt nhiều yêu cầu
  - ai bịa trích dẫn
  - mẹo viết prompt chatgpt claude
category: "Chuyên sâu"
topic: "Prompt Engineering"
level: "Cơ bản"
author: "Trung Hiếu"
publishDate: "2026-08-20"
emoji: "🔬"
tags: ["AI", "Prompt Engineering", "LLM", "Nghiên cứu", "ChatGPT", "Claude"]
sources:
  - name: "Tag Questions and the Generational Reversal of Sycophancy Across 45 Language Models (arXiv 2607.23976)"
    url: "https://arxiv.org/abs/2607.23976"
  - name: "When \"A Helpful Assistant\" Is Not Really Helpful: Personas in System Prompts Do Not Improve Performances of Large Language Models (arXiv 2311.10054)"
    url: "https://arxiv.org/abs/2311.10054"
  - name: "Large Language Models as Optimizers — paper gốc của câu \"take a deep breath\" (arXiv 2309.03409)"
    url: "https://arxiv.org/abs/2309.03409"
  - name: "GPTZero — trích dẫn bịa đặt trong các paper được nhận tại NeurIPS 2025"
    url: "https://gptzero.me/news/neurips/"
  - name: "Compound Deception in Elite Peer Review: A Failure Mode Taxonomy of 100 Fabricated Citations at NeurIPS 2025 (arXiv 2602.05930)"
    url: "https://arxiv.org/abs/2602.05930"
  - name: "Instruction Stacking Collapse: A Benchmark and the Capability-Dependent Value of Prompt Compilation (arXiv 2608.02639)"
    url: "https://arxiv.org/abs/2608.02639"
  - name: "When Instructions Multiply: Measuring and Estimating LLM Capabilities of Multiple Instructions Following (arXiv 2509.21051)"
    url: "https://arxiv.org/abs/2509.21051"
  - name: "Order Matters: Investigate the Position Bias in Multi-constraint Instruction Following (arXiv 2502.17204)"
    url: "https://arxiv.org/abs/2502.17204"
  - name: "SEQUOR: A Multi-Turn Benchmark for Realistic Constraint Following (arXiv 2605.06353)"
    url: "https://arxiv.org/abs/2605.06353"
draft: false
---

Gần đây có một bài tóm tắt "khoa học đằng sau prompt engineering" được chia sẻ rất nhiều, dựa trên năm kết quả nghiên cứu. Danh sách ý tưởng thì hay. Nhưng mấy con số đi kèm lại thuộc kiểu được copy từ bài này sang bài khác mà không ai mở paper gốc ra coi. Nên mình mở ra coi.

Hai trong năm tuyên bố là đúng. Ba cái còn lại thì không — ít nhất là không đúng theo cách đang được lan truyền. Có một trường hợp nghiên cứu thật còn cho kết quả **ngược lại** với lời khuyên.

Không phải vì vậy mà vứt cả danh sách đi. Phần lời khuyên nền tảng phần lớn vẫn hợp lý. Nhưng nếu bạn định thay đổi cách làm việc dựa trên một nghiên cứu, thì nên biết đó là nghiên cứu nào và nó thật sự đo cái gì.

Dưới đây là từng tuyên bố, phần nào mình kiểm chứng được, và mình sẽ làm gì với nó.

## Tóm tắt nhanh

| Tuyên bố | Kết luận |
| --- | --- |
| Câu hỏi mớm đáp án sẽ đẩy model theo hướng bạn đã ngụ ý | ✅ Đúng |
| "Think step by step" giờ thua một role ngắn (IBM, 430.000 lượt đánh giá) | ❌ Không tìm được nghiên cứu — và research về persona cho kết quả ngược lại |
| ~1/4 paper NeurIPS 2025 được kiểm có trích dẫn bịa (Microsoft, 2,6 triệu nguồn) | ⚠️ Vấn đề có thật, con số sai |
| Model sụp đổ khi vượt quá ~3 ràng buộc cùng lúc (Meta, 15 model) | ⚠️ Hiện tượng có thật và được ghi nhận rõ; nghiên cứu cụ thể đó thì không tìm thấy |
| Bỏ ví dụ đi thì độ chính xác tăng từ 74% lên 83,8% (EPFL/Apple/Mistral) | ❌ Không kiểm chứng được |

## 1. Đừng hỏi "…đúng không?" — cái này đúng

**Tuyên bố:** một nghiên cứu của Cornell Tech thử 45 model, chỉ đổi vài từ trong câu hỏi, và thấy rằng cách hỏi kiểu "X là lựa chọn tốt hơn, đúng không?" kéo câu trả lời về phía X.

**Kết luận: đúng.** Paper là [*Tag Questions and the Generational Reversal of Sycophancy Across 45 Language Models*](https://arxiv.org/abs/2607.23976). "Tag question" chính là cái đuôi `…, đúng không?` hay `…, phải không?`. Nghiên cứu giữ nguyên nội dung câu hỏi, chỉ đổi phần đuôi, chạy trên 45 model và đo mức độ đồng ý dịch chuyển bao nhiêu.

Chi tiết thú vị mà bản tóm tắt phổ biến bỏ mất: hiệu ứng này **không đồng đều giữa các thế hệ model**. Model mới không đơn giản là "ngoan hơn" — ở một số chỗ xu hướng còn đảo ngược. Nên "model mới ít nịnh hơn" cũng không phải giả định an toàn.

**Nên làm gì.** Bóc câu trả lời ra khỏi câu hỏi. Khác biệt không hề nhỏ:

```text
❌ Thuê nhà là lựa chọn khôn ngoan hơn với tình hình của tôi, đúng không?
✅ So sánh mua và thuê nhà cho tình huống của tôi: 32 tuổi, thu nhập
   freelance trung bình 25 triệu/tháng nhưng dao động 30%, đã tiết kiệm
   được 1,5 tỷ, dự định ở lại thành phố này ít nhất 3 năm nữa.
   Nêu rõ giả định nào ảnh hưởng nhiều nhất tới kết luận.
```

Bản thứ hai dài hơn nhưng **ít chỉ thị hơn**. Đó mới là điểm chính — bạn đưa dữ kiện để nó suy luận, chứ không đưa kết luận để nó gật đầu.

Chuyện này đúng xa hơn phạm vi lời khuyên đời sống. `Cách tổ chức API này ổn đúng không?` là mời model đồng ý. `Phản biện cách tổ chức API này so với các phương án khác mà bạn sẽ cân nhắc` là mời model làm việc.

## 2. "Think step by step" so với role ngắn — tuyên bố này không đứng vững

**Tuyên bố:** IBM chạy hơn 430.000 lượt đánh giá trên 8 kiểu prompt, thấy "think step by step" thua cách hỏi thường, và kiểu thắng là câu hỏi cộng một vai trò ngắn như *"với góc nhìn của một kỹ sư độ tin cậy."*

**Kết luận: mình không tìm được nghiên cứu này.** Tìm theo mọi hướng đều không ra thứ gì khớp với mô tả hay con số đó. Nếu nó tồn tại thì không nằm ở chỗ các bài tóm tắt nói.

Quan trọng hơn, nghiên cứu được ghi nhận rõ ràng nhất gần với chủ đề này lại cho kết quả **ngược lại** ở phần persona. [*When "A Helpful Assistant" Is Not Really Helpful*](https://arxiv.org/abs/2311.10054) (Findings of EMNLP 2024) thử persona trong system prompt một cách có hệ thống, qua nhiều vai trò và nhiều bộ câu hỏi kiến thức, và thấy persona **không** cải thiện độ chính xác một cách đáng tin cậy — ở khá nhiều trường hợp, điểm khi có persona còn *thấp hơn* baseline không persona. Các nghiên cứu sau đó lặp lại cùng một hình dạng kết quả: nói với model rằng nó là chuyên gia không làm nó trả lời đúng hơn ở những câu có đáp án kiểm chứng được.

Vậy nên lời khuyên đang lan truyền — "bỏ step-by-step, thêm role vào" — theo bằng chứng hiện tại thì một nửa không có cơ sở, một nửa còn ngược.

**Phần trực giác đằng sau vẫn đúng.** Nửa đầu của tuyên bố có chạm vào cái gì đó thật. Câu "take a deep breath and work through this step by step" đến từ [*Large Language Models as Optimizers*](https://arxiv.org/abs/2309.03409), và bản tóm tắt gốc nói đúng: nó được tìm ra trên PaLM 2-L năm 2023. Đó là thời model sẽ không tự chia nhỏ bài toán nếu bạn không yêu cầu. Model reasoning bây giờ tự chia nhỏ mặc định, gắn thêm câu đó lên trên chẳng thêm được gì.

**Nên làm gì:**

- Đừng thêm "think step by step" vào model reasoning. Nó làm sẵn rồi.
- Vẫn nên dùng với model nhỏ/nhanh, hoặc khi bạn cần thấy các bước trung gian để kiểm tra.
- Coi persona là **công cụ điều chỉnh giọng văn và đối tượng, không phải công cụ tăng độ chính xác.** "Giải thích như một kỹ sư độ tin cậy đang báo cáo cho ban giám đốc" là chỉ dẫn hợp lệ về văn phong và cách đóng khung. Nó không làm model biết thêm điều gì.

Phân biệt cuối cùng đó mới là phần dùng được. Persona định hình **cách** câu trả lời đọc lên như thế nào. Nó không định hình **việc câu trả lời có đúng hay không**.

## 3. Tự tin ≠ chính xác — kết luận đúng, con số sai

**Tuyên bố:** Microsoft kiểm 2,6 triệu nguồn tham khảo và thấy khoảng 1/4 paper NeurIPS 2025 được kiểm có ít nhất một trích dẫn do AI bịa.

**Kết luận: hiện tượng được ghi nhận rất kỹ; nhưng con số thì không.** Cuộc kiểm tra mà mọi người đang nhắc tới thật ra là của [GPTZero](https://gptzero.me/news/neurips/), không phải Microsoft. Nó quét 4.841 trong khoảng 5.290 paper được nhận tại NeurIPS 2025 và xác nhận **hơn 100 trích dẫn bịa nằm rải trong 51 paper**.

Con số đó gần 1% hơn là 25%. Rất khác nhau — và vẫn đáng báo động, vì mỗi paper trong số đó đã qua phản biện với ít nhất ba reviewer.

Paper phân loại đi sau, [*Compound Deception in Elite Peer Review*](https://arxiv.org/abs/2602.05930), mới là bài đáng đọc hơn. Nó phân loại 100 trích dẫn bịa đó, và phân bố cho bạn biết cần cảnh giác với cái gì:

| Kiểu lỗi | Tỷ lệ |
| --- | --- |
| Bịa hoàn toàn — paper không hề tồn tại | 66% |
| Sai thuộc tính — paper có thật, sai tác giả/năm/hội nghị | 27% |
| Chiếm dụng định danh — DOI thật nhưng trỏ sang công trình khác | 4% |
| Placeholder — để nguyên chữ "Firstname Lastname" | 2% |
| Sai ngữ nghĩa — trích dẫn thật nhưng không hề chứng minh điều được nêu | 1% |

**Nên làm gì.** Để ý: 27% + 4% = **31% số trích dẫn bịa có dính tới một paper thật, tìm được**. Đó mới là loại nguy hiểm. Một lần search trả về *một cái gì đó* tạo cảm giác đã kiểm chứng, nhưng thật ra chưa.

Nên quy trình kiểm phải cụ thể:

1. Paper có tồn tại không? (Search đúng tiêu đề.)
2. **Tác giả và năm** có đúng không? Một phần ba lỗi nằm ở đây.
3. Paper có **thật sự nói điều nó đang được trích cho** không? Mở ra và tìm đúng câu đó.

Bước 3 là bước mọi người hay bỏ, và cũng chính là lý do bài viết này tồn tại — mấy tuyên bố mình đang kiểm chứng đều *nghe như* đã có nguồn.

## 4. Đừng nhét mười điều luật vào một prompt — hiệu ứng có thật, nguồn thì không

**Tuyên bố:** Meta thử 15 model với prompt có từ 1 đến 12 yêu cầu. Ở mức 8 yêu cầu, model làm đúng từng yêu cầu khoảng 41%, đúng cả 8 cùng lúc chỉ khoảng 5,7%, và 12/15 model mất ổn định khi vượt quá 3 yêu cầu.

**Kết luận: mình không tìm được nghiên cứu cụ thể đó,** nhưng hiện tượng mà nó mô tả lại là một trong những kiểu lỗi được đo đạc kỹ nhất hiện nay. Nhiều benchmark 2025–2026 đo thẳng vào chuyện này:

- [*Instruction Stacking Collapse*](https://arxiv.org/abs/2608.02639) xếp chồng 24 chỉ thị có verifier, áp từ 1 tới 20 chỉ thị mỗi lần, trên các model production. Tỷ lệ tuân thủ giảm **phi tuyến** khi chồng dày lên — mức giảm tăng tốc chứ không dốc đều.
- [*When Instructions Multiply*](https://arxiv.org/abs/2509.21051) đo và ước lượng năng lực khi số chỉ thị tăng dần.
- [*SEQUOR*](https://arxiv.org/abs/2605.06353) cho thấy đúng kiểu suy giảm đó trong hội thoại nhiều lượt, và thấy nó **tệ hơn đáng kể khi các ràng buộc xuất hiện dần theo thời gian** thay vì đưa hết một lần — tức đúng như cách hội thoại thật diễn ra.
- [*Order Matters*](https://arxiv.org/abs/2502.17204) tìm thấy position bias trong prompt nhiều ràng buộc: **vị trí** của ràng buộc trong prompt ảnh hưởng tới việc nó có sống sót hay không.

Nên là: đừng trích "41% và 5,7%". Nhưng hãy hành động theo kết luận, vì chiều của hiệu ứng thì không ai tranh cãi, và kết quả từ SEQUOR nghĩa là nó áp dụng cho các cuộc chat kéo dài của bạn chứ không chỉ prompt một phát.

**Nên làm gì.** Tách phần tạo nội dung khỏi phần kiểm ràng buộc:

```text
Lượt 1 — tạo:
  Viết bài hướng dẫn migration. Hai yêu cầu bắt buộc: tách riêng
  Android và iOS, và mọi code block phải chạy được nguyên trạng.

Lượt 2 — kiểm (tin nhắn mới, đính kèm bản nháp):
  Đối chiếu bản nháp này với từng mục dưới đây. Mỗi mục trả lời
  PASS hay FAIL kèm một câu trích từ bản nháp làm bằng chứng.
  Chưa sửa gì cả.
  1. Dưới 1.500 từ
  2. Không dùng dấu gạch ngang dài
  3. Mọi khẳng định từ nguồn ngoài đều có link
  4. Xưng hô nhất quán "bạn" xuyên suốt
  5. Kết bằng một checklist

Lượt 3 — sửa:
  Chỉ sửa những mục bị đánh FAIL. Giữ nguyên phần còn lại.
```

Kiểm dễ hơn vừa-tạo-vừa-kiểm. Và yêu cầu *"trích bằng chứng"* rất quan trọng: không có nó, model sẽ tự tin đánh PASS cho những mục rõ ràng đã fail — tức là lặp lại đúng vấn đề ở mục #3.

Thêm một thói quen nữa, xuất phát từ kết quả position bias: đặt ràng buộc quan trọng nhất ở **cuối** prompt, gần chỗ model bắt đầu sinh nội dung.

## 5. Mục tiêu quan trọng hơn ví dụ — không kiểm chứng được

**Tuyên bố:** nghiên cứu từ EPFL, Apple và Mistral AI cho thấy prompt có ví dụ đạt 74%, còn bỏ ví dụ và nói rõ mục tiêu thì đạt 83,8%.

**Kết luận: không kiểm chứng được.** Mình không tìm được paper nào khớp với tổ hợp ba tổ chức đó cùng những con số đó. Có nghiên cứu hợp lệ cho thấy few-shot có thể gây hại trong một số bối cảnh cụ thể — code synthesis là một trường hợp được ghi nhận — nhưng "ví dụ thua mục tiêu, 74% so với 83,8%" thì không phải kết quả mình chỉ ra được cho bạn.

**Phần còn lại sau khi bỏ con số đi.** Lời khuyên vẫn hợp lý, vì một lý do rất cơ học: ví dụ thì **thiếu xác định**. Đưa model ba bản newsletter rồi nói "viết giống vậy", nó phải tự đoán bạn đang muốn giống ở điểm nào. Độ dài? Giọng văn? Câu đùa ở đoạn hai? Rất thường nó sẽ chọn đặc điểm chung bề mặt nhất — mà đặc điểm bề mặt lại đúng là thứ khiến văn AI đọc lên biết ngay là văn AI.

So sánh:

```text
❌ Đây là 3 bản newsletter của tôi. Viết bản thứ 4 giống mấy bản này.

✅ Tỷ lệ mở newsletter của tôi giảm từ 34% xuống 21% trong 3 tháng.
   Vẫn gửi thứ Ba 9h sáng, vẫn format cũ, danh sách không đổi,
   kiểu đặt tiêu đề cũng không đổi. Trước khi kết luận gì, hãy nói
   cho tôi biết bạn cần thêm dữ liệu nào để phân biệt được vấn đề
   deliverability với chuyện người đọc chán nội dung.
```

Bản thứ hai đưa cho model một bài toán để giải thay vì một cái vỏ để bắt chước. Nó cũng kết thúc bằng việc hỏi model *chưa biết gì* — làm lộ giả định trước khi giả định đó bị nướng vào câu trả lời.

Giữ ví dụ lại cho những việc thuần cơ học: định dạng output, cấu trúc JSON, nhãn phân loại, style guide có luật rõ ràng. Bỏ ví dụ đi khi bạn cần model **phán đoán**.

## Cái gì thật sự khái quát được

Bỏ hết mấy con số không kiểm chứng được ra, còn lại một bức tranh khá nhất quán:

**Nêu mục tiêu và ràng buộc, đừng nêu đáp án và khuôn mẫu.** Tuyên bố 1 và tuyên bố 5 thật ra là cùng một phát hiện nhìn từ hai phía. Câu hỏi mớm thì trao sẵn kết luận; một đống ví dụ thì trao sẵn khuôn. Cả hai đều thay thế phần suy luận của model bằng phỏng đoán của bạn về output.

**Kiểm tra tách khỏi tạo nội dung.** Tuyên bố 3 và 4 đi cùng nhau. Model vừa không đáng tin khi phải thỏa nhiều ràng buộc một lúc, vừa không đáng tin khi tự báo cáo độ chính xác của chính nó. Cả hai đều tốt lên khi việc kiểm là một lượt riêng và bắt buộc có bằng chứng.

**Mẹo prompt có hạn sử dụng.** "Take a deep breath" là thật, được đo, được công bố — và được đo trên PaLM 2-L năm 2023. Nó hết hạn. Mọi thứ bạn đọc hôm nay, kể cả bài này, đều có hạn dùng gắn với một thế hệ model.

**Và kiểm nguồn trước khi chia sẻ lại.** Ba trong năm tuyên bố của một bản tóm tắt được chia sẻ rộng rãi, viết rất chắc nịch, đã không sống sót qua một lần mở nguồn ra coi. Đó mới là bài học thật, và nó áp dụng cho cả output của AI lẫn bài viết của con người.

## Câu hỏi thường gặp

**Có nên bỏ hẳn câu "think step by step" không?**
Với model reasoning hiện tại thì có, nó thừa. Vẫn giữ lại cho model nhỏ/nhanh, hoặc khi bạn cần soi các bước trung gian.

**Persona có gây hại không?**
Bằng chứng cho thấy nó không giúp tăng độ chính xác một cách đáng tin cậy, và đôi khi còn làm giảm ở các câu hỏi kiến thức. Nhưng vẫn dùng tốt — và hữu ích — để điều chỉnh giọng văn, đối tượng và cách đóng khung.

**Một prompt nhét được bao nhiêu ràng buộc thì an toàn?**
Các benchmark đã công bố cho thấy chất lượng bắt đầu giảm khá sớm và giảm phi tuyến. Hai tới ba yêu cầu cứng mỗi lượt, phần còn lại kiểm riêng — đó là quy tắc làm việc có cơ sở.

**Chain-of-thought chết rồi à?**
Không. Nó được tích hợp sẵn rồi. Câu prompt thì thừa, kỹ thuật thì không.

**Kiểm nhanh một trích dẫn do AI đưa ra bằng cách nào?**
Search đúng tiêu đề, rồi đối chiếu tác giả và năm, rồi mở ra tìm câu chứng minh cho khẳng định. Khoảng một phần ba trích dẫn bịa vẫn trỏ tới paper có thật, nên "nó tồn tại" là chưa đủ.

---

*Năm tuyên bố được xem xét trong bài đến từ một bản tóm tắt tiếng Việt được chia sẻ rộng rãi, dựa trên bài viết của Ruben Hassid về khoa học đằng sau prompt engineering. Các ý tưởng trong đó đáng để đào sâu, nên chúng xứng đáng được kiểm chứng thay vì chép lại. Mọi paper được nhắc tới đều có link ở trên; chỗ nào mình không tìm được nguồn, mình nói thẳng là không tìm được thay vì chuyển tiếp con số đi.*
