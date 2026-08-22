---
title: "Fine-tune, RAG hay chỉ cần prompt tốt hơn: một quyết định bạn bảo vệ được"
description: "Ba thứ này hay bị đem so sánh như thể chúng giải cùng một bài toán. Không phải. Prompt đổi chỉ dẫn, retrieval đổi kiến thức, fine-tuning đổi hành vi — ánh xạ triệu chứng đúng tầng là hết tranh cãi."
seoDescription: "Khi nào nên fine-tune, khi nào dùng RAG, khi nào chỉ cần sửa prompt: bản đồ triệu chứng, chi phí thật của fine-tuning, chỗ đứng của LoRA và một bảng quyết định."
keywords:
  - fine tuning hay rag
  - khi nào nên fine tune llm
  - rag là gì
  - lora fine tuning chi phí
  - llm sai định dạng output
  - dữ liệu huấn luyện fine tune
category: "Phân tích"
topic: "AI Engineering"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-22"
emoji: "🎛️"
tags: ["AI", "LLM", "RAG", "Fine-tuning", "Kiến trúc"]
sources:
  - name: "OpenAI — Fine-tuning guide"
    url: "https://platform.openai.com/docs/guides/fine-tuning"
  - name: "OpenAI — Structured Outputs"
    url: "https://platform.openai.com/docs/guides/structured-outputs"
  - name: "Hugging Face PEFT — parameter-efficient fine-tuning"
    url: "https://huggingface.co/docs/peft/index"
  - name: "LoRA: Low-Rank Adaptation of Large Language Models"
    url: "https://arxiv.org/abs/2106.09685"
  - name: "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks"
    url: "https://arxiv.org/abs/2005.11401"
related:
  - slug: "what-the-research-says-about-prompt-engineering"
    title: "Nghiên cứu thật sự nói gì về prompt engineering — kiểm chứng 5 tuyên bố đang lan truyền"
  - slug: "cutting-ai-costs-free-tiers-caching-and-routing"
    title: "Dùng AI mà không đốt tiền: free tier, caching và định tuyến model"
draft: false
---

Cứ vài tuần lại có người chiếu đúng cái slide đó lên: ba cái hộp ghi **Prompt Engineering**, **RAG** và **Fine-tuning**, kèm mũi tên ngụ ý rằng bài toán càng nghiêm túc thì bạn càng "lên hạng" từ trái sang phải. Rồi cả phòng cãi nhau xem chọn cái nào, như thể đó là ba nhà thầu đang đấu cùng một gói việc.

Chúng không tranh nhau cùng một gói việc. Chúng tác động vào ba phần khác nhau của hệ thống, và một khi bạn gọi tên được phần nào đang hỏng, cuộc tranh luận thường kết thúc trong khoảng một phút:

- **Prompt đổi phần chỉ dẫn.** Model đang được yêu cầu làm gì, dưới những ràng buộc nào.
- **Retrieval đổi phần kiến thức.** Những dữ kiện nào thật sự có mặt trong context window lúc model trả lời.
- **Fine-tuning đổi phần hành vi.** Model làm gì theo mặc định, dưới dạng nào, khi chỉ dẫn đã hết.

Gần như mọi quyết định sai trong mảng này đều đến từ việc đem một tầng đi chữa vấn đề nằm ở tầng khác. Fine-tune một model để nó "biết" danh mục sản phẩm của bạn là ca kinh điển — bỏ ra sáu tuần để có một model tự tin nói sai giá của tuần trước, và bạn thậm chí không biết đổ lỗi cho trọng số nào. Dựng cả một pipeline retrieval trước một model mà vấn đề thật sự chỉ là nó viết sáu đoạn trong khi bạn muốn một đoạn, cũng là đúng sai lầm đó theo chiều ngược lại.

Nên đừng bắt đầu từ kỹ thuật. Hãy bắt đầu từ triệu chứng.

## Bốn tầng, không phải ba

Cái slide kia còn thiếu một hộp. Có bốn thứ bạn có thể thay đổi, và chúng khác nhau chủ yếu ở chỗ: một *thay đổi* tốn bao nhiêu khi hệ thống đã chạy production.

| Tầng | Thay đổi cái gì | Thay đổi bằng cách | Chi phí cho một lần đổi |
| --- | --- | --- | --- |
| **Prompt** | Chỉ dẫn và ràng buộc | Sửa một chuỗi string | Vài phút. Quay lại được. |
| **Schema / tools** | Output nào là *khả dĩ* về mặt cấu trúc | Một JSON schema, một tool definition | Vài giờ. Quay lại được. |
| **Retrieval** | Dữ kiện nào đang nằm trước mặt model | Nạp hoặc index lại một tài liệu | Vài phút mỗi tài liệu, một khi pipeline đã có |
| **Fine-tuning** | Hành vi và hình thức mặc định của model | Một lần train trên dữ liệu đã gán nhãn | Vài ngày đến vài tuần. Thêm một artefact phải nuôi. |

Tầng ở giữa là tầng các team hay bỏ qua, và nó lại chính là tầng giải quyết than phiền phổ biến nhất. "Nó không giữ đúng định dạng output" thường không phải vấn đề huấn luyện — đó là vấn đề decoding, và constrained decoding xử lý nó ở mức cấu trúc chứ không phải mức xác suất. Structured Outputs của OpenAI với `strict: true`, hoặc tính năng constrained generation tương đương trong stack bạn dùng, khiến một response sai định dạng trở thành *bất khả thi* chứ không chỉ là "ít khi xảy ra". Không cần dataset nào cả.

## Bắt đầu từ triệu chứng, đừng bắt đầu từ kỹ thuật

Đây là bản đồ tôi thật sự dùng. Hãy đọc cột trái như một câu ai đó vừa nói ra miệng trong cuộc họp.

| Bạn quan sát thấy | Thứ thật sự đang thiếu | Nên dùng |
| --- | --- | --- |
| "Nó không biết sản phẩm / bảng giá / chính sách của mình" | Kiến thức | Retrieval |
| "Nó bịa ra một internal API không tồn tại" | Kiến thức, cộng với quyền được từ chối | Retrieval + một chỉ dẫn rõ ràng "không biết thì nói không biết" |
| "Nó trả lời cũ — tài liệu đã sửa hôm thứ Ba" | Độ tươi của kiến thức | Retrieval. Tuyệt đối không fine-tuning. |
| "Nó dài dòng quá" / "sai giọng văn" | Chỉ dẫn | Prompt |
| "Nó tuân thủ năm trong sáu quy tắc của tôi" | Quá tải chỉ dẫn | Cấu trúc lại prompt: tách thành hai lần gọi, hoặc đẩy một quy tắc xuống schema |
| "Cứ năm mươi lần gọi thì có một lần JSON hỏng" | Bảo đảm về cấu trúc | Schema / constrained decoding |
| "Đúng, nhưng nó không giống giọng của team support mình" | Hình thức và phong cách | Fine-tuning (sau khi few-shot đã thất bại) |
| "Đúng ở ca bình thường, sai ở mấy ca kỳ quặc của mình" | Hành vi riêng của tác vụ | Few-shot trước, rồi mới fine-tuning |
| "Chạy được, nhưng system prompt tốn hàng ngàn token mỗi lần gọi" | Chi phí và latency | Prompt caching trước, rồi mới fine-tuning |
| "Câu trả lời khác nhau giữa những user không được thấy cùng dữ liệu" | Phân quyền truy cập | Retrieval. Fine-tuning hoàn toàn không làm được việc này. |

Có hai dòng trong bảng đó là chịu lực, và cũng là hai dòng người ta hay lướt qua.

**Độ tươi và phân quyền là hai điều kiện loại trực tiếp fine-tuning.** Nếu một dữ kiện có thể thay đổi, hoặc nếu những user khác nhau được phép thấy những dữ kiện khác nhau, thì nó không thể nằm trong trọng số. Một index retrieval có các dòng bạn cập nhật, xoá và lọc theo quyền được. Trọng số không có bất kỳ khả năng nào trong số đó. Không có `DELETE` cho một dữ kiện mà model đã hấp thụ khi train, và cũng không có `WHERE tenant_id = ?`.

## Prompt là tầng duy nhất có nút undo trong ngày

Luôn bắt đầu ở đây, không phải vì prompt mạnh, mà vì ở đây *sai thì rẻ*. Một thay đổi prompt đi kèm một commit, được review như code, và revert trong vài giây. Không tầng nào khác trong danh sách này làm được vậy.

Chỗ prompt thật sự hết đường:

- **Nó không cài được dữ kiện mà model vốn không có.** Dán cả cuốn cẩm nang vào prompt chính là retrieval làm bằng tay — và là retrieval làm dở, vì bạn trả tiền cho toàn bộ cuốn cẩm nang ở mọi lần gọi.
- **Mức tuân thủ tụt dần khi ràng buộc chồng lên nhau.** Một prompt với mười hai quy tắc đồng thời không đáng tin gấp mười hai lần một prompt có một quy tắc. Khi bạn thấy mình đang viết quy tắc thứ mười bốn, cách sửa thường là tách công việc thành hai lần gọi, hoặc hạ một quy tắc xuống thành thứ mà decoder cưỡng chế. (Tôi đã viết riêng về [nghiên cứu thật sự nói gì về prompt engineering](/vi/blog/what-the-research-says-about-prompt-engineering/) và kỹ thuật dân gian nào thật sự trụ được.)
- **Mọi token đều bị tính tiền ở mọi lần gọi.** Một system prompt dài là khoản thuế cố định đánh lên toàn bộ workload.

Điểm cuối cùng chính là động cơ chính đáng để fine-tune mà người ta hay với tới quá sớm — và có một can thiệp rẻ hơn cần thử trước. Prompt caching cho phép tái sử dụng phần đầu ổn định của prompt qua nhiều lần gọi với mức giá giảm, gỡ bỏ phần lớn lập luận về chi phí mà không cần sản xuất dataset nào. Hãy thử cái đó trước khi thử train. Chi tiết hơn về đòn bẩy này nằm trong [bài về chi phí](/vi/blog/cutting-ai-costs-free-tiers-caching-and-routing/).

## Retrieval là miếng vá kiến thức, và chỉ là miếng vá kiến thức

[Paper RAG gốc](https://arxiv.org/abs/2005.11401) đặt vấn đề rất thẳng: đặt một bộ nhớ phi tham số bên cạnh bộ nhớ tham số, để kiến thức nằm ở chỗ bạn sửa được. Cách đóng khung đó đến giờ vẫn là cách đúng để quyết định bạn có cần nó hay không.

Retrieval là câu trả lời khi một trong những điều sau đúng:

- dữ kiện thay đổi theo một nhịp bạn không kiểm soát
- dữ kiện là riêng tư và chưa từng nằm trong bất kỳ corpus pre-training nào
- số lượng dữ kiện lớn hơn nhiều so với sức chứa của context window
- bạn cần chỉ cho người dùng thấy câu trả lời *đến từ đâu*
- những user khác nhau chỉ được quyền thấy những tập con khác nhau

Cái bạn phải gánh khi nói "có": một pipeline nạp dữ liệu, các quyết định chunking ảnh hưởng tới chất lượng trả lời theo những cách không hiển nhiên, một index phải luôn đồng bộ với nguồn sự thật, thêm một chặng network làm tăng latency, và một chế độ hỏng hoàn toàn mới — model giờ có thể sai vì retrieval đưa nhầm ba đoạn văn cho nó, và cái sai đó nhìn y hệt như model tự sai.

Vấn đề cuối cùng đó đủ sâu để xứng đáng một bài riêng; đo xem retrieval có lấy đúng thứ cần lấy không là một môn khác với đo xem model trả lời tốt không, và nó cần bộ test riêng. Với phạm vi *quyết định* của bài này, thứ cần khắc vào đầu chỉ đơn giản là: nói "có" với retrieval nghĩa là từ nay bạn sở hữu thêm một hệ thống search, bên cạnh một tính năng LLM.

## Fine-tuning mua được hình thức, latency và giá — không mua được kiến thức

Những thứ fine-tuning thật sự mua được, một cách đáng tin cậy:

- **Hình thức nhất quán.** Giọng văn, cấu trúc, văn phong, quy ước nội bộ — những thứ tả bằng cả trang style guide vẫn được áp dụng lúc được lúc không. Cho xem ví dụ dạy được điều này tốt hơn nhiều so với mô tả bằng lời.
- **Prompt ngắn hơn.** Hành vi mà lẽ ra bạn phải viết ra ở mọi lần gọi được gấp gọn vào trong model. Ít token input hơn mỗi request, ít chỗ để sai hơn.
- **Latency và chi phí mỗi lần gọi thấp hơn**, như hệ quả của prompt ngắn hơn — và đôi khi vì một base model nhỏ hơn, đã tune cho tác vụ hẹp của bạn, sánh ngang một model lớn hơn nhưng chưa tune.
- **Những dạng tác vụ khó mô tả bằng lời.** Một hệ nhãn phân loại rất riêng, phương ngữ SQL của team bạn, một ranh giới phân loại mà ai cũng nhận ra nhưng không ai viết ra được. Nếu prompt tốt nhất bạn viết được là "nhìn là biết", thì bạn đang có một bài toán fine-tuning.

Thứ nó không mua được là kiến thức đáng tin. Dữ kiện đã hấp thụ vào trọng số thì không có nguồn, không có phiên bản, không xoá được, và mờ đi một cách âm thầm — và không có gì báo cho bạn biết khi một dữ kiện đã hết hạn. Một bản fine-tune là một nhánh rẽ của cách bạn hiểu tác vụ, bị đóng băng tại một ngày cụ thể.

Còn đây là mặt chi phí, nói thẳng. Không phải hoá đơn tiền train — hoá đơn tiền train thường là khoản nhỏ nhất trong danh sách này.

1. **Một dataset đã gán nhãn.** Đây mới là phần việc thật: những ví dụ vừa đúng vừa *nhất quán với nhau*. Hai người gán nhãn bất đồng thì không "triệt tiêu lẫn nhau"; nó đi vào model dưới dạng nhiễu, và về sau lộ ra thành một hành vi không ai giải thích nổi.
2. **Bảo trì dataset.** Tác vụ dịch chuyển. Một quy tắc thay đổi. Thế là một phần ví dụ của bạn đang dạy sai, và bạn phải đi tìm xem phần nào.
3. **Một vòng lặp retrain.** Mỗi thay đổi đáng kể của tác vụ là thêm một lần train, thêm một artefact, thêm một lần rollout.
4. **Một bộ evaluation mà bạn tự sở hữu.** Bạn không còn dựa vào benchmark của nhà cung cấp được nữa, vì model không còn là của họ. Bạn cần một tập held-out, các kiểm tra hồi quy so với phiên bản trước, và một kiểm tra rằng bạn không làm hỏng những gì model vốn giỏi bên ngoài tác vụ hẹp đó.
5. **Một model phải giữ đồng bộ.** Đây là thứ cắn bạn sau mười tám tháng. Base model bị deprecate và bị thay thế. Khi một base tốt hơn ra mắt, bản fine-tune của bạn vẫn ngồi trên base cũ, và muốn chuyển thì phải train lại — rồi thẩm định lại toàn bộ, vì một dataset dạy tốt base cũ không tự động dạy base mới đúng bài học đó.

Bản thân phần kỹ thuật thì dễ, và chính vì thế các chi phí bên trên hay bị đánh giá thấp. Một tập supervised fine-tuning chỉ là các đoạn hội thoại:

```json
{"messages": [{"role": "system", "content": "You are a support triage assistant."}, {"role": "user", "content": "card declined at checkout, third time today"}, {"role": "assistant", "content": "{\"category\": \"billing.payment_failure\", \"severity\": \"high\", \"needs_human\": true}"}]}
{"messages": [{"role": "system", "content": "You are a support triage assistant."}, {"role": "user", "content": "how do I change my avatar"}, {"role": "assistant", "content": "{\"category\": \"account.profile\", \"severity\": \"low\", \"needs_human\": false}"}]}
```

```python
job = client.fine_tuning.jobs.create(
    training_file=train_file.id,
    validation_file=val_file.id,   # hold this out. always.
    model="<base-model-id>",
    suffix="triage-v3",            # version it; you will have a v4
)
```

Hai dòng trong đoạn code đó là toàn bộ lập luận. `validation_file` không phải phép lịch sự tuỳ chọn — không có tập held-out thì bạn không có cách nào phân biệt một model đã học được tác vụ với một model chỉ học thuộc ví dụ của bạn. Và `suffix` là một số hiệu phiên bản, bởi vì sẽ có v4, và sẽ có thứ gì đó trên production cần được ghim vào v3 trong lúc bạn đánh giá v4.

## LoRA và adapter: khoảng giữa giá rẻ

Fine-tuning đầy đủ cập nhật mọi trọng số, nghĩa là một bản sao model đầy đủ cho mỗi tác vụ. [LoRA](https://arxiv.org/abs/2106.09685) làm một việc nhẹ hơn nhiều: đóng băng trọng số gốc, và huấn luyện một phần cập nhật hạng thấp nhỏ bên cạnh chúng. Artefact thu được nặng vài megabyte thay vì cả một model, nên bạn có thể giữ nhiều adapter trên chung một base và tráo chúng theo tác vụ, theo tenant, hoặc theo thí nghiệm.

Với [PEFT](https://huggingface.co/docs/peft/index), việc này chỉ là vài dòng đặt lên trên một vòng train bình thường:

```python
from peft import LoraConfig, get_peft_model

config = LoraConfig(
    r=16,                    # rank of the update
    lora_alpha=32,
    lora_dropout=0.05,
    target_modules=["q_proj", "v_proj"],
    task_type="CAUSAL_LM",
)
model = get_peft_model(base_model, config)
model.print_trainable_parameters()   # a small fraction of the base
```

Đây thật sự là khoảng giữa thực dụng của thị trường hiện nay, và nó thay đổi bài toán kinh tế đủ nhiều để câu "bọn tôi không đủ tiền fine-tune" hiếm khi còn đúng. Nhưng hãy nói chính xác về thứ nó làm rẻ đi. LoRA giảm **chi phí tính toán và chi phí lưu trữ** của việc huấn luyện. Nó không giảm chi phí dataset, chi phí giữ nhãn nhất quán, chi phí evaluation, hay chi phí giữ đồng bộ — mà đó mới luôn là những phần đắt. Một lần train rẻ trên một dataset tệ chỉ tạo ra một model tệ nhanh hơn.

## Quy tắc thứ tự, và vì sao nó là chuyện bảo trì

Vắt kiệt từng tầng trước khi thêm tầng kế tiếp: **prompt → schema → retrieval → fine-tune**. Không phải vì các tầng sau khó dựng hơn — với một API được quản lý, fine-tune có khi còn gọn hơn một buổi chiều dựng pipeline retrieval — mà vì mỗi bậc đi lên đều nhân vĩnh viễn diện tích bề mặt bạn phải bảo trì.

| Bạn đã nhận | Từ giờ bạn sở hữu, mãi mãi |
| --- | --- |
| Prompt | Một chuỗi string trong version control, và eval cho nó |
| + Schema | Một hợp đồng, cộng việc migrate khi hợp đồng đổi |
| + Retrieval | Một pipeline nạp dữ liệu, một index, việc đồng bộ, và eval chất lượng retrieval |
| + Fine-tuning | Một dataset, một quy trình gán nhãn, một pipeline huấn luyện, eval theo phiên bản model, và một cuộc migrate base model mà bạn không quyết được thời điểm |

Hãy đọc dòng cuối như một câu hỏi về nhân sự chứ không phải về kỹ thuật. Một năm nữa vẫn phải có người làm tất cả những việc đó.

Cũng cần nói thẳng, vì cách đóng khung "chọn một trong ba" che mất điều này: **chúng kết hợp được với nhau, và những hệ thống tốt nhất dùng nhiều hơn một.** Hình hài trưởng thành phổ biến là fine-tuning cho hình thức cộng retrieval cho dữ kiện — một model đã tune luôn sinh đúng cấu trúc output nội bộ của bạn, được nạp tài liệu mới nhất tại thời điểm request. Chọn một thứ và loại trừ các thứ còn lại thường tự nó đã là sai lầm.

## Bảng quyết định

| Tình huống | Prompt | Retrieval | Fine-tune |
| --- | --- | --- | --- |
| Model thiếu dữ kiện riêng tư hoặc mới | Không | **Có** | Không |
| Dữ kiện thay đổi hằng tuần | Không | **Có** | Có hại |
| Câu trả lời phải trích nguồn | Không | **Có** | Không |
| User khác nhau thấy dữ liệu khác nhau | Không | **Có** | Bất khả thi |
| Output dài quá, sai giọng, sai trọng tâm | **Có** | Không | Chỉ khi prompt đã chạm trần |
| Định dạng output thỉnh thoảng hỏng | Có ích | Không | **Schema trước đã** |
| Văn phong nội bộ, áp dụng hàng ngàn lần mỗi ngày | Thử trước | Không | **Có** |
| Tác vụ hiển nhiên với người, khó viết thành lời | Few-shot trước | Không | **Có** |
| Prompt cố định khổng lồ là nguyên nhân tốn tiền | Caching trước | Không | **Có** |
| Cần model nhỏ hơn, nhanh hơn cho một tác vụ hẹp | Không | Không | **Có** |
| Đang là prototype và bạn còn đang hiểu dần tác vụ | **Có** | Có thể | **Không** |

Dòng cuối là dòng tôi sẽ bảo vệ mạnh nhất. Fine-tuning mã hoá một quyết định về "thế nào là tốt". Cam kết điều đó khi tác vụ còn chưa đứng yên, và bạn sẽ dành cả quý sau để bảo trì một model đang giữ giùm bạn một quan điểm mà bạn không còn giữ nữa.

## FAQ

**Tôi cứ fine-tune trên tài liệu của công ty để model biết nó, được không?**

Bạn chạy job được, và kết quả sẽ rất khích lệ trong mười lần thử tay đầu tiên — model bắt được từ vựng và giọng văn của bạn, và điều đó đọc lên giống như "nó biết". Rồi nó bịa ra một tham số không tồn tại, không kèm trích dẫn, và không có cách nào truy ngược xem tài liệu nào đã dạy nó thế. Fine-tune trên tài liệu dạy được *phong cách* tài liệu của bạn một cách đáng tin, còn *nội dung* thì không. Nếu mục tiêu là trả lời đúng dữ kiện trong tài liệu, đó là việc của retrieval.

**Tôi cần bao nhiêu ví dụ huấn luyện?**

Không ai trả lời được từ bên ngoài, và ai đưa ra một con số duy nhất cho mọi tác vụ là đang đoán. Cách trung thực là thực nghiệm: gom một tập vừa phải, train, đo trên tập held-out, rồi gấp đôi dữ liệu và đo lại. Khi đường cong đi ngang, số lượng ví dụ không còn là nút thắt nữa — chất lượng và tính nhất quán của nhãn mới là. Tác vụ hẹp, định nghĩa rõ, gán nhãn nhất quán cần ít dữ liệu hơn nhiều so với tác vụ rộng và mang tính chủ quan.

**Context window lớn có làm retrieval trở nên thừa không?**

Nó gỡ bỏ lý do "không nhét vừa", vốn chỉ là một trong năm lý do. Nó không giúp gì cho độ tươi, phân quyền theo user, truy nguồn, hay chi phí — và đẩy cả corpus qua context ở mỗi request là một cách đắt đỏ để né việc dựng index. Context window lớn làm retrieval *dễ hơn* vì giảm áp lực chunking; nó không làm retrieval trở nên không cần thiết.

**Bọn tôi fine-tune xong thì nó giỏi hơn ở tác vụ đó nhưng dở đi ở mọi thứ khác. Chuyện gì vậy?**

Đó là kết quả được dự đoán trước, không phải bug: bạn đã kéo model về phía phân phối dữ liệu của mình, và nó rời xa mọi thứ còn lại. Đây chính là lý do bộ evaluation phải bao gồm cả những năng lực bạn không hề định thay đổi. Nếu model vẫn cần giỏi tổng quát, một adapter nhẹ tay cùng learning rate nhỏ hơn phù hợp hơn là fine-tune toàn phần quyết liệt — hoặc phần việc tổng quát nên được định tuyến sang base model chưa tune.

**Rốt cuộc cái nào rẻ nhất?**

Tính trên mỗi lần gọi, một model đã fine-tune với prompt ngắn thường rẻ nhất, và đó là con số người ta hay đem ra so. Tính trên mỗi quý thì hiếm khi sát nhau: dataset, gán nhãn, eval và các đợt migrate base model là chi phí con người lặp lại, không hiện lên trên hoá đơn. Prompt là thứ rẻ nhất để làm sai, và ở giai đoạn đầu điều đó quan trọng hơn nhiều so với rẻ nhất để vận hành.

---

*Mô hình phân tầng ở đây — chỉ dẫn, kiến thức, hành vi — là cách đóng khung của riêng tôi để ra quyết định cho nhanh, không phải một chuẩn ngành; còn các khẳng định bên dưới về việc mỗi kỹ thuật làm được và không làm được gì thì không phải ý kiến cá nhân. Mọi thứ phụ thuộc phiên bản (endpoint fine-tuning hiện có, mức hỗ trợ structured output, lịch deprecate base model) đều thay đổi thường xuyên — hãy kiểm tra tài liệu chính thức của nhà cung cấp trước khi xây dựng lên trên nó.*
