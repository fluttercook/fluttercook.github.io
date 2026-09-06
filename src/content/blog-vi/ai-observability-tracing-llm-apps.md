---
title: "Quan sát ứng dụng LLM: truy vết một hệ thống không tất định"
description: "Bạn không tái hiện được một câu trả lời tệ bằng cách chạy lại yêu cầu. Điều bạn làm được là ghi lại đủ về lần chạy đó để không bao giờ cần chạy lại. Đây là những gì cần ghi, cần lấy mẫu, và cần bỏ qua."
seoDescription: "Cách gắn công cụ quan sát cho ứng dụng LLM: ghi gì cho mỗi yêu cầu và mỗi bước, span OpenTelemetry cho lần chạy agent, quy chi phí và độ trễ, xử lý dữ liệu cá nhân, lấy mẫu, và biến trace thành bộ đánh giá."
keywords:
  - quan sat truy vet llm
  - opentelemetry span llm
  - go loi agent bang trace
  - theo doi chi phi llm moi yeu cau
  - ghi log prompt du lieu ca nhan
  - danh gia llm tu log
category: "Hướng dẫn"
topic: "AI"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-07"
emoji: "🔭"
tags: ["AI", "Quan sát hệ thống", "Truy vết", "LLM", "Vận hành"]
sources:
  - name: "OpenTelemetry — đặc tả traces"
    url: "https://opentelemetry.io/docs/concepts/signals/traces/"
  - name: "OpenTelemetry semantic conventions cho GenAI"
    url: "https://opentelemetry.io/docs/specs/semconv/gen-ai/"
  - name: "Messages API — tài liệu Anthropic API"
    url: "https://docs.anthropic.com/en/api/messages"
  - name: "Building effective agents — Anthropic engineering"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
  - name: "Structured logging — OpenTelemetry logs"
    url: "https://opentelemetry.io/docs/concepts/signals/logs/"
  - name: "OWASP Top 10 for LLM Applications"
    url: "https://owasp.org/www-project-top-10-for-large-language-model-applications/"
related:
  - slug: "ai-agent-tool-design"
    title: "Thiết kế công cụ mà AI agent thật sự dùng được"
  - slug: "ai-guardrails-prompt-injection-defense"
    title: "Prompt injection: cái gì thật sự phòng thủ được"
draft: false
---

"Một khách hàng nói trợ lý bảo họ rằng chúng ta cho đổi trả trong 90 ngày. Chúng ta không có chính sách đó."

Trong một dịch vụ bình thường, bạn tìm yêu cầu đó, chạy lại, và đọc đường đi của mã. Trong ứng dụng LLM, chạy lại cho bạn một câu trả lời khác, phần truy hồi có thể đã đổi, và đường đi của mã giống hệt với cả nghìn yêu cầu đã hành xử đúng đắn. **Trace ở đây không phải công cụ hỗ trợ gỡ lỗi; nó là bằng chứng duy nhất rằng sự việc từng xảy ra.**

## Ghi lại toàn bộ lần chạy, không chỉ điểm cuối

Một tin nhắn của người dùng có thể sinh ra cả chục lời gọi mô hình, truy hồi và gọi công cụ. Chỉ ghi phản hồi cuối cùng thì cho bạn biết cái gì sai mà không cho biết sai ở đâu.

Hãy mô hình hoá lần chạy thành một trace với các span lồng nhau:

```
trace: conversation_turn          user_id, conversation_id, turn_index
├── span: retrieve                query, k, latency, chunk_ids, scores
├── span: llm_call                model, temperature, tokens_in/out, stop_reason
│   └── span: tool.search_orders  arguments, result_size, error, latency
├── span: llm_call                (lượt thứ hai, sau kết quả công cụ)
└── span: guardrail_check         verdict, rule_id
```

Bộ quy ước ngữ nghĩa GenAI của OpenTelemetry cho bạn tên thuộc tính chuẩn cho các span gọi mô hình, và việc áp dụng chúng là đáng ngay cả khi bạn chưa xuất dữ liệu sang một backend truy vết nào — đặt tên là `gen_ai.request.model` thay vì `model_name` nghĩa là sau này bạn chuyển sang công cụ chuẩn mà không phải viết lại phần gắn công cụ.

Những thuộc tính mà lần nào thiếu tôi cũng tiếc:

- **Prompt thật sự đã gửi đi**, sau khi điền khuôn mẫu — không phải cái khuôn mẫu. Lỗi thường nằm ở khâu điền vào.
- **ID các đoạn đã truy hồi cùng điểm số của chúng**, không phải chuỗi ngữ cảnh đã nối lại. ID cho phép bạn hỏi "tài liệu đúng có được truy hồi không?", câu hỏi chia mọi thất bại RAG thành hai vấn đề rất khác nhau.
- **Toàn bộ tham số và kết quả của công cụ.** Cắt chúng còn 200 ký tự thì tiết kiệm được dung lượng và huỷ hoại tính hữu dụng của trace.
- **`stop_reason` hoặc thứ tương đương.** Một phản hồi bị cắt vì chạm trần token trông giống câu trả lời tệ nhưng thật ra là lỗi cấu hình.
- **Phiên bản prompt hoặc cấu hình.** Không có nó thì một lần thoái lui sau khi triển khai là không quy được cho ai.

## Chi phí và độ trễ thuộc về span

Mỗi lời gọi mô hình đều có giá, và trong vòng lặp agent thì cái giá đó là hàm của một quyết định luồng điều khiển mà không ai review. Hãy gắn số token và chi phí vào từng span rồi cộng dồn lên trace:

```python
span.set_attribute("gen_ai.usage.input_tokens", usage.input_tokens)
span.set_attribute("gen_ai.usage.output_tokens", usage.output_tokens)
span.set_attribute("app.cost_usd", price(model, usage))
span.set_attribute("app.cache_read_tokens", usage.cache_read_input_tokens)
```

Rồi hãy nhìn vào **phân phối**, đừng bao giờ nhìn giá trị trung bình. Độ trễ và chi phí LLM lệch rất mạnh: p50 thì ổn còn p99 là một lần chạy lặp mười một vòng rồi bỏ cuộc. Số trung bình che giấu đúng những lần chạy bạn cần nhìn.

Hai chỉ số dẫn xuất mà tôi thấy luôn đáng đặt cảnh báo:

- **Số bước mỗi lần chạy.** Nó tăng nghĩa là agent đang vật lộn — thường là một công cụ bắt đầu hỏng, hoặc một mô tả vừa bị đổi.
- **Chi phí trên mỗi kết quả thành công**, không phải chi phí trên mỗi yêu cầu. Lần chạy thất bại cũng tốn tiền, và một thay đổi làm giảm chi phí mỗi yêu cầu trong khi hạ tỉ lệ thành công là một bước lùi.

## Đối diện thẳng với vấn đề riêng tư

Prompt chứa bất cứ thứ gì người dùng gõ vào, và ngữ cảnh truy hồi chứa bất cứ thứ gì có trong tài liệu của bạn. Một kho trace làm ngây thơ chính là một bản sao dữ liệu nhạy cảm nhất của bạn nằm trong hệ thống có kiểm soát truy cập yếu hơn bản gốc.

Những gì đã hiệu quả với tôi:

- **Che dữ liệu ngay tại điểm ghi nhận**, không phải trong một tác vụ ở phía sau. Một bộ che theo mẫu cho email, số điện thoại, dãy số dạng thẻ và số định danh cá nhân, áp dụng trước khi span rời khỏi tiến trình.
- **Lưu nội dung và siêu dữ liệu tách biệt.** Siêu dữ liệu — thời lượng, số token, ID đoạn, mã lỗi, phán quyết — không nhạy cảm và có thể giữ lâu. Nội dung thì nhạy cảm và nên có thời hạn lưu ngắn.
- **Tham chiếu, đừng sao chép.** Lưu ID đoạn thay vì văn bản đoạn; văn bản vốn đã nằm trong kho tài liệu của bạn cùng cơ chế kiểm soát truy cập riêng.
- **Bắt việc ghi toàn bộ nội dung phải được bật thủ công theo môi trường**, và mặc định tắt ở sản phẩm. Một tập mẫu cộng với việc ghi tường minh cho những hội thoại bị gắn cờ đáp ứng phần lớn nhu cầu gỡ lỗi.
- **Cho người dùng một đường xoá dữ liệu** thật sự chạm tới kho trace. Nếu một yêu cầu xoá không gỡ được trace, bạn có vấn đề tuân thủ bất kể tài liệu chính sách viết gì.

## Lấy mẫu mà không đánh mất các thất bại

Truy vết đầy đủ mọi lần chạy là tốn kém ở quy mô lớn. Lấy mẫu đều là cách giảm sai, vì nó vứt bỏ thất bại với cùng tỉ lệ như thành công, mà thất bại mới là toàn bộ mục đích.

Hãy dùng lấy mẫu ở đuôi: đệm trace lại, quyết định ở cuối.

```python
def should_keep(trace):
    if trace.had_error or trace.guardrail_triggered:
        return True
    if trace.steps > STEP_THRESHOLD or trace.cost_usd > COST_THRESHOLD:
        return True
    if trace.user_feedback in ("thumbs_down", "reported"):
        return True
    if trace.latency_ms > LATENCY_P99:
        return True
    return random.random() < 0.02   # mức nền cho nhóm chạy khoẻ mạnh
```

Hãy giữ mức nền 2%. Không có mẫu của những lần chạy thành công thì bạn không có gì để so sánh, và mọi dị thường đều trông có ý nghĩa.

## Khép vòng: trace trở thành bộ đánh giá của bạn

Đây là phần các nhóm hay bỏ qua, và là nơi phần thưởng nằm.

Mỗi thất bại trong sản phẩm là một ca kiểm thử bạn không phải nghĩ ra. Một quy trình có tác dụng:

1. Người dùng báo một câu trả lời tệ, hoặc một guardrail kích hoạt, hoặc phản hồi là tiêu cực.
2. Trace được lôi ra, xem xét, và hành vi đúng được viết xuống.
3. Các đầu vào — tin nhắn người dùng, các đoạn đã truy hồi, kết quả công cụ — trở thành một fixture trong bộ đánh giá của bạn.
4. Mọi thay đổi prompt hay mô hình đều chạy trên bộ đó trước khi triển khai.

Sáu tháng làm như vậy sẽ tạo ra một bộ đánh giá bám vào những thứ thật sự từng sai, và điều đó giá trị hơn nhiều so với bất kỳ tập ca kiểm thử nào bạn nghĩ ra từ đầu. **Một nhóm không có vòng lặp này sẽ sửa đi sửa lại cùng một nhóm thất bại mãi mãi**, vì chẳng có gì ngăn một thay đổi mang nó trở lại.

## Câu hỏi thường gặp

**Tôi có cần một sản phẩm quan sát chuyên cho LLM không?**

Không cần để bắt đầu. Log có cấu trúc kèm một trace ID, truy vấn bằng công cụ bạn đang có, đã bao phủ một lượng công việc đáng ngạc nhiên. Hãy dùng tên thuộc tính chuẩn sớm để việc chuyển đổi sau này rẻ.

**Nên giữ trace bao lâu?**

Siêu dữ liệu vài tháng; nội dung đầy đủ vài ngày tới vài tuần, tuỳ vào lập trường riêng tư của bạn. Bất cứ thứ gì đã trở thành fixture đánh giá thì chuyển sang một kho riêng, lưu vĩnh viễn.

**Tôi có nên ghi system prompt ở mọi lời gọi không?**

Ghi phiên bản hoặc mã băm của nó ở mọi lời gọi, và ghi toàn văn một lần cho mỗi phiên bản. Lặp lại một system prompt dài trên mọi span thì tốn kém mà chẳng thêm gì.

**Truy vết phản hồi dạng streaming thế nào?**

Bắt đầu span lúc gửi yêu cầu, kết thúc khi luồng hoàn tất, và ghi riêng thời gian tới token đầu tiên — đó mới là độ trễ người dùng thật sự cảm nhận.

**Còn trace cho các lần chạy đánh giá thì sao?**

Hãy gắn công cụ y hệt và gắn thẻ môi trường. Việc so sánh được một ca đánh giá thất bại với chính trace sản phẩm mà nó bắt nguồn là đáng với chút công thêm.

---

*Các khái niệm trace của OpenTelemetry và bộ quy ước ngữ nghĩa GenAI đều nằm trong tài liệu liên kết bên trên; tên thuộc tính trong đặc tả đó còn tiến hoá, nên hãy kiểm tra phiên bản hiện hành trước khi chuẩn hoá theo. Danh sách thuộc tính, chính sách lấy mẫu, các thực hành về riêng tư và vòng lặp trace-thành-eval là đánh giá riêng của tôi từ việc vận hành ứng dụng LLM trong sản phẩm thật.*
