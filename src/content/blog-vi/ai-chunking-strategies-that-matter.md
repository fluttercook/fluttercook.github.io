---
title: "Chia nhỏ tài liệu cho truy hồi: quyết định âm thầm chặn trần chất lượng RAG"
description: "Kích thước đoạn không phải cái núm bạn vặn tới khi con số đẹp. Nó mã hoá một giả định về việc câu hỏi là gì, và mọi vấn đề phía sau trong hệ thống RAG của bạn đều truy ngược về nó."
seoDescription: "Chiến lược chia đoạn thực tế cho RAG: chia theo kích thước cố định và chia theo cấu trúc, phần chồng lấn, siêu dữ liệu và tiền tố ngữ cảnh, truy hồi tài liệu cha, bảng biểu và mã nguồn, cùng cách đo xem thay đổi có hiệu quả không."
keywords:
  - chien luoc chia doan rag
  - kich thuoc doan chong lan truy hoi
  - chia doan ngu nghia tai lieu
  - truy hoi tai lieu cha
  - chia theo tieu de markdown
  - doan ngu canh rag
category: "Phân tích"
topic: "AI"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-08"
emoji: "✂️"
tags: ["AI", "RAG", "Truy hồi", "Embedding", "Kiến trúc"]
sources:
  - name: "Text splitters — tài liệu LangChain"
    url: "https://python.langchain.com/docs/concepts/text_splitters/"
  - name: "Node parsers and text splitters — tài liệu LlamaIndex"
    url: "https://docs.llamaindex.ai/en/stable/module_guides/loading/node_parsers/"
  - name: "Contextual retrieval — Anthropic engineering"
    url: "https://www.anthropic.com/news/contextual-retrieval"
  - name: "Sentence Transformers — tài liệu"
    url: "https://www.sbert.net/"
  - name: "tiktoken — thư viện đếm token"
    url: "https://github.com/openai/tiktoken"
  - name: "pgvector — extension vector cho PostgreSQL"
    url: "https://github.com/pgvector/pgvector"
related:
  - slug: "ai-embeddings-choosing-a-model"
    title: "Chọn mô hình embedding: những câu hỏi thật sự quan trọng"
  - slug: "ai-observability-tracing-llm-apps"
    title: "Quan sát ứng dụng LLM: truy vết một hệ thống không tất định"
draft: false
---

Một hệ thống truy hồi trả lời đúng câu "thời hạn hoàn tiền của chúng ta là bao lâu?" nhưng thất bại với câu "thời hạn hoàn tiền có khác với khách doanh nghiệp không?" thường không có vấn đề về mô hình. Nó có một đoạn chứa chính sách chung và một đoạn khác, không bao giờ được truy hồi, chứa ngoại lệ.

Việc chia đoạn quyết định một đơn vị truy hồi *là gì*. Làm sai và không lượng rerank, kỹ thuật prompt hay nâng cấp mô hình nào cứu lại được thông tin bạn đã cắt rời.

## Chia theo kích thước cố định là mốc so sánh, không phải chiến lược

Cách mặc định ai cũng bắt đầu — cắt mỗi N ký tự với M ký tự chồng lấn — đáng được hiểu chính xác, vì đó là thứ bạn sẽ đem ra so sánh.

```python
def fixed_chunks(text, size=1000, overlap=200):
    chunks, start = [], 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks
```

Nó làm đúng chỗ nào: đoạn đều nhau, chi phí đoán được, không giả định gì về định dạng tài liệu.

Nó làm sai chỗ nào: nó cắt ngang câu, bảng, khối mã và — tệ nhất — cắt đứt quan hệ giữa một tiêu đề với phần văn bản bên dưới. Một đoạn bắt đầu giữa câu mà không có dấu hiệu nó đến từ mục nào là một đoạn nhúng kém và đọc cũng dở khi bộ sinh nhìn thấy nó.

Hai cải tiến tức thì, đều rẻ:

- **Chia theo cấu trúc trước, kích thước sau.** Cắt ở tiêu đề, rồi đoạn văn, rồi câu, và chỉ lùi về đếm ký tự khi một đơn vị vượt ngân sách. Đa số thư viện splitter gọi đây là chia đệ quy và nó nên là sàn của bạn chứ không phải trần.
- **Đo bằng token, không phải ký tự.** Giới hạn 1.000 ký tự tương đương khoảng 250 token tiếng Anh và ít hơn khá nhiều với tiếng Việt hoặc với mã nguồn. Nếu bạn đo bằng ký tự thì bạn đang đo bằng đơn vị mà cả bộ nhúng lẫn bộ sinh đều không dùng.

## Chồng lấn mang lại ít hơn người ta tưởng

Chồng lấn tồn tại để tránh việc một câu trả lời bị cắt đứt ở ranh giới. Nó có tác dụng, nhưng là công cụ thô: 200 token chồng lấn trên đoạn 1.000 token nghĩa là nhiều hơn 20% vector, 20% lưu trữ, 20% chi phí tìm kiếm, và những kết quả gần trùng nhau chen chỗ trong top k của bạn.

Tôi dùng 10-15% chồng lấn cho văn xuôi và **bằng không** cho nội dung chia theo cấu trúc, nơi ranh giới vốn đã có ý nghĩa. Nếu chồng lấn đang gánh nhiều việc trong hệ thống của bạn, đó là bằng chứng rằng cách chia đang cắt nhầm chỗ, và cách sửa là ranh giới tốt hơn chứ không phải nhiều dư thừa hơn.

## Thay đổi giá trị nhất: cho mỗi đoạn ngữ cảnh của nó

Một đoạn bị tách rời sẽ mất hết những gì tài liệu xung quanh đã thiết lập. "Điều này chỉ áp dụng cho tài khoản tạo trước đợt di chuyển dữ liệu" chẳng có nghĩa gì nếu không biết "điều này" là điều gì.

Cách sửa là gắn ngữ cảnh vào trước văn bản mà bạn đem đi nhúng:

```python
def contextualise(chunk, doc_title, section_path, doc_date):
    header = f"Tài liệu: {doc_title}\nMục: {' > '.join(section_path)}\nCập nhật: {doc_date}\n\n"
    return header + chunk
```

Phần đầu đề đó được nhúng cùng với đoạn, nên một truy vấn có nhắc tên sản phẩm hay chủ đề của mục giờ khớp được với những đoạn không hề viết ra điều đó. Theo kinh nghiệm của tôi, **đây là cải tiến lớn nhất từ một thay đổi đơn lẻ mà đa số hệ thống RAG có thể thực hiện**, và nó tốn đúng một phép nối chuỗi lúc dựng chỉ mục.

Phiên bản kỹ hơn sẽ sinh một câu tóm tắt về việc mỗi đoạn nằm ở đâu trong tài liệu rồi gắn vào trước. Nó tốn một lời gọi mô hình cho mỗi đoạn lúc dựng chỉ mục, tức là tiền thật với kho lớn, nhưng nó xử lý được những ca mà một đầu đề tĩnh không xử lý nổi — tham chiếu ngầm, đại từ, sự nối tiếp từ mục trước.

Dù theo cách nào, hãy giữ đoạn thô tách biệt với văn bản đem nhúng, để bộ sinh nhận được nội dung sạch chứ không phải phần đầu đề soạn sẵn của bạn.

## Đoạn nhỏ để truy hồi, đoạn lớn để trả lời

Hai mục tiêu này xung đột trực tiếp. Đoạn nhỏ nhúng chính xác và khớp với câu hỏi cụ thể; đoạn lớn cho bộ sinh đủ chất liệu xung quanh để thật sự trả lời được.

**Truy hồi tài liệu cha** hoá giải xung đột: đánh chỉ mục cái nhỏ, trả về cái lớn.

```python
# Dựng chỉ mục: chia thành các đoạn con ~200 token, mỗi cái trỏ về cha của nó
for parent in documents:
    for child in split(parent, size=200):
        index.add(embed(contextualise(child)), metadata={"parent_id": parent.id})

# Truy vấn: tìm trên đoạn con, khử trùng lặp, lấy về tài liệu cha
hits = index.search(embed(query), k=10)
parent_ids = dict.fromkeys(h.metadata["parent_id"] for h in hits)  # giữ thứ tự, không trùng
context = [store.get(pid) for pid in list(parent_ids)[:3]]
```

Việc khử trùng lặp rất quan trọng: nhiều đoạn con của cùng một cha sẽ thường cùng khớp, và thiếu nó thì ba "kết quả" của bạn hoá ra là một tài liệu lặp lại ba lần.

Một mẹo họ hàng, rẻ hơn: truy hồi đoạn nhỏ rồi mở rộng mỗi đoạn để bao gồm các đoạn liền kề trước khi đưa cho bộ sinh. Kém chính xác hơn truy hồi tài liệu cha thật sự, nhưng không cần kho thứ hai.

## Nội dung không chia được

Một số nội dung phá vỡ mọi splitter tổng quát:

- **Bảng biểu.** Cắt một bảng là các dòng mất tiêu đề cột. Hãy giữ nguyên bảng khi nó vừa, và khi không vừa thì lặp lại dòng tiêu đề trong từng mảnh và thêm một chú thích mô tả chủ đề của bảng.
- **Mã nguồn.** Chia theo hàm hoặc lớp, không bao giờ theo số dòng. Một mảnh thân hàm gần như vô dụng trong truy hồi.
- **Hội thoại và ticket.** Chia theo ranh giới lượt nói, và giữ phần giải quyết dính với phần mô tả vấn đề — một đoạn chỉ chứa lời phàn nàn sẽ được truy hồi đúng truy vấn nhưng không trả lời được câu nào.
- **Danh mục tham chiếu và bảng thuật ngữ dài.** Mỗi mục là một đoạn riêng. Đây là trường hợp duy nhất mà đoạn rất nhỏ là hoàn toàn đúng.
- **PDF nhiều cột hoặc trang quét.** Hãy sửa khâu trích xuất trước khi nghĩ tới chia đoạn; văn bản sai thứ tự đọc thì không splitter nào cứu được.

## Đo xem thay đổi có hiệu quả không

Thay đổi cách chia đoạn thì dễ làm và cũng dễ tự lừa mình. Kỷ luật cần có:

1. Giữ một bộ đánh giá cố định gồm các truy vấn với tài liệu nguồn đúng đã biết.
2. Đổi **một** thứ.
3. Đo recall@k trên cùng bộ đó, với cùng mô hình nhúng và cùng k.
4. Đọc từng cái trong mười thất bại tệ nhất. Chỉ số tổng hợp cho bạn biết nó có nhúc nhích không; chỉ việc đọc thất bại mới cho biết vì sao.

Chia lại đoạn nghĩa là nhúng lại, nên hãy dựng đường ống với giả định rằng bạn sẽ làm việc đó nhiều lần: giữ văn bản gốc trong kho của chính bạn, đánh phiên bản cấu hình chia đoạn cạnh các vector, và biến việc dựng lại toàn bộ thành một câu lệnh duy nhất. Một nhóm không thể chia lại đoạn với chi phí thấp sẽ ngừng thử nghiệm, và ngừng cải thiện.

## Câu hỏi thường gặp

**Nên bắt đầu với kích thước đoạn bao nhiêu?**

Khoảng 200-400 token cho đoạn con trong thiết lập tài liệu cha, hoặc 500-800 token cho chỉ mục phẳng. Rồi đo — câu trả lời đúng phụ thuộc vào tài liệu và câu hỏi của bạn, không phụ thuộc vào một khuyến nghị chung.

**Chia đoạn ngữ nghĩa — cắt ở chỗ độ tương đồng embedding tụt xuống — có đáng không?**

Đôi khi, với văn xuôi không cấu trúc và không có tiêu đề. Với tài liệu có cấu trúc thật, chia theo cấu trúc rẻ hơn và thường tốt hơn.

**Siêu dữ liệu của đoạn nên nhúng hay lưu riêng?**

Cả hai. Hãy nhúng phần đầu đề ngữ cảnh để nó ảnh hưởng tới việc khớp; lưu các trường có cấu trúc riêng để bạn lọc được trước khi tìm bằng vector.

**Xử lý tài liệu hay thay đổi thế nào?**

Hãy chia đoạn một cách tất định để những mục không đổi sinh ra ID đoạn giống hệt, rồi chỉ nhúng lại phần đã đổi. Băm nội dung từng đoạn khiến việc này đơn giản.

**Mô hình ngữ cảnh dài có xoá bỏ nhu cầu chia đoạn không?**

Không. Bạn vẫn phải chọn cái gì đi vào cửa sổ, và chất lượng truy hồi — chứ không phải kích thước cửa sổ — mới là thứ quyết định đoạn đúng có ở đó hay không.

---

*Hành vi của splitter, cách chia đệ quy và chia theo cấu trúc, cùng kỹ thuật truy hồi theo ngữ cảnh được mô tả trong các tài liệu framework và bài kỹ thuật liên kết bên trên. Các tỉ lệ chồng lấn, kích thước cho truy hồi tài liệu cha, hướng dẫn theo loại nội dung và kỷ luật đo đạc là đánh giá riêng của tôi từ việc xây các hệ thống truy hồi; con số đúng cho kho tài liệu của bạn chỉ có thể đến từ việc đo trên chính nó.*
