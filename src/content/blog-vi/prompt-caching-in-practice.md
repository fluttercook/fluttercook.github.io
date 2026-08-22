---
title: "Prompt caching thực chiến: thắng thua nằm ở thứ tự prompt, không nằm ở cái flag"
description: "Bật prompt caching chỉ mất một dòng. Nhưng để thật sự có cache hit thì đó là quyết định kiến trúc: phần bất biến phải nằm trước, phần thay đổi theo từng request phải nằm sau cùng. Bài này nói về cách sắp thứ tự prompt, và cách chứng minh cache đã trúng."
seoDescription: "Prompt caching hoạt động ra sao: prefix matching, thứ gì âm thầm phá cache, cách sắp prompt cho agent loop, và cách kiểm chứng cache hit từ usage."
keywords:
  - prompt caching
  - cache prefix llm
  - cache_control breakpoint
  - tỉ lệ cache hit llm api
  - prompt caching cho agent
  - cache_read_input_tokens
category: "Chuyên sâu"
topic: "AI Engineering"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-22"
emoji: "🧊"
tags: ["AI", "LLM", "Prompt Engineering", "Performance", "API"]
sources:
  - name: "Anthropic — Prompt caching"
    url: "https://platform.claude.com/docs/en/build-with-claude/prompt-caching"
  - name: "OpenAI — Prompt caching"
    url: "https://platform.openai.com/docs/guides/prompt-caching"
  - name: "Google — Gemini API context caching"
    url: "https://ai.google.dev/gemini-api/docs/caching"
related:
  - slug: "cutting-ai-costs-free-tiers-caching-and-routing"
    title: "Dùng AI mà không đốt tiền: free tier, caching và định tuyến model"
  - slug: "building-an-ai-agent-team-chief-of-staff-pattern"
    title: "Mô hình Chief of Staff: biến đống chat AI rời rạc thành một đội ngũ agent"
draft: false
---

Lần đầu bật prompt caching, đa số mọi người thêm một field vào request, deploy, rồi thấy… không có gì thay đổi. Hoá đơn y hệt. Latency y hệt. Tính năng đã bật và nó không làm gì cả.

Đó là kết quả bình thường, và không phải bug. Prompt caching không phải một cái công tắc kiểu "tái sử dụng được gì thì tái sử dụng". Nó là **so khớp prefix trên đúng từng byte của prompt sau khi render**. Provider băm prompt của bạn từ byte đầu tiên trở đi và tìm một entry đã lưu để nối tiếp. Nếu byte thứ 47 trong prompt 30.000 token của bạn khác lần trước — vì đó là một cái đồng hồ — thì không còn prefix nào tái dùng được, và 29.900 token còn lại bị xử lý lại từ đầu với giá đầy đủ.

Nên cái flag không phải là phần việc. Phần việc là sắp lại prompt sao cho phần bất biến nằm trước về mặt vật lý, còn phần theo từng request nằm sau cùng. Đó là thay đổi trong code dựng prompt, không phải trong lời gọi API. Khi thứ tự đã đúng, cái flag gần như là tiền cho không. Khi thứ tự còn sai, có rắc bao nhiêu cache marker cũng vô ích.

Bài này nói về việc sắp lại đó: prefix thực chất là gì, vài thứ âm thầm phá nó, cách bố trí một agent loop, vì sao conversation đang dài ra là ca dễ còn RAG là ca khó, và cách kiểm chứng bạn đang có cache hit thay vì chỉ hy vọng.

## Prefix là prefix — mọi thứ sau điểm khác biệt đều mất

Hãy hình dung prompt là một chuỗi byte dài. Provider lưu trạng thái trung gian của model (KV cache) tính tới một điểm nào đó trong chuỗi này. Ở request sau, nó chỉ bỏ qua được phần tính toán đó nếu các byte của request mới **giống hệt từ vị trí 0 tới điểm đó**.

Không có so khớp mờ, không có "gần giống là được", không có tái dùng từng block rời rạc. Đúng nghĩa prefix.

```text
Request 1:  [ system 8k ][ tools 3k ][ history 12k ][ câu hỏi A ]
Request 2:  [ system 8k ][ tools 3k ][ history 12k ][ câu hỏi B ]
                                                    ^ điểm rẽ
            └────────── 23k tái dùng được ────────┘  tính lại 40 token
```

Giờ đẩy một byte biến động lên đầu:

```text
Request 1:  [ 2026-08-22T09:14:02Z ][ system 8k ][ tools 3k ][ history 12k ][ A ]
Request 2:  [ 2026-08-22T09:14:47Z ][ system 8k ][ tools 3k ][ history 12k ][ B ]
            ^ rẽ ngay byte thứ 3
            └── 0 tái dùng được. 23k token tính lại. ──┘
```

Cùng nội dung, cùng kích thước, cùng cache flag. Một bên là cache hit 23.000 token, bên kia trượt hoàn toàn, khác biệt duy nhất là cái timestamp nằm ở đâu. Riêng sự thật này giải thích gần như mọi câu chuyện "bọn mình bật caching mà chẳng ăn thua".

Nó cũng cho bạn một quy tắc sắp xếp áp dụng được máy móc: **sắp các phần của prompt theo tần suất thay đổi, ổn định nhất lên trước.** Không phải theo thứ tự nào đọc cho xuôi.

## Biết thứ tự render, vì nó không phải thứ tự bạn viết

Provider ghép định dạng gửi lên theo một thứ tự cố định, và chính thứ tự đó mới được băm — không phải thứ tự tham số trong code của bạn. Với Claude API, thứ tự render là `tools` → `system` → `messages`. Định nghĩa tool nằm ở vị trí 0, trước cả system prompt.

Hệ quả khiến nhiều người bất ngờ: **đổi danh sách tool sẽ phá cache của system prompt.** Chứ không phải chiều ngược lại. Nếu bạn dựng mảng tool bằng cách duyệt một dict, hoặc thêm tool `admin_delete` cho một số user, hoặc plugin registry nạp theo thứ tự không xác định, thì vị trí 0 biến động và không gì phía sau còn tái dùng được.

Hãy serialize tool một cách xác định. Sort theo tên. Làm một lần lúc khởi động và giữ mảng đó như hằng số module thay vì dựng lại mỗi request.

```python
# Bad: order depends on dict iteration and on who's calling.
def build_tools(user):
    tools = [TOOLS[name] for name in registry.keys()]
    if user.is_admin:
        tools.append(ADMIN_TOOL)
    return tools

# Good: one frozen array, sorted, built once.
TOOLS = sorted(ALL_TOOLS, key=lambda t: t["name"])
# Admin capability becomes a permission checked inside the handler,
# not a difference in the tool list.
```

Provider khác sắp xếp khác, nhưng nguyên tắc y hệt: tìm hiểu xem cái gì thực sự render trước, rồi coi vùng đó là bất khả xâm phạm.

## Năm thứ âm thầm phá cache

Gần như mọi cú trượt cache đều quy về một trong số này. Đáng để grep thẳng trong code.

| Kiểu code | Vì sao nó giết cache |
| --- | --- |
| `datetime.now()` nhét vào system prompt | Prefix khác nhau ở từng request |
| Request ID, trace ID hay `uuid4()` nằm gần đầu | Tương tự — mỗi request là duy nhất theo thiết kế |
| `json.dumps(obj)` không có `sort_keys=True`, hoặc duyệt một `set` | Thứ tự serialize ở mức byte trôi giữa các process |
| Section system có điều kiện (`if flag: system += ...`) | Mỗi tổ hợp flag là một prefix riêng, phải warm riêng |
| Danh sách tool dựng theo user hoặc theo request | Render ở vị trí 0; không cache được xuyên các caller |

Cái timestamp phổ biến nhất và nghe có lý nhất. "Model cần biết hôm nay ngày mấy" là đúng. Nó chỉ không cần biết điều đó *ở đầu system prompt*. Đẩy nó xuống user message cuối, hoặc — nếu provider của bạn có kênh operator giữa hội thoại — gửi nó như một message nối sau phần history đã cache. Một ngày tháng ở lượt 12 không phá gì trước lượt 12.

Cái section có điều kiện tinh vi hơn và hay xuất hiện trong codebase đã trưởng thành. Mỗi câu `if` trong bộ dựng prompt nhân lên số prefix khác nhau mà traffic của bạn phải giữ ấm. Bốn boolean độc lập là mười sáu prefix, mỗi cái cần warm riêng và cần lưu lượng riêng. Cách sửa thường là bỏ điều kiện đi (trả vài trăm token luôn-được-cache rẻ hơn mười sáu prefix nguội) hoặc đẩy section đó xuống sau breakpoint.

## Sắp thứ tự cho một agent loop

Request của agent là ca ăn nhiều nhất, vì cùng một phần mở đầu khổng lồ bị gửi lại ở mỗi vòng lặp. Sắp theo độ ổn định:

1. **Định nghĩa tool.** Đóng băng, đã sort, giống nhau với mọi user.
2. **System instructions.** Vai trò, luật, hợp đồng đầu ra. Không nội suy biến vào.
3. **Tài liệu ổn định.** Style guide, dump schema, tài liệu API, ví dụ few-shot — thứ gì giống nhau cho cả một lớp request.
4. **Context theo session.** Repo agent đang làm, ticket được giao. Đổi theo session, không theo lượt.
5. **Lịch sử hội thoại.** Dài ra ở phía cuối, đúng cái bạn muốn.
6. **Input của lượt này.** User message mới, tool result vừa về, timestamp hiện tại.

Chỗ nào provider cho đặt cache breakpoint tường minh, hãy đặt ở *ranh giới giữa các tầng ổn định* — thường là cuối bước 3 và cuối bước 5. Claude API giới hạn bốn breakpoint mỗi request, quá đủ nếu bạn đặt ở ranh giới thật chứ không rải bừa.

Lỗi hay gặp nhất ở đây là đặt marker ở cuối toàn bộ prompt. Nghe rất tự nhiên — cache hết cho chắc! — nhưng nếu block cuối khác nhau ở mỗi request thì mỗi request ghi một entry mới toanh và không bao giờ đọc được entry nào. Bạn trả phí ghi mãi mãi mà không đọc gì. Breakpoint thuộc về cuối phần **dùng chung**.

```json
{
  "system": [
    { "type": "text", "text": "<frozen instructions + style guide>",
      "cache_control": { "type": "ephemeral" } }
  ],
  "messages": [
    { "role": "user", "content": [
      { "type": "text", "text": "<shared few-shot block>",
        "cache_control": { "type": "ephemeral" } },
      { "type": "text", "text": "<this request's question — no marker>" }
    ]}
  ]
}
```

Thêm một chi tiết riêng cho agent loop: trên Claude API, một breakpoint chỉ dò ngược lại một số lượng content block giới hạn để tìm entry cũ (tài liệu ghi là 20). Một lượt agent bắn cả chục tool song song có thể vượt qua cửa sổ đó, và breakpoint của request kế tiếp âm thầm không tìm thấy gì. Nếu các lượt của bạn sinh ra chuỗi block dài, hãy đặt thêm một breakpoint trung gian ngay trong lượt. Kiểm tra tài liệu provider xem có giới hạn tương đương không.

## Conversation dài ra là ca dễ; RAG là ca khó

Hai thứ này trông giống nhau — đều thêm text vào prompt — nhưng hành xử ngược nhau.

**Lịch sử hội thoại dài ra ở phía cuối.** Prompt của lượt 5 là prefix byte-đúng-nghĩa của prompt lượt 6. Đó là hình dạng lý tưởng: mỗi lượt đọc lại toàn bộ những gì lượt trước đã ghi, và vùng cache lớn dần đơn điệu. Một phiên agent dài là workload caching tốt nhất tồn tại, và nó gần như không cần nỗ lực gì ngoài việc đừng đụng vào phần đầu prompt giữa chừng.

Chính vì vậy thói quen "sửa system prompt một tí để báo là đã đổi mode" lại đắt đến thế. Sửa nội dung system ở top-level nghĩa là đổi prefix nằm trước *toàn bộ history* — mọi lượt bạn tích luỹ được đều bị xử lý lại không cache. Nếu provider hỗ trợ nối chỉ thị operator như một message sau history, hãy dùng cách đó. Nếu không, nhét chỉ thị vào lượt user. Kiểu gì cũng được, miễn đừng đụng vào phần đầu.

**Chunk truy hồi thì đổi theo từng query.** RAG là anti-pattern theo đúng cấu tạo: retriever trả về tài liệu khác nhau cho câu hỏi khác nhau, nên nếu bạn đặt context truy hồi lên đầu — chỗ mà đa số tutorial đặt — bạn có một prefix riêng cho từng query và chẳng còn gì để tái dùng.

Cách sửa vẫn là thứ tự. Chunk truy hồi là nội dung theo từng request, và thuộc về phía cuối, ngay cạnh câu hỏi:

```text
[ tools ][ system ][ corpus/schema ổn định ][ ---breakpoint--- ][ chunk truy hồi ][ câu hỏi ]
```

Nếu có một bộ tài liệu *cố định* dùng cho cả một lớp query — sổ tay sản phẩm, kho văn bản pháp lý, codebase bạn luôn ground vào — thì đó không phải RAG theo nghĩa biến động. Đó là tài liệu ổn định, nó thuộc tầng 3, và nó cache rất đẹp. Một số provider có hẳn API context caching cho đúng hình dạng này: bạn upload corpus một lần rồi tham chiếu bằng handle. Đáng kiểm tra xem provider của bạn có không, trước khi tự dựng lại.

Một phép thử hữu ích: tự hỏi hai request thật liên tiếp có sinh ra text giống nhau từng byte ở section này không. Nếu có, đó là nội dung ổn định. Nếu không, đó là nội dung theo request và phải nằm cuối.

## Tuổi thọ cache quyết định endpoint ít traffic có bao giờ hit không

Entry cache sẽ hết hạn. Cơ chế ai cũng quên là đồng hồ thường **được làm mới mỗi lần dùng** — mỗi cache hit gia hạn entry — nhưng một khoảng nghỉ dài hơn tuổi thọ sẽ làm nó rơi, và request kế tiếp lại trả phí ghi đầy đủ.

Chuyện này tạo ra kiểu hỏng vô hình trong load test nhưng lồ lộ trên production: một endpoint phục vụ vài phút một request trong giờ hành chính thì cache rất ngọt, còn chính endpoint đó lúc 3 giờ sáng thì không bao giờ cache. Tệ hơn, một công cụ nội bộ ít traffic có thể rơi vào trạng thái *chỉ ghi mà không bao giờ đọc*: mọi request đều đến sau khi entry hết hạn, trả phí ghi, và không request nào đọc được. Như vậy đắt hơn hẳn so với không bật cache.

Anthropic ghi nhận tuổi thọ mặc định ngắn, tính bằng phút, cộng thêm một mức dài hơn phải chọn và trả phí ghi cao hơn. Provider khác thì khác, và những con số này thay đổi; hãy kiểm tra tài liệu hiện hành thay vì tin một con số trong bài blog, kể cả bài này. Thứ ổn định là cách suy luận:

- **Khoảng cách giữa các request ngắn hơn tuổi thọ** — caching tự chạy tốt, không cần thêm gì.
- **Traffic giật cục, có khoảng nghỉ dài** — hoặc dùng mức tuổi thọ dài hơn, hoặc pre-warm prefix ở đầu mỗi đợt.
- **Traffic thưa thật sự và prefix nhỏ** — tắt caching đi. Bạn chỉ đang trả phí ghi.

Bài toán kinh tế giống nhau giữa các provider: một lần đọc cache tốn một phần nhỏ so với token input thường, còn một lần ghi cache tốn *nhiều hơn* token input thường một chút. Nên điểm hoà vốn là một số lần đọc nhỏ trên mỗi lần ghi — vài lần với entry ngắn hạn, nhiều hơn với entry dài hạn vì chúng đắt hơn khi tạo. Câu hỏi thiết kế không phải "caching có rẻ hơn không" (có, khi nó hit) mà là "prefix này có được đọc đủ số lần trước khi hết hạn không".

Nếu provider hỗ trợ, pre-warm là công cụ thật cho ca giật cục: bắn một request vào prefix dùng chung lúc worker khởi động hoặc đầu một khung giờ đã lên lịch, để request thật đầu tiên gặp cache ấm thay vì trả latency nguội. Anthropic hỗ trợ request `max_tokens: 0` đúng cho việc này — nó chạy prefill, ghi cache, rồi trả về ngay mà không sinh output. Đừng pre-warm những prefix vốn đã được phục vụ liên tục; traffic thật đã giữ ấm rồi, lần ghi thêm chỉ là chi phí thuần.

## Kiểm chứng bằng usage — đoán mò là chỗ mọi thứ đi chệch

Mọi provider có caching đều báo lại chuyện gì đã xảy ra trong object usage của response, và toàn bộ ý của phần này là **bạn phải nhìn vào đó**. Caching hỏng trong im lặng. Không có lỗi, không cảnh báo, không dòng log degraded-mode nào. Cache cấu hình sai và cache cấu hình chuẩn cho ra response giống hệt nhau.

Trên Claude API có ba field:

| Field | Ý nghĩa |
| --- | --- |
| `cache_creation_input_tokens` | Số token ghi vào cache ở request này — bạn đã trả phí ghi |
| `cache_read_input_tokens` | Số token phục vụ từ cache — bạn trả mức giá giảm |
| `input_tokens` | Số token xử lý ở giá đầy đủ |

Cái bẫy trong bảng trên: **`input_tokens` chỉ là phần dư chưa cache, không phải tổng.** Tổng kích thước prompt là tổng của cả ba. Không ít dashboard chỉ báo `input_tokens` rồi khiến một agent cache tốt trông rẻ đến mức phi lý, hoặc khiến người ta tưởng prompt 40k token của mình tự co lại.

Hãy log tỉ lệ này, theo từng request, ngay từ ngày đầu:

```python
u = response.usage
total = u.input_tokens + u.cache_creation_input_tokens + u.cache_read_input_tokens
hit_rate = u.cache_read_input_tokens / total if total else 0.0
log.info("cache", extra={
    "read": u.cache_read_input_tokens,
    "written": u.cache_creation_input_tokens,
    "fresh": u.input_tokens,
    "hit_rate": round(hit_rate, 3),
})
```

Rồi đọc hình dạng của nó:

| Bạn thấy gì qua nhiều request lặp lại | Nghĩa là gì |
| --- | --- |
| `read` tăng dần, `written` gần bằng 0 sau lần đầu | Đang chạy đúng ý |
| `written` lớn ở *mọi* request, `read` luôn bằng 0 | Breakpoint nằm sau phần biến động, hoặc có kẻ phá cache ở đầu prompt |
| Cả hai bằng 0 dù đã đặt marker | Prefix ngắn hơn mức tối thiểu cache được của provider — cái này hỏng im lặng, không báo lỗi |
| `read` ổn ở dev, bằng 0 ở prod | Khác biệt theo instance: serialize không sort, config theo pod, hoặc section system phụ thuộc env |

Khi `read` cứ đứng ở 0 mà bạn không thấy vì sao, thôi đoán, đi diff byte. Serialize toàn bộ request body đã render của hai lần gọi liên tiếp, ghi cả hai ra file, rồi chạy `diff`. Kẻ phá cache luôn hiện ra trong bản diff đó, và thường là một dòng bạn chẳng ngờ tới.

```python
import json, pathlib
pathlib.Path(f"/tmp/req-{n}.json").write_text(json.dumps(payload, indent=2, sort_keys=True))
# then: diff /tmp/req-1.json /tmp/req-2.json
```

Thêm hai điều nên biết trước khi kết luận setup của bạn hỏng. Thứ nhất, một entry cache thường chưa đọc được cho tới khi request ghi nó bắt đầu trả lời — nên N request song song cùng prefix sẽ trượt hết. Với fan-out, gửi một cái, đợi nó bắt đầu stream, rồi mới bắn phần còn lại. Thứ hai, cache gắn với model: đổi model giữa hội thoại, kể cả sang một model rẻ hơn cùng nhà cho một tác vụ phụ, là bắt đầu lại từ nguội. Hãy tách tác vụ phụ rẻ tiền thành lời gọi riêng với prefix riêng thay vì hoán model ngay trong vòng lặp chính.

## FAQ

**Mình có phải sửa prompt để dùng caching không, hay chỉ cần bật lên?**
Gần như luôn phải sửa. Bật caching trên một prompt mang timestamp, request ID hay danh sách tool theo user ở phía đầu sẽ cho ra 0 hit, vì prefix tái dùng được là rỗng. Việc sắp lại thứ tự mới là tính năng; cái flag chỉ báo với provider rằng bạn muốn nó.

**Đặt cache breakpoint chính xác ở đâu?**
Ở cuối section cuối cùng còn giống nhau từng byte giữa các request — không phải ở cuối prompt. Nếu block mang marker của bạn đổi theo từng request thì mỗi request ghi một entry mới và không đọc gì cả, tốn hơn cả không cache.

**Sao tỉ lệ cache hit bằng 0 dù prompt của mình không đổi gì?**
Kiểm ba thứ theo thứ tự: prefix có đủ dài để cache được không (có ngưỡng tối thiểu tuỳ provider, và dưới ngưỡng thì hỏng im lặng), mảng tool hay khâu serialize JSON có thứ tự bất định không, và các request có đến cách nhau xa hơn tuổi thọ cache không. Sau đó diff hai request body đã render.

**Hội thoại dài ra có phá cache không?**
Không — đó là ca tốt nhất. History dài ra ở cuối prompt, nên prompt của mỗi lượt là prefix đúng nghĩa của lượt sau, và vùng cache cứ lớn dần. Cái phá nó là sửa system prompt hay danh sách tool giữa chừng, vì việc đó đổi byte nằm trước toàn bộ history.

**Có nên cache các chunk RAG truy hồi không?**
Không, nếu chúng đổi theo từng query — hãy đặt chúng ở cuối, ngay trước câu hỏi, và cache mọi thứ phía trước. Nếu là một corpus cố định dùng chung cho nhiều query thì đó là tài liệu ổn định chứ không phải truy hồi theo query, và nó thuộc về phía đầu, nơi nó cache rất tốt.

---

*Cơ chế so khớp prefix, thứ tự render và ý nghĩa các field usage mô tả ở trên là hành vi có tài liệu của Claude API; phần lời khuyên về thứ tự và quy trình debug là quan điểm cá nhân mình, rút ra từ việc đã làm sai. Tuổi thọ cache, hệ số giá, độ dài tối thiểu cache được và giới hạn số breakpoint đều tuỳ provider và tuỳ model, và chúng thay đổi — hãy đối chiếu từng thứ với tài liệu hiện hành ở phần nguồn thay vì tin bài viết này.*
