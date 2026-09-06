---
title: "Thiết kế công cụ mà AI agent thật sự dùng được"
description: "Một agent dùng sai công cụ của bạn thường không phải lỗi mô hình. Đó là lỗi đặt tên, lỗi schema, hoặc lỗi thông báo lỗi — và cả ba đều thuộc về bạn."
seoDescription: "Hướng dẫn thực tế về thiết kế định nghĩa công cụ cho agent LLM: đặt tên, mô tả JSON Schema, độ mịn, thông báo lỗi biết dạy, tính bất biến khi lặp lại, và cách đánh giá một bộ công cụ."
keywords:
  - thiet ke cong cu llm
  - function calling thuc hanh tot
  - schema cong cu ai agent
  - dinh nghia cong cu mcp
  - xu ly loi cong cu llm
  - do min cong cu agent
category: "Phân tích"
topic: "AI"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-10"
emoji: "🛠️"
tags: ["AI", "Agent", "Dùng công cụ", "Thiết kế API", "LLM"]
sources:
  - name: "Tool use — tài liệu Anthropic API"
    url: "https://docs.anthropic.com/en/docs/build-with-claude/tool-use"
  - name: "Model Context Protocol — đặc tả"
    url: "https://modelcontextprotocol.io/"
  - name: "Function calling — tài liệu OpenAI API"
    url: "https://platform.openai.com/docs/guides/function-calling"
  - name: "JSON Schema specification"
    url: "https://json-schema.org/"
  - name: "Building effective agents — Anthropic engineering"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
  - name: "OpenAPI Specification"
    url: "https://spec.openapis.org/oas/latest.html"
related:
  - slug: "ai-observability-tracing-llm-apps"
    title: "Quan sát ứng dụng LLM: truy vết một hệ thống không tất định"
  - slug: "ai-embeddings-choosing-a-model"
    title: "Chọn mô hình embedding: những câu hỏi thật sự quan trọng"
draft: false
---

Agent đầu tiên tôi đưa lên sản phẩm có một công cụ tên là `query`. Nó nhận một chuỗi và trả về các dòng. Mô hình dùng nó liên tục, sai bét, và ngày càng tuyệt vọng, vì `query` chẳng nói cho nó biết có thể truy vấn cái gì, schema ra sao, hay một lần thất bại nghĩa là gì.

Đổi tên thành `search_orders_by_customer_email` và cho tham số một mô tả tử tế đã sửa gần hết hành vi mà không cần đụng tới mô hình hay prompt. Đó là hình dạng chung của thiết kế công cụ: **năng lực của mô hình với công cụ của bạn phần lớn là hàm của việc bạn mô tả chúng tốt đến đâu.**

## Định nghĩa là tài liệu cho một người đọc không hỏi lại được

Một định nghĩa công cụ được đọc đúng một lần, không có bối cảnh gì trước đó, bởi một thứ không mở được codebase của bạn và không nhắn được cho bạn trên Slack. Mọi thứ nó cần phải nằm trong schema.

```json
{
  "name": "search_orders",
  "description": "Tìm đơn hàng của một khách theo địa chỉ email. Trả về tối đa 50 đơn, mới nhất trước. Chỉ những đơn trong 24 tháng gần nhất được đánh chỉ mục — với đơn cũ hơn hãy dùng fetch_order_archive. Trả về danh sách rỗng nếu khách không có đơn nào; đây không phải lỗi.",
  "input_schema": {
    "type": "object",
    "properties": {
      "email": {
        "type": "string",
        "description": "Email của khách, đúng như đã lưu. Không phân biệt hoa thường. Không khớp một phần — nếu bạn chỉ có tên thì hãy dùng search_customers trước."
      },
      "status": {
        "type": "string",
        "enum": ["pending", "shipped", "delivered", "cancelled"],
        "description": "Bộ lọc tuỳ chọn. Bỏ trống để lấy mọi trạng thái."
      }
    },
    "required": ["email"]
  }
}
```

Bốn thứ trong định nghĩa đó đang làm việc thật, và mỗi thứ ứng với một kiểu hỏng tôi từng chứng kiến:

- **Giới hạn được nói rõ.** Thiếu "tối đa 50", một mô hình được nhờ đếm số đơn của khách sẽ tự tin báo là 50.
- **Ranh giới được nói rõ.** "24 tháng gần nhất" cộng với con trỏ sang công cụ khác ngăn mô hình kết luận rằng một đơn cũ không tồn tại.
- **Trường hợp rỗng được nói rõ.** Nếu không, kết quả rỗng sẽ được thuật lại cho người dùng như một thất bại.
- **Tham số nói rõ nó *không* là gì.** "Không khớp một phần" ngăn cái vòng lặp trong đó mô hình thử `"john"`, không ra gì, thử `"john%"`, không ra gì, rồi xin lỗi.

Hãy viết mô tả cho các kiểu hỏng, không phải cho đường đi thuận lợi. Đường thuận lợi thường suy ra được từ chính cái tên.

## Độ mịn: đánh đổi không ai cảnh báo bạn

Với một cơ sở dữ liệu, bạn có thể phơi ra một công cụ (`run_sql`) hoặc bốn mươi (`get_customer`, `list_orders`, `update_shipping_address`, …). Cả hai đều sai ở hai thái cực.

| Cách làm | Tốt ở chỗ | Hỏng ở chỗ |
| --- | --- | --- |
| Một công cụ tổng quát | Linh hoạt, tập định nghĩa nhỏ | Mô hình phải biết schema của bạn; lỗi mờ mịt; không ràng buộc được nó làm gì |
| Nhiều công cụ chuyên biệt | Ý định rõ, phân quyền được, lỗi tốt | Danh sách công cụ phình bối cảnh; mô hình phải chọn giữa những cái gần trùng nhau |

Quy tắc làm việc của tôi: **một công cụ cho mỗi hành động có nghĩa với người dùng, không phải cho mỗi thao tác cơ sở dữ liệu.** "Huỷ đơn hàng" là một công cụ dù nó ghi vào ba bảng. Ngược lại `get_customer_by_id` và `get_customer_by_email` nên là một công cụ với tham số kiểu hoặc-cái-này-hoặc-cái-kia, vì dưới góc nhìn của mô hình chúng là một ý định.

Khi số công cụ vượt khoảng hai mươi, vấn đề chuyển từ chất lượng mô tả sang việc lựa chọn: những công cụ gần trùng nhau với mô tả tương tự sẽ bị lẫn lộn. Tới lúc đó, hoặc hợp nhất lại, hoặc chẻ agent ra để mỗi agent con chỉ thấy tập con của riêng nó.

## Thông báo lỗi là cơ hội thứ hai để dạy

Bề mặt bị dùng ít nhất trong thiết kế agent là giá trị lỗi trả về. Một công cụ thất bại với `{"error": "Invalid input"}` đã phí một lượt. Một công cụ thất bại kèm chỉ dẫn sửa thường làm đúng ngay ở lần gọi kế tiếp.

```python
# Tệ
return {"error": "not found"}

# Tốt hơn
return {
    "error": "no_customer_with_email",
    "message": "Không tìm thấy khách với email 'jon@example.com'. "
               "Hãy kiểm tra chính tả, hoặc gọi search_customers với một phần "
               "tên để tìm địa chỉ đúng.",
    "did_you_mean": ["john@example.com"],
}
```

Những quy tắc tôi áp cho mọi lỗi của công cụ:

- Nói xem **đầu vào** sai chỗ nào, không phải chuyện gì xảy ra bên trong. "Stack trace" thì không hành động được.
- Nêu tên công cụ nên gọi thay thế, nếu có.
- Kèm dữ liệu gần đúng khi việc đó rẻ — `did_you_mean` ở trên biến hai lượt lãng phí thành không lượt nào.
- Phân biệt **thử lại được** với **kết thúc**. Lỗi vượt hạn mức nên nói "thử lại sau 5 giây"; lỗi phân quyền nên nói "đừng thử lại, hãy báo người dùng."

Điểm cuối quan trọng hơn vẻ ngoài của nó. Thiếu nó, một agent gặp lỗi phân quyền sẽ thử lại vô hạn với những biến thể nhỏ, đốt token và trông như bị hỏng.

## Thiết kế cho việc lặp lại và thất bại một phần

Agent hay thử lại. Chúng thử lại sau những lần hết giờ mà chúng không phân biệt được với thất bại, và chúng thử lại khi đầu ra của bước trước mơ hồ.

Hãy làm mọi công cụ có thay đổi dữ liệu trở nên **bất biến khi gọi lại, hoặc được canh giữ tường minh**. Nhận một khoá idempotency do phía gọi cung cấp, hoặc trả về một câu "đã xong rồi" rõ ràng thay vì thực hiện hành động hai lần:

```json
{
  "status": "already_cancelled",
  "message": "Đơn 1182 đã được huỷ lúc 2026-08-02T11:04Z. Không thực hiện gì thêm."
}
```

Phản hồi đó tốt hơn hẳn cả việc âm thầm thành công lẫn việc trả về lỗi, vì nó nói cho mô hình biết *trạng thái cuối mong muốn đang đúng* — và đó mới là điều nó thật sự muốn biết.

Với bất cứ thứ gì thật sự phá huỷ, đừng trông cậy vào phán đoán của mô hình chút nào. Hãy trả về một token xác nhận mà công cụ đòi hỏi ở lần gọi thứ hai, để một tầng có con người có thể xen vào giữa hai lần gọi đó.

## Đánh giá bộ công cụ, không chỉ prompt

Phần khó chịu: bạn không thể biết một bộ công cụ có tốt hay không chỉ bằng cách đọc nó. Hãy dựng một bộ đánh giá nhỏ trước khi lặp cải tiến.

1. Viết 20-40 yêu cầu người dùng thực tế, bao gồm cả những yêu cầu mà công cụ của bạn **không** đáp ứng được.
2. Ghi lại với từng cái: mô hình có chọn đúng công cụ, điền đúng tham số, phục hồi được sau lỗi, và dừng đúng lúc không?
3. Đọc những lần thất bại như phản hồi về thiết kế, không phải phản hồi về mô hình.

Những ca yêu cầu bất khả thi là thứ người ta hay bỏ qua và cũng là thứ quan trọng nhất. Một bộ công cụ tốt sẽ tạo ra câu "tôi không làm được việc đó với những công cụ đang có"; một bộ tồi tạo ra một lời gọi công cụ sai đầy tự tin. **Nếu agent của bạn không bao giờ nói nó không làm được gì, thì bộ đánh giá của bạn quá dễ.**

Khi một thất bại xuất hiện, cách sửa gần như luôn là một trong số: đổi tên công cụ, thêm một câu vào mô tả, gộp hai công cụ, hoặc cải thiện một thông báo lỗi. Sửa prompt là phương án cuối, vì nó không đi theo khi công cụ được một agent khác dùng.

## Câu hỏi thường gặp

**Mô tả có nên kèm ví dụ không?**

Một ví dụ trong mô tả sẽ giúp ích với những công cụ có định dạng không hiển nhiên (khoảng ngày, cú pháp truy vấn). Nhiều hơn một thường có nghĩa là chính schema nên rõ ràng hơn.

**Mô tả dài được bao nhiêu?**

Đủ dài để ngăn dùng sai; mỗi token là phần bối cảnh bạn chi cho mọi yêu cầu. Vài câu cho mỗi công cụ và một câu cho mỗi tham số là ngân sách hợp lý.

**Tôi có cần MCP cho việc này không?**

Không — MCP là chuẩn vận chuyển và đóng gói cho công cụ. Các nguyên tắc thiết kế ở đây áp dụng dù bạn phơi công cụ qua MCP, qua function calling gốc của nhà cung cấp, hay qua vòng lặp tự viết.

**Công cụ nên trả về JSON hay văn xuôi?**

Dữ liệu có cấu trúc cho bất cứ thứ gì mô hình phải suy luận chính xác; văn xuôi thì ổn cho phần tóm tắt. Hãy nhất quán, vì hình dạng lẫn lộn khiến việc phân tích thất bại khó hơn.

**Làm sao chặn agent gọi một công cụ trong vòng lặp?**

Đặt trần số vòng lặp, và làm cho lỗi trở thành kết thúc ở những chỗ thử lại vô ích. Đừng chỉ trông cậy vào chỉ dẫn bằng lời.

---

*Cơ chế định nghĩa công cụ, cấu trúc JSON Schema và luồng function calling đều nằm trong tài liệu nhà cung cấp và đặc tả liên kết bên trên. Quy tắc độ mịn, danh sách kiểm tra thông báo lỗi, hướng dẫn về idempotency và cách tiếp cận đánh giá là đánh giá riêng của tôi từ việc xây và gỡ lỗi các bộ công cụ agent; hành vi mô hình khác nhau giữa các nhà cung cấp và phiên bản, nên hãy kiểm chứng với cái bạn triển khai.*
