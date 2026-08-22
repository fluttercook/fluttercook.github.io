---
title: "Đừng parse văn xuôi nữa: schema, tool calling và output type-check được"
description: "Hành trình từ regex bóc chữ trong câu trả lời của model, sang xin JSON trong prompt, rồi tới schema được ép ngay ở tầng API. Mỗi bước xóa sổ một nhóm bug — và bước cuối cùng vẫn không nói được câu trả lời có đúng hay không."
seoDescription: "JSON Schema và tool calling biến output LLM thành dữ liệu có kiểu: thiết kế schema, validate và retry, stream JSON, và vì sao hợp lệ không có nghĩa là đúng."
keywords:
  - structured output llm
  - json schema tool calling
  - pydantic validate output llm
  - ép model trả về json
  - stream json dở dang llm
  - validate và retry output llm
category: "Chuyên sâu"
topic: "AI Engineering"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-22"
emoji: "📐"
tags: ["AI", "LLM", "Python", "JSON Schema", "Pydantic"]
sources:
  - name: "Claude — Structured outputs"
    url: "https://platform.claude.com/docs/en/build-with-claude/structured-outputs"
  - name: "Claude — Tool use overview"
    url: "https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview"
  - name: "Claude — Streaming"
    url: "https://platform.claude.com/docs/en/build-with-claude/streaming"
  - name: "Understanding JSON Schema"
    url: "https://json-schema.org/understanding-json-schema"
  - name: "Tài liệu Pydantic"
    url: "https://docs.pydantic.dev/latest/"
related:
  - slug: "what-the-research-says-about-prompt-engineering"
    title: "Nghiên cứu thật sự nói gì về prompt engineering — kiểm chứng 5 tuyên bố đang lan truyền"
  - slug: "building-an-ai-agent-team-chief-of-staff-pattern"
    title: "Mô hình Chief of Staff: biến đống chat AI rời rạc thành một đội ngũ agent"
draft: false
---

Mọi tính năng LLM có đụng tới database đều bắt đầu giống nhau. Bạn nhờ model phân loại một ticket support, nó trả lời `This looks like a billing issue, probably high priority.`, và bạn viết một cái regex. Chạy được. Bạn ship. Hai tuần sau model đổi giọng thành `I'd categorise this as billing-related`, regex của bạn trả về `None`, nhánh `if severity == "high"` lặng lẽ false, và một ticket nghiêm trọng nằm im trong hàng đợi ưu tiên thấp ba ngày.

Không có gì hỏng. Không exception nào được raise. Model cũng chẳng hallucinate. Nó chỉ diễn đạt một câu trả lời đúng theo cách khác, còn cái parser của bạn — vốn chưa bao giờ là parser, chỉ là một phỏng đoán về pattern — âm thầm không đồng ý.

Cách sửa đầu tiên ai cũng nghĩ tới là xin gắt hơn: "chỉ trả về JSON, không markdown." Cách đó có giúp, nhưng nó dời chỗ lỗi chứ không xóa lỗi. Cách sửa thật là ngừng coi response như văn bản cần diễn giải, và bắt đầu coi nó như một giá trị mà API bị **ràng buộc** phải sinh ra. Đó chính là thứ JSON Schema và tool calling thật sự mang lại.

Bài này đi qua ba giai đoạn đó, mỗi giai đoạn xóa được gì, cách thiết kế schema để model điền được mà không phải gồng, và cái lỗi sống sót qua tất cả: một response validate sạch sẽ mà vẫn sai.

## Ba giai đoạn, ba nhóm bug khác nhau

| Giai đoạn | Bạn viết gì | Nhóm bug bị xóa | Nhóm bug còn nguyên |
| --- | --- | --- | --- |
| Regex trên văn xuôi | `re.search(r"priority: (\w+)", text)` | — | Đổi cách diễn đạt, đổi format, `None` âm thầm |
| "Trả về JSON" trong prompt | `json.loads(strip_fences(text))` | Đổi cách diễn đạt | Code fence, câu dạo đầu, sai key, sai kiểu |
| Schema ở tầng API | `output_config={"format": {...}}` hoặc tool `strict` | Toàn bộ phần cú pháp | Ngữ nghĩa — câu trả lời hợp lệ nhưng không đúng sự thật |

Đọc cột cuối theo chiều dọc. Mỗi bước mua cho bạn một nhóm vấn đề không bao giờ phải viết code xử lý nữa. Không bước nào mua được dòng cuối cùng.

## Regex trên văn xuôi hỏng đúng vào những ngày model làm tốt

Thứ khiến việc parse văn xuôi khó bị bắt trong review là nó hỏng trên output **đúng**. Nếu model trả lời sai, ít nhất bạn còn thấy một câu trả lời sai. Đằng này model trả lời đúng, chỉ là diễn đạt theo dạng regex chưa lường tới, và lỗi trông y hệt "không khớp".

Chỗ gọi hàm còn lại hai lựa chọn tệ: raise khi không khớp (giờ câu trả lời đúng làm sập pipeline), hoặc rơi về giá trị mặc định (giờ câu trả lời đúng biến thành mặc định, không ai thấy). Phần lớn codebase chọn cách thứ hai, vì cách thứ nhất làm ai đó bị gọi lúc nửa đêm. Đó là lý do bạn có một classifier mà phân bố output thật sự là 60% `"unknown"` và cả quý không ai để ý.

Vấn đề sâu hơn: ngôn ngữ tự nhiên không có ranh giới giữa câu trả lời và lời bình về câu trả lời. `Probably high, though it depends on the SLA tier` chứa cả giá trị bạn cần lẫn một lời rào đón, và không regex nào chỉ ra được chỗ rào đón bắt đầu.

## Xin JSON chỉ dời chỗ lỗi, không xóa lỗi

Bỏ "chỉ trả về một JSON object, không gì khác" vào prompt thì hình dạng lỗi đổi. Bạn sẽ gặp, xếp theo tần suất:

- JSON bị bọc trong ` ```json `.
- Một câu lịch sự đứng trước object.
- JSON đúng nhưng thừa key bạn không hỏi, hoặc key viết khác đi (`customerId` thay vì `customer_id`).
- `"severity": "High"` trong khi enum của bạn viết thường.
- `"severity": "high-ish"`, vì model thật sự không chắc và chuỗi tự do cho nó chỗ để nhét sự lưỡng lự.
- Cụt giữa chừng, vì object vượt `max_tokens` và mất dấu ngoặc cuối.

Thế là bạn viết parser phòng thủ. Bóc fence. Tìm `{` đầu tiên và `}` cuối cùng. Hạ chữ thường cho enum. Ép `"3"` thành `3`. Xử lý dấu ngoặc thiếu. Đoạn code này phình ra mỗi lần bạn thấy một kiểu lỗi mới trong log, không bao giờ xong, và — đây mới là điểm chính — **nó là parser cho một ngôn ngữ chưa ai định nghĩa.** Bạn đang dịch ngược một format từ mẫu.

Prompt là một lời đề nghị. Nó không phải một bất biến.

## Schema ở tầng API mới là bất biến

Cả hai cơ chế structured output đều đẩy việc thực thi ra khỏi prompt và vào chính request. Schema được áp trong lúc response đang được sinh, nên một token làm hỏng schema là token model không thể phát ra. Bạn không còn phải xin nữa.

JSON Schema thô, dùng làm định dạng output cho response:

```python
import json, anthropic

client = anthropic.Anthropic()

TRIAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "evidence": {
            "type": "string",
            "description": "Verbatim quote from the ticket that decided the category.",
        },
        "category": {
            "type": "string",
            "enum": ["billing", "bug", "feature_request", "account", "other"],
        },
        "severity": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
        "customer_id": {
            "type": ["string", "null"],
            "description": "Customer ID if the ticket states one. null if it does not.",
        },
        "needs_human": {"type": "boolean"},
    },
    "required": ["evidence", "category", "severity", "customer_id", "needs_human"],
    "additionalProperties": False,
}

response = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": ticket_text}],
    output_config={"format": {"type": "json_schema", "schema": TRIAGE_SCHEMA}},
)

data = json.loads(next(b.text for b in response.content if b.type == "text"))
```

Hai chi tiết trong schema đó gánh việc chính và rất dễ bỏ qua. `additionalProperties: False` là thứ chặn các key tự chế. Và `customer_id` vừa nằm trong `required` vừa cho phép `null` — với schema strict, "optional" thường được diễn đạt bằng một field bắt buộc nhưng được phép `null`, chứ không phải một key có thể vắng mặt. Điều đó tốt cho bạn: `null` tường minh nghĩa là model đã cân nhắc field đó và không có gì để điền; còn key vắng mặt thì mập mờ giữa "không có gì" và "quên".

Đường Pydantic cho cùng một đảm bảo, kèm một kiểu mà editor hiểu được:

```python
from typing import Literal
from pydantic import BaseModel, Field

class TicketTriage(BaseModel):
    evidence: str = Field(
        description="Verbatim quote from the ticket that decided the category."
    )
    category: Literal["billing", "bug", "feature_request", "account", "other"]
    severity: Literal["low", "medium", "high", "critical"]
    customer_id: str | None = Field(
        default=None, description="Customer ID if stated in the ticket, else null."
    )
    needs_human: bool
    unresolved: list[str] = Field(
        default_factory=list,
        description="Questions you could not answer from the ticket alone.",
    )

response = client.messages.parse(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": ticket_text}],
    output_format=TicketTriage,
)

triage: TicketTriage = response.parsed_output
```

`str | None` cần Python 3.10 trở lên. `parsed_output` là một `TicketTriage` thật, nên `triage.severity` là `Literal` mà type checker có thể match đủ nhánh, và gõ sai một nhánh sẽ là lỗi lúc build thay vì một phát hiện lúc 2 giờ sáng.

## Output format hay tool call? Chúng trả lời hai câu hỏi khác nhau

Trong tutorial thì hai cơ chế này trông thay thế được cho nhau. Thực tế thì không.

| | Output format (`output_config.format`) | Tool call (`strict: true` trên tool) |
| --- | --- | --- |
| Hình dạng mọi response | Một schema, luôn luôn | Model chọn tool nào, hoặc không chọn |
| Ý nghĩa tự nhiên | "Trả về bản ghi này" | "Làm việc này, với các tham số này" |
| Nhiều hình dạng | Không | Có — mỗi tool một cái |
| Model được phép từ chối | Không | Có, bằng cách không gọi gì cả |
| Hợp với | Trích xuất, phân loại, chấm điểm | Agent, routing, tác vụ có side effect |

Nếu mọi request đều phải sinh đúng một bản ghi đúng một hình dạng, dùng output format — ép gọi một tool duy nhất chỉ là phiên bản vụng về hơn của cùng chuyện đó. Nếu model đang chọn giữa các hành động, hoặc có quyền chính đáng để không làm gì, dùng tool; chính **lựa chọn đó** là thông tin bạn cần.

```python
TRIAGE_TOOL = {
    "name": "record_triage",
    "description": "Record the triage decision for one support ticket.",
    "strict": True,
    "input_schema": TRIAGE_SCHEMA,
}

response = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    tools=[TRIAGE_TOOL, ESCALATE_TOOL],
    messages=[{"role": "user", "content": ticket_text}],
)
```

Một quy tắc với tool input: luôn `json.loads` / đọc chúng như giá trị đã parse, đừng bao giờ so khớp chuỗi trên phần input đã serialize. Cách escape Unicode và dấu gạch chéo khác nhau giữa các model, và một phép kiểm tra substring chạy tốt hôm nay là một cú vỡ âm thầm đang chờ phiên bản model kế tiếp.

## Thiết kế schema để model điền được

Schema không chỉ là hợp đồng. Theo nghĩa rất đen, nó còn là một phần của prompt — tên field và chuỗi `description` đều được model đọc. Nghĩa là thiết kế schema chính là thiết kế prompt, và những nguyên tắc quen thuộc vẫn đúng.

**Phẳng hơn lồng sâu.** Mỗi tầng lồng là thêm một cấu trúc mở mà model phải giữ cân bằng trong khi vẫn phải làm việc chính, và nó khiến lỗi validate của bạn kém hữu ích đi ("fail ở `items[3].meta.tags[1]`" nói ít hơn hẳn "fail ở `severity`"). Nếu dữ liệu có phân cấp tự nhiên, thử xem một bản ghi phẳng kèm `parent_id` có cho bạn đúng thứ đó không.

**Enum hơn chuỗi tự do.** Một `"severity": string` tự do mời gọi `"high-ish"`, `"High"`, `"P1"` — ba biến thể mà rồi bạn phải chuẩn hóa bằng tay. Enum biến quyết định thành một lựa chọn giữa các phương án cố định, đúng hình dạng thật của quyết định đó. Dùng enum ở bất cứ đâu code phía sau có một `switch`.

**Xếp field sao cho lập luận đi trước phán quyết.** JSON object được sinh từ trái sang phải. Nếu `severity` là key đầu tiên, model chốt mức độ trước rồi mới viết lý do biện hộ cho nó. Đặt `evidence` lên đầu thì câu trích dẫn đã nằm trên bàn trước khi nhãn được chọn. Việc này không tốn gì ngoài thứ tự field.

**Cho sự không chắc chắn một chỗ để ở.** Đây là điều hay bị bỏ nhất, và là field giá trị nhất trong cả schema. Một model bị bắt điền `customer_id: string` cho ticket không hề có customer ID sẽ sinh ra một customer ID trông rất hợp lý, vì schema đòi một chuỗi và không có cách hợp lệ nào để nói "không có". Field nullable, một `unresolved: list[str]`, một `needs_human: bool` — mỗi thứ là một lối thoát hợp lệ. Không có chúng, "tôi không biết" buộc phải được diễn đạt bằng một điều bịa ra.

**Description chính là chỉ dẫn.** `"description": "ISO 8601 date, or null if the ticket gives no date"` làm được nhiều việc hơn ba câu trong system prompt, vì nó nằm ngay cạnh field mà nó chi phối.

## Validate và retry: bạn phản hồi lại cái gì mới quan trọng

Schema đảm bảo tính hợp lệ về cú pháp. Nó không diễn đạt được những thứ kiểu "`needs_human` phải là true khi `severity` là `critical`", hay "`customer_id` phải tồn tại trong database của mình", hay "`evidence` phải là substring thật của input". Đó là phần validator của bạn, và Pydantic cho bạn chỗ để đặt chúng:

```python
from pydantic import ValidationError, model_validator

class TicketTriage(BaseModel):
    # ... fields as above ...

    @model_validator(mode="after")
    def critical_needs_human(self):
        if self.severity == "critical" and not self.needs_human:
            raise ValueError("severity 'critical' requires needs_human=true")
        return self
```

Khi một trong số đó fail, lần retry phải mang theo thông tin mới. Gửi lại y hệt request cũ là tung đồng xu, và nếu schema mới là vấn đề thì đó là đồng xu bạn cứ thua mãi. Hãy đưa lỗi vào hội thoại như một lượt model đọc được:

```python
def triage_with_retry(ticket_text: str, max_attempts: int = 3) -> TicketTriage:
    messages = [{"role": "user", "content": ticket_text}]
    for attempt in range(max_attempts):
        response = client.messages.parse(
            model="claude-opus-5",
            max_tokens=1024,
            messages=messages,
            output_format=TicketTriage,
        )
        try:
            return response.parsed_output
        except ValidationError as err:
            if attempt == max_attempts - 1:
                raise
            messages += [
                {"role": "assistant", "content": response.content},
                {"role": "user", "content": f"That failed validation:\n{err}\nFix it."},
            ]
```

Ba thói quen nên có, bất kể framework. Chặn số lần thử — một vòng retry không giới hạn trên API tính tiền là một sự cố hóa đơn. Log lại output thô không hợp lệ chứ đừng chỉ log exception; pattern trong các lần fail thường chỉ ra field nào thiết kế tệ. Và giữ retry idempotent: nếu lần thử đầu đã ghi một row, lần thứ hai không được ghi thêm row nữa.

Kết quả tốt nhất của một vòng retry là nó dạy bạn sửa schema. Một field thường xuyên fail validate là field mà model đang bị bắt đoán mò.

## Stream structured output dở dang

Structured output và streaming đi chung được, nhưng stream JSON không giống stream văn xuôi. Tool input về theo các event `input_json_delta` mang mảnh `partial_json` — bạn nối chúng lại, và ở không thời điểm trung gian nào buffer là JSON hợp lệ:

```python
buffer = ""
with client.messages.stream(
    model="claude-opus-5",
    max_tokens=4096,
    tools=[TRIAGE_TOOL],
    tool_choice={"type": "tool", "name": "record_triage"},
    messages=[{"role": "user", "content": ticket_text}],
) as stream:
    for event in stream:
        if event.type == "content_block_delta" and event.delta.type == "input_json_delta":
            buffer += event.delta.partial_json
            render_preview(buffer)   # buffer is NOT parseable yet
    final = stream.get_final_message()
```

Muốn hiển thị cái gì đó có ích giữa chừng, bạn cần một parser khoan dung — loại tự đóng các chuỗi, mảng và object đang mở trước khi parse — và phải coi kết quả là bản xem trước, không bao giờ là dữ liệu. Trên API này, đặt `eager_input_streaming: true` trên định nghĩa tool sẽ khiến các mảnh đó bắt đầu về sớm hơn.

Hai lưu ý thực tế. Thứ tự field quyết định người dùng thấy gì trước, thêm một lý do nữa để đặt field đọc-được-bằng-mắt lên gần đầu: một `summary` stream ra ngay lập tức tạo cảm giác nhanh dù mấy field số còn mất thêm một giây. Và không có gì dở dang được phép chạm vào business logic. Render nó, đừng hành động theo nó. Chính cái field bạn hào hứng muốn hiện sớm nhất cũng là field dễ đổi nhất trước khi `content_block_stop`.

## Cái lỗi sống sót qua tất cả những thứ trên

Đây là response mà schema của bạn hoàn toàn hài lòng:

```json
{
  "evidence": "the charge on my card looks wrong",
  "category": "billing",
  "severity": "low",
  "customer_id": "CUS-4471",
  "needs_human": false
}
```

Mọi kiểu đều đúng. Giá trị enum hợp lệ. `additionalProperties` giữ vững. Vấn đề là ticket nói khách bị trừ tiền gấp đôi suốt mười một tháng, `CUS-4471` là customer ID model dựng ra vì format quá dễ đoán từ các ví dụ khác của bạn, và `severity: "low"` đơn giản là sai.

**Validate kiểm tra hình dạng câu trả lời. Verify kiểm tra câu trả lời.** Schema không làm được vế thứ hai, và pipeline structured output của bạn càng bóng bẩy thì càng dễ quên điều đó — dữ liệu có kiểu *cho cảm giác* đáng tin theo cách một đoạn văn xuôi chưa bao giờ có. Chính cảm giác đó mới là rủi ro. Văn xuôi trông như thứ cần hoài nghi. Một Pydantic model trông như một row lấy ra từ chính database của bạn.

Những gì thật sự giúp được:

- **Neo các định danh vào thực tế.** Mọi ID, SKU, URL hay số tài khoản model trả về đều phải tra lại nguồn thật trước khi dùng. Sinh ra một ID đúng format là chuyện quá dễ và schema sẽ ban phước cho tất cả.
- **Bắt buộc có evidence, rồi kiểm tra nó.** `assert triage.evidence in ticket_text` chỉ một dòng và chặn được cả một họ lỗi bịa đặt. Nếu câu trích dẫn không có trong nguồn thì mọi thứ dựng trên nó đều không an toàn.
- **Mã hóa các bất biến bạn đã biết.** Ràng buộc chéo field, khoảng giá trị hợp lý, ngày bắt buộc phải ở quá khứ. Đó là những kiểm tra ngữ nghĩa mà tầng schema không nhìn thấy.
- **Lấy mẫu và đọc bằng mắt.** Mỗi tuần rút năm mươi output ra đọc đối chiếu với input. Lỗi "hợp-lệ-mà-sai" vô hình với mọi kiểm tra tự động của bạn, chính xác vì nó vượt qua hết.
- **Giữ cho field thể hiện độ chắc chắn còn sống.** Nếu `needs_human` chưa bao giờ true, nó không hoạt động, và cái lối thoát bạn thiết kế chỉ là đồ trang trí.

Tiến trình trong bài này là có thật và đáng đi tới cuối. Regex → JSON xin trong prompt → schema được ép buộc xóa sổ ba nhóm bug thật, và code còn lại nhỏ hơn, nhàm chán hơn. Chỉ đừng để bước cuối thuyết phục bạn rằng phần việc còn lại cũng nhỏ đi theo. Nó không nhúc nhích chút nào.

## FAQ

**Có schema rồi thì còn cần mô tả format trong prompt nữa không?**
Liệt kê lại danh sách field là thừa — schema đã nằm trong request rồi. Thứ vẫn đáng nói trong prompt là phần **phán đoán**: thế nào thì tính là `critical`, khi nào nên chọn `null` thay vì đoán, câu evidence dùng để làm gì. Đặt quy tắc ngay cạnh field bằng `description`, và để dành prompt cho bối cảnh mà schema không chứa được.

**Sao model cứ trả `null` cho mọi thứ?**
Thường vì bạn thêm field nullable mà không kèm chỉ dẫn khi nào được dùng, nên null là câu trả lời hợp lệ an toàn nhất cho mọi field. Siết lại description ("null chỉ khi ticket hoàn toàn không có ngày nào") và kiểm tra xem input có thật sự chứa thông tin đó không — tỷ lệ null cao đôi khi là schema đang báo đúng rằng tài liệu nguồn của bạn không có dữ liệu.

**Có khi nào output lồng sâu là lựa chọn đúng không?**
Khi phần lồng là có thật — một danh sách line item mà mỗi item cùng bộ field thì đúng là dữ liệu lồng, làm phẳng đi còn tệ hơn. Thứ cần tránh là lồng vì cho gọn gàng, kiểu gom mấy field không liên quan vào một object `meta`. Nếu một tầng tồn tại chỉ để sắp xếp cho đẹp, xóa nó đi.

**Validate fail thì nên retry hay nên fail to tiếng?**
Cả hai, ở hai nhịp khác nhau. Retry một hai lần với lỗi được đưa ngược vào, vì lỗi nhất thời là có thật. Nhưng hãy cảnh báo theo **tỷ lệ retry** chứ đừng chỉ theo exception cuối cùng — một pipeline lần nào cũng lặng lẽ thành công ở lần thử thứ hai đang nói với bạn rằng schema cần sửa, và một metric thành công đơn thuần che mất chuyện đó hoàn toàn.

**Structured output có làm giảm chất lượng câu trả lời không?**
Có thể, nếu schema đánh nhau với bài toán — ép một nhãn duy nhất trong khi câu trả lời trung thực là "hai cái cùng đúng" sẽ làm output tệ đi bất kể JSON validate đẹp cỡ nào. Đó là vấn đề thiết kế schema chứ không phải lý lẽ chống lại schema. Cho model đủ field để nó chính xác, kể cả các field dành cho sự không chắc chắn, thì ràng buộc gần như không tốn gì.

---

*Các tham số API trong bài — `output_config.format`, tool `strict`, `input_json_delta` — là của Claude; cùng một tiến trình ba giai đoạn áp dụng được cho các provider khác với tên tham số khác, nên hãy kiểm tra tài liệu hiện hành của provider bạn dùng trước khi copy, vì phần bề mặt này đã đổi hơn một lần. Phần hướng dẫn thiết kế schema và lập luận validate-khác-verify là quan điểm làm việc của mình, rút ra từ việc dựng các pipeline kiểu này, không phải kết quả đo đạc.*
