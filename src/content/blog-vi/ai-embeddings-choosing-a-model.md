---
title: "Chọn mô hình embedding: những câu hỏi thật sự quan trọng"
description: "Thứ hạng trên bảng xếp hạng là tín hiệu ít hữu ích nhất. Số chiều, độ dài ngữ cảnh, khả năng đa ngôn ngữ, chi phí ở quy mô của bạn và nỗi đau khi đổi ý mới là những thứ quan trọng hơn nhiều."
seoDescription: "Cách chọn mô hình embedding cho truy hồi: số chiều và chi phí lưu trữ, độ dài chuỗi, hỗ trợ đa ngôn ngữ, tìm kiếm đối xứng và bất đối xứng, tự vận hành hay dùng API, và đánh giá trên dữ liệu của chính bạn."
keywords:
  - chon mo hinh embedding
  - so chieu embedding chi phi
  - embedding da ngon ngu truy hoi
  - so chieu vector database
  - han che bang xep hang mteb
  - danh gia embedding rag
category: "Phân tích"
topic: "AI"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-09"
emoji: "🧭"
tags: ["AI", "Embedding", "RAG", "Tìm kiếm", "Kiến trúc"]
sources:
  - name: "MTEB leaderboard — Hugging Face"
    url: "https://huggingface.co/spaces/mteb/leaderboard"
  - name: "Sentence Transformers — tài liệu"
    url: "https://www.sbert.net/"
  - name: "Embeddings — tài liệu OpenAI API"
    url: "https://platform.openai.com/docs/guides/embeddings"
  - name: "Embeddings — tài liệu Anthropic"
    url: "https://docs.anthropic.com/en/docs/build-with-claude/embeddings"
  - name: "pgvector — extension vector cho PostgreSQL"
    url: "https://github.com/pgvector/pgvector"
  - name: "FAISS — thư viện tìm kiếm tương đồng"
    url: "https://faiss.ai/"
related:
  - slug: "ai-chunking-strategies-that-matter"
    title: "Chia nhỏ tài liệu cho truy hồi: quyết định âm thầm chặn trần chất lượng RAG"
  - slug: "ai-agent-tool-design"
    title: "Thiết kế công cụ mà AI agent thật sự dùng được"
draft: false
---

Quy trình thường thấy là: mở bảng xếp hạng, sắp theo điểm trung bình, lấy mô hình đứng đầu vừa túi tiền, rồi đi tiếp. Nó cho ra lựa chọn bảo vệ được khoảng một nửa số lần, và ở nửa còn lại, nó hỏng một cách đắt đỏ — vì đổi mô hình embedding nghĩa là nhúng lại toàn bộ và dựng lại mọi chỉ mục.

Đây là những câu hỏi dự báo kết quả tốt hơn thứ hạng.

## Nó có chạy tốt trên văn bản *của bạn* không?

Điểm trung bình trên benchmark là một hỗn hợp có trọng số của nhiều tác vụ, mà phần lớn không phải tác vụ của bạn. Một mô hình dẫn đầu tổng thể có thể tụt hậu tệ hại ở đúng cái bạn cần — điều khoản pháp lý, mã hàng, ticket hỗ trợ khách hàng tiếng Việt, hay mã nguồn.

Bài đánh giá thật sự quan trọng chỉ mất một buổi chiều:

1. Thu 50-100 truy vấn thật từ log của bạn (hoặc tự viết, nếu chưa có lưu lượng).
2. Với mỗi truy vấn, đánh dấu những tài liệu trong kho *đáng lẽ* phải được truy hồi. Việc gán nhãn này chính là phần công việc thật.
3. Nhúng kho tài liệu bằng từng mô hình ứng viên, chạy các truy vấn, đo recall@k với đúng k mà bạn thật sự đưa cho mô hình sinh.

**Recall@k mới là chỉ số cần tối ưu, không phải điểm tương đồng.** Bộ sinh của bạn nhìn thấy k đoạn hàng đầu; nếu đoạn đúng nằm trong đó thì thứ hạng bên trong k gần như không quan trọng. Nếu nó không nằm trong đó, không có gì ở phía sau cứu vãn được.

Hãy kèm cả những truy vấn *đáng lẽ không trả về gì*. Một mô hình trả về các láng giềng gần đầy tự tin cho câu hỏi ngoài phạm vi sẽ nạp bối cảnh không liên quan cho bộ sinh, và đó chính là nơi ảo giác sinh ra trong hệ thống truy hồi.

## Số chiều là quyết định về lưu trữ và độ trễ

Số chiều là tham số có hệ quả kỹ thuật trực tiếp nhất.

| Số chiều | Lưu trữ cho 1 triệu đoạn (float32) | Ghi chú |
| --- | --- | --- |
| 384 | ~1,5 GB | Nhanh, rẻ, đủ dùng cho nhiều lĩnh vực |
| 768 | ~3 GB | Điểm cân bằng phổ biến |
| 1536 | ~6 GB | Thường gặp ở các mô hình API lớn |
| 3072 | ~12 GB | Lợi ích giảm dần với đa số kho tài liệu |

Lưu trữ là chi phí nhìn thấy được; thời gian dựng chỉ mục, bộ nhớ khi tìm kiếm và độ trễ mỗi truy vấn đều tăng theo cách tương tự. Và đây là con số *trước khi* tính nhân bản và phần phụ trội của chỉ mục — một chỉ mục HNSW cộng thêm khá nhiều so với kích thước vector thô.

Hai cách giảm nhẹ đáng biết:

- **Lượng tử hoá.** Lưu vector dạng int8 cắt bộ nhớ khoảng bốn lần với mức mất recall khiêm tốn trên đa số kho. Lượng tử hoá nhị phân còn đi xa hơn và khả thi như một bộ lọc giai đoạn một, sau đó chấm điểm lại chính xác vài trăm kết quả đầu.
- **Cắt bớt chiều.** Một số mô hình được huấn luyện sao cho phần đầu của vector vẫn dùng được — bạn có thể lưu 512 trong 1536 chiều mà giữ được phần lớn chất lượng. Hãy kiểm tra ứng viên của bạn có hỗ trợ điều này không trước khi giả định.

Mặc định của tôi: bắt đầu ở 768 trở xuống, và chỉ tăng lên nếu phép đo recall của chính bạn nói rằng mô hình lớn hơn xứng đáng. Nó thường xứng đáng ít hơn khoảng cách trên bảng xếp hạng gợi ý.

## Độ dài chuỗi, và cái bẫy trong đó

Mọi mô hình embedding đều có độ dài đầu vào tối đa, và phần văn bản vượt quá sẽ bị cắt — thường là âm thầm. Một mô hình giới hạn 512 token khi nhận một đoạn 2.000 token sẽ nhúng một phần tư đầu và vứt phần còn lại, đúng kiểu hỏng tạo ra một hệ thống truy hồi "thỉnh thoảng cứ bỏ sót cái gì đó".

Nhưng cửa sổ ngữ cảnh dài không phải cách sửa như người ta tưởng. **Một vector duy nhất cho tài liệu 8.000 token sẽ bình quân hoá mất mọi thứ đặc thù của nó.** Đoạn dài truy hồi kém cho câu hỏi cụ thể bất kể giới hạn công bố của mô hình, vì embedding là bản tóm tắt của một bản tóm tắt.

Vậy nên độ dài chuỗi ràng buộc việc chia đoạn chứ không thay thế nó: hãy chọn kích thước đoạn nằm thoải mái trong giới hạn với dư địa rộng rãi, và coi giới hạn ấy là cái trần bạn không bao giờ tiến tới gần.

## Đối xứng hay bất đối xứng?

Hai tác vụ khác nhau hay bị gộp làm một:

- **Đối xứng**: truy vấn và tài liệu là cùng loại văn bản. "Tìm các ticket hỗ trợ tương tự."
- **Bất đối xứng**: một câu hỏi ngắn đi truy hồi những đoạn dài. Đây là RAG tiêu chuẩn.

Mô hình được huấn luyện cho loại này hoặc loại kia, và nhiều mô hình đòi một **tiền tố** để biết chúng đang nhúng phía nào — kiểu như `query: …` so với `passage: …`. Bỏ qua tiền tố mà mô hình được huấn luyện cùng sẽ làm giảm chất lượng truy hồi một cách đo được, và đây là kiểu hỏng âm thầm: mọi thứ vẫn chạy, chỉ là kết quả tệ hơn.

Nếu bạn chỉ lấy một chi tiết vận hành từ bài này, hãy lấy chi tiết đó. Đọc model card để biết tiền tố bắt buộc, và áp dụng nhất quán cả lúc dựng chỉ mục lẫn lúc truy vấn.

## Đa ngôn ngữ, và tiếng Việt nói riêng

Nếu kho tài liệu hoặc người dùng của bạn không hoàn toàn dùng tiếng Anh, bảng xếp hạng tổng quát gần như vô dụng như một tín hiệu. Mô hình đa ngôn ngữ đánh đổi một phần chất lượng tiếng Anh lấy khả năng xuyên ngôn ngữ, và chất lượng theo từng ngôn ngữ dao động rất lớn tuỳ vào lượng ngôn ngữ đó có trong dữ liệu huấn luyện.

Những câu hỏi cần trả lời tường minh:

- Truy vấn bằng một ngôn ngữ có cần truy hồi tài liệu bằng ngôn ngữ khác không? Đó là truy hồi xuyên ngôn ngữ, một yêu cầu khó hơn việc chỉ xử lý được nhiều ngôn ngữ.
- Bộ tách token có xử lý ngôn ngữ của bạn hiệu quả không? Một mô hình tốn ba token cho mỗi âm tiết tiếng Việt vừa đắt hơn vừa thực chất có ngữ cảnh ngắn hơn.
- Dấu thanh có được xử lý không? Người dùng gõ không dấu suốt ngày. Hãy thử `"thanh toan"` có truy hồi được tài liệu chứa "thanh toán" không — nếu không, bạn cần chuẩn hoá hoặc một lớp dự phòng theo từ khoá, bất kể chọn mô hình nào.

## API hay tự vận hành

| | Mô hình API | Tự vận hành |
| --- | --- | --- |
| Cài đặt | Vài phút | Cần GPU hoặc đường CPU chậm |
| Hình dạng chi phí | Theo token, mãi mãi | Hạ tầng cố định |
| Nhúng lại hàng loạt | Có thể thật sự tốn kém | Chỉ tốn thời gian |
| Nơi lưu dữ liệu | Rời khỏi hạ tầng của bạn | Ở nguyên chỗ |
| Ổn định phiên bản | Nhà cung cấp có thể ngừng hỗ trợ | Đóng băng cho tới khi bạn đổi |

Ranh giới tôi dùng: **nếu bạn nhúng lại kho tài liệu hơn mức thỉnh thoảng, hãy tự vận hành.** Nhúng lại không hiếm — nó xảy ra mỗi khi bạn đổi chiến lược chia đoạn, mà bạn sẽ đổi, hai lần, trong vài tháng đầu.

Dòng về ổn định phiên bản đáng được nhấn mạnh. Một mô hình embedding qua API bị ngừng hỗ trợ sẽ ép bạn dựng lại chỉ mục theo lịch của nhà cung cấp chứ không phải lịch của bạn. Hãy hỏi chính sách ngừng hỗ trợ trước khi xây dựng trên nó.

## Chuẩn bị cho việc đổi ý

Bất cứ thứ gì bạn chọn rồi cũng sẽ sai vào lúc nào đó. Vài khoản bảo hiểm rẻ tiền:

- **Luôn lưu văn bản gốc bên cạnh vector.** Nhúng lại từ kho của chính bạn tốt hơn là đi lấy lại từ hệ thống nguồn.
- **Ghi tên và phiên bản mô hình trong mọi dòng.** Chỉ mục trộn mô hình sinh ra điểm tương đồng vô nghĩa, và không có cột này thì bạn sẽ không biết chuyện đó đang xảy ra.
- **Giữ lời gọi embedding sau một interface duy nhất** để đổi nhà cung cấp chỉ là sửa một file.
- **Hỗ trợ ghi kép trong lúc chuyển đổi**: dựng chỉ mục vào cột mới, đánh giá, chuyển sang, rồi bỏ cột cũ. Điều này biến việc đổi mô hình thành một lần triển khai thông thường thay vì một sự cố.

## Câu hỏi thường gặp

**Tôi có nên tinh chỉnh mô hình embedding không?**

Chỉ sau khi đã dùng cạn việc chia đoạn và tìm kiếm lai. Tinh chỉnh cần các cặp có nhãn và phải nhúng lại sau mỗi lần cập nhật; nó chủ yếu đáng giá với từ vựng thật sự chuyên biệt.

**Kết hợp tìm kiếm từ khoá và vector có đáng không?**

Thường là có, và đó là phần bổ sung giá trị nhất sau khi đã chọn mô hình hợp lý. Vector bỏ sót những định danh chính xác — mã sản phẩm, số hiệu lỗi, tên riêng — mà tìm kiếm từ khoá tìm ra dễ dàng.

**Làm sao so sánh các mô hình một cách công bằng?**

Cùng đoạn, cùng truy vấn, cùng k, cùng tiền tố. Đổi một biến mỗi lần, và hãy nghi ngờ khi thấy bước nhảy lớn — nó thường là khác biệt về tiền tố hoặc cắt chuỗi, không phải chất lượng mô hình.

**Embedding có hết hạn không?**

Vector thì không, nhưng nội dung của bạn thì có. Hãy nhúng lại tài liệu đã thay đổi; nhúng lại tài liệu không đổi bằng cùng mô hình thì chẳng có lợi ích gì.

**Tôi trộn nhiều mô hình trong một chỉ mục được không?**

Không. Vector từ các mô hình khác nhau không so sánh được với nhau, kể cả khi cùng số chiều.

---

*Các đặc tính mô hình như số chiều, giới hạn chuỗi, yêu cầu tiền tố và hỗ trợ lượng tử hoá khác nhau tuỳ mô hình và được ghi trên model card của từng mô hình cùng các tài liệu liên kết bên trên — hãy kiểm chứng với đúng mô hình bạn chọn thay vì dựa vào các khoảng giá trị ở đây. Quy trình đánh giá, khuyến nghị về số chiều, ranh giới API-so-với-tự-vận-hành và danh sách kiểm tra chuyển đổi là đánh giá riêng của tôi từ việc xây các hệ thống truy hồi.*
