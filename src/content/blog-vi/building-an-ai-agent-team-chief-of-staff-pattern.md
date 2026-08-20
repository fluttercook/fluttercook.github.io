---
title: "Mô hình Chief of Staff: biến đống chat AI rời rạc thành một đội ngũ agent"
description: "Chín thói quen biến một mớ hội thoại AI dùng một lần thành hệ thống có cửa ngõ duy nhất, bộ nhớ phân tầng, công việc được ghi lại và routine chạy cả khi bạn đang ngủ."
seoDescription: "Cách xây đội ngũ AI agent: mô hình chief of staff điều phối, tách bộ nhớ chung và riêng, cầu nối công cụ, ghi log công việc, dạy bằng làm mẫu và routine tự động. Áp dụng cho mọi nền tảng."
keywords:
  - đội ngũ ai agent
  - chief of staff ai
  - mô hình orchestrator agent
  - bộ nhớ ai agent
  - mẹo grok bot
  - custom gpt điều phối
  - tự động hóa ai
category: "Hướng dẫn"
topic: "AI Agents"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-20"
emoji: "🧑‍✈️"
tags: ["AI", "AI Agents", "Tự động hóa", "Năng suất", "Grok", "Claude"]
sources:
  - name: "Composio — nền tảng tích hợp cho AI agent"
    url: "https://composio.dev/"
  - name: "Anthropic — Building effective agents"
    url: "https://www.anthropic.com/engineering/building-effective-agents"
  - name: "Anthropic — Agent Skills"
    url: "https://www.anthropic.com/news/skills"
draft: false
---

Sau nửa năm, setup AI của phần lớn mọi người trông giống hệt nhau: mười một con trợ lý tự tạo nhớ mang máng, một nghĩa địa tab trình duyệt, và cảm giác lấn cấn rằng cái mình mò ra hồi tháng Ba đang nằm đâu đó trong một cuộc chat không bao giờ tìm lại được.

Tạo agent là phần dễ. Nền tảng nào — Grok Bot, custom GPT, Claude Projects — cũng làm được trong hai phút. Thứ phân biệt một setup hữu ích với một mớ bừa bộn không phải là số lượng agent. Mà là chúng có dùng chung bối cảnh không, có báo cáo công việc không, và có chạy được khi bạn không ngồi đó không.

Chín thói quen dưới đây đưa bạn tới đó. Mình viết theo hướng không phụ thuộc nền tảng, vì mô hình này sống lâu hơn công cụ bạn đang xài năm nay.

## Phần 1 — Dạy hệ thống hiểu bạn là ai

### 1. Phỏng vấn chính mình trước

Một đội ngũ agent chỉ tốt bằng mức nó hiểu tình hình của bạn. Mà phần lớn mọi người không bao giờ viết cái đó ra, vì nó chán và vì mình đã biết rồi.

Vậy thì để AI moi nó ra. Tạo một skill hoặc prompt lưu sẵn với nhiệm vụ duy nhất là chất vấn bạn — mỗi lần một câu, không gợi ý đáp án, cho tới khi nó tóm tắt lại chính xác công việc, mục tiêu và ràng buộc của bạn.

```text
Bạn đang phỏng vấn tôi để dựng một tài liệu bối cảnh về công việc của tôi.

Quy tắc:
- Hỏi MỖI LẦN MỘT CÂU và chờ tôi trả lời.
- Không bao giờ gợi ý đáp án hay đưa lựa chọn sẵn.
- Câu trả lời nào mơ hồ thì hỏi tiếp, đừng bỏ qua.
- Cần bao phủ: hằng ngày tôi thật sự làm gì, tôi bị đánh giá dựa
  trên cái gì, ai phụ thuộc vào tôi, hiện đang tắc ở đâu, tôi đang
  né việc gì, và trong 90 ngày tới tôi muốn điều gì thành hiện thực.
- Dừng lại khi bạn tóm tắt được tình hình của tôi trong 10 gạch đầu
  dòng mà tôi sẽ gật đầu. Đưa 10 gạch đó ra và hỏi tôi sai chỗ nào.
```

Quy tắc cuối quan trọng hơn tất cả những cái còn lại. "Đưa bản tóm tắt ra và hỏi sai chỗ nào" là thứ biến một buổi phỏng vấn thành một vòng lặp sửa sai.

Chạy cái này trước khi lập kế hoạch quý, trước khi bắt đầu dự án, trước khi xây bất kỳ automation nào. Lưu kết quả lại. Nó trở thành bối cảnh chung mà mọi agent khác đều đọc.

**Vì sao nó hiệu quả:** bạn không phải viết tài liệu — thứ mà bạn sẽ chẳng bao giờ viết xong. Bạn chỉ trả lời câu hỏi, việc đó dễ hơn nhiều, còn phần viết thì thứ khác lo.

### 2. Chỉ một cửa ngõ duy nhất

Bạn có thể có agent cho content, research, lập kế hoạch và việc hành chính. Cái bạn không muốn là mỗi lần dùng lại phải nhớ con nào lo việc gì.

Chọn một agent làm cửa ngõ. Đặt tên cho nó — nói chuyện với *Klaus* thật sự dễ chịu hơn nói chuyện với *Trợ lý 4*. Mọi thứ đi qua nó.

Quy tắc vận hành của nó ngắn thôi:

```text
Bạn là chief of staff của tôi. Bạn là agent duy nhất tôi nói chuyện
trực tiếp.

Trước khi tự làm bất kỳ việc gì:
1. Kiểm tra xem có agent chuyên trách nào phụ trách việc đó không.
   Danh sách hiện có:
   - Motion — hình ảnh, video, animation
   - Eyes — research và kiểm chứng thông tin
   - Miner — nghiên cứu nội dung, tìm nguồn, quét đối thủ
   - Coffee — lập kế hoạch buổi sáng và ưu tiên trong ngày
   - Views — chiến lược nội dung và phân phối
2. Nếu có agent phù hợp thì giao việc cho nó và mang kết quả về đây.
3. Chỉ tự làm khi không agent nào phù hợp.
4. Nếu đã giao việc, nói rõ bạn dùng agent nào và vì sao.

Đừng bao giờ bắt tôi phải mở thêm một cuộc trò chuyện khác.
```

Dòng cuối chính là toàn bộ vấn đề. Chi phí của một setup nhiều agent không nằm ở token, mà ở gánh nặng phải tự điều phối trong đầu. Hãy đẩy phần điều phối đó vào hệ thống.

**Mỗi agent chuyên trách cần một mô tả thật sắc.** "Trợ lý chung" thì vô dụng với một bộ điều phối. "Lo sinh ảnh, prompt dựng video và brief motion graphics" thì điều phối được. Chief of staff đọc chính những mô tả này để quyết định — mô tả mơ hồ thì điều phối sai.

### 3. Để cửa ngõ tự thiết kế phần còn lại của đội

Sau khi làm xong buổi phỏng vấn ở thói quen #1, bạn không cần đoán mò xem nên tạo agent gì tiếp theo nữa. Cứ hỏi:

```text
Đây là tài liệu bối cảnh và danh sách agent hiện có của tôi.

Với các mục tiêu trong tài liệu bối cảnh, đang thiếu những vai trò nào?
Quy tắc:
- Không đề xuất thêm một chief of staff thứ hai hay một trợ lý chung.
- Không đề xuất vai trò trùng lặp với agent đã có — thay vào đó hãy
  chỉ ra agent hiện tại nào đã lo phần đó rồi.
- Với mỗi đề xuất: nêu đúng vấn đề lặp đi lặp lại mà nó giải quyết,
  nó cần làm được gì, và nó tuyệt đối không được đụng vào gì.
- Xếp hạng theo số giờ tiết kiệm được mỗi tháng. Ghi rõ cách bạn ước lượng.
```

Hai quy tắc "không" là phần chịu lực. Cứ để tự do, model sẽ đề xuất một con trợ lý chung chung và một con điều phối trùng lặp, vì đó là hai hình dạng phổ biến nhất trong dữ liệu huấn luyện của nó. Cấm hai cái đó đi thì bạn nhận được đề xuất bám theo vấn đề thật của mình.

Khi ưu tiên thay đổi, cứ nói cho chief of staff biết cái gì đã đổi và để nó thiết kế lại đội ngũ. Đội hình nên là thứ có thể vứt đi và dựng lại.

## Phần 2 — Kiểm soát ai được biết gì

### 4. Tách bộ nhớ chung khỏi bộ nhớ riêng

Phần lớn nền tảng giờ đều có bộ nhớ lâu dài. Sai lầm là quăng tất cả vào chung một đống.

Hai tầng:

| Bộ nhớ chung — mọi agent đọc được | Bộ nhớ riêng — chỉ một agent |
| --- | --- |
| Công ty, vai trò, địa điểm, múi giờ | Ghi chú công việc riêng của agent đó |
| Tên các thành viên và ai phụ trách gì | Sở thích văn phong riêng cho output của nó |
| Sản phẩm, kênh, phễu bán hàng | Trạng thái to-do riêng của nó |
| Đang dùng công cụ gì, nối với nhau ra sao | Feedback bạn đã đưa cho *chính nó* |

Phép thử rất đơn giản: **agent khác có ra quyết định tệ hơn nếu không biết điều này không?** Có thì là bộ nhớ chung. Chỉ ảnh hưởng tới công việc của một agent thì để riêng.

Chuyện này càng quan trọng khi đội càng đông. Nhiều agent có thể cùng dùng lịch của bạn — nhưng bối cảnh về *lý do* sáng thứ Ba là khung giờ bất khả xâm phạm thì phải nằm ở bộ nhớ chung, không thì con nào cũng đặt lịch đè lên.

Khi bảo agent ghi nhớ điều gì, hãy nói rõ:

```text
Lưu vào bộ nhớ chung: team ship hàng vào thứ Năm, không bao giờ thứ Sáu.
Lưu vào bộ nhớ riêng của bạn: tôi thích bản nháp 400 chữ, không phải 800.
```

**Thêm một thói quen:** phần lớn công cụ cho phép tách một tin nhắn quan trọng thành thread riêng. Hãy dùng nó. Đào sâu một nhánh ý tưởng trong thread phụ, giữ cuộc trò chuyện chính sạch sẽ. Thread chính là xương sống của hệ thống — đừng làm nó rối bằng những lần thăm dò.

## Phần 3 — Nối công cụ, ghi lại công việc

### 5. Bắc cầu tới những app nền tảng của bạn không hỗ trợ

Nền tảng AI nào cũng có sẵn plugin. Không nền tảng nào có đủ hết. Khi bạn cần YouTube, Reddit, LinkedIn, một CRM hay một API tìm kiếm không được hỗ trợ sẵn, một nền tảng tích hợp như [Composio](https://composio.dev/) đứng ở giữa — hàng trăm tích hợp nằm sau một kết nối duy nhất mà agent của bạn gọi được.

Rồi ghi cái cầu đó vào bộ nhớ **chung**, để mọi agent đều biết năng lực này tồn tại:

```text
Lưu vào bộ nhớ chung: YouTube, LinkedIn, Reddit và Perplexity đều
truy cập được qua Composio. Hãy kiểm tra Composio trước khi nói với
tôi rằng việc gì đó không làm được.
```

Không có dòng đó, agent sẽ liên tục báo với bạn rằng nó không làm được những việc nó làm được. **Năng lực không được ghi ra thì coi như không tồn tại.**

**Lưu ý bảo mật, và cái này không phải tùy chọn:** một cầu nối tích hợp đang giữ credential sống của các tài khoản của bạn. Cấp scope hẹp nhất mà vẫn chạy được, xem lại từng kết nối thật sự làm được gì, và tuyệt đối đừng cho một agent chạy tự động không giám sát quyền ghi vào thứ mà bạn sẽ đau tim nếu nó ghi đè sai. Sự tiện lợi là thật, nhưng bán kính thiệt hại cũng thật.

### 6. Ghi log công việc của agent ra ngoài cuộc chat

Ngay khi bạn bắt đầu giao việc từ cả điện thoại lẫn laptop, mọi thứ tuột khỏi tầm kiểm soát. Công việc biến mất vào những cuộc hội thoại chẳng ai mở lại.

Cách xử lý là biến việc ghi log thành một phần của task, không phải chuyện làm cho có sau đó. Một skill kiểu *"ghi việc này vào tracker"* chạy **trước** khi bắt đầu làm:

```text
Khi tôi giao một task research hoặc task nhiều bước:
1. Tạo project trong tracker TRƯỚC, trước khi làm bất cứ điều gì.
2. Thêm một task cho mỗi việc con, kèm: agent phụ trách, thời gian
   bắt đầu, đang chờ điều gì, và một trường link cho kết quả.
3. Giao việc.
4. Cập nhật task với ghi chú tiến độ và link kết quả khi xong.
5. Đưa tôi link project trong phần trả lời.
```

Bạn yêu cầu so sánh 5 nhà cung cấp voice agent, thì tracker có project trước khi bất kỳ phần research nào diễn ra. Về sau bạn thấy được cái gì đã chạy, cái gì đã xong, ai làm, kết quả nằm ở đâu — mà không phải đào bới lịch sử chat.

Giá trị không nằm ở việc diễn trò quản lý dự án. Nó nằm ở chỗ **công việc không còn bốc hơi.**

## Phần 4 — Dạy một lần, rồi tự động hóa

### 7. Làm mẫu cho những workflow không diễn tả được bằng lời

Có những quy trình thiên về thị giác và thật sự khổ sở khi phải viết ra. Bấm chỗ nào, trong bốn cái nút giống nhau thì chọn cái nào, layout xê dịch thì xử lý sao.

Nếu nền tảng của bạn cho agent một máy tính đám mây dùng chung kèm chế độ ghi hình "teach a task", hãy dùng nó đúng cho những việc này. Bấm ghi, làm quy trình ở tốc độ bình thường, bấm dừng. Agent phân tích thao tác vừa rồi và biến nó thành một skill tái sử dụng được.

Việc phù hợp: tìm ảnh và lưu theo một quy ước đặt tên cụ thể; thao tác với giao diện không có API; bất kỳ việc gì mà bước kế tiếp phụ thuộc vào cái đang hiển thị trên màn hình.

Việc không phù hợp: bất cứ thứ gì đã có API sạch sẽ. Ghi lại thao tác click đè lên một API được hỗ trợ vừa chậm hơn vừa dễ vỡ hơn nhiều. Làm mẫu là để lấp chỗ trống.

### 8. Routine mới là thứ khiến hệ thống chạy không cần bạn

App chat dành cho lúc bạn đang suy nghĩ. Routine dành cho lúc bạn không.

Routine là một công việc lặp lại mà agent chạy theo lịch hoặc theo trigger. Đặt tên, viết yêu cầu, và chỉ định skill hay agent cần gọi.

Hai loại trigger, giải quyết hai vấn đề khác nhau:

- **Theo lịch** — mỗi giờ, mỗi ngày, hoặc khoảng thời gian tùy chỉnh. Hợp với bản tin tổng hợp, rà soát định kỳ, báo cáo lặp lại.
- **Theo sự kiện** — tin nhắn Slack, hoạt động Git, tin nhắn Teams và tương tự. Hợp với việc phản ứng lại những thứ bạn không kiểm soát được thời điểm.

Vì routine chạy trên cloud nên nó vẫn tiếp tục khi laptop đã tắt và điện thoại đang nằm trong ngăn kéo. Đó là khác biệt giữa một trợ lý và một hệ thống.

Hãy bắt đầu từ những cái nhàm chán nhất. Một bản brief 7 giờ sáng mỗi ngày, đọc lịch và hộp thư rồi nói cho bạn ba việc thật sự quan trọng, có giá trị hơn bất kỳ automation thông minh nào bạn sẽ xây sau này rồi chẳng bao giờ tin tưởng.

**Đặt rào chắn cho mọi thứ chạy không giám sát:** agent chạy tự động nên mặc định chỉ tạo bản nháp và thông báo, không gửi, không đăng, không xóa. Chỉ chuyển một routine sang chế độ hoàn toàn tự động sau khi bạn đã theo dõi output của nó vài tuần và lần nào nó cũng đúng.

### 9. Lưu profile trình duyệt đã đăng nhập

Máy tính của agent trở nên hữu ích hơn hẳn khi nó dùng lại được một profile trình duyệt đã đăng nhập sẵn.

Đăng nhập agent vào dịch vụ một lần, trong profile đã lưu của nó. Dạy nó thao tác. Gắn thao tác đó vào một routine. Phiên đăng nhập được giữ lại — nên bạn không phải dán mật khẩu vào cuộc trò chuyện mỗi lần chạy.

Đó mới là lập luận bảo mật thật sự của tính năng này, và nên nói thẳng ra: **credential nằm trong profile đã lưu tốt hơn credential nằm trong lịch sử chat.** Lịch sử chat bị tóm tắt, bị export, rồi bị nạp ngược vào các bối cảnh khác. Một phiên trình duyệt được lưu thì không.

Hai quy tắc nếu bạn làm cách này:

1. Dùng tài khoản riêng cho việc của agent ở những dịch vụ cho phép — đừng dùng tài khoản chính.
2. Không bao giờ dán mật khẩu, API key hay mã 2FA vào cuộc trò chuyện, kể cả "chỉ lần này để setup thôi". Hãy đăng nhập thủ công ngay trong profile đó.

## Ráp lại thành một hệ thống

Một cuối tuần là đủ, theo thứ tự này:

1. **Chạy buổi tự phỏng vấn.** Lưu kết quả làm tài liệu bối cảnh.
2. **Tạo chief of staff.** Dán quy tắc điều phối vào. Đưa nó tài liệu bối cảnh.
3. **Hỏi nó đang thiếu agent nào.** Xây hai con đầu bảng. Không phải tám.
4. **Tách bộ nhớ.** Dữ kiện chung ở tầng trên, ghi chú từng agent ở tầng dưới.
5. **Nối một cây cầu** cho công cụ mà bạn cứ ước gì nó chạy được, rồi ghi vào bộ nhớ chung.
6. **Thêm phần ghi log** vào chỉ dẫn của chief of staff.
7. **Dựng một routine** — bản brief buổi sáng là lựa chọn đầu tiên kinh điển.
8. **Sau đó mới** tính tới chuyện dạy bằng làm mẫu và lưu profile.

Bước 1–3 mang lại phần lớn giá trị. Phần còn lại là lãi kép.

## Điều gì thật sự khiến nó chạy được

Setup tốt nhất không phải setup nhiều agent nhất. Mà là setup trong đó mỗi agent biết rõ vai trò của mình, có đủ bối cảnh cần thiết, báo cáo lại việc đã làm, và biến được một quy trình bạn từng làm tốt thành thứ dùng lại được.

Ba kiểu hỏng cần canh chừng:

**Quá nhiều agent.** Mỗi agent là một quyết định điều phối. Năm con sắc nét hơn mười lăm con mờ nhạt — và một danh sách mờ nhạt còn làm hỏng khả năng điều phối của chief of staff, vì nó chọn dựa trên chính mấy dòng mô tả đó.

**Bộ nhớ không bao giờ được dọn.** Bộ nhớ chung đã lỗi thời còn tệ hơn không có bộ nhớ chung, vì agent hành động theo nó một cách rất tự tin. Rà lại mỗi tháng và xóa những gì không còn đúng.

**Routine không ai đọc.** Một automation tạo ra output mà bạn lướt qua là chi phí thuần túy. Nếu bạn đã bỏ qua output của một routine hai lần liên tiếp, hoặc sửa nó, hoặc xóa nó.

## Câu hỏi thường gặp

**Có cần nền tảng cụ thể nào không?**
Không. Mô hình này chạy trên mọi hệ thống có trợ lý tùy chỉnh lưu được và có bộ nhớ — Grok Bot, custom GPT, Claude Projects. Chỉ thói quen 7 và 8 cần tính năng riêng của nền tảng (máy tính cho agent, routine theo lịch).

**Nên bắt đầu với bao nhiêu agent?**
Hai: chief of staff, và một con chuyên trách cho việc lặp lại nhiều nhất của bạn. Chỉ thêm khi bạn thấy rõ agent hiện có cho ra kết quả tệ hơn hẳn so với một con chuyên trách.

**Cái gì vào bộ nhớ chung, cái gì để riêng?**
Chung nếu agent khác sẽ ra quyết định tệ hơn khi không biết. Riêng nếu nó chỉ ảnh hưởng tới công việc của chính agent đó.

**Để agent chạy không giám sát có an toàn không?**
Có, nếu kỷ luật về scope. Mặc định cho routine chạy tự động quyền đọc và chỉ xuất bản nháp. Mọi thứ gửi đi, đăng lên, tiêu tiền hay xóa dữ liệu đều nên cần bạn duyệt, cho tới khi bạn đã theo dõi nó chạy đúng trong nhiều tuần.

**Thói quen nào giá trị nhất trong danh sách này?**
Buổi tự phỏng vấn. Mọi thói quen còn lại đều tốt lên khi hệ thống thật sự hiểu tình hình của bạn, và đều xuống cấp khi nó không hiểu.

---

*Bài này khai triển từ một bộ chín mẹo đang được chia sẻ trong cộng đồng AI Việt Nam, vốn được viết ra sau một tuần dùng Grok Bot hằng ngày. Phần prompt và cách đóng khung trong bài là của mình; còn các thói quen nền tảng thì đáng học bất kể bạn đang dùng nền tảng nào.*
