---
title: "Context engineering: window to không có nghĩa là được phép nhét đầy"
description: "Model hiện đại nhận cả triệu token đầu vào. Điều đó thay đổi cái gì khả thi, chứ không thay đổi cái gì nên làm. Một cách làm cụ thể để quyết định đưa gì vào context, theo thứ tự nào, và cắt gì trước khi tràn."
seoDescription: "Cách quyết định đưa gì vào context window của LLM: thứ tự sắp xếp, compaction, context suy luận so với tài liệu tra cứu, và budget token cụ thể cho agent."
keywords:
  - context engineering là gì
  - context window llm
  - nên đưa gì vào context window
  - prompt caching thứ tự prefix
  - compaction context agent
  - budget token cho ai agent
category: "Hướng dẫn"
topic: "AI Engineering"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-22"
emoji: "🪟"
tags: ["AI", "LLM", "Context Engineering", "Agent", "RAG"]
sources:
  - name: "Claude Docs — Context windows"
    url: "https://platform.claude.com/docs/en/build-with-claude/context-windows"
  - name: "Claude Docs — Prompt caching"
    url: "https://platform.claude.com/docs/en/build-with-claude/prompt-caching"
  - name: "Claude Docs — Context editing"
    url: "https://platform.claude.com/docs/en/build-with-claude/context-editing"
  - name: "Claude Docs — Compaction"
    url: "https://platform.claude.com/docs/en/build-with-claude/compaction"
  - name: "Claude Docs — Token counting"
    url: "https://platform.claude.com/docs/en/build-with-claude/token-counting"
  - name: "Claude Docs — Tool search tool"
    url: "https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-search-tool"
related:
  - slug: "cutting-ai-costs-free-tiers-caching-and-routing"
    title: "Dùng AI mà không đốt tiền: free tier, caching và định tuyến model"
  - slug: "building-an-ai-agent-team-chief-of-staff-pattern"
    title: "Mô hình Chief of Staff: biến đống chat AI rời rạc thành một đội ngũ agent"
draft: false
---

Context window của các model đầu bảng giờ là một triệu token. Chừng đó tương đương một codebase cỡ vừa, hoặc vài trăm trang tài liệu, hoặc một buổi chiều rất dài agent gọi tool. Phản ứng hiển nhiên là thôi khỏi nghĩ nên đưa gì vào nữa — nhét hết schema, cả file README, đủ bốn mươi tool, toàn bộ hội thoại, để model tự lọc.

Cách đó chạy được cho tới lúc không chạy nữa, và khi hỏng thì nó hỏng rất im lặng. Model không báo lỗi. Nó trả lời, đầy tự tin, dựa trên đúng cái file config sai trong ba file config mâu thuẫn nhau mà bạn vừa dán vào. Latency bò từ bốn giây lên hai mươi giây. Hoá đơn tăng ở **mọi** lượt gọi chứ không phải một lần, bởi API là stateless và bạn gửi lại toàn bộ ở mỗi lượt. Không dòng log nào ghi "context quá nhiều" — bạn chỉ thấy con trợ lý hơi ngu đi so với tháng trước.

**Context engineering** là kỷ luật quyết định cái gì được chiếm chỗ trong window đó. Nó không phải prompt engineering — chữ nghĩa của prompt chỉ là một phần nhỏ. Nó gần với thiết kế cache hoặc quản lý working set hơn: bạn có một tài nguyên cố định, đắt, tính phí mỗi lượt, và mọi thứ bạn nhét vào đều tranh giành sự chú ý của model với mọi thứ khác.

Dưới đây là cách tôi chia budget, theo đúng thứ tự tôi ra quyết định trong thực tế.

## Window là budget bạn tự chọn, không phải cái thùng để đổ đầy

Chuyển đổi tư duy đầu tiên: context tối đa của model là giới hạn cứng do nhà cung cấp đặt. **Working budget** là giới hạn mềm do chính bạn đặt, và nó nên nhỏ hơn nhiều.

Có ba thứ tệ đi khi bạn tiến gần mức tối đa, và chúng tệ đi độc lập với nhau:

**Chi phí nhân theo từng lượt, không phải theo hội thoại.** Context 300K token ở lượt thứ 12 của một vòng lặp agent không phải là khoản phí 300K một lần — đó là 300K token gửi lại ở lượt 12, và gần chừng đó nữa ở lượt 13. Tổng token của một phiên agent dài tăng theo bình phương số lượt nếu bạn không chủ động can thiệp. Đây là kiểu hỏng người ta phát hiện đầu tiên, thường là qua hoá đơn.

**Latency tăng theo độ dài đầu vào.** Time to first token lớn dần theo lượng chữ phải đọc. Một agent gọi mười lăm lần tool sẽ trả cái giá prefill đang phình ra đó mười lăm lần. Caching giúp rất nhiều ở đây, và đó là lý do thiết kế cache với thiết kế context thực ra là cùng một bài toán.

**Độ liên quan bị pha loãng.** Đây là thứ khó thấy nhất. Model phải định vị phần nội dung có ích giữa đống nội dung vô ích. Thêm một tài liệu mà 90% không liên quan tới câu hỏi hiện tại không phải là thêm 10% giá trị của một tài liệu — đó là thêm nguyên một tài liệu những thứ phải phân biệt với nhau. Tệ nhất là các bản gần giống nhau: hai phiên bản của cùng một config, chữ ký API cũ nằm cạnh chữ ký mới, một hàm deprecated nằm cạnh hàm thay thế nó. Model không có cách nào chắc chắn để biết bạn muốn cái nào, và đôi khi nó sẽ chọn sai.

Hiệu ứng thứ ba là lý do "cứ nhét hết vào" làm giảm chất lượng và tăng chi phí *cùng lúc*. Đây không phải một sự đánh đổi bạn đang cân nhắc. Đây là cùng một sai lầm.

## Context để suy luận và tài liệu để tra cứu là hai thứ khác nhau

Phân biệt hữu ích nhất trong toàn bộ chủ đề này: có thứ model phải **suy luận cùng**, và có thứ nó chỉ cần **tra khi cần**.

Context để suy luận là tất cả những gì model phải giữ đồng thời trong đầu để cho ra câu trả lời đúng. Nếu bạn nhờ nó dung hoà hai thiết kế API, cả hai thiết kế phải nằm trong window. Nếu bạn nhờ nó sửa bug, cả test đang fail lẫn hàm bị lỗi đều phải có mặt. Không thể lách bằng retrieval — việc suy luận thật sự cần các mảnh nằm cạnh nhau.

Tài liệu tra cứu là tất cả những gì nó *có thể* cần, tuỳ điều kiện, tuỳ hướng suy luận đi tới đâu. Toàn bộ bảng mã lỗi. Hai trăm file còn lại trong repo. Changelog hai năm qua. Loại này không nên nằm trong window. Nó nên nằm sau một tool.

```typescript
// Not this: 40K tokens of API reference in the system prompt, every turn.
// This: a tool the model calls only when it actually needs a symbol.
const tools: Anthropic.Tool[] = [
  {
    name: "lookup_api",
    description:
      "Look up the signature and docs for one symbol in the SDK reference. " +
      "Use when you need exact parameter names or types. Returns one entry.",
    input_schema: {
      type: "object",
      properties: { symbol: { type: "string" } },
      required: ["symbol"],
      additionalProperties: false,
    },
    strict: true,
  },
];
```

Cái giá phải trả là có thật và nên nói thẳng: một lần gọi tool tốn một vòng round trip, và đôi khi model quên gọi lúc đáng lẽ phải gọi. Còn một context bị nhồi thì tốn token ở mọi lượt, mãi mãi. Với thứ chỉ thỉnh thoảng cần tra, tool thắng cách biệt. Với thứ gần như lượt nào cũng cần, hãy đưa thẳng vào context và cache nó lại.

Một phép thử tiện dụng: **nếu bạn không chỉ ra được nội dung này đã trả lời câu hỏi cụ thể nào trong mười lượt gần nhất, nó thuộc về phía sau một tool.**

Logic đó áp dụng cho chính các định nghĩa tool. Ba mươi tool schema dễ dàng chiếm vài nghìn token nằm chắn trước mọi request, và một model phải chọn giữa ba mươi tool sẽ chọn tệ hơn hẳn so với khi chọn giữa sáu tool. Tool search tool của Anthropic sinh ra chính vì việc này: đánh dấu các tool ít dùng bằng `defer_loading: true` và để model tự tìm, chỉ giữ thường trú những tool hay dùng. (Phải có ít nhất một tool không defer, và bản thân tool search không bao giờ được defer, nếu không request bị từ chối.)

## Thứ tự không phải chuyện hình thức

Context được render thành một chuỗi phẳng duy nhất. Với Claude API, thứ tự đó là `tools` → `system` → `messages`, và có hai cơ chế riêng biệt khiến thứ tự trở nên quan trọng.

Cơ chế mang tính máy móc là caching. Prompt caching khớp theo **prefix**: vùng được cache chạy từ đầu request tới breakpoint của bạn, và chỉ một byte thay đổi ở bất kỳ đâu phía trước điểm đó là vô hiệu hoá toàn bộ phần sau. Đọc từ cache tốn khoảng một phần mười token input thường; ghi cache tốn khoảng 1.25 lần. Nghĩa là bạn hoà vốn ngay ở lần gọi thứ hai, và từ đó trở đi phần ổn định được giảm gần chín mươi phần trăm.

Từ đó ra một quy tắc cứng: **ổn định nhất đặt trước, dễ đổi nhất đặt sau.** System prompt đóng băng, rồi danh sách tool sắp xếp tất định, rồi tài liệu retrieve dùng lâu dài, rồi lịch sử hội thoại, rồi câu hỏi thật sự của người dùng. Một timestamp hay request ID lỡ chèn vào system prompt là kẻ giết cache kinh điển — không lỗi, không cảnh báo, chỉ là cache lạnh vĩnh viễn và hoá đơn không bao giờ giảm.

```typescript
const response = await client.messages.create({
  model: "claude-opus-5",
  max_tokens: 16000,
  system: [
    { type: "text", text: FROZEN_INSTRUCTIONS },
    { type: "text", text: retrievedDocs, cache_control: { type: "ephemeral" } },
  ],
  messages: [
    ...history,
    // Volatile material goes after the last breakpoint, never before it.
    { role: "user", content: `Today is ${today}.\n\n${question}` },
  ],
});
```

Cơ chế thứ hai tinh tế hơn. Chỉ dẫn đặt xa phần cuối của một context dài phải cạnh tranh với mọi thứ đứng sau nó để giành sự chú ý của model. Hệ quả thực dụng là: *nhiệm vụ thật sự* — thứ bạn muốn làm ngay bây giờ — nên là thứ cuối cùng trong window, nói thẳng, chứ không chôn ở đầu một system prompt viết từ sáu tháng trước. Nếu có ràng buộc cứ bị bỏ qua khi context dài, việc đầu tiên nên thử là chuyển nó xuống lượt user cuối cùng. Trên các model hỗ trợ system message giữa hội thoại, đó là kênh sạch hơn cho cùng công việc: nó mang thẩm quyền của operator mà không phá prefix đã cache.

## Một budget cụ thể cho agent

Ví dụ cụ thể. Một agent hỗ trợ khách hàng: đọc tài liệu nội bộ, truy vấn hệ thống ticket, soạn thư trả lời. Window của model là một triệu token. Tôi sẽ cấp cho nó working budget **60.000**.

Con số đó không phải vì nhát tay, nó là một quyết định thiết kế: 60K là điểm mà agent này vẫn có đủ mọi thứ nó cần và không có thứ nó không cần. Nâng lên 200K sẽ không làm nó giỏi hơn ở bất cứ việc gì, chỉ làm mỗi lượt trong mười tới hai mươi lượt của nó đắt gấp ba và khởi động chậm hơn.

| Ô | Budget | Có cache? | Chứa gì |
| --- | --- | --- | --- |
| System instructions | 2.000 | Có | Vai trò, chính sách escalate, quy tắc giọng văn, ranh giới từ chối |
| Định nghĩa tool | 4.000 | Có | 6 tool thường trú; 20 tool còn lại nằm sau tool search |
| Tài liệu retrieve | 20.000 | Có (theo session) | 6–8 chunk tốt nhất cho chủ đề của ticket này |
| Hội thoại + tool result | 30.000 | Một phần | Cuốn chiếu; nén theo lịch |
| Nhiệm vụ hiện tại | 1.000 | Không | Ticket, tin nhắn mới nhất của khách, ngày hôm nay |
| Dự phòng | ~3.000 | — | Chỗ trống cho một tool result dài trước lần nén kế tiếp |

Hai điều về bảng này quan trọng hơn các con số.

Thứ nhất, **ô lớn nhất lại là ô bạn kiểm soát ít nhất.** Lịch sử hội thoại và tool result tự phình ra, không có trần, theo cách các ô khác không làm. Đó là nơi toàn bộ công sức kỹ thuật của bạn nên đổ vào. System prompt 2.000 token thay vì 3.000 chẳng tiết kiệm được gì đáng kể; một chiến lược xử lý tool result giữ lịch sử ở 30K thay vì 150K mới là toàn bộ trận đấu.

Thứ hai, **retrieval có một ô cố định, và chính cái ô đó mới là điểm mấu chốt.** "6–8 chunk tốt nhất" là một budget, không phải một chỉ tiêu chất lượng. Nếu retriever trả về hai mươi chunk và bạn đưa hết cả hai mươi vì chúng đều vượt ngưỡng điểm, bạn không có budget — bạn có một chỗ rò. Hãy chốt kích thước ô trước, và để nó ép khâu rerank thật sự phải xếp hạng.

## Tràn rồi thì cắt gì trước

Nó sẽ tràn. Đây là thứ tự tôi bỏ bớt, ít thiệt hại nhất trước:

1. **Phần thân thô của tool result ở các lượt cũ.** Cái file agent đọc từ chín lượt trước, cái response API 4.000 token mà nó chỉ rút ra đúng một field. *Việc* lời gọi đó đã xảy ra thì quan trọng; nội dung payload thì gần như không. Đây thường chiếm 60–80% phần tràn và mất đi gần như chẳng tốn gì.
2. **Chunk retrieve mà model chưa hề nhắc tới.** Nếu qua vài lượt mà một chunk không được trích, không được dẫn, không được dùng, thì nó là một cú retrieve trượt. Bỏ.
3. **Nội dung trùng lặp và đã bị thay thế.** Ba bản sửa của cùng một file, bản trước và bản sau khi edit. Giữ bản hiện tại. Cắt cái này còn cải thiện chất lượng chứ không chỉ giảm chi phí.
4. **Khúc giữa của hội thoại.** Tóm tắt nó lại. Các lượt đầu mang định nghĩa nhiệm vụ, các lượt gần đây mang trạng thái; phần thương lượng ở giữa nén rất gọn.
5. **Định nghĩa của các tool mà session này chưa đụng tới.** Đẩy chúng sang chế độ defer loading.
6. **Tài liệu tham khảo.** Đẩy ra sau một tool tra cứu, chấp nhận thêm vài vòng round trip.
7. **System prompt.** Cuối cùng, và bằng cách viết lại, tuyệt đối không cắt cụt. Cắt cụt sẽ mất phần quy tắc an toàn và escalate, vốn thường nằm ở cuối.

Chú ý những gì *không* có trong danh sách: nhiệm vụ hiện tại, vài lượt gần nhất, và nội dung model đang trực tiếp suy luận cùng. Nếu bạn thấy mình đang cắt vào đó thì hoặc working budget đặt sai, hoặc nhiệm vụ quá lớn cho một context và cần chia cho nhiều sub-agent.

## Compaction là một bước có lịch, không phải phao cứu sinh

Đa số team viết compaction như một handler khẩn cấp: bắt lỗi vượt context, hớt hải tóm tắt, retry. Đó là thời điểm tệ nhất để làm, vì bạn đang tóm tắt trong lúc hết hạn, không còn budget, bằng đúng cái heuristic thô sơ bạn viết lúc 2 giờ sáng.

Hãy coi nó là một phần bình thường của vòng lặp. Có hai cơ chế và chúng làm hai việc khác nhau:

**Context editing thì xoá.** Nó gỡ hẳn các tool result cũ (và tuỳ chọn cả thinking block) — không tóm tắt, không tốn thêm một lần gọi model. Rẻ, tất định, và là mặc định hợp lý cho những agent nặng tool, nơi payload cũ thuần tuý là nhiễu.

```typescript
const response = await client.beta.messages.create({
  model: "claude-opus-5",
  max_tokens: 16000,
  betas: ["context-management-2025-06-27"],
  context_management: { edits: [{ type: "clear_tool_uses_20250919" }] },
  tools,
  messages,
});
```

**Compaction thì tóm tắt.** Khi bản thân hội thoại mang ý nghĩa mà việc xoá sẽ phá mất — các quyết định đã chốt, các ràng buộc mới phát hiện, những chỗ người dùng đã đính chính — bạn cần một bản tóm tắt chứ không phải một lệnh xoá. Compaction phía server xử lý việc này tự động khi hội thoại tiến gần ngưỡng.

```typescript
const response = await client.beta.messages.create({
  model: "claude-opus-5",
  max_tokens: 16000,
  betas: ["compact-2026-01-12"],
  context_management: { edits: [{ type: "compact_20260112" }] },
  messages,
});

// Append the whole content array. The compaction block is state — extract
// only the text and you silently lose it, and the next request recompacts.
messages.push({ role: "assistant", content: response.content });
```

Kiểu hỏng đáng ghi nhớ: nếu bạn tự viết phần này, bộ tóm tắt của bạn phải giữ lại **quyết định và ràng buộc**, không phải diễn biến. "Người dùng muốn một REST API" là thứ đáng giữ. "Rồi trợ lý giải thích khác biệt giữa REST và GraphQL" thì không. Đa số bộ tóm tắt ngây thơ làm ngược lại, vì chúng tối ưu cho dễ đọc thay vì cho thứ lượt kế tiếp thật sự cần.

## Đo đi, không thì bạn đang đoán

Hai con số làm cho toàn bộ chuyện này quan sát được, và cả hai đều rẻ.

**Đếm token trước khi gửi.** Endpoint đếm token miễn phí và chính xác, hơn hẳn mọi cách ước lượng theo ký tự bạn có thể tự viết.

```typescript
const { input_tokens } = await client.messages.countTokens({
  model: "claude-opus-5",
  system,
  tools,
  messages,
});
if (input_tokens > WORKING_BUDGET) {
  messages = await compact(messages, input_tokens - WORKING_BUDGET);
}
```

**Tỉ lệ trúng cache sau khi gửi.** `usage.cache_read_input_tokens` phải lớn và ổn định ở mọi request lặp lại. Nếu nó bằng không ở những lần gọi đáng lẽ chung prefix, tức là có gì đó trong prefix đang xê dịch — một ngày tháng, một UUID, một `Set` duyệt theo thứ tự không tất định, một danh sách tool ghép từ key của object. Hãy log tỉ lệ giữa token đọc từ cache và token input mới ở mỗi request, và cảnh báo khi nó tụt. Đó là chỉ báo tốt nhất cho câu hỏi "có ai vừa phá layout context không", và nó thường bắt được lỗi ngay trong chính lần deploy gây ra lỗi.

Nếu theo dõi thêm đúng một thứ nữa, hãy theo dõi **token trên mỗi nhiệm vụ hoàn thành** chứ đừng theo dõi token trên mỗi request. Một cách làm context giảm token mỗi request nhưng khiến agent cần thêm bốn lượt là đã làm mọi thứ tệ đi, và chỉ số theo request sẽ báo với bạn rằng nó tốt lên.

## FAQ

**Context window lớn có làm RAG trở nên thừa không?**

Không, nó đổi mục đích của retrieval. Hồi window còn nhỏ, retrieval là cách chữa cháy cho vấn đề sức chứa. Giờ nó là bộ lọc độ liên quan — việc cần làm là quyết định 20K token nào trong kho tài liệu xứng đáng cạnh tranh sự chú ý của model cho đúng câu hỏi này. Việc đó không biến mất khi window lớn lên; nếu có gì thì kỷ luật còn quan trọng hơn, vì chẳng còn gì ép bạn phải chọn lọc nữa.

**Tôi nên tự tóm tắt lịch sử hay dùng compaction phía server?**

Bắt đầu với bản phía server — chỉ một field cấu hình, tự kích hoạt, và tự lo phần sổ sách. Hãy tự viết khi bạn có cấu trúc đặc thù đáng giữ mà một bộ tóm tắt chung chung không thể biết, ví dụ danh sách yêu cầu đã xác nhận hoặc một state machine mà agent đang đi qua. Nếu tự viết, hãy giữ nguyên văn phần quyết định và ràng buộc, còn lại nén hết.

**Vậy system prompt nên dài bao nhiêu?**

Ngắn hơn bạn muốn. System prompt nên chứa những thứ đúng ở *mọi* lượt: vai trò, ranh giới cứng, định dạng đầu ra, quy tắc escalate. Mọi thứ có điều kiện — "nếu người dùng hỏi về thanh toán thì đây là các mức hoàn tiền" — là tài liệu tra cứu và thuộc về phía sau một tool hoặc trong retrieval. System prompt dài còn hay tích tụ những quy tắc viết cho model đời cũ mà nay lại gây hại, nên hãy đọc lại nó mỗi lần bạn nâng model.

**Vì sao agent của tôi bỏ qua một chỉ dẫn rõ ràng đang nằm trong context?**

Thường là do vị trí và cạnh tranh. Một chỉ dẫn nằm ở token thứ 4.000 của một context 90.000 token đang phải cạnh tranh với 86.000 token nội dung khác, mà phần nhiều trong đó có thể ngầm mâu thuẫn với nó. Hãy chuyển ràng buộc xuống lượt cuối, gỡ bỏ thứ đang mâu thuẫn với nó, và thu nhỏ context. Nếu sau đó vẫn bị bỏ qua thì đó là vấn đề câu chữ, không phải vấn đề context — và lúc đó prompt engineering mới là công cụ đúng.

**Những chi tiết API này có áp dụng cho nhà cung cấp khác ngoài Anthropic không?**

Các cơ chế thì có — cache theo prefix, hiệu ứng thứ tự, retrieval như bộ lọc độ liên quan, tóm tắt thay vì cắt cụt. Còn tên tham số, beta header và mức giá cache cụ thể trong bài là của Anthropic, và chúng có thay đổi. Mọi nhà cung cấp lớn đều có một dạng prefix caching với ngữ nghĩa khớp prefix tương tự, nhưng hãy kiểm tra tài liệu của chính nhà cung cấp bạn dùng về độ dài tối thiểu để cache được và mức chiết khấu trước khi thiết kế dựa vào đó.

---

*Bảng budget và thứ tự cắt là mặc định tôi đang dùng, không phải con số tối ưu đã đo đạc — hãy coi đó là hình dạng khởi đầu để tinh chỉnh theo lưu lượng thật của bạn. Các tham số API, beta header và hệ số giá cache là đúng tại thời điểm viết và thuộc đúng loại thứ hay thay đổi; hãy đối chiếu với tài liệu được dẫn trước khi đưa lên production.*
