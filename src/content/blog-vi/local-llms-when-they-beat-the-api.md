---
title: "Chạy model ngay trên máy mình: bốn trường hợp local thật sự thắng API"
description: "Local LLM không phải thứ thay thế API frontier, cũng không phải đồ chơi. Có đúng bốn loại workload mà tự chạy weight là câu trả lời kỹ thuật đúng — và rất nhiều phép tính bạn làm được trước khi tải bất cứ thứ gì."
seoDescription: "Khi nào local LLM thắng API: ràng buộc dữ liệu, phân loại số lượng lớn, làm offline, vòng lặp độ trễ thấp — kèm cách ước lượng VRAM cho model."
keywords:
  - local llm và api
  - chạy llm trên máy cá nhân
  - quantization 4-bit llm
  - ước lượng vram cho llm
  - ollama llama.cpp mlx
  - băng thông bộ nhớ sinh token
category: "Phân tích"
topic: "AI Engineering"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-22"
emoji: "🖥️"
tags: ["AI", "LLM", "Local Inference", "Hiệu năng", "Công cụ lập trình"]
sources:
  - name: "llama.cpp — inference engine và bộ công cụ GGUF"
    url: "https://github.com/ggml-org/llama.cpp"
  - name: "Ollama"
    url: "https://github.com/ollama/ollama"
  - name: "MLX — array framework cho Apple silicon"
    url: "https://github.com/ml-explore/mlx"
  - name: "mlx-lm — bộ công cụ LLM trên MLX"
    url: "https://github.com/ml-explore/mlx-lm"
  - name: "LM Studio"
    url: "https://lmstudio.ai/"
  - name: "vLLM — serving engine cho throughput cao"
    url: "https://github.com/vllm-project/vllm"
related:
  - slug: "cutting-ai-costs-free-tiers-caching-and-routing"
    title: "Dùng AI mà không đốt tiền: free tier, caching và định tuyến model"
  - slug: "free-ai-coding-agents-opencode-safely"
    title: "AI coding agent miễn phí: dùng model free của OpenCode sao cho khỏi hối hận"
draft: false
---

Có hai câu trả lời rất tự tin cho câu hỏi "tôi có nên chạy model ở local không", và cả hai đều sai. Một phe bảo model local giờ đủ tốt rồi, trả tiền cho API là phí. Phe kia bảo thứ gì nhét vừa cái laptop thì cũng chỉ là đồ chơi, đừng phí buổi tối.

Câu trả lời có ích là: "local hay API" vốn không phải câu hỏi về model. Nó là câu hỏi về một workload cụ thể, và xoay quanh bốn thuộc tính của workload đó — dữ liệu có được phép rời khỏi máy không, mỗi tháng bạn đẩy qua bao nhiêu token, có mạng hay không, và một vòng round trip ăn mất bao nhiêu phần trong ngân sách độ trễ. Nếu không thuộc tính nào trong bốn cái đó ràng buộc bạn, gần như chắc chắn API là lựa chọn đúng, và lý do trung thực là năng lực: với reasoning thật sự khó, model frontier bạn đi thuê vẫn thắng model đã quantise bạn sở hữu.

Bài này nói phần nhượng bộ trước, rồi tới bốn trường hợp mà local không phải là sự thỏa hiệp mà là đáp án đúng, rồi tới phần cơ chế: làm sao biết model có vừa bộ nhớ không trước khi tải 40 GB, quantisation 4-bit thật sự lấy đi cái gì, và vì sao thứ giới hạn tốc độ sinh token gần như không bao giờ là thứ người ta tưởng.

## Nhượng bộ trước: reasoning khó vẫn thuộc về API

Bắt đầu từ đây, vì bỏ qua đoạn này thì mọi thứ phía sau đọc như biện hộ.

Những model bạn chạy được trên một máy tiêu dùng phần lớn là model nhỏ. Khoảng cách giữa chúng và model frontier không đồng đều giữa các tác vụ — nó hẹp ở việc định dạng, trích xuất, phân loại, tóm tắt văn bản ngắn, code completion thường ngày; và giãn rất rộng ở reasoning nhiều bước, tổng hợp trên context dài, kiến thức chuyên ngành hiếm, và các vòng lặp agent nơi một bước sai làm hỏng hai mươi bước sau.

Cái cuối cần nhấn mạnh, vì đó là chỗ local làm người ta thất vọng nhất mà lại ít ai lường trước. Một agent đọc file, quyết định, sửa, đọc lại, rồi quyết định tiếp sẽ tự cộng dồn lỗi của chính nó. Model đúng 90% mỗi bước không có nghĩa là đúng 90% trên một tác vụ mười bước. Đó là lý do câu "tôi thử model local làm coding agent và nó cứ chạy vòng vòng" phổ biến đến vậy — đó không phải lỗi tooling, và prompt hay hơn cũng không cứu được.

Nên mặc định vẫn là: thuê model lớn. Bốn trường hợp dưới đây là những chỗ mặc định đó sai.

## Trường hợp 1 — dữ liệu về mặt pháp lý không được rời khỏi máy

Đây là trường hợp quyết định phần lớn các triển khai doanh nghiệp, và nó là một câu hỏi hợp đồng khoác áo kỹ thuật.

Nếu bạn xử lý hồ sơ bệnh án, tài liệu tố tụng, số liệu tài chính chưa công bố, source code của khách hàng dưới NDA, hay bất cứ thứ gì nằm trong một biên giới tuân thủ cấm bên thứ ba xử lý, thì model phải đi tới chỗ dữ liệu. Không phải vì nhà cung cấp API không đáng tin, mà vì "chúng tôi gửi cho bên thứ ba và họ hứa không giữ lại" là một câu phải có người ký tên, và đôi khi không ai chịu ký.

Hãy xác định chính xác bạn đang gặp phiên bản nào của ràng buộc này, vì đáp án khác nhau:

- **"Tuyệt đối không cho bên thứ ba xử lý."** Air-gapped, hoặc bị cấm rõ ràng. Local là đáp án duy nhất.
- **"Không train trên dữ liệu của chúng tôi, không lưu trữ."** Các nhà cung cấp lớn đều có điều khoản zero-retention và hợp đồng doanh nghiệp; triển khai y tế ở Mỹ thường chạy dưới một BAA đã ký. Đây là bài toán mua sắm, không phải bài toán kỹ thuật.
- **"Dữ liệu phải nằm trong một khu vực pháp lý cụ thể."** Endpoint ghim theo region là có thật. Kiểm tra trước khi bạn định xây trung tâm dữ liệu.
- **"Quý này pháp chế không duyệt thêm cái gì mới đâu."** Cực kỳ phổ biến, hiếm khi nói ra thành lời, và local đúng là đường nhanh — một model chạy trên phần cứng bạn đã có thường dễ duyệt hơn một nhà xử lý dữ liệu mới.

Hệ quả kỹ thuật của trường hợp 1 là bạn phải *hoang tưởng về egress*, chứ không chỉ về model. Một model local nằm sau một app có gửi telemetry, gửi crash report chứa nội dung prompt, hay log sang một dịch vụ observability hosted thì vẫn chưa giải quyết được gì. Nếu yêu cầu là "không gì được rời khỏi máy", hãy kiểm chứng ở tầng network, đừng kiểm chứng trên sơ đồ kiến trúc.

## Trường hợp 2 — số lượng lớn, khi giá mỗi token là toàn bộ chi phí

Trường hợp thứ hai là bài toán số học, và nó chỉ đúng với một hình dạng workload hẹp nhưng có thật: cực nhiều lệnh gọi nhỏ, giống nhau, độ khó thấp. Phân loại ticket hỗ trợ. Gắn tag cho catalogue. Định tuyến email vào. Trích ba trường từ một tài liệu. Lọc bớt luồng dữ liệu trước khi model đắt tiền nhìn tới.

Hình dạng này hợp với local vì một model nhỏ thật sự đủ dùng, và ở khối lượng lớn thì giá mỗi token thôi làm tròn thành số không. Hãy tính bằng số liệu của chính bạn:

```
số item mỗi tháng        × token mỗi item = token mỗi tháng
token mỗi tháng ÷ 1e6    × giá mỗi Mtok   = chi phí API hằng tháng
```

Năm triệu ticket mỗi tháng, mỗi cái ~600 input token, là 3 tỷ input token. Kể cả ở mức giả định $0.10 cho mỗi triệu input token — rẻ, ở phân khúc model nhỏ — thì vẫn là $300 mỗi tháng, tháng nào cũng vậy, cho công việc mà một cái máy mua một lần có thể nghiền xong qua đêm. Hạ khối lượng xuống năm mươi nghìn item thì cùng phép tính đó ra $3, và bạn tuyệt đối không nên mua GPU vì chuyện đó.

Có hai điều làm trường hợp này kém hiển nhiên hơn vẻ ngoài, và cả hai đều bất lợi cho local:

**Ở quy mô nhỏ, thời gian kỹ sư của bạn mới là khoản lớn nhất.** Một cuối tuần dựng hệ thống, cộng với việc phải nuôi một inference server về sau, đáng giá nhiều năm hóa đơn $300/tháng. Điểm hòa vốn xa hơn nhiều so với những gì phép tính token gợi ý.

**Giá batch đã tồn tại sẵn.** Endpoint batch bất đồng bộ của các nhà cung cấp lớn được giảm giá đáng kể, và phân loại số lượng lớn đúng là workload chúng sinh ra để phục vụ. Hãy so với giá batch, đừng so với giá interactive, nếu không bạn sẽ tự thuyết phục mình mua phần cứng không cần thiết.

Khi local thắng ở khối lượng lớn, hãy thắng cho đúng cách: dùng serving engine sinh ra cho throughput chứ đừng dùng app chat. [vLLM](https://github.com/vllm-project/vllm) với continuous batching giữ GPU luôn bận theo cách mà một công cụ chạy đơn luồng không bao giờ làm được, và throughput — không phải độ trễ — mới là con số quan trọng khi chẳng có ai ngồi chờ.

## Trường hợp 3 — không có mạng, hoặc mạng không đáng tin

Cơ sở air-gapped, tàu biển, máy bay, hầm mỏ, phòng khám vùng sâu, một xưởng sản xuất nhiễu sóng, một cái laptop trên chuyến bay. Trường hợp này không hào nhoáng nhưng dứt khoát: một tính năng cần gọi API là một tính năng không tồn tại khi đường truyền chết.

Có một phiên bản mềm hơn của cùng lập luận này, áp dụng cho cả những team có mạng rất tốt. Weight local là thứ được *ghim*. Model bạn đã kiểm thử chính là model bạn sẽ chạy sau mười tám tháng nữa, với đúng những nét kỳ quặc và đúng những kiểu hỏng đó, vì nó là một file nằm trên đĩa. Model hosted có thể được cập nhật dưới chân bạn, bị khai tử theo lịch công bố, hoặc bị rate-limit trong cơn bùng traffic của người khác. Nếu bạn đã bỏ nhiều tháng tinh chỉnh prompt và dựng bộ eval quanh hành vi của một model, sự ổn định đó có giá trị thật — và đó là lợi thế duy nhất của local chẳng liên quan gì tới phần cứng.

Mặt trái cũng đúng và đáng nói ra: weight bị ghim thì không tự khá lên. Bạn thừa hưởng vĩnh viễn mốc kiến thức của model đó, và nâng cấp là một dự án migration chứ không phải đổi một chuỗi version.

## Trường hợp 4 — vòng lặp mà round trip chính là ngân sách độ trễ

Trường hợp thứ tư nói về vật lý của đường truyền, không phải giá của nó.

Bất kỳ lệnh gọi API nào cũng mang theo một sàn: DNS, TLS, bản thân round trip, hàng đợi ở phía nhà cung cấp, rồi mới tới time-to-first-token. Với giao diện chat, cái sàn đó vô hình. Với một tương tác xảy ra *giữa hai lần gõ phím*, nó là toàn bộ ngân sách:

- **Code completion / fill-in-the-middle.** Gợi ý trở nên vô dụng nếu nó đến sau khi bạn đã tự gõ xong token tiếp theo.
- **Transcription trên thiết bị.** Streaming giọng nói kèm bản ghi tạm hiện dần; `whisper.cpp` là con đường đã mòn ở đây, và nó chạy được trên điện thoại.
- **Các affordance trên UI** — viết lại tại chỗ, chọn thông minh, dịch inline — nơi một cái spinner biến tính năng dễ thương thành tính năng gây khó chịu.

Local thắng hai lần ở đây. Nó bỏ được round trip, và nó thay đổi kinh tế học của việc chạy *đầu cơ*: khi một lệnh gọi chỉ tốn vài mili giây của một GPU đang rảnh, bạn có thể chạy nó ở mỗi lần gõ phím rồi vứt đi 90% kết quả. Bạn sẽ chẳng bao giờ làm vậy với một API tính tiền, nghĩa là có những tương tác chỉ thiết kế được ở local.

Điều cần lưu ý: "local" không tự động có nghĩa là "nhanh". Một model đang swap ra đĩa, hay một model mà token đầu tiên phải xếp hàng sau 6.000 token prompt đang được xử lý lại từ đầu, sẽ chậm hơn một API được cấp phát tử tế. Điều đó dẫn ta tới phần số học.

## Có vừa không, và cái gì đặt trần tốc độ?

Hai con số quyết định một model có dùng được trên máy bạn hay không, và bạn tính được cả hai trước khi tải bất cứ thứ gì.

### Bộ nhớ: tham số × số bit, cộng KV cache

Weight chiếm phần lớn. Quy tắc ước lượng là số byte trên mỗi tham số nhân với số tham số, trong đó số byte trên mỗi tham số do quantisation quyết định:

| Độ chính xác | Byte / tham số | ≈ GB cho 1B tham số | Model 7B | Model 70B |
| --- | --- | --- | --- | --- |
| FP16 / BF16 | 2 | ~2.0 | ~14 GB | ~140 GB |
| 8-bit | 1 | ~1.05 | ~7.5 GB | ~75 GB |
| 4-bit (GGUF thực tế) | ~0.55–0.65 | ~0.6 | ~4.5 GB | ~40 GB |

Dòng 4-bit cao hơn con số ngây thơ 0.5 byte vì một lý do đáng biết: các định dạng 4-bit thực tế không lưu mọi tensor ở 4 bit. Embedding và một số attention projection được giữ rộng hơn, và mỗi block weight còn mang theo scale và offset riêng. Số bit hiệu dụng trên mỗi weight rơi vào khoảng 4.5–5, nên file "4-bit" luôn lớn hơn một nửa file 8-bit tương ứng.

Rồi cộng thêm **KV cache**, thứ ai cũng quên và lại tăng tuyến tính theo context:

```
kv_bytes = 2 × layers × kv_heads × head_dim × context_length × bytes_per_element
```

Một model có 32 layer, 8 KV head (grouped-query attention), head dimension 128, ở 8.192 token với FP16:

```
2 × 32 × 8 × 128 × 8192 × 2 = 1,073,741,824 byte  ≈ 1 GB
```

Hai điều rút ra từ đó. Nhân đôi context là nhân đôi số GB kia. Và grouped-query attention chính là lý do nó là 1 GB chứ không phải 4 — cùng model đó với 32 KV head thay vì 8 sẽ cần gấp bốn lần. Nếu bạn đang thiếu bộ nhớ, thu nhỏ context thường lợi hơn thu nhỏ model, và llama.cpp còn quantise được chính cái cache (`--cache-type-k q8_0`) để cắt thêm nữa.

Ước lượng đại khái: **weight + KV cache + ~1 GB overhead runtime**, và chừa dư. Trên GPU rời, vượt VRAM nghĩa là các layer tràn sang RAM hệ thống qua PCIe và throughput sụp đổ — nó không báo lỗi, nó chỉ trở nên không dùng được, và như vậy còn tệ hơn. Trên Apple silicon bộ nhớ là unified, nhưng macOS vẫn giới hạn phần bộ nhớ mà GPU được phép ghim (mặc định khoảng ba phần tư tổng RAM; `sysctl iogpu.wired_limit_mb` là cái núm, và đó là thiết lập hệ thống nên hãy hiểu rõ trước khi đổi).

### Tốc độ: mỗi token sinh ra đều phải đọc lại toàn bộ model

Đây là phần đảo lộn trực giác của phần lớn mọi người. Sinh một token ở batch size 1 đòi hỏi đọc **toàn bộ weight của model** ra khỏi bộ nhớ, để làm cái mà về mặt toán học chỉ là một chồng phép nhân ma trận–vector. Phần tính toán không đáng kể; lưu lượng bộ nhớ mới đáng kể. Nên cái trần là:

```
tokens/giây tối đa ≈ băng thông bộ nhớ (GB/s) ÷ kích thước model trong bộ nhớ (GB)
```

Lấy con số băng thông từ chính bảng thông số phần cứng của bạn rồi chia. Đó là trần, không phải dự đoán — throughput thực tế thấp hơn đáng kể — nhưng nó cho bạn thấy ngay hình dạng của câu trả lời, và nó giải thích vì sao quantise một model lại làm nó nhanh hơn: bạn giảm một nửa số byte phải đi qua bus cho mỗi token, chứ không giảm phần số học.

Xử lý prompt lại hành xử hoàn toàn khác. Toàn bộ token của prompt được xử lý song song, nên ma trận–vector thành ma trận–ma trận và workload trở thành **compute-bound**. So sánh hai pha với model 7B ở 4-bit (~4.5 GB), dùng ước lượng chuẩn ~2 FLOP cho mỗi tham số mỗi token:

| Pha | Prompt 8.000 token | Sinh 500 token |
| --- | --- | --- |
| Tính toán | ~112 TFLOP | ~7 TFLOP |
| Đọc bộ nhớ | ~4.5 GB (một lần) | ~2.250 GB (4.5 GB × 500) |

Prompt tốn gấp mười sáu lần tính toán; phần sinh token tốn gấp năm trăm lần lưu lượng bộ nhớ. Chỉ một cái bảng đó giải thích được phần lớn những lời than phiền về hiệu năng local LLM. Nó là lý do một system prompt dài gây đau ở local hơn hẳn so với ở API (nơi có batching luôn ấm và thường có cả prompt caching để phân bổ chi phí đó), lý do "time to first token" và "token mỗi giây" phải đo tách bạch, và lý do một cỗ máy tính toán khiêm tốn nhưng băng thông rộng vẫn sinh token thoải mái trong khi bò từng bước qua một tài liệu dài.

Hãy đo thay vì đoán: `llama-bench` trong repo llama.cpp báo tốc độ xử lý prompt và tốc độ sinh token thành hai con số riêng, trên phần cứng của bạn, với mức quantisation của bạn.

## 4-bit thật sự lấy đi cái gì

Quantisation là vé vào cửa của inference local, và cách mô tả quen thuộc — "gần như không mất chất lượng" — đúng theo kiểu che mất chỗ mà chất lượng thật sự rơi.

- **8-bit gần như không mất gì** ở mức thực dụng, với hầu hết tác vụ. Nếu vừa ở 8-bit, hãy chạy 8-bit và đừng nghĩ nữa.
- **4-bit là chỗ có sự đánh đổi thú vị.** Các chỉ số tổng hợp như perplexity nhúc nhích rất ít, và chính vì thế perplexity là cách đánh giá gây hiểu lầm. Suy giảm tập trung ở: reasoning nhiều bước, các tác vụ đòi đầu ra chính xác như code phải biên dịch được, khả năng nhớ sự kiện hiếm và danh từ riêng, hiệu năng ngoài tiếng Anh, và hành vi ở cuối một context dài. Chat, tóm tắt và phân loại thì trụ khá vững.
- **Dưới 4-bit, suy giảm hết tinh tế.** Quant 3-bit và 2-bit tồn tại và có chỗ dùng khi model vốn không vừa nổi, nhưng hãy coi chúng là một model khác chứ không phải một model rẻ hơn.

Quy tắc hay được lặp lại là: với cùng một ngân sách bộ nhớ, model lớn hơn ở 4-bit thắng model nhỏ hơn ở 8-bit. Đó là một mặc định hợp lý, và cũng đúng là loại tuyên bố bạn nên tự kiểm chứng trên tác vụ của mình thay vì tin ngay — vì ý của gạch đầu dòng phía trên chính là: chỗ mà model 4-bit suy giảm phụ thuộc vào việc bạn bắt nó làm gì.

Những tên định dạng bạn sẽ gặp thật: k-quant của **GGUF** (`Q4_K_M` là mặc định phổ biến, `Q5_K_M` và `Q6_K` khi còn dư chỗ), thường được dựng kèm importance matrix để dữ liệu hiệu chỉnh quyết định weight nào giữ độ chính xác; **AWQ** và **GPTQ** ở phía serving trên GPU; và các định dạng 4-bit, 8-bit riêng của MLX trên Apple silicon. Chúng không thay thế lẫn nhau được — định dạng đi theo runtime bạn chọn.

## Bộ công cụ, và mỗi thứ thật sự dùng để làm gì

Bốn thứ, với vai trò thật và phần lớn không chồng lấn.

| Công cụ | Nó là gì | Dùng khi |
| --- | --- | --- |
| [llama.cpp](https://github.com/ggml-org/llama.cpp) | Engine C/C++ nằm dưới phần lớn hệ sinh thái này. GGUF, CPU + offload một phần lên GPU, `llama-server`, `llama-bench` | Bạn muốn kiểm soát: context size chính xác, offload theo layer, quantise cache, hoặc đang benchmark |
| [Ollama](https://github.com/ollama/ollama) | Trình quản lý model kèm daemon, cài một dòng, kéo model theo tên | Bạn muốn chạy được trong năm phút, hoặc muốn nhiều app trên máy dùng chung một model đang chạy |
| [LM Studio](https://lmstudio.ai/) | GUI desktop bọc GGUF và MLX, có chế độ server local | Bạn đang đánh giá model bằng cảm nhận, hoặc bạn không phải người của terminal |
| [MLX](https://github.com/ml-explore/mlx) / [mlx-lm](https://github.com/ml-explore/mlx-lm) | Array framework của Apple và bộ công cụ LLM của nó, làm cho unified memory | Bạn ở trên Apple silicon và muốn runtime thiết kế riêng cho kiến trúc bộ nhớ đó |

Đủ để có một model trả lời trên localhost:

```bash
# Ollama: pull and chat
ollama pull <model-name>
ollama run <model-name>

# llama.cpp: serve a GGUF with an explicit context and full GPU offload
llama-server -m ./model.Q4_K_M.gguf -c 8192 -ngl 99

# Apple silicon via mlx-lm
pip install mlx-lm
mlx_lm.generate --model <mlx-community/model-id> --prompt "Summarise this:"
```

Cả Ollama lẫn `llama-server` đều phơi ra một bề mặt tương thích OpenAI, và đó là lý do thực dụng để chọn chúng cho bất cứ thứ gì bạn tích hợp: code client giống hệt code gọi API, còn chuyển qua lại giữa local và hosted chỉ là đổi base URL. Đó cũng là con đường migration tỉnh táo: dựng trên API trước, rồi chuyển phần nào đủ điều kiện.

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")

resp = client.chat.completions.create(
    model="<model-name>",
    messages=[
        {"role": "system", "content": "Reply with exactly one of: BILLING, BUG, FEATURE, OTHER."},
        {"role": "user", "content": ticket_text},
    ],
    temperature=0,
    max_tokens=4,
)
```

Đoạn đó chính là trường hợp 2 thu nhỏ: một việc hẹp, đầu ra bị ràng buộc, `temperature=0`, và `max_tokens` bé xíu để pha sinh token vốn bị chặn bởi bộ nhớ gần như không phải chạy. Hãy định tuyến những ticket khó sang model frontier và để model local xử 95% còn lại. Lai ghép là câu trả lời đúng thường xuyên hơn nhiều so với bất kỳ lập trường thuần túy nào.

## FAQ

**Model local có đủ tốt để thay coding assistant của tôi không?**
Với completion inline thì thường là có — đó là tác vụ context ngắn, nhạy độ trễ, độ khó thấp, đúng khẩu vị của local. Với một agent nhiều bước biết sửa file và chạy test thì thường là không, vì tỉ lệ lỗi mỗi bước cộng dồn qua một chuỗi dài. Tách hai việc đó cho hai model là cách bố trí bình thường và hợp lý.

**Tôi thật sự cần bao nhiêu RAM?**
Hãy tính thay vì đoán: weight (≈0.6 GB cho mỗi tỷ tham số ở 4-bit) cộng KV cache (theo công thức ở trên, tăng theo độ dài context) cộng khoảng một gigabyte overhead, rồi chừa dư. Trên GPU rời, vượt VRAM không báo lỗi — nó tràn sang bộ nhớ hệ thống và throughput sụp đổ, một kiểu hỏng khó hiểu hơn nhiều.

**Quantisation làm model nhanh hơn, hay chỉ nhỏ hơn?**
Cả hai, và vì cùng một lý do. Sinh token bị giới hạn bởi số byte phải đọc từ bộ nhớ cho mỗi token, nên giảm một nửa kích thước model thì gần như nhân đôi cái trần tốc độ sinh. Nó không giúp nhiều cho pha xử lý prompt, vì pha đó bị chặn bởi tính toán và việc giải quantise còn thêm chút việc.

**Nếu dữ liệu của tôi nhạy cảm, dùng gói API doanh nghiệp không đủ sao?**
Rất thường là đủ — điều khoản zero-retention, hợp đồng đã ký và endpoint ghim theo region bao được rất nhiều yêu cầu thực tế, và chúng đỡ việc hơn là tự nuôi inference. Local trở nên bắt buộc khi ràng buộc là tuyệt đối (không cho bên thứ ba xử lý, hoặc không có mạng), hoặc khi ký được cái hợp đồng kia còn lâu hơn dựng một server.

**Mua GPU có rẻ hơn trả tiền API không?**
Chỉ khi khối lượng lớn và kéo dài, trên loại việc mà model nhỏ làm được. Hãy nhân số token hằng tháng với một mức giá model nhỏ thực tế — và so với giá endpoint batch, đừng so với giá interactive — trước khi đem ra so với phần cứng cộng điện cộng thời gian của chính bạn. Với phần lớn team, câu trả lời trung thực là API rẻ hơn, và lý do để đi local nằm ở ba trường hợp còn lại.

---

*Phần số học ở đây — dung lượng bộ nhớ, kích thước KV cache, cái trần do băng thông đặt ra cho việc sinh token — là máy móc, và bạn nên tính lại bằng cấu hình model của chính mình thay vì tin vào các con số minh họa. Những nhận định về chỗ quantisation 4-bit suy giảm, và về chỗ giao nhau giữa local và API, là cách tôi đọc các đánh đổi chứ không phải số đo; hãy benchmark trên tác vụ của bạn. Cờ dòng lệnh, định dạng model và điều khoản nhà cung cấp đều thay đổi, nên hãy kiểm tra các repository được dẫn và điều khoản hiện hành của từng nhà cung cấp trước khi chốt thiết kế.*
