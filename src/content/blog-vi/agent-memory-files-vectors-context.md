---
title: "Bộ nhớ cho AI agent: file phẳng, vector store, hay chỉ cần context window to hơn"
description: "\"Bộ nhớ\" thật ra là ba bài toán khác nhau dùng chung một cái tên — nhớ một sự thật, nhớ một quyết định, nhớ một quy trình. Mỗi cái cần một cơ chế riêng, và chọn nhầm là lý do agent tự tin lặp lại đúng cái sai hồi tháng Ba."
seoDescription: "So sánh file phẳng, vector store và context window làm bộ nhớ cho AI agent: mỗi thứ mạnh ở đâu, chính sách ghi, vấn đề dữ liệu cũ và thiết kế index lai."
keywords:
  - bộ nhớ ai agent
  - vector store hay file
  - context window làm bộ nhớ
  - thiết kế memory cho agent
  - rag truy hồi sai
  - bộ nhớ agent lỗi thời
category: "Phân tích"
topic: "AI Engineering"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-22"
emoji: "🗃️"
tags: ["AI", "AI Agents", "Bộ nhớ", "RAG", "Context Engineering"]
sources:
  - name: "Anthropic — Effective context engineering for AI agents"
    url: "https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents"
  - name: "Anthropic — Building effective agents"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
  - name: "Claude Code — Quản lý bộ nhớ của Claude"
    url: "https://docs.claude.com/en/docs/claude-code/memory"
  - name: "pgvector — tìm kiếm tương đồng vector cho Postgres"
    url: "https://github.com/pgvector/pgvector"
  - name: "SQLite — FTS5 full-text search"
    url: "https://sqlite.org/fts5.html"
related:
  - slug: "building-an-ai-agent-team-chief-of-staff-pattern"
    title: "Mô hình Chief of Staff: biến đống chat AI rời rạc thành một đội ngũ agent"
  - slug: "cutting-ai-costs-free-tiers-caching-and-routing"
    title: "Dùng AI mà không đốt tiền: free tier, caching và định tuyến model"
draft: false
---

Có người hỏi làm sao cho agent của họ có bộ nhớ, và câu trả lời rơi xuống như một danh sách mua sắm: một vector database, một bước tóm tắt, một context window to hơn, và nếu cuộc trò chuyện đủ dài thì thêm cả knowledge graph. Tất cả đều là cơ chế có thật. Không cái nào là câu trả lời, vì câu hỏi chưa được tách ra.

"Bộ nhớ" đang gọi chung ba bài toán chẳng liên quan gì nhau. Nhớ **một sự thật người dùng đã nói** — họ deploy từ `main`, họ ghét emoji trong commit message, database staging của họ là cái ở `eu-west-1`. Nhớ **một quyết định chính agent đã ra** — hồi tháng Ba nó đã bỏ Riverpod ở luồng checkout, và có lý do cho việc đó. Nhớ **một việc thường được làm như thế nào** — runbook release, năm bước trước khi mở PR, cái thứ về code signing mà lần nào cũng quên.

Ba thứ này có hình dạng khác nhau. Một sự thật thì ngắn, ổn định, và chỉ có đúng một đáp án. Một quyết định là một tài liệu nhỏ có ngày tháng và lý do, mà giá trị nằm chủ yếu ở phần lý do. Một quy trình là một danh sách có thứ tự và phải lấy ra *trọn vẹn* — nửa cái runbook còn tệ hơn không có, vì agent sẽ rất tự tin làm từ bước một tới bước bốn rồi dừng.

Ném cả ba vào cùng một cơ chế thì ít nhất hai cái bị phục vụ tệ. Dưới đây là từng cơ chế thật sự mạnh ở đâu, một chính sách ghi tỉnh táo trông ra sao, vì sao dữ liệu cũ rốt cuộc sẽ phá hỏng mọi hệ bộ nhớ, và một kiến trúc lai có tính chất rất hữu ích: con người sửa được nó lúc 11 giờ đêm.

## File phẳng là bộ nhớ duy nhất mà con người sửa được

Bộ nhớ dựa trên file là một thư mục markdown mà agent đọc và ghi, nạp nguyên khối hoặc mở theo đường dẫn cụ thể. `CLAUDE.md` của Claude Code chính là ý tưởng này ở dạng nhỏ nhất: một file được ghép vào đầu phiên làm việc, kèm cơ chế import file khác và ghi thêm dòng mới vào đó.

Lý lẽ quen thuộc cho file là "nó đơn giản". Đúng, nhưng đó không phải phần quan trọng. Phần quan trọng là file thì **grep được, diff được, và con người sửa tay được**:

- `grep` thắng semantic search khi bạn biết chính xác token cần tìm — một tên file, một flag, một chuỗi lỗi. Khớp chính xác thì không có hàng xóm giả.
- `git diff` cho bạn thấy tuần này agent đã quyết định tin những gì. Vector store không cho bạn bề mặt review nào cả; embedding đã đổi và bạn chỉ biết qua hành vi.
- Khi một mẩu nhớ sai, bạn mở ra và xóa dòng đó. Ba mươi giây, không phải embed lại, không eventual consistency, không phải phân vân vector cũ còn nằm trong đó không.

Tính chất thứ ba đáng giá hơn chất lượng truy hồi, và nó là cái hay bị coi nhẹ trong các buổi bàn thiết kế vì không benchmark được. Kiểu hỏng của một hệ bộ nhớ không phải là "nó không tìm ra gì". Mà là "nó tìm ra một thứ sai và agent đã hành động theo". Thời gian phục hồi từ trạng thái đó mới là chỉ số đáng quan tâm, và file thắng cách biệt.

Giới hạn của file là có thật. File không scale tới trăm nghìn tài liệu, và một thư mục đã phình quá mức nhét vừa context thì cần một index hoặc một bước search đứng trước — chính là kiến trúc lai ở cuối bài. Nhưng trần của nó cao hơn nhiều so với mọi người nghĩ, bởi bộ nhớ dài hạn thật sự hữu ích thì nhỏ. Một năm những sự thật thật sự bền về một con người và một codebase không tới mức megabyte.

## Vector store thật sự giỏi ở chỗ nào

Tìm kiếm vector trả lời tốt đúng một câu hỏi: *trong kho này, cái gì nói về cùng một thứ với truy vấn, dù dùng từ ngữ khác?* Đó là năng lực có thật và không cơ chế nào khác trong bài này có. Nếu người dùng nói "cái vụ mình xử lý scroll giật trên máy Android rẻ tiền" mà ghi chú lại đặt tên là "jank on low-end devices", embedding tìm ra còn `grep` thì không.

Nên các use case trung thực là:

- Một kho quá lớn để đọc hết — ticket hỗ trợ, biên bản họp, một bộ tài liệu, nhiều năm log chat.
- Truy vấn do người viết ra mà người đó không biết từ vựng của kho.
- Trường hợp mà **gần đúng vẫn dùng được** — đưa ra ứng viên để người hoặc agent kiểm lại sau đó.

Kiểu hỏng của nó là hỏng về cấu trúc, không phải chuyện tinh chỉnh. Similarity search luôn trả về *k* hàng xóm gần nhất của vector truy vấn, luôn luôn. Không có kết quả "ở đây chẳng có gì liên quan", vì thứ hạng là tương đối. Hỏi về một quyết định bạn chưa từng ghi lại, bạn nhận về ba quyết định *đã* ghi có độ tương đồng cao nhất — cùng lĩnh vực, cùng từ vựng, giọng nghe hợp lý, nội dung sai. Agent không có cách đáng tin nào phân biệt cái đó với một kết quả trúng, và nó sẽ trích dẫn bằng đúng giọng tự tin ấy.

Hai chỗ đau cụ thể trong bộ nhớ agent:

**Quy trình bị cắt khúc.** Một runbook chia thành các chunk 400 token sẽ được truy hồi về dưới dạng bước 2, 3 và 6. Agent không có tín hiệu nào cho biết bước 4 và 5 tồn tại. Bất cứ thứ gì có thứ tự và phải-đủ-hoặc-không đều không hợp với chunked retrieval — hãy lưu nó thành một tài liệu và lấy nguyên khối theo tên.

**Sự thật bị lấn phiếu.** "Deploy đi qua `make release`" là một câu ngắn phải cạnh tranh với một thread dài nơi ba lệnh deploy được bàn rồi bị loại. Độ dài và mật độ chủ đề quyết định độ tương đồng; tính đúng đắn không tham gia cuộc chơi.

Nếu bạn thật sự cần vector, lưu ý là bạn có lẽ không cần một database riêng. [pgvector](https://github.com/pgvector/pgvector) đặt vector ngay trong Postgres bạn đang chạy, nằm cạnh những dòng dữ liệu mà nó mô tả, trong cùng transaction và cùng bản backup. Còn một index từ khóa thuần — [SQLite FTS5](https://sqlite.org/fts5.html) — xử lý được nhiều truy vấn bộ nhớ agent hơn tiếng tăm của nó gợi ý, vì agent tìm định danh nhiều hơn hẳn so với tìm cảm giác. Truy hồi lai từ khóa cộng vector thắng từng cái riêng lẻ đủ thường xuyên để việc bắt đầu bằng từ khóa và chỉ thêm vector khi bạn chỉ ra được đúng những truy vấn nó trượt là một thứ tự làm việc hợp lý.

## Context window là bộ nhớ bạn thuê theo token

Nhồi tất cả vào prompt là lựa chọn hấp dẫn nhất, vì không cần hạ tầng gì và chất lượng truy hồi ở mức tốt nhất có thể: model không truy hồi gì cả, nó đang đọc. Với một phiên duy nhất kết thúc khi bạn đóng tab, đây là lựa chọn đúng và bạn nên dừng việc kỹ thuật lại ở đó.

Nhưng làm một hệ bộ nhớ thì nó có ba vấn đề.

Nó **đắt nhất** trên mỗi đơn vị hồi tưởng. Bạn trả tiền cho từng token ở từng lượt, kể cả bốn trăm dòng bối cảnh hóa ra chẳng liên quan gì tới câu hỏi lần này. Caching làm dịu đáng kể — phần prefix lặp lại được tính giá thấp hơn — nhưng caching thưởng cho prefix *ổn định*, mà bộ nhớ phình lên mỗi phiên thì đúng là thứ ngược lại với ổn định. Mỗi lần ghi thêm là vô hiệu hóa cache từ điểm đó trở đi, và đó là một lý lẽ thật cho việc giữ phần luôn-được-nạp thật nhỏ và thay đổi thật hiếm.

Nó **kém bền nhất**. Cửa sổ là theo từng phiên. Một bước tóm tắt hay nén giữ lại *một cái gì đó* qua ranh giới phiên, nhưng bản tóm tắt mất mát theo một kiểu rất cụ thể và rất bất lợi: nó giữ mạch kể và bỏ định danh. Chính xác tên bảng, chính xác cái flag, chính xác chuỗi lỗi — đó đúng là những token mà bộ tóm tắt đánh giá là nhiễu, và cũng đúng là những thứ bạn cần.

Và nhiều bối cảnh hơn **không phải lúc nào cũng tốt hơn**. Đầu vào dài làm loãng attention; một chỉ dẫn quan trọng nằm giữa một prompt rất dài phải cạnh tranh với mọi thứ quanh nó, còn tài liệu không liên quan nhưng nghe hợp lý thì chủ động kéo model về phía câu trả lời sai. "Cứ dùng cửa sổ to hơn" là đổi một vấn đề truy hồi lấy một vấn đề attention rồi gọi đó là giải pháp.

| | File phẳng | Vector store | Context window |
|---|---|---|---|
| Mạnh ở | nhớ chính xác, người sửa được | nhớ mờ trên kho lớn | suy luận trên thứ đã nạp |
| Người sửa được không | mở ra sửa dòng đó | embed lại và cầu may | không áp dụng |
| Review được không | `git diff` | không | không |
| Dạng chi phí | lưu gần như free, tốn token khi nạp | hạ tầng + lời gọi embedding | theo token, mỗi lượt |
| Độ bền | vĩnh viễn | vĩnh viễn | chỉ trong phiên |
| Kiểu hỏng đặc trưng | file phình tới mức không ai đọc | ba hàng xóm nghe hợp lý mà sai | cắt cụt và loãng |

## Chính sách ghi: phần lớn những gì agent học được đều không đáng giữ

Cuộc tranh luận về cơ chế thì ồn ào, nhưng thứ quyết định hệ bộ nhớ còn dùng được sau hai tháng hay không là **chính sách ghi** — và gần như không ai viết nó ra. Một agent được tự quyết nên nhớ gì sẽ nhớ tất cả, vì tại thời điểm xảy ra thì cái gì cũng thấy quan trọng.

Ranh giới đứng vững được: giữ lại **sở thích ổn định và quyết định**, không giữ **chi tiết tình huống**.

Đáng ghi: "thích `make release` hơn lệnh build thô". "State của checkout cố ý dùng `InheritedWidget` thuần, không dùng Riverpod — xem ghi chú quyết định". "Không đụng vào `lib/legacy/` nếu chưa hỏi".

Không đáng ghi: "người dùng nhờ sửa một null check trong `cart_page.dart`". Đó là việc của transcript. Nó đúng, nó cụ thể, và nó sẽ không bao giờ còn làm thay đổi việc agent nên làm gì nữa — đó mới là phép thử thật sự.

Một chính sách đủ nhỏ để dán thẳng vào system prompt:

```text
Chỉ ghi vào memory khi thỏa TẤT CẢ các điều sau:
- Tháng sau nó vẫn còn đúng.
- Nó làm thay đổi việc bạn sẽ LÀM, không chỉ việc bạn sẽ nói.
- Không thể suy ra lại từ repo trong vòng một phút.
- Người dùng nhìn bản một dòng sẽ nhận ra đó là của họ.

Không bao giờ ghi: nội dung file, output của lệnh, bất cứ thứ gì
chứa credential, hay lời thuật lại phiên làm việc này.

Định dạng: một dòng, thì hiện tại, kèm lý do nếu có.
Tệ:  "Đã bàn về state management và chốt vài thứ."
Tốt: "Checkout dùng InheritedWidget, không dùng Riverpod — provider
      graph làm rebuild payment sheet. 2026-03-11."
```

Hai quy tắc nữa chỉ trở nên hiển nhiên sau khi một hệ thống đã mục:

**Ưu tiên sửa hơn là ghi thêm.** Khi một sự thật mới mâu thuẫn với cái cũ, agent nên thay thế dòng đó chứ đừng thêm dòng thứ hai. Bộ nhớ chỉ biết phình lên sẽ tích tụ mâu thuẫn, và bộ truy hồi khi cầm hai dòng chọi nhau sẽ vui vẻ trả về cái cũ hơn.

**Ghi rõ nguồn.** Một mẩu nhớ có xuất xứ "người dùng nói vậy" đứng trên một mẩu có xuất xứ "tôi suy ra từ code một lần nọ". Giữ lại ngày tháng. Bạn sẽ cần nó ở phần tiếp theo.

## Dữ liệu cũ: mẩu nhớ trỏ tới một file không còn tồn tại

Hỏng thật sự của mọi hệ bộ nhớ không nằm ở truy hồi — mà ở một mẩu nhớ đúng hồi tháng Hai và bây giờ là một lời nói dối. Ghi chú bảo cấu hình nằm ở `lib/config/env.dart`. File đó đã bị tách ra ba tháng trước. Agent đọc mẩu nhớ, không thấy file, rồi hoặc bịa ra một thứ thay thế nghe hợp lý, hoặc "nhiệt tình" tạo lại nó.

Không có lời giải sạch sẽ, nhưng có vài lời giải một phần rất rẻ.

**Làm cho mẩu nhớ kiểm chứng được rồi đi kiểm chứng.** Một mẩu nhớ có nhắc tới đường dẫn cụ thể thì máy kiểm được. Chạy cái này trong CI, hoặc ở đầu mỗi phiên, và bạn bắt được nhóm mục ruỗng ồn ào nhất mà không tốn gì:

```bash
# Every file path quoted in memory/ that no longer exists on disk
grep -rhoE '`[A-Za-z0-9_./-]+\.(dart|md|ya?ml|json|sh|ts)`' memory/ \
  | tr -d '`' | sort -u \
  | while read -r p; do
      [ -e "$p" ] || echo "stale reference: $p"
    done
```

**Ghi ngày cho mọi entry và để agent nhìn thấy ngày đó.** Một mẩu nhớ hiện ra dưới dạng `2026-03-11 — checkout dùng InheritedWidget` mang một tín hiệu mà cùng đoạn text không có ngày thì không có. Nó không ngăn model tin vào thông tin cũ, nhưng cho model một thứ để cân nhắc, và cho *bạn* một thứ để sắp xếp khi dọn dẹp.

**Gắn tuổi thọ của mẩu nhớ với thứ mà nó mô tả.** Mẩu nhớ về sở thích của một người già đi rất chậm. Mẩu nhớ về vị trí của một file già đi đúng bằng tốc độ file đó bị di chuyển. Nếu chỉ đủ ngân sách cho một quy tắc, hãy chọn quy tắc này: ưu tiên nhớ *ý định* hơn nhớ *bố cục*. "Config gom về một module chứ không rải theo từng feature" sống sót qua một đợt refactor. "Config nằm ở `lib/config/env.dart`" thì không.

**Dọn lúc đọc, đừng dọn theo lịch.** Không ai chạy đợt dọn bộ nhớ hằng quý cả. Nhưng một agent vừa phát hiện một mẩu nhớ sai đang cầm đúng thông tin cần để sửa nó, và đó là lúc phải làm cho việc sửa thật rẻ — một lần edit, một file, ngay trong phiên đó, với con người đang ngồi ngay đấy.

## Kiến trúc lai: index toàn con trỏ, chi tiết lấy theo yêu cầu

Đây là cách bố trí sống sót khi va vào một dự án thật. Một file index, nạp ở mỗi phiên, không chứa gì ngoài những mệnh đề một dòng và con trỏ. Mọi thứ còn lại nằm trên đĩa và chỉ được lấy theo tên khi một dòng nào đó hóa ra có liên quan.

```markdown
# memory/INDEX.md — nạp ở đầu mỗi phiên

## Sở thích (ổn định, do người dùng nói)
- Release đi qua `make release`, không bao giờ dùng lệnh build thô.
- Tóm tắt bằng bảng, không bằng gạch đầu dòng.
- Không sửa `lib/legacy/` nếu chưa hỏi.

## Quyết định (một dòng + nơi chứa lý do)
- 2026-03-11 State của checkout giữ InheritedWidget, không Riverpod.
  → decisions/2026-03-checkout-state.md
- 2026-05-02 Impeller chỉ bật trên iOS; Android giữ đường cũ.
  → decisions/2026-05-impeller.md

## Quy trình (lấy nguyên khối, không bao giờ cắt chunk)
- Cắt bản release → runbooks/release.md
- Thêm một locale → runbooks/i18n.md
- Xoay khóa ký → runbooks/signing.md
```

Vì sao hình dạng này chạy được:

**Index đủ nhỏ để lúc nào cũng nạp.** Không bước truy hồi, không ngưỡng tương đồng, không có chuyện trượt mất một sự thật chỉ vì câu hỏi được diễn đạt lạ. Phần luôn bật là một trang, không phải một thư viện.

**Một dòng là đủ để ra quyết định.** Agent không cần lý do đằng sau quyết định về Riverpod để *khỏi lôi nó ra bàn lại* — nó chỉ cần biết quyết định đó tồn tại. Nó mở file được link tới chỉ khi thật sự sắp đụng vào state của checkout.

**Quy trình giữ nguyên khối.** `runbooks/release.md` được lấy theo đường dẫn, đầy đủ, đúng thứ tự. Không ranh giới chunk nào ăn mất bước 4 được.

**Con người soát nó trong một phút.** Đọc mười hai dòng, xóa hai dòng sai. Thử làm vậy với một index embedding xem.

**Nó xuống cấp một cách trung thực.** Nếu index không có dòng nào về deployment, agent không tìm thấy gì và nói thẳng ra như vậy — thay vì lôi về ba thứ gần với deployment nhất mà nó biết rồi ứng biến.

Thêm vector search lên trên khi bạn có một kho mà index không tóm nổi — hàng nghìn cuộc hội thoại cũ, một bộ tài liệu lớn — và giữ nó ở vai trò *bổ sung* cho index chứ không phải thay thế. Index gánh những thứ không được phép trượt; similarity search gánh những thứ tìm được thì tốt.

## Ghép cơ chế với bài toán

Quay lại ba bài toán, giờ đã có đáp án:

| Bài toán | Cơ chế | Vì sao |
|---|---|---|
| Sự thật người dùng nói | một dòng trong index luôn được nạp | ngắn, không được phép trượt, người phải sửa được |
| Quyết định agent đã ra | một dòng có ngày + một ghi chú được link | dòng đó chặn việc bàn lại, ghi chú giữ phần lý do |
| Việc này thường làm thế nào | một file nguyên khối lấy theo đường dẫn | có thứ tự và phải đủ hoặc không; chunk chính là cái bug |
| Bất cứ thứ gì trong kho quá to để index | tìm từ khóa trước, thêm vector nếu trượt | gần đúng là ổn khi phía sau có bước kiểm chứng |

Hệ quả hơi khó chịu là: thành phần tinh vi nhất lại ít quan trọng nhất. File index và chính sách ghi làm phần lớn công việc, và cả hai đều là text thuần. Đó không phải lý do để bỏ qua vector store khi bạn thật sự có kho lớn — mà là lý do để đừng bắt đầu từ đó, vì một vector store dựng trên một chính sách ghi không tồn tại chỉ là cách truy hồi ra thứ sai nhanh hơn.

## FAQ

**Tôi có thật sự cần vector database cho bộ nhớ agent không?**
Chỉ khi bạn có một kho mà người thường sẽ không muốn ngồi đọc — hàng nghìn ticket, biên bản, hay tài liệu. Với một người và một codebase, một thư mục markdown cộng tìm kiếm từ khóa bao gần hết nhu cầu, và sửa được khi nó sai. Thêm vector khi bạn gọi tên được đúng những truy vấn mà tìm từ khóa đang trượt.

**Nạp một file bộ nhớ ở mỗi phiên có phí phạm hơn so với chỉ truy hồi đúng phần cần không?**
Nó rẻ hơn vẻ ngoài nếu bạn giữ nó trong một trang và giữ nó ổn định, vì prefix ổn định thì cache tốt, còn một bước truy hồi thì thêm độ trễ, thêm một lời gọi embedding, và thêm khả năng trượt mất đúng cái dòng quan trọng. Truy hồi kiếm cơm ở các file chi tiết, không phải ở index.

**Làm sao ngăn agent ghi rác vào bộ nhớ?**
Cho nó một chính sách ghi tường minh với phép thử "tháng sau cái này còn đúng không", và làm cho mọi lần ghi đều nhìn thấy được — memory nằm trong git, review qua diff như mọi thay đổi khác. Một agent ghi được vào bộ nhớ mà không qua review thì sớm muộn cũng ghi một thứ lặng lẽ đổi hành vi của nó, và bạn sẽ đi debug cái đó như một vụ model bị suy giảm.

**Còn chuyện tự động tóm tắt hội thoại vào bộ nhớ thì sao?**
Tóm tắt ổn với mạch kể và tệ với định danh — nó giữ "chúng ta đã bàn về quy trình deploy" và làm rơi mất chính xác câu lệnh. Nếu bạn tự động tóm tắt, hãy trích ra các mệnh đề có cấu trúc thay vì văn xuôi, và bắt mỗi mệnh đề phải là một câu hoàn chỉnh đứng vững được bên ngoài cuộc hội thoại sinh ra nó.

**Có nên cho agent xóa bộ nhớ không?**
Có, và điều đó còn quan trọng hơn việc cho nó ghi thêm. Một hệ chỉ biết append sẽ tích tụ mâu thuẫn cho tới lúc truy hồi thành trò tung đồng xu. Hãy ghép quyền xóa với version control để mọi lần xóa nhầm chỉ cách một lệnh `git revert`.

---

*Các mô tả cơ chế ở đây — similarity search xếp hạng ra sao, prefix caching hành xử thế nào, chunking làm gì với tài liệu có thứ tự — là những tính chất ổn định, nhưng công cụ cụ thể quanh bộ nhớ agent đổi rất nhanh, nên hãy kiểm lại tài liệu hiện hành của nhà cung cấp trước khi ráp bất cứ thứ gì. Thiết kế index-cộng-con-trỏ và chính sách ghi là quan điểm cá nhân, rút ra từ những thứ thường mục trước nhất; hãy coi chúng là một hình dạng khởi đầu để phản biện, không phải một bản spec.*
