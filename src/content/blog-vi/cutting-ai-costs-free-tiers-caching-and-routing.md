---
title: "Dùng AI mà không đốt tiền: free tier, caching và định tuyến model"
description: "Ba đòn bẩy quyết định hóa đơn AI của bạn: đừng trả tiền cho thứ đang miễn phí, đừng trả tiền hai lần cho cùng một mớ token, và đừng trả giá frontier cho việc của thực tập sinh. Kèm số liệu thật."
seoDescription: "Hướng dẫn thực dụng để cắt chi phí LLM: hạn mức free tier hiện hành của Cerebras, Groq và OpenRouter, cách gộp chúng bằng FreeLLMAPI, cùng các đòn bẩy phía trả phí — prompt caching, Batch API, định tuyến model và dọn context — kèm bài toán chi phí cụ thể."
keywords:
  - giảm chi phí api llm
  - llm api miễn phí
  - cerebras free tier
  - prompt caching tiết kiệm chi phí
  - batch api giảm giá
  - định tuyến model llm
  - freellmapi
category: "Hướng dẫn"
topic: "AI Engineering"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-20"
emoji: "💸"
tags: ["AI", "Tối ưu chi phí", "LLM", "Công cụ lập trình", "API"]
sources:
  - name: "Cerebras Inference — rate limit theo từng tier"
    url: "https://inference-docs.cerebras.ai/support/rate-limits"
  - name: "Groq — rate limits"
    url: "https://console.groq.com/docs/rate-limits"
  - name: "OpenRouter — giới hạn API và hạn mức model miễn phí"
    url: "https://openrouter.ai/docs/api-reference/limits"
  - name: "Gemini API — điều khoản bổ sung (bản trả phí và bản miễn phí)"
    url: "https://ai.google.dev/gemini-api/terms"
  - name: "FreeLLMAPI — bộ gộp free tier tự host"
    url: "https://github.com/tashfeenahmed/freellmapi"
  - name: "Anthropic — bảng giá"
    url: "https://claude.com/pricing"
draft: false
---

Phần lớn mọi người cắt hóa đơn AI bằng cách đổi sang model rẻ hơn. Đó là đòn bẩy nhỏ nhất trong đám, và thường là đòn bẩy trả giá đắt nhất bằng chất lượng.

Hóa đơn được quyết định bởi ba thứ, theo đúng thứ tự này:

1. **Thứ bạn đang trả tiền dù nó vốn miễn phí.** Vài nhà cung cấp cho hạn mức thật, không cần thẻ.
2. **Thứ bạn trả tiền hai lần.** Cùng một system prompt 20.000 token, gửi lại nguyên giá ở mỗi request.
3. **Thứ bạn trả giá frontier trong khi nó không cần.** Phân loại, trích xuất, đổi tên, định dạng.

Sửa theo đúng thứ tự đó. Cái đầu là tiền cho không, cái thứ hai thường giảm 5–10 lần trên cùng một model, và chỉ sau đó việc chọn model mới đáng bàn. Dưới đây là giá trị thật của từng cái ngay lúc này, với số liệu lấy từ tài liệu chính chủ chứ không phải từ trí nhớ.

## Tier 0: hôm nay cái gì thật sự miễn phí

Free tier là thật, và rộng hơn phần lớn mọi người tưởng. Nhưng con số quan trọng không phải cái tổng theo ngày mà ai cũng đem đi khoe — mà là con số **theo phút**, vì đó mới là thứ chặn bạn giữa chừng.

| Nhà cung cấp | Model miễn phí | Mỗi phút | Mỗi ngày | Cần thẻ |
| --- | --- | --- | --- | --- |
| **Cerebras** | `gpt-oss-120b`, `gemma-4-31b` | 5 RPM, 30K TPM | 1M TPD (và 1M mỗi *giờ*) | Không |
| **Groq** | `openai/gpt-oss-120b` / `20b`, `qwen/qwen3.6-27b` | 30 RPM, 8K TPM | 1K RPD, 200K TPD | Không |
| **Groq** (compound) | `groq/compound`, `compound-mini` | 30 RPM, 70K TPM | 250 RPD | Không |
| **OpenRouter** | mọi model `:free` | 20 RPM | 50 RPD — hoặc 1.000 RPD sau khi đã mua tổng cộng ≥10 credit | Không (credit là tùy chọn) |
| **Google AI Studio** | Gemini free tier | theo tài khoản | theo tài khoản | Không |

Vài thứ bảng này giấu đi mà bạn sẽ vấp:

**TPM mới là trần thật, không phải TPD.** Cerebras cho một triệu token mỗi ngày nhưng chỉ 30.000 token mỗi phút. Một request mang theo tài liệu 40.000 token không bị làm chậm — nó bị từ chối. Free tier được thiết kế cho nhiều request nhỏ, không phải cho vài request lớn. Nếu workload của bạn là "tóm tắt cái PDF 60 trang này" thì free tier sai hình dạng, bất kể con số theo ngày nghe to cỡ nào.

**Cerebras còn tính hạn mức theo giờ.** 1M token mỗi giờ *và* 1M mỗi ngày nghĩa là toàn bộ ngân sách cả ngày có thể bay hết trong một tiếng. Không có cơ chế san đều.

**Giới hạn của Google là theo tài khoản, không công bố thành bảng cố định.** Nó hiện trong dashboard rate limit của AI Studio ứng với key của bạn. Mọi con số bạn đọc trong một bài blog — kể cả bài này — là tài khoản của người khác.

**Hạn mức RPD miễn phí nhỏ tới mức vòng lặp agent nuốt sạch.** 50 request/ngày trên OpenRouter tương đương khoảng ba task agentic, vì mỗi task đều tỏa ra thành chu kỳ đọc file / chạy test / sửa / đọc lại.

### Phần giá không tính bằng tiền

Cái giá thứ hai của free tier là dữ liệu của bạn, và ít nhất một nhà cung cấp nói thẳng ra. Điều khoản Gemini API vạch ranh giới ngay ở chỗ trả tiền: với dịch vụ **không trả phí**, Google dùng nội dung bạn gửi lên "để cung cấp, cải thiện và phát triển các sản phẩm, dịch vụ của Google", và người thật "có thể đọc, chú thích và xử lý input cũng như output API của bạn" — sau khi đã tách khỏi tài khoản và API key. Với dịch vụ **trả phí**, Google "không dùng prompt... hay phản hồi của bạn để cải thiện sản phẩm", chỉ ghi log trong thời gian ngắn để phát hiện lạm dụng.

Đó là cùng một sự đánh đổi mà mọi free tier đều thực hiện dưới hình thức nào đó, chỉ khác nhau ở mức minh bạch. Hãy đọc điều khoản của từng bên thay vì suy đoán — nhưng cứ mặc định là dữ liệu **được giữ lại**.

Nguyên tắc vận hành rút ra rất gọn: **free tier dành cho công việc mà bạn thấy thoải mái nếu nó được công khai.** Học, prototype, dự án cá nhân, code mã nguồn mở, tài liệu công khai. Không phải code của khách hàng, không phải dữ liệu người dùng, không phải thứ gì đang trong NDA. Đây không phải nghi ngờ thiện chí của nhà cung cấp — đây là chuyện bạn đã đồng ý cái gì khi bỏ qua bước nhập thẻ.

## Gộp các free tier lại: FreeLLMAPI

Khi bạn đã xài ba bốn free tier, thứ gây khó chịu không còn là quota nữa — mà là đường ống. Mỗi bên một base URL, một key, một kiểu trả 429, và không có failover khi một bên cạn quota giữa chừng.

[FreeLLMAPI](https://github.com/tashfeenahmed/freellmapi) (MIT, ~19k sao) là câu trả lời hiện tại cho chuyện đó. Bạn tự host, dán API key của mình vào, và nó bày ra một endpoint `/v1` tương thích OpenAI duy nhất — kèm cả bề mặt Anthropic Messages và Gemini — đứng trước tất cả. Dự án công bố khoảng **4 tỷ token mỗi tháng qua 29 nhà cung cấp và 358 endpoint model miễn phí**, theo dõi RPM/RPD/TPM/TPD cho từng key, và khi gặp 429 hoặc 5xx thì áp cooldown rồi rơi xuống model kế tiếp trong chuỗi. Key nằm trong file SQLite cục bộ, mã hóa AES-256-GCM; dashboard chạy ở `localhost:3001`.

Con số này thay đổi, và điều đó đáng nhắc: một bài chia sẻ đang lan truyền về dự án ghi 1,3 tỷ token/tháng, còn repo hiện tại ghi 4 tỷ. Hãy coi mọi con số cụ thể là ảnh chụp tại một thời điểm, kể cả con số phía trên.

Ba lưu ý trước khi cắm nó vào bất cứ thứ gì:

- **README nói thẳng:** dự án "dành cho thử nghiệm và học tập cá nhân, không phải cho production". Hãy hiểu đúng nghĩa đen. Một router tự host đứng trước cả tá free tier là một điểm chết duy nhất kèm cả tá kiểu hỏng từ thượng nguồn.
- **Điều khoản của từng nhà cung cấp vẫn thuộc về bạn.** Việc gộp lại không thay đổi thứ bạn đã đồng ý ở mỗi tài khoản, và free tier nhìn chung được tính cho một ứng dụng chứ không phải cho một router tỏa ra nhiều nhánh.
- **Lệnh cài nhanh là `curl … | bash`.** Đó là một script từ xa chạy với quyền của shell nhà bạn. Đọc nó trước khi chạy — lời khuyên này đúng với mọi one-liner cài đặt, không riêng cái này.

Dùng trong đúng giới hạn đó thì nó thật sự tốt: nó biến câu hỏi "free tier nào còn quota" từ thứ bạn phải nghĩ thành thứ tự nó giải quyết.

## Khi nào free hết còn là câu trả lời đúng

Free tier hỏng ở ba trục, và hỏng theo cách đoán trước được:

| Bạn cần | Free tier đưa bạn |
| --- | --- |
| Độ trễ ổn định | Best-effort, dùng chung hạ tầng |
| Rate limit đủ để lên kế hoạch cho một sprint | 5–30 RPM, TPM nhỏ |
| Cam kết xử lý dữ liệu bằng văn bản | Nội dung được dùng để cải thiện model của nhà cung cấp |

Ngay khi output của model chạm tới thứ khách hàng nhìn thấy hoặc thứ có người trả tiền, cả ba điều trên đều không còn chấp nhận được. Đó mới là mốc để chuyển — không phải một con số token nào cả.

## Các đòn bẩy phía trả phí, xếp theo mức thu về

Đây mới là chỗ chứa phần lớn số tiền, và gần như không ai nhìn vào đầu tiên. Giá bên dưới là bảng giá công bố của Anthropic; *cơ chế* thì nhà cung cấp lớn nào cũng có, chỉ khác hệ số.

### 1. Prompt caching — đòn bẩy lớn nhất (giảm ~90% phần input lặp lại)

Nếu có phần nào trong request của bạn giống hệt nhau mỗi lần — system prompt, danh sách tool, một kho tri thức, một bộ quy tắc văn phong — thì hiện tại bạn đang trả nguyên giá để gửi lại nó ở từng lượt gọi.

Caching tính khoảng **1,25x để ghi** một prefix và khoảng **0,1x để đọc**. Nghĩa là nó hoàn vốn ngay ở lượt gọi **thứ hai**: 1,25 + 0,1 = 1,35 so với 2,0 nếu gửi thẳng hai lần. Mọi lượt sau đó rẻ đi khoảng 90%.

Hai nguyên tắc quyết định nó có chạy hay không:

- **Nó khớp theo prefix.** Thứ tự dựng request là `tools` → `system` → `messages`. Chỉ một byte đổi ở bất cứ đâu trong prefix là vô hiệu hóa toàn bộ phần phía sau. Đặt nội dung ổn định lên trước; đặt timestamp, request ID và câu hỏi thật của người dùng *sau* breakpoint cache cuối cùng.
- **Có ngưỡng tối thiểu.** Prefix dưới khoảng 1.024 token lặng lẽ không được cache. Không báo lỗi — chỉ là không tiết kiệm được gì.

Thủ phạm giết cache âm thầm hay gặp nhất là một `datetime.now()` hoặc một UUID chèn vào system prompt. Hãy kiểm chứng thay vì tin: `usage.cache_read_input_tokens` phải khác 0 ở các lượt gọi lặp lại. Nếu lần nào cũng bằng 0 thì có thứ gì đó trong prefix đang nhúc nhích.

### 2. Batch API — giảm 50% cho mọi thứ không cần tương tác

Chạy bù dữ liệu cũ, eval hằng đêm, phân loại một bảng, dịch một kho nội dung, sinh embedding cho cả tập tài liệu: không cái nào cần trả lời trong hai giây. Gửi chúng dưới dạng batch job là được **giảm thẳng 50%** để đổi lấy việc nhận kết quả bất đồng bộ.

Đây là tối ưu rẻ nhất trong danh sách vì nó không đòi sửa prompt — chỉ đổi chỗ gọi và thêm một vòng poll. Kết quả trả về không theo thứ tự, nên hãy khóa theo `custom_id` của bạn, đừng bao giờ theo vị trí.

### 3. Định tuyến theo task, đừng theo thói quen

Các tier hiện tại của Anthropic, tính trên một triệu token:

| Model | Input | Output | Hợp với |
| --- | --- | --- | --- |
| Claude Haiku 4.5 | $1 | $5 | Phân loại, trích xuất, định tuyến, gắn nhãn, tóm tắt ngắn |
| Claude Sonnet 5 | $3 | $15 | Việc phát triển hằng ngày, viết nháp, review |
| Claude Opus 5 | $5 | $25 | Suy luận khó, kiến trúc, refactor nhiều file, mọi thứ sai thì đắt |

Phần lớn đội làm ngược ở cả hai đầu: dùng model frontier để format JSON, và dùng model rẻ cho con bug concurrency đã ăn mất hai ngày. Cái đầu phí token; cái sau phí một thứ đắt hơn token.

Một quy tắc dễ dùng: **nếu bạn viết ra trước được hình dạng của câu trả lời đúng, thì tier rẻ nhất nhiều khả năng làm được.** Phân loại có không gian output biết trước. Kiến trúc thì không.

### 4. Hạ effort trước khi hạ model

Trên các model hiện tại, độ sâu suy luận là một tham số của request (`output_config.effort`, từ `low` tới `max`) và token suy nghĩ được tính tiền như mọi token output khác. Hạ một task thường ngày từ `high` xuống `low` cắt chi phí mà không đổi model — và với việc thật sự đơn giản, nó thường còn *cải thiện* kết quả nhờ bớt phần rào đón.

Hãy dùng nó trước khi hạ cấp model. Model rẻ hơn thay đổi thứ hệ thống có thể làm được; effort thấp hơn chủ yếu chỉ thay đổi mức độ nó đắn đo.

### 5. Dọn context — khoản chi không ai nhìn thấy

API là stateless: **bạn gửi lại toàn bộ hội thoại ở mỗi lượt, và bị tính tiền cho tất cả.** Một cuộc chat 200 lượt không phải là 200 request nhỏ. Nó là một request nhỏ cộng 199 request ngày càng phình. Cứ để mặc, một phiên agent dài sẽ tiêu phần lớn ngân sách chỉ để đọc lại lịch sử của chính nó.

Ba cách sửa, theo mức công sức tăng dần:

- **Mở phiên mới** khi đổi chủ đề. Miễn phí, và bị bỏ quên nhiều nhất.
- **Context editing** — xóa các tool result cũ (`clear_tool_uses_20250919`) hoặc các khối thinking khỏi lịch sử. Output tool cũ chiếm phần lớn context của một agent và gần như không còn giá trị.
- **Compaction** — tóm tắt phía server các lượt cũ khi cửa sổ đầy. Lưu ý phải gửi trả lại các khối compaction, nếu không trạng thái sẽ âm thầm reset.

### 6. Nhớ rằng output đắt gấp ~5 lần input

Ở mọi tier bên trên, output có giá khoảng gấp năm lần input. "Nói ngắn gọn" không phải sở thích văn phong, nó là một dòng trong hóa đơn. Ở đâu được thì hãy yêu cầu output có cấu trúc thay vì văn xuôi — một object JSON bốn trường tốn một phần nhỏ số token so với một đoạn văn giải thích đúng bốn trường đó, mà lại parse được.

## Cộng lại thì ra bao nhiêu

Một trợ lý hỗ trợ khách hàng: kho tri thức 20.000 token nằm trong system prompt, câu hỏi ~500 token, câu trả lời ~300 token, 10.000 request mỗi tháng.

| Cấu hình | Mỗi tháng |
| --- | --- |
| Opus 5, không cache | **~$1.100** |
| Sonnet 5, không cache | ~$660 |
| Sonnet 5 + prompt caching | ~$155 |
| Sonnet 5 + caching, một nửa lưu lượng chạy batch | **~$116** |

Phép tính của dòng thứ ba, để bạn kiểm lại: giả định lưu lượng đều và tỉ lệ cache hit 95% trên prefix 20K. Cache read là 190M token ở $0,30/M (~$57), cache write 10M ở $3,75/M (~$38), phần câu hỏi không cache 5M ở $3/M ($15), output 3M ở $15/M ($45).

**Khoảng 9 lần, mà không đổi một câu trả lời nào người dùng nhìn thấy.** Việc chọn tier model đóng góp khoảng một phần ba mức cải thiện; caching chiếm gần hết phần còn lại. Tỉ lệ đó là điển hình, và đó là lý do "chọn model rẻ hơn" là nước đi đầu tiên sai.

(Giá dùng ở đây là bảng giá công bố tiêu chuẩn. Giá giới thiệu hay khuyến mãi làm đổi con số tuyệt đối chứ không đổi tỉ lệ — các đòn bẩy nhân với nhau chứ không cộng vào nhau.)

## Thứ tự nên làm

1. **Đo trước đã.** Đếm token bằng endpoint `count_tokens` của nhà cung cấp thay vì ước lượng, và tìm xem bao nhiêu phần trăm input của bạn giống hệt nhau giữa các request. Chính con số phần trăm đó **là** dư địa caching của bạn.
2. **Cache phần prefix ổn định.** Kiểm chứng bằng `cache_read_input_tokens`. Mọi thứ khác đều nằm sau bước này.
3. **Đẩy mọi thứ không cần tương tác sang batch.** Không đổi prompt, giảm 50%.
4. **Chia lưu lượng theo task.** Tier rẻ nhất cho output có hình dạng biết trước, tier giữa cho việc thật, frontier chỉ ở chỗ sai thì tốn kém.
5. **Rồi mới chỉnh effort và cắt context.**
6. **Đặt việc học, prototype và code công khai lên free tier** — và giữ mọi thứ còn lại ở ngoài.

Một lưu ý sòng phẳng cho bước 6: đừng để việc săn free tier tốn nhiều giờ kỹ thuật hơn số tiền nó tiết kiệm. Đấu dây một router đa nhà cung cấp để tiết kiệm $5 mỗi tháng là một vụ đổi chác tệ ở mọi mức lương. Free tier dành cho phần việc mà đằng nào bạn cũng không trả đồng nào, vì nếu phải trả thì bạn đã không làm.

## Câu hỏi thường gặp

**Free tier nào tốt nhất?**
Tùy hình dạng request của bạn. Cerebras có lượng token theo ngày cao nhất nhưng trần theo phút thấp nhất (5 RPM / 30K TPM), hợp với ít request, nhỏ và nhanh. Groq với 30 RPM và 200K TPD hợp với workload nói nhiều hơn. Điểm hấp dẫn của OpenRouter là độ phủ model, nhưng 50 request/ngày khi chưa mua credit là rất chật.

**Gộp nhiều free tier có vi phạm điều khoản không?**
Bản thân việc gộp không đương nhiên là vi phạm, nhưng điều khoản của từng tài khoản vẫn ràng buộc bạn riêng lẻ, và free tier được tính cho một ứng dụng chứ không phải một router tỏa nhánh. Hãy đọc điều khoản từng bên; chính dự án gộp cũng ghi rõ trách nhiệm đó thuộc về bạn.

**Prompt caching có làm đổi câu trả lời của model không?**
Không. Nó đổi cách phần input được tính tiền và tốc độ xử lý, không đổi thứ model nhìn thấy. Một lượt cache hit và một lượt cache miss đưa tới model nội dung y hệt nhau.

**Một entry cache sống được bao lâu?**
Mặc định năm phút, được làm mới ở mỗi lần trúng, và có tùy chọn một giờ. Với lưu lượng đều thì mặc định là đủ; với lưu lượng giật cục — một job mỗi 20 phút — bạn trả phí ghi mỗi lần, và đó là lý do tỉ lệ 95% ở trên là một giả định chứ không phải một lời hứa.

**Batch API chậm tới mức đáng ngại không?**
Nó bất đồng bộ theo thiết kế, nên không hợp với bất cứ thứ gì có người ngồi chờ. Với việc chạy đêm và việc nền, độ trễ đó vô hình còn 50% thì không.

**Có nên tự host model mã nguồn mở để cắt chi phí không?**
Chỉ khi lưu lượng cao và đều. Dưới ngưỡng đó, tiền thuê GPU cộng thời gian kỹ thuật của chính bạn vượt giá API, và bạn ôm thêm phần vận hành. Các free tier bên trên chính là cách rẻ để dùng model open-weights mà không phải ôm vận hành.

---

*Rate limit, giá và danh sách model miễn phí trong bài là theo công bố của từng nhà cung cấp tại thời điểm viết và thay đổi thường xuyên. Mọi con số đều có link tới nguồn — hãy kiểm lại trước khi ra quyết định ngân sách. Phần về FreeLLMAPI mô tả đúng những gì dự án tự công bố, bao gồm cả lưu ý của chính họ rằng nó dành cho thử nghiệm cá nhân chứ không phải production.*
