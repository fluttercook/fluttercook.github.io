---
title: "Retrieval không nói dối: dựng eval trước khi dựng RAG"
description: "Phần lớn lỗi RAG là lỗi retrieval khoác áo generation. Đây là cách tách hai phần đó ra: một golden set 50 câu tự tay gán nhãn, recall@k và MRR, cùng một bộ regression chạy trong CI."
seoDescription: "Hướng dẫn đánh giá RAG thực dụng: tự gán nhãn golden set, đo retrieval bằng recall@k và MRR, rồi đo generation với retrieval hoàn hảo."
keywords:
  - đánh giá rag
  - recall@k là gì
  - mrr trong retrieval
  - golden set cho rag
  - chọn chunk size cho rag
  - hybrid search và reranking
category: "Hướng dẫn"
topic: "AI Engineering"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-22"
emoji: "🎯"
tags: ["AI", "RAG", "Đánh giá", "Python", "Search"]
sources:
  - name: "BEIR — heterogeneous benchmark for zero-shot information retrieval"
    url: "https://github.com/beir-cellar/beir"
  - name: "MTEB — Massive Text Embedding Benchmark"
    url: "https://github.com/embeddings-benchmark/mteb"
  - name: "Ragas — bộ công cụ đánh giá cho retrieval-augmented generation"
    url: "https://github.com/explodinggradients/ragas"
  - name: "rank-bm25 — cài đặt BM25 bằng Python"
    url: "https://pypi.org/project/rank-bm25/"
  - name: "Sentence Transformers — model embedding và cross-encoder"
    url: "https://github.com/UKPLab/sentence-transformers"
  - name: "Tài liệu pytest"
    url: "https://docs.pytest.org/"
related:
  - slug: "cutting-ai-costs-free-tiers-caching-and-routing"
    title: "Dùng AI mà không đốt tiền: free tier, caching và định tuyến model"
  - slug: "what-the-research-says-about-prompt-engineering"
    title: "Nghiên cứu thật sự nói gì về prompt engineering — kiểm chứng 5 tuyên bố đang lan truyền"
draft: false
---

Bug report lúc nào cũng cùng một dạng. "Trợ lý bịa ra thời hạn hoàn tiền của mình." Ai đó mở trace, thấy một đoạn văn sai nhưng đầy tự tin, rồi quy lỗi cho model. Prompt được thêm một đoạn hướng dẫn nữa. Có khi temperature bị hạ xuống. Có khi ai đó đề xuất đổi model.

Rồi bạn nhìn lên một tầng và thấy retriever đã đưa cho model ba chunk: chính sách vận chuyển, phần mở đầu của điều khoản dịch vụ, và một chunk đứt giữa câu ngay trước chỗ nêu thời hạn hoàn tiền. Model không hẳn là hallucinate — nó ứng biến trên một lỗ hổng. Không prompt nào sửa được chuyện đó. Đổi model cũng không: một model tốt hơn với đúng ba chunk ấy sẽ cho ra một đoạn sai *thuyết phục hơn*.

Đây là dạng lỗi RAG phổ biến nhất, và bạn không thể nhìn ra nó từ output. Generation là phần duy nhất bạn đọc, nên generation là phần bạn đổ lỗi. Cách sửa là một phép đo tách đôi hai nửa, dựng *trước khi* bạn tinh chỉnh bất cứ thứ gì — nếu không, mọi thay đổi bạn làm đều là tung đồng xu mà không chấm điểm được. Dưới đây là phiên bản nhỏ nhất của phép đo đó mà tôi vẫn gọi là trung thực: một golden set tự tay gán nhãn, hai metric retrieval tính được bằng số học, một bài test generation giả định retrieval hoàn hảo, và một cổng CI để không ai âm thầm làm nó tệ đi.

## Một hệ RAG là hai hệ thống, và thường chỉ một cái hỏng

Cắt pipeline tại đúng chỗ context được lắp ráp:

1. **Retrieval.** Vào là câu hỏi, ra là một danh sách chunk ID có thứ tự. Thành công nghĩa là chunk chứa câu trả lời nằm đâu đó trong top *k* bạn đưa cho model.
2. **Generation.** Vào là câu hỏi cộng các chunk, ra là câu trả lời. Thành công nghĩa là câu trả lời bám vào các chunk đó và thực sự trả lời đúng câu hỏi.

Giờ đến phần chẩn đoán. Với mỗi câu hỏi bị sai, hỏi hai điều:

- Chunk chứa câu trả lời có nằm trong context đã lấy về không? Nếu không, đó là bug retrieval. Bạn làm gì với prompt cũng vô nghĩa.
- Nếu có mà câu trả lời vẫn sai, đó là bug generation — model đã cầm đủ nguyên liệu và vẫn làm hỏng.

Toàn bộ ý tưởng chỉ có vậy. Mọi thứ bên dưới là bộ máy để trả lời hai câu đó lặp đi lặp lại với chi phí thấp — trả lời bằng tay cho một bug report thì dễ, còn trả lời cho năm mươi câu hỏi sau mỗi lần đổi chunking thì không.

## Năm mươi câu bạn tự gán nhãn hơn năm nghìn câu bạn sinh ra

Golden set là một danh sách cặp câu hỏi → nguồn mong đợi. Nguồn mong đợi là một **chunk ID**, không phải chuỗi câu trả lời. Bạn đang ghi lại *câu trả lời nằm ở đâu* — một sự thật về corpus của bạn, và nó ổn định ngay cả khi model đổi.

Câu hỏi đến từ đâu quan trọng hơn có bao nhiêu câu. Tốt nhất: câu hỏi thật từ log, từ ticket hỗ trợ, hoặc từ cái kênh Slack nơi mọi người hỏi đúng thứ mà RAG của bạn sinh ra để thay thế. Tốt nhì: câu hỏi từ người sở hữu domain — trưởng nhóm support, người phụ trách compliance — diễn đạt theo cách *họ* nghe được. Cuối cùng mới đến: câu hỏi tổng hợp sinh ra từ chính tài liệu của bạn.

Câu hỏi tổng hợp trông rất hấp dẫn và phần lớn đo sai thứ cần đo. Một model đọc chunk 47 rồi viết "thời hạn hoàn tiền là bao lâu?" sẽ tạo ra câu hỏi mượn sẵn từ vựng của chunk 47. Model embedding của bạn tìm ra nó dễ dàng. Người dùng thật viết "bao lâu thì tôi phải gửi lại hàng" và không bao giờ dùng chữ *hoàn tiền*. Khoảng cách từ vựng giữa câu hỏi và tài liệu chính là toàn bộ độ khó của retrieval, còn câu hỏi sinh tự động thì được thiết kế — vô tình nhưng rất đều đặn — để không có khoảng cách nào.

Năm mươi là đủ để có ích. Với năm mươi item, mỗi câu hỏi đáng hai điểm phần trăm của giá trị trung bình, nên chênh lệch một hai câu là nhiễu và bạn không nên đuổi theo — nhưng một thay đổi làm dịch chuyển năm hay mười câu là thật và nhìn thấy được. Năm mươi cũng đủ nhỏ để một người gán nhãn xong trong một buổi chiều, đó là lý do thứ hai cho con số này.

Tự gán nhãn không phải việc vặt bạn miễn cưỡng chấp nhận; đó là chỗ chứa phần lớn giá trị. Gán nhãn buộc bạn mở corpus ra và đi tìm chunk, và trên đường đi bạn phát hiện những thứ không metric nào báo cáo: câu trả lời bị chẻ làm hai chunk, cùng một chính sách được nêu hai lần với hai con số khác nhau, bản có thẩm quyền thì nằm trong một file PDF chưa ai index.

Giữ file thật buồn tẻ — mỗi dòng một JSON object, nằm trong repo, có version control:

```jsonl
{"qid": "q001", "question": "how long do i have to send something back", "relevant_chunk_ids": ["policy-refunds#3"], "answer_must_mention": ["30 days"]}
{"qid": "q002", "question": "do i pay for return shipping", "relevant_chunk_ids": ["policy-refunds#5", "policy-shipping#2"], "answer_must_mention": ["prepaid label"]}
```

`relevant_chunk_ids` là một list vì có những câu trả lời thật sự cần hai chunk. `answer_must_mention` là một phép kiểm tra grounding rẻ tiền để dùng về sau — một chuỗi bắt buộc phải xuất hiện trong mọi câu trả lời đúng. Không phải câu hỏi nào cũng có; để trống còn hơn bịa ra một cái.

Một lưu ý về độ bền: chunk ID phải sống sót qua việc index lại. Nếu chúng là vị trí trong mảng thì mỗi lần đổi chunking là cả bộ golden set thành vô nghĩa. Hãy suy ra ID từ thứ gì đó ổn định — `{document_slug}#{ordinal}` — và lưu thêm document ID, để khi ranh giới chunk dịch chuyển bạn vẫn còn cách chấm điểm ở mức tài liệu.

## recall@k và MRR, bằng số học đơn giản

Hai metric gánh phần lớn công việc. Không cái nào phức tạp một khi bạn nhìn công thức cạnh một ví dụ tính tay.

**recall@k** trả lời: *trong số các chunk đáng lẽ phải tìm ra, bao nhiêu phần đã xuất hiện trong top k?* Tức là `|retrieved_top_k ∩ relevant| / |relevant|`. Với phần lớn câu hỏi trong golden set chỉ có đúng một chunk liên quan, nên recall@k bằng 1 nếu chunk nằm trong top k và bằng 0 nếu không, và trung bình trên cả bộ chính là tỉ lệ câu hỏi mà retrieval làm đúng. Đó là con số nên đưa lên dashboard.

**MRR** — mean reciprocal rank — trả lời: *chunk đúng đầu tiên nằm cao đến đâu?* Với một câu hỏi, reciprocal rank là `RR = 1 / thứ_hạng_chunk_đúng_đầu_tiên`, hoặc 0 nếu không lấy được cái nào; MRR là trung bình của RR trên toàn bộ câu hỏi.

Ví dụ tính tay. Câu `q001` có đúng một chunk liên quan là `policy-refunds#3`. Retrieval trả về theo thứ tự: `policy-shipping#1`, `policy-refunds#3`, `terms#7`, `policy-refunds#4`, `faq#2`. Chunk liên quan nằm ở hạng 2, nên recall@1 = 0/1 = **0.0**, recall@3 = recall@5 = 1/1 = **1.0**, và RR = 1/2 = **0.5**.

Giờ giả sử cả bộ có ba câu hỏi với reciprocal rank lần lượt là 1.0 (tìm thấy ở hạng 1), 0.5 (hạng 2) và 0.0 (không tìm thấy). MRR = (1.0 + 0.5 + 0.0) / 3 = **0.5**.

Bạn cần cả hai, vì chúng trả lời hai câu hỏi khác nhau. recall@k cho biết câu trả lời có *nằm trong cái hộp bạn đưa cho model* hay không; MRR cho biết nó nằm ở đâu trong cái hộp đó. Một hệ có thể có recall@10 rất đẹp mà MRR tầm thường — chunk đúng luôn được tìm ra, nhưng ở hạng 8, dưới bảy chunk gây nhiễu. Nhìn trên dashboard recall thì ổn mà trả lời vẫn tệ, vì model đọc bảy chunk vô dụng trước. MRR tăng trong khi recall đứng yên là một cải thiện thật, dù con số tiêu đề không nhúc nhích. Đây là phần tính toán, không cần thư viện nào:

```python
from statistics import mean


def recall_at_k(retrieved_ids: list[str], relevant_ids: list[str], k: int) -> float:
    """Fraction of relevant chunks that appear in the top k results."""
    if not relevant_ids:
        raise ValueError("golden item has no relevant chunks")
    hits = set(retrieved_ids[:k]) & set(relevant_ids)
    return len(hits) / len(relevant_ids)


def reciprocal_rank(retrieved_ids: list[str], relevant_ids: list[str]) -> float:
    """1 / rank of the first relevant chunk; 0.0 if none was retrieved."""
    relevant = set(relevant_ids)
    for rank, chunk_id in enumerate(retrieved_ids, start=1):
        if chunk_id in relevant:
            return 1.0 / rank
    return 0.0


def score_retrieval(results: list[tuple[list[str], list[str]]], ks=(1, 3, 5, 10)) -> dict:
    """results: list of (retrieved_ids, relevant_ids), one entry per question."""
    report = {f"recall@{k}": mean(recall_at_k(r, g, k) for r, g in results) for k in ks}
    report["mrr"] = mean(reciprocal_rank(r, g) for r, g in results)
    return report
```

Chọn `k` để báo cáo cho khớp với số chunk bạn thật sự nhét vào prompt. Đo recall@20 trong khi chạy production với năm chunk là đo một hệ thống bạn không hề vận hành.

## Rồi đo generation với retrieval được loại khỏi phương trình

Khi retrieval đã có điểm, chạy nửa generation hai lần trên cùng golden set:

- **Chế độ oracle.** Đưa cho model đúng các chunk ghi trong `relevant_chunk_ids`. Retrieval hoàn hảo theo định nghĩa. Cái gì hỏng ở đây là vấn đề generation thật — prompt, định dạng, hành vi từ chối, model đánh rơi một chỉ dẫn.
- **Chế độ live.** Đưa cho model đúng những gì retriever thật sự trả về.

Khoảng cách giữa hai điểm số là khoản thuế retrieval bạn đang trả. Nếu oracle tốt mà live tệ, hãy ngừng sửa prompt — việc nằm ở retrieval. Nếu oracle cũng yếu thì model không dùng được nguyên liệu đã đưa tận tay, và lúc đó sửa prompt mới chính đáng. Đây là phép so sánh duy nhất nói cho bạn biết chắc chắn nên dồn cả tuần vào nửa nào.

```python
from dataclasses import dataclass


@dataclass
class GoldenItem:
    qid: str
    question: str
    relevant_chunk_ids: list[str]
    answer_must_mention: list[str]


def grade(answer: str, item: GoldenItem) -> bool:
    """Cheap deterministic grading. Escalate to a judge only when this can't decide."""
    if item.answer_must_mention:
        return all(s.lower() in answer.lower() for s in item.answer_must_mention)
    return judge(item.question, answer)  # LLM-as-judge, or a human review queue


def run_eval(golden: list[GoldenItem], retrieve, generate, get_chunks, k: int = 5) -> dict:
    retrieval_pairs, live_correct, oracle_correct = [], [], []

    for item in golden:
        retrieved_ids = retrieve(item.question, k=k)
        retrieval_pairs.append((retrieved_ids, item.relevant_chunk_ids))
        live = generate(item.question, get_chunks(retrieved_ids))
        live_correct.append(grade(live, item))
        oracle = generate(item.question, get_chunks(item.relevant_chunk_ids))
        oracle_correct.append(grade(oracle, item))

    report = score_retrieval(retrieval_pairs, ks=(1, k))
    report["answer_accuracy_live"] = mean(live_correct)
    report["answer_accuracy_oracle"] = mean(oracle_correct)
    report["retrieval_tax"] = report["answer_accuracy_oracle"] - report["answer_accuracy_live"]
    return report
```

`retrieve`, `generate` và `get_chunks` là của bạn — bộ khung không quan tâm vector store hay nhà cung cấp model nào nằm phía sau, và giữ ranh giới đó sạch chính là thứ cho phép bạn thay một trong hai rồi so sánh. Để ý rằng `grade` ưu tiên kiểm tra chuỗi tất định và chỉ rơi về judge khi bí. Judge hữu ích, nhưng nó cũng là một model thứ hai với các kiểu hỏng của riêng nó; mỗi câu hỏi bạn chấm được bằng substring là một câu hỏi có điểm số đáng tin mà không cần đi đánh giá cái bộ đánh giá.

## Chunking là biến thí nghiệm, không phải config đặt một lần

Chunk size thường được chọn trong giờ đầu tiên của dự án, lấy từ một bài tutorial, rồi không bao giờ được xem lại. Nó là một trong những biến có đòn bẩy lớn nhất của cả hệ, và nó tương tác với mọi thứ — đúng vì thế mà bạn không suy luận ra được, phải đo.

Mâu thuẫn thì đơn giản. Chunk nhỏ embed chính xác (một chủ đề, một vector) nhưng cắt cụt ngữ cảnh, nên model nhận được một mẩu nhắc tên chính sách mà không nêu nội dung. Chunk lớn mang đủ ngữ cảnh nhưng embed nhòe — một vector trung bình hóa sáu chủ đề thì khớp yếu với mọi thứ và không khớp mạnh với thứ nào. Điểm tối ưu nằm ở đâu là tùy tài liệu của bạn.

Với bộ khung ở trên, quét tham số chỉ là một vòng lặp:

| Biến | Vì sao nó làm dịch chuyển các con số | Cần theo dõi gì |
| --- | --- | --- |
| Chunk size | Độ chính xác của embedding đấu với độ trọn vẹn của đoạn văn | recall@k tăng mà độ chính xác câu trả lời giảm nghĩa là chunk quá nhỏ |
| Overlap | Câu trả lời nằm vắt qua ranh giới sẽ có một bản trọn vẹn trong một chunk | Recall cải thiện, kích thước index và chi phí tăng |
| Ranh giới cắt | Cắt theo heading/đoạn văn giữ nguyên đơn vị ngữ nghĩa | So với cắt theo số token cố định trên cùng bộ câu hỏi |
| Chèn header | Thêm tiêu đề tài liệu và tiêu đề mục vào đầu mỗi chunk cho embedding một điểm neo chủ đề | Thường giúp nhiều nhất với chunk ngắn, mơ hồ |
| Model embedding | Dữ liệu huấn luyện khác, khoảng cách từ vựng khác | Chạy lại toàn bộ vòng quét; chunk size tốt nhất có thể đổi theo model |

Chạy từng cấu hình trên cùng năm mươi câu hỏi và giữ các báo cáo trong một bảng. Embed lại corpus cho mỗi cấu hình tốn tiền thật và thời gian thật, nên hãy quét thô trước — ba mức size, không phải mười — rồi tinh chỉnh quanh cái thắng cuộc. Và đừng tin một chiến thắng về chunking chỉ hiện ra ở metric retrieval mà không hiện ở độ chính xác câu trả lời: thường thì đó là dấu hiệu bạn đã tối ưu cho việc tìm chunk chứ không phải cho việc trả lời câu hỏi.

## Hybrid search và reranking, và khi nào mỗi cái đáng đánh đổi latency

Khi recall là vấn đề, hai kỹ thuật giúp theo hai cách khác nhau với hai kiểu chi phí khác nhau.

**Hybrid search** chạy một retriever từ vựng (BM25) song song với retriever vector rồi trộn hai danh sách xếp hạng. Nó tồn tại vì embedding rất dở với token chính xác: mã linh kiện, mã lỗi, tên sản phẩm, từ viết tắt, bất cứ thứ gì không có vùng lân cận ngữ nghĩa hữu ích. Nếu người dùng tìm `ERR_4021` và corpus của bạn chứa `ERR_4021` nguyên văn, BM25 tìm ra còn model ngữ nghĩa thì có thể không. Việc trộn thường dùng reciprocal rank fusion, tức là kết hợp theo vị trí xếp hạng thay vì theo điểm số, nên không đòi hỏi điểm của hai hệ phải so sánh được với nhau — một lợi thế thực dụng có thật, vì chúng vốn không so sánh được.

Cái giá là một index thứ hai phải dựng và giữ đồng bộ. Hai retriever chạy song song, nên latency thực tế tăng khoảng bằng cái chậm hơn chứ không phải tổng của hai.

**Reranking** lấy top *n* từ retriever tầng một — chẳng hạn 50 — rồi chấm lại bằng một cross-encoder, tức model đọc câu hỏi và chunk *cùng lúc* thay vì embed riêng từng cái. Chính việc đọc chung đó làm nó chính xác hơn, và cũng làm nó chậm hơn: không precompute được gì cả, nên mỗi truy vấn là *n* lượt chạy model.

| | Hybrid search | Reranking |
| --- | --- | --- |
| Sửa được | Bỏ sót token chính xác, từ hiếm, mã ID | Chunk đúng có lấy về nhưng xếp hạng thấp |
| Biểu hiện | recall@k thấp, RR = 0 ở một nhóm truy vấn cụ thể | recall@10 ổn, recall@3 và MRR kém |
| Chi phí | Thêm một index; truy vấn song song | n lượt chấm mỗi truy vấn, nối tiếp sau retrieval |
| Dáng latency | Xấp xỉ retriever chậm hơn | Tăng theo n; đây là núm chỉnh chính |
| Nên thử khi | Corpus có mã, tên riêng, thuật ngữ | Golden set cho thấy câu trả lời nằm ở hạng 5-15 |

Đọc quyết định thẳng từ golden set. Nếu reciprocal rank bằng 0 trên một cụm câu hỏi — chunk chưa bao giờ được lấy về — thì reranking không cứu được, vì nó chỉ sắp xếp lại những gì tầng một đã tìm ra; bạn cần hybrid search hoặc một embedding tốt hơn. Nếu chunk luôn được lấy về nhưng nằm ở hạng 8 thì reranking đúng là công cụ cần dùng.

Hãy đo latency trên phần cứng và corpus của chính bạn thay vì tin một con số trong bài blog nào đó — kể cả bài này. Số liệu công bố đến từ độ dài chunk, batch size và phần cứng của người khác.

## Nối vào CI để một thay đổi chunking không thể lọt qua im lặng

Một bộ eval chỉ chạy khi bạn nhớ ra là một bộ eval sẽ lặng lẽ ngừng chạy. Hãy lưu một baseline của các con số hiện tại vào repo, và với mọi pull request chạm vào đường retrieval — chunker, config embedding, thiết lập index, tham số truy vấn — chạy golden set rồi cho build fail nếu bất kỳ metric nào tụt quá một ngưỡng dung sai cố định so với baseline:

```python
import json
import pytest

BASELINE = json.load(open("evals/baseline.json"))
TOLERANCE = 0.05  # absolute; below this, n=50 can't tell signal from noise


@pytest.mark.parametrize("metric", ["recall@5", "mrr", "answer_accuracy_live"])
def test_no_regression(report, metric):
    got, want = report[metric], BASELINE[metric]
    assert got >= want - TOLERANCE, f"{metric} regressed: {got:.3f} < {want:.3f} - {TOLERANCE}"
```

Ba điều khiến cách này chạy được trong thực tế.

**Đặt dung sai theo kích thước bộ dữ liệu, không theo sự lạc quan.** Với năm mươi câu hỏi, một câu là hai điểm, nên dung sai dưới khoảng năm điểm sẽ fail vì nhiễu, bạn sẽ bắt đầu chạy lại job cho đến khi nó pass, và cái cổng đó thành đồ trang trí. Nếu muốn dung sai chặt hơn, câu trả lời là gán nhãn thêm câu hỏi, không phải hạ con số xuống.

**Kéo baseline tiến lên như bánh cóc.** Khi một thay đổi thật sự cải thiện một metric, cập nhật `baseline.json` trong cùng pull request đó. Baseline chỉ nên đi lên, và diff của file đó trở thành một lịch sử đọc được về những gì thật sự có ích.

**Giữ lời gọi model ra khỏi đường chạy nhanh.** Metric retrieval không cần LLM — chúng là phép toán tập hợp trên ID, chạy trong vài giây, và có thể gác mọi PR. Metric generation tốn token và thời gian; hãy chạy chúng hằng đêm hoặc sau một label. Chính sự tách đôi đó làm bộ test duy trì được lâu dài, và duy trì được là tính chất duy nhất đáng kể của một cổng chống regression.

## FAQ

**Năm mươi câu hỏi thật sự là đủ à?**

Đủ để bắt những lỗi đáng bắt và để ra quyết định về chunking mà không phải ngượng. Nó không đủ để phân biệt hai cấu hình sát nhau — với n=50 thì chênh hai điểm là đúng một câu hỏi. Hãy coi năm mươi là điểm mà bộ eval bắt đầu tự trả cho chi phí của nó, rồi cho nó lớn lên bằng cách thêm vào mọi câu hỏi từng tạo ra câu trả lời tệ trên production. Riêng thói quen đó sẽ đưa bạn tới hai trăm câu hỏi được chọn kỹ trong vài tháng, tốt hơn hẳn hai trăm câu sinh tự động ngay ngày đầu.

**Tôi sinh golden set bằng LLM cho nhanh được không?**

Bạn có thể sinh ra các câu hỏi *ứng viên* rồi viết lại và kiểm chứng bằng tay, việc đó tiết kiệm được kha khá thời gian gõ phím. Thứ không thể bỏ qua là mở corpus ra để gán chunk ID, vì đó chính là bước làm lộ ra các vấn đề của tài liệu. Câu hỏi sinh tự động cũng có xu hướng dùng chung từ vựng với chunk nguồn, làm điểm retrieval của bạn bị thổi phồng và che đi đúng cái khoảng cách từ vựng mà bộ eval sinh ra để đo.

**Còn các metric trong Ragas và những bộ tương tự — faithfulness, answer relevancy?**

Chúng hữu ích, và phần lớn đo nửa generation. Hãy thêm chúng khi retrieval đã nằm trong tầm kiểm soát; bắt đầu từ đó là sai chỗ, vì một điểm faithfulness tính trên các chunk sai là một phép đo rất chính xác cho một thứ không liên quan. Cũng lưu ý phần lớn các metric đó bản thân là lời gọi model, nên chúng tốn token và mang phương sai riêng — hãy ghim model judge và phiên bản của nó nếu bạn định theo dõi xu hướng các con số theo thời gian.

**Có đáng làm không với một công cụ nội bộ nhỏ chỉ hai mươi tài liệu?**

Golden set thì đáng, và nó có thể là hai mươi câu hỏi thay vì năm mươi. Bộ khung CI thì cứ bỏ qua cho tới khi có thứ gì đó thay đổi đủ thường xuyên để làm hỏng mọi thứ. Phần không nên bỏ ở bất kỳ quy mô nào là phép so sánh với chế độ oracle, vì đó là khác biệt giữa sửa đúng hệ thống của bạn và ngồi viết lại prompt cả tuần cho một bug retrieval.

---

*Định nghĩa metric, công thức và ví dụ tính tay ở đây là kiến thức chuẩn của information retrieval và được nêu như sự thật; còn các khuyến nghị — năm mươi câu hỏi, dung sai năm điểm, retrieval trong CI và generation chạy hằng đêm — là mặc định làm việc của tôi, không phải tối ưu đã đo đạc, và corpus của bạn hoàn toàn có quyền phản đối. Mọi phát biểu về latency đều được mô tả như cơ chế chứ không phải con số, một cách có chủ ý: hãy tự đo trên dữ liệu của bạn. API thư viện và hành vi model đều thay đổi, nên hãy kiểm chứng mọi thứ phụ thuộc phiên bản với tài liệu hiện hành trước khi dựa vào nó.*
