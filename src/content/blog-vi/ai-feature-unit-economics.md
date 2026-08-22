---
title: "Chi phí mỗi request: con số mà hầu hết feature AI không bao giờ tính"
description: "Bạn biết hóa đơn API hàng tháng. Nhưng gần như chắc chắn bạn không biết một request tốn bao nhiêu — nghĩa là bạn không phân biệt được vấn đề nằm ở giá hay ở mức sử dụng. Đây là mô hình đầy đủ, kèm những hệ số biến một cú gọi nửa xu thành một hành động người dùng bốn xu."
seoDescription: "Dựng mô hình chi phí mỗi request cho feature LLM: công thức token gốc, vòng lặp agent, hội thoại tăng bậc hai, retrieval, retry — rồi xếp hạng đòn bẩy và instrument nó."
keywords:
  - chi phí llm mỗi request
  - unit economics feature ai
  - tính chi phí token
  - chi phí vòng lặp agent
  - đo lường chi phí llm
  - chi phí mỗi hành động người dùng
category: "Phân tích"
topic: "AI Engineering"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-22"
emoji: "🧮"
tags: ["AI", "LLM", "Tối ưu chi phí", "Observability"]
sources:
  - name: "Anthropic — endpoint đếm token"
    url: "https://docs.claude.com/en/docs/build-with-claude/token-counting"
  - name: "Anthropic — prompt caching"
    url: "https://docs.claude.com/en/docs/build-with-claude/prompt-caching"
  - name: "Anthropic — bảng giá"
    url: "https://claude.com/pricing"
  - name: "OpenAI — bảng giá"
    url: "https://platform.openai.com/docs/pricing"
  - name: "Gemini API — hiểu và đếm token"
    url: "https://ai.google.dev/gemini-api/docs/tokens"
  - name: "tiktoken — bộ tokenizer BPE của OpenAI"
    url: "https://github.com/openai/tiktoken"
related:
  - slug: "cutting-ai-costs-free-tiers-caching-and-routing"
    title: "Dùng AI mà không đốt tiền: free tier, caching và định tuyến model"
  - slug: "building-an-ai-agent-team-chief-of-staff-pattern"
    title: "Mô hình Chief of Staff: biến đống chat AI rời rạc thành một đội ngũ agent"
draft: false
---

Đội nào ship feature AI cũng biết hóa đơn API hàng tháng của mình. Gần như không đội nào biết một request đơn lẻ tốn bao nhiêu. Đó là hai con số khác nhau, và chỉ con số thứ hai mới hành động được.

Hóa đơn là một tổng. Nó không nói cho bạn biết tổng đó lớn vì mỗi request đắt, hay vì số request nhiều hơn nhiều so với dự tính. Hai vấn đề này có cách sửa ngược nhau — một cái là vấn đề kiến trúc, một cái là vấn đề đóng gói sản phẩm — nên đội chỉ có mỗi cái tổng thường phản ứng y hệt nhau trong cả hai trường hợp: ai đó bỏ một tuần cắt gọt system prompt. Như bạn sẽ thấy bên dưới, đó thường là đòn bẩy nhỏ nhất hiện có, và là đòn bẩy đầu tiên mọi người với tay tới.

Hóa đơn còn là một con số duy nhất cho một tài khoản có thể đang phục vụ sáu feature. Nếu summarization rẻ còn workflow agentic mới thì đắt, hóa đơn gộp chúng thành một con số vô nghĩa và con số đó cứ tăng.

Bài này dựng con số còn thiếu đó từ đầu: một hành động người dùng tốn bao nhiêu, từ đầu đến cuối, tính cả mọi hệ số nằm giữa công thức hai số hạng trong sách giáo khoa và thực tế. Còn làm gì sau khi nhìn thấy con số — free tier, định tuyến model, giá batch — thì [Dùng AI mà không đốt tiền](/vi/blog/cutting-ai-costs-free-tiers-caching-and-routing/) đã bàn rồi. Ở đây mục tiêu duy nhất là làm cho con số đó tồn tại.

> **Mọi mức giá trong bài này đều là số giả định.** Xuyên suốt bài tôi dùng **$1.00 cho mỗi triệu input token** và **$5.00 cho mỗi triệu output token**, vì số tròn thì bạn kiểm tra lại bằng tay được. Đó không phải giá thật của nhà cung cấp nào cả. Hãy thay bằng bảng giá hiện hành của nhà cung cấp bạn đang dùng — có link ở phần nguồn cuối bài — trước khi ra quyết định dựa trên bất cứ con số nào ở đây.

## Công thức hai số hạng mới là phần dễ

Chi phí gốc của một cú gọi API:

```text
cost = (input_tokens  / 1_000_000) * input_rate
     + (output_tokens / 1_000_000) * output_rate
```

Lấy feature "tóm tắt ticket hỗ trợ": prompt 3.000 token (system instruction cộng nội dung ticket), tóm tắt ra 400 token.

```text
input:  3,000 / 1e6 * $1.00 = $0.0030
output:   400 / 1e6 * $5.00 = $0.0020
total                       = $0.0050
```

Nửa xu. Với 200.000 ticket một tháng là $1.000, và nếu dashboard của bạn hiện đúng như vậy thì mô hình này đã đủ.

Có hai điểm đáng để ý trước khi làm nó phức tạp lên. Thứ nhất, **output được tính giá cao hơn input vài lần ở hầu hết mọi nhà cung cấp**, nên "trả lời ngắn gọn" là một khoản chi phí chứ không phải một sở thích văn phong. Thứ hai, công thức này chỉ đúng cho đúng một dạng feature: một hành động người dùng, một cú gọi API, không retry, không lịch sử hội thoại. Phần lớn feature không có dạng đó, và mỗi lần lệch khỏi nó là thêm một hệ số nhân.

## Hệ số 1: một hành động người dùng không phải một cú gọi API

Một agent biết lập kế hoạch, gọi tool rồi mới trả lời không tạo ra một request. Nó tạo một request cho mỗi turn, và API thì stateless — **mỗi turn gửi lại toàn bộ hội thoại tính đến thời điểm đó**, gồm cả system prompt, định nghĩa tool, và mọi tool result đã nhận về.

Cụ thể, lấy một agent với:

- prefix ổn định 2.000 token (system prompt cộng schema của tool),
- request người dùng 500 token,
- 6 turn: năm lần gọi tool, mỗi lần 150 output token, rồi câu trả lời cuối 400 token,
- mỗi turn nối thêm 800 token tool result, nên lịch sử phình thêm 950 token mỗi turn.

| Turn | Input token | Output token |
| --- | --- | --- |
| 1 | 2.500 | 150 |
| 2 | 3.450 | 150 |
| 3 | 4.400 | 150 |
| 4 | 5.350 | 150 |
| 5 | 6.300 | 150 |
| 6 | 7.250 | 400 |
| **Tổng** | **29.250** | **1.150** |

```text
input:  29,250 / 1e6 * $1.00 = $0.02925
output:  1,150 / 1e6 * $5.00 = $0.00575
mỗi hành động người dùng      = $0.0350
```

Ba xu rưỡi. Ước lượng ngây thơ — 2.500 vào, 400 ra, một cú gọi — cho $0.0045. **Vòng lặp tốn khoảng 7,8 lần con số mà ước lượng một-cú-gọi dự đoán**, và không có gì trong tỉ lệ đó nhìn thấy được từ hóa đơn.

Dạng tổng quát, với `n` turn, prefix cố định `S` (system + tool + request gốc), và `g` token phình thêm mỗi turn:

```text
total_input_tokens = n * S + g * n * (n - 1) / 2
```

Số hạng thứ hai là bậc hai theo `n`. Tăng vòng lặp từ 6 turn lên 12 đưa tổng input từ 29.250 lên 92.700 — **3,2 lần số token cho 2 lần số turn**. Đây là lý do một agent "thỉnh thoảng đi thêm vài bước" không phải chuyện nhỏ: turn biên luôn là turn đắt nhất tính đến lúc đó.

## Hệ số 2: hội thoại tự trả tiền cho lịch sử của chính nó

Cùng tính chất bậc hai đó áp cho mọi cuộc chat nhiều turn, và ở đây còn dễ bỏ sót hơn vì từng turn riêng lẻ vẫn có vẻ rẻ.

Lấy system prompt 1.000 token, mỗi lượt trao đổi gồm câu hỏi 100 token và trả lời 300 token — lịch sử phình 400 token mỗi turn, nên turn thứ `n` gửi `1.100 + 400*(n-1)` input token.

| Turn | Input token | Chi phí turn này | Lũy kế | Turn này so với turn 1 |
| --- | --- | --- | --- | --- |
| 1 | 1.100 | $0.0026 | $0.0026 | 1,0x |
| 5 | 2.700 | $0.0042 | $0.0170 | 1,6x |
| 10 | 4.700 | $0.0062 | $0.0440 | 2,4x |
| 20 | 8.700 | $0.0102 | $0.1280 | 3,9x |
| 30 | 12.700 | $0.0142 | $0.2520 | 5,5x |

Một hội thoại 30 turn tốn $0,252. Nếu bạn ước lượng nó là "30 turn, mỗi turn bằng chi phí turn 1" thì bạn đã dự trù $0,078 — lệch 3,2 lần. **Những người dùng gắn bó nhất là những người tốn kém nhất theo cách siêu tuyến tính**, ngược hẳn với trực giác mà phần lớn trang pricing được xây trên đó.

Cách giảm nhẹ nằm ở kiến trúc chứ không phải tài chính: mở session mới khi đổi chủ đề, bỏ tool result cũ khỏi lịch sử, hoặc dùng cơ chế compaction phía server nếu nhà cung cấp có. Tất cả đều làm giảm `g`, mà `g` thì đang bị nhân với `n(n-1)/2`.

## Hệ số 3: context lấy về là một giá trị config, không phải input của người dùng

Trong một feature RAG, các chunk lấy về thường lớn hơn hẳn câu hỏi. Với `k = 8` chunk, mỗi chunk khoảng 600 token, mỗi request cõng 4.800 token context bất kể người dùng gõ ba chữ hay ba mươi chữ.

Điều quan trọng là **`k` là một con số trong config, nên chi phí mỗi request thay đổi khi ai đó sửa một file config**. Một lời phàn nàn về recall được xử lý bằng cách nâng `k` từ 8 lên 20; context lấy về đi từ 4.800 lên 12.000 token; chi phí input mỗi request đi từ $0,0053 lên $0,0125. Đó là thay đổi 2,4 lần unit economics của feature, ship bằng một dòng diff, trong một PR có tiêu đề nói về chất lượng câu trả lời.

Corpus lớn lên cũng đẩy theo hướng đó một cách gián tiếp. Corpus lớn nghĩa là nhiều chunk gần đúng hơn, nên đội sẽ nâng `k`, thêm một pass rerank trên tập ứng viên rộng hơn, hoặc chuyển sang chunk to hơn. Không cái nào xuất hiện trong changelog dưới dạng "chúng ta vừa làm feature này đắt lên". Hãy đưa `k`, chunk size và giới hạn độ dài output vào cùng checklist review với mọi thứ khác làm dịch chuyển chi phí, và in ra mức chênh token mỗi request ngay trong PR.

## Hệ số 4: bạn trả tiền cho cả những lần thất bại

Mọi thứ ở trên đều giả định cú gọi nào cũng thành công. Bốn thứ phá vỡ giả định đó:

- **Retry do validation.** Nếu một structured output trượt schema validation và bạn retry, với tỉ lệ lỗi độc lập `p` bạn tốn trung bình `1 / (1 - p)` lần thử — tỉ lệ lỗi 10% là hệ số 1,11. Không nhiều. Nhưng lần thử hỏng vẫn bị tính output token, và một response JSON bị cắt cụt thường có nghĩa model đã sinh *rất nhiều* output trước khi đụng trần.
- **Vòng sửa lỗi tool.** Một agent gọi tool sai, đọc lỗi rồi thử lại không thêm một cú gọi — nó thêm một turn, mà turn thì bậc hai (Hệ số 1).
- **Guardrail và judge pass.** Nếu bạn chạy một model thứ hai kiểm tra mọi output, đó không phải hệ số nhân mà là một khoản chi phí riêng hẳn. Hãy tính giá nó riêng và ghi vào cùng một sổ.
- **Reasoning token.** Ở các nhà cung cấp có extended thinking, reasoning token bị tính theo giá output ngay cả khi chúng không bao giờ xuất hiện trong câu trả lời. Câu trả lời ngắn không phải bằng chứng rằng request đó rẻ.

Stream bị bỏ giữa chừng thì nên kiểm tra chứ đừng đoán: việc một stream bị hủy có bị tính số token đã sinh hay không là tùy nhà cung cấp, và trên một chat UI thì chuyện người dùng bỏ ngang rất phổ biến.

## Xếp hạng các đòn bẩy — và thứ hạng phụ thuộc vào hình dạng feature của bạn

Giờ áp các đòn bẩy vào con agent 6 turn ở Hệ số 1, với mốc **$0,0350 mỗi hành động người dùng**.

| Đòn bẩy | Nó làm gì | Chi phí mới | Thay đổi |
| --- | --- | --- | --- |
| Rút ngắn vòng lặp (6 turn → 3) | Giảm `n`, tức giảm luôn số hạng bậc hai | $0,0139 | **−60%** |
| Cache phần prefix đang phình | Turn `k` đọc lại prefix của turn `k−1` theo giá cache read | $0,0170 | **−51%** |
| Định tuyến nửa lưu lượng sang model rẻ hơn 10 lần | Trung bình theo tập người dùng, chi phí từng request không đổi | $0,0193 | −45% |
| Cắt đôi câu trả lời cuối (400 → 200 token) | Output chỉ chiếm 16% chi phí request này | $0,0340 | −3% |
| Cắt 30% system prompt | Bớt 600 token, nhân với 6 lần gửi lại | $0,0314 | −10% |

Dòng caching giả định giá cache giả định là 1,25 lần giá input để ghi và 0,1 lần để đọc, với một breakpoint tăng dần mỗi turn: 7.250 token ghi, 22.000 token đọc. Vòng lặp agent là ứng viên caching cực tốt chính *vì* tính bậc hai — cùng một hành động gửi lại prefix của chính nó vài lần chỉ trong vài giây, nên cache có lời mà không cần giả định gì về lưu lượng giữa các request. Chuyện đặt breakpoint ở đâu và khi nào cache bị vô hiệu là một chủ đề riêng; [tài liệu prompt caching](https://docs.claude.com/en/docs/build-with-claude/prompt-caching) là chỗ nên bắt đầu.

**Cắt gọt prompt xếp cuối, và caching còn làm nó tệ hơn.** Một khi prefix đã được cache, 600 token đó được tính theo giá cache read, nên mức tiết kiệm 10% co lại còn khoảng 1%. Cách tối ưu được thử nhiều nhất lại là cách kém hiệu quả nhất, và cách tối ưu phổ biến thứ hai *lấy nốt phần giá trị còn lại của nó*.

**Thứ hạng này không phổ quát.** Trong con agent trên, output chiếm 16% chi phí, nên giới hạn độ dài output gần như vô nghĩa. Trong một feature sinh tài liệu — prompt ngắn, output 4.000 token — output chiếm áp đảo và giới hạn nó là đòn bẩy số một, còn rút ngắn vòng lặp thì vô nghĩa vì làm gì có vòng lặp nào. **Không có thứ hạng mặc định đúng. Chỉ có hình dạng đo được của bạn**, và đó chính là toàn bộ lý do phải instrument chuyện này.

## Instrument nó: một dòng cho mỗi cú gọi API, nối với nhau bằng action

Đơn vị để log là **cú gọi API**, không phải feature. Đơn vị để phân tích là **hành động người dùng**. Bạn đi từ cái thứ nhất sang cái thứ hai bằng một `action_id` xuyên suốt mọi cú gọi mà một hành động người dùng kích hoạt.

Hãy tính chi phí ngay lúc ghi, từ số token mà API trả về — đừng bao giờ suy lại về sau từ một bảng giá đã thay đổi, và đừng bao giờ ước lượng token bằng tokenizer phía client để hạch toán. Các bộ đếm phía client như [tiktoken](https://github.com/openai/tiktoken) và endpoint `count_tokens` của nhà cung cấp là để dự trù trước khi gọi; object `usage` trong response mới là sự thật được tính tiền.

```typescript
// PLACEHOLDER rates, $ per 1M tokens. Replace with your provider's published rates.
const RATES = {
  "model-large": { in: 1.0, out: 5.0, cacheWrite: 1.25, cacheRead: 0.1 },
  "model-small": { in: 0.1, out: 0.5, cacheWrite: 0.125, cacheRead: 0.01 },
} as const;

type Usage = {
  input_tokens: number;
  output_tokens: number;
  cache_creation_input_tokens?: number;
  cache_read_input_tokens?: number;
};

function costUsd(model: keyof typeof RATES, u: Usage): number {
  const r = RATES[model];
  return (
    u.input_tokens * r.in +
    u.output_tokens * r.out +
    (u.cache_creation_input_tokens ?? 0) * r.cacheWrite +
    (u.cache_read_input_tokens ?? 0) * r.cacheRead
  ) / 1_000_000;
}
```

Một cái bẫy về tính đúng đắn: hãy kiểm tra xem `input_tokens` của nhà cung cấp bạn dùng **có bao gồm hay không bao gồm** token đã cache. Trên Claude API, ba con số này rời nhau — `input_tokens` chỉ tính phần chưa cache — nên cộng chúng lại là đúng. Nếu nhà cung cấp của bạn báo một tổng đã bao gồm, đúng đoạn code đó sẽ đếm trùng mọi cache hit và thổi phồng con số của bạn.

Mỗi cú gọi sinh ra một dòng:

```json
{
  "action_id": "01JQ8T5V2K9",
  "feature": "ticket_agent",
  "model": "model-large",
  "turn": 3,
  "attempt": 1,
  "input_tokens": 4400,
  "cache_read_input_tokens": 2000,
  "output_tokens": 150,
  "cost_usd": 0.00535,
  "rates_version": "2026-08-01",
  "latency_ms": 1840,
  "outcome": "tool_use"
}
```

`rates_version` là trường mọi người bỏ qua rồi tiếc. Giá thay đổi; không có nó, các dòng lịch sử mất khả năng tái lập và bạn không bao giờ trả lời được câu "chi phí mỗi hành động của mình tăng thật, hay là giá tăng?"

Gộp theo hành động, rồi nhìn phân phối thay vì nhìn trung bình:

```sql
WITH per_action AS (
  SELECT feature, action_id,
         sum(cost_usd)                     AS cost_usd,
         sum(input_tokens + output_tokens) AS tokens,
         count(*)                          AS calls
  FROM llm_calls
  WHERE ts >= now() - interval '7 days'
  GROUP BY feature, action_id
)
SELECT feature,
       count(*)      AS actions,
       avg(calls)    AS calls_per_action,
       avg(cost_usd) AS mean_cost,
       percentile_cont(0.50) WITHIN GROUP (ORDER BY cost_usd) AS p50,
       percentile_cont(0.95) WITHIN GROUP (ORDER BY cost_usd) AS p95,
       sum(cost_usd) AS total
FROM per_action
GROUP BY feature
ORDER BY total DESC;
```

`calls_per_action` là cột chẩn đoán mạnh nhất trong câu query đó. Nếu nó bằng 1,0, bạn có một feature đơn giản và công thức hai số hạng là toàn bộ mô hình của bạn. Nếu nó bằng 6,4 trong khi bạn thiết kế cho 3, bạn đã tìm ra vấn đề chi phí mà chưa cần đọc con số nào khác.

Và hãy đặt cảnh báo trên **chi phí mỗi hành động**, đừng đặt trên hóa đơn. Hóa đơn dịch chuyển khi lưu lượng dịch chuyển, chuyện đó không mới. Chi phí mỗi hành động dịch chuyển khi code của bạn thay đổi — một lần sửa prompt, một lần nâng `k`, một lần đổi model, một vòng lặp bắt đầu đi thêm một turn trên nhóm input mà trước đây nó không gặp. Đó mới là tín hiệu.

## Có con số rồi thì nó nói lên điều gì

Có chi phí mỗi hành động trong tay, hai phép nhân biến dữ liệu kỹ thuật thành dữ liệu kinh doanh:

```text
cost_to_serve_a_user = cost_per_action * actions_per_user_per_month
gross_margin         = (price - cost_to_serve) / price
```

Giờ chẩn đoán trở thành máy móc. Nếu chi phí mỗi hành động đạt mục tiêu nhưng `actions_per_user_per_month` gấp năm lần mức bạn định giá, đó là **vấn đề mức sử dụng** — sửa bằng quota, phân tier, hoặc một đường đi rẻ hơn cho hành động tần suất cao, chứ không phải bằng cách viết lại prompt. Nếu một hành động đơn lẻ tốn một phần đáng kể toàn bộ giá tháng của người dùng, đó là **vấn đề kiến trúc** và không cách đóng gói nào cứu được.

Hãy nhìn p95 thay vì trung bình. Phân phối chi phí LLM có đuôi dài — cuộc hội thoại 30 turn, con agent đi 14 bước, người dùng dán cả một cuốn tiểu thuyết — và trung bình giấu chúng sau một con số trông rất dễ chịu. Nếu p95 gấp nhiều lần p50, một nhóm nhỏ session đang quyết định hóa đơn của bạn, và cách sửa là đặt một cái trần ở đâu đó (giới hạn turn, giới hạn context, giới hạn output) chứ không phải tối ưu dàn trải.

Không cần vendor nào cho chuyện này: một bảng, một `action_id`, và một hàm tính chi phí mười dòng. Lý do phần lớn đội không có nó không phải vì khó — mà vì không ai sở hữu con số đó cho tới khi hóa đơn đã đủ đáng sợ.

## FAQ

**Dashboard usage của nhà cung cấp chưa đủ sao?**
Nó cho bạn tổng theo API key và thường theo model, tức trả lời "bao nhiêu" chứ không trả lời "cho cái gì". Nó không biết feature nào của bạn tạo ra cú gọi, những cú gọi nào thuộc cùng một hành động người dùng, hay phân phối giữa các request trông thế nào. Bạn có thể xấp xỉ việc quy về feature bằng cách tách một API key cho mỗi feature — một giải pháp tạm chấp nhận được — nhưng nó vẫn không cho bạn chi phí mỗi hành động hay p95.

**Làm sao ước lượng chi phí khi chưa ship gì?**
Chạy endpoint đếm token của nhà cung cấp trên một mẫu input thực tế — không phải prompt đồ chơi — để có phía input, chặn phía output ở `max_tokens` của bạn, rồi nhân với số turn bạn nghĩ vòng lặp sẽ chạy. Sau đó giả định vòng lặp chạy nhiều turn hơn bạn nghĩ, vì nó sẽ như vậy. Ship sau một feature flag và thay ước lượng bằng số đo ngay khi có lưu lượng thật.

**Reasoning token hay "thinking" có làm đổi phép tính không?**
Có, và theo cách rất dễ bỏ sót. Ở nơi nhà cung cấp tính tiền reasoning token, chúng bị tính theo giá output dù người dùng không bao giờ nhìn thấy, nên một request trả về hai câu có thể mang hóa đơn output lớn hơn nhiều lần so với vẻ ngoài của hai câu đó. Hãy đọc chúng từ object `usage` thay vì suy ra chi phí từ độ dài câu trả lời nhìn thấy được.

**Có nên tính giá theo token trực tiếp cho người dùng cuối?**
Thường là không, và đây là quan điểm cá nhân chứ không phải phân tích: giá theo token làm hóa đơn của khách hàng khó dự đoán và cột giá của bạn vào một bảng giá của nhà cung cấp mà bạn không kiểm soát. Credit hoặc quota theo hành động giữ phần khó đoán ở phía bạn, nơi bạn thực sự quản được — nhưng cách đó chỉ chạy nếu bạn biết chi phí mỗi hành động, mà đó chính là toàn bộ ý của bài này.

**Những điều trên có áp dụng khi tôi tự host model open-weights không?**
Cấu trúc giữ nguyên; mẫu số đổi. Thay vì một mức giá công bố theo token, bạn tính mức giá hiệu dụng từ chi phí GPU-giờ chia cho throughput đo được ở batch size và độ dài context của bạn, rồi đưa vào cùng công thức. Các hệ số nhân — số turn, lịch sử bậc hai, kích thước retrieval, retry — thì y hệt, vì chúng là tính chất của kiến trúc bạn chứ không phải của bảng giá ai cả.

---

*Các công thức, phép tính và cấu trúc hệ số ở đây đều mang tính máy móc và bạn kiểm chứng được từng dòng bằng tay. Mọi mức giá đều là số giả định được chọn cho tròn — hãy thay bằng bảng giá hiện hành của nhà cung cấp bạn dùng trước khi rút ra kết luận, và kiểm tra lại định kỳ vì chúng thay đổi. Thứ hạng các đòn bẩy chỉ đúng cho workload ví dụ và sẽ đảo lại với feature của bạn; đó là luận điểm chính chứ không phải một lời rào trước. Cách tính tiền cho stream bị hủy, token đã cache và reasoning token tùy thuộc nhà cung cấp và phiên bản — hãy đối chiếu với tài liệu hiện hành.*
