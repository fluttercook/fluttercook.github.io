Đã có một tuần đào sâu vào Grok Bot, và phải nói là cách thiết lập mặc định của nó mới chỉ là điểm bắt đầu.
Tạo vài Bot thì rất dễ. Cái đáng giá hơn nằm ở việc dạy Bot hiểu bối cảnh của mình, giao cho nó một vai trò rõ ràng và xây cả một hệ thống có thể tự chạy mà không cần ngồi canh từng cuộc hội thoại.
9 mẹo dưới đây có thể biến những cuộc chat AI riêng lẻ thành một đội ngũ AI có thể phối hợp với nhau.
Dạy hệ thống hiểu bối cảnh của mình
Mẹo #1: Dùng Skill “Grill Me”
Giá trị của một đội ngũ Agent phụ thuộc rất nhiều vào việc nó hiểu mình tới đâu.
Có thể dùng một Skill kiểu “Grill Me”, để Grok Bot liên tục hỏi lại cho tới khi hiểu rõ công việc, mục tiêu và kế hoạch. Có thể đưa cùng Skill đang dùng với Claude hoặc Codex vào Grok Bot, yêu cầu nó đọc file, tạo một Skill riêng rồi phỏng vấn về công việc và mục tiêu hiện tại.
Cách này khá hữu ích trước khi lập kế hoạch theo quý, bắt đầu một dự án mới, xây automation hoặc triển khai bất kỳ ý tưởng nào mà AI cần hiểu rõ những gì đang nằm trong đầu mình trước khi bắt tay làm.
Skill sau khi hoàn thành sẽ nằm trong Plugins → Yours và có thể gọi lại bất cứ lúc nào bằng câu kiểu: “Grill me about this plan.”
Không cần setup phức tạp, cũng không cần một system prompt dài ngoằng. Chỉ cần một cuộc phỏng vấn có cấu trúc, sau đó biến nó thành bối cảnh có thể tái sử dụng.
Chỉ cần nói chuyện với một Bot
Mẹo #2: Tạo một Chief of Staff
Có thể có Bot chuyên làm content, research, lập kế hoạch hay xử lý công việc chung, nhưng không ai muốn phải nhớ việc nào thuộc về Bot nào.
Vì vậy có thể tạo một Chief of Staff làm cửa ngõ duy nhất. Chẳng hạn Klaus là Bot duy nhất cần nói chuyện trực tiếp.
Quy tắc khá đơn giản: trước khi làm một việc, Klaus kiểm tra xem có Bot chuyên trách nào phù hợp không. Nếu có thì giao việc cho Bot đó. Chỉ tự làm khi không có Bot chuyên môn nào phù hợp, rồi mang kết quả về lại cuộc trò chuyện chính.
Mỗi Bot chuyên môn chỉ cần một mô tả thật rõ. Motion làm hình ảnh và animation. Eyes phụ trách research. Miner làm nghiên cứu content. Coffee lo kế hoạch buổi sáng. Views hỗ trợ chiến lược nội dung.
Klaus đọc các mô tả đó, giao việc cho đúng Bot và giữ mọi thứ trong một cuộc trò chuyện duy nhất.
Mẹo #3: Để Chief of Staff tự xây đội ngũ
Vậy nên tạo Bot nào tiếp theo?
Sau khi hoàn thành cuộc phỏng vấn “Grill Me”, có thể yêu cầu Klaus nhìn vào mục tiêu hiện tại và đề xuất những vai trò còn thiếu.
Nó có thể xem những Bot đang có, tránh tạo những vai trò bị trùng như thêm một Chief of Staff khác, rồi đề xuất các Bot chuyên môn phù hợp với vấn đề đang gặp.
Trong hệ thống này, nó đề xuất ba Bot mới là Tube, Community và Voice, thay vì một Bot trợ lý chung chung, thêm một Bot làm thumbnail hay một Chief of Staff thứ hai.
Khi ưu tiên công việc thay đổi, chỉ cần nói cho Klaus biết vấn đề đang gặp và để nó thiết kế lại đội ngũ xoay quanh vấn đề đó.
Kiểm soát Bot nào được biết thông tin gì
Mẹo #4: Tách bộ nhớ chung và bộ nhớ riêng
Grok Bot có khả năng tự lưu memory, nhưng cần phân biệt giữa thông tin một Bot cần biết và thông tin tất cả Bot đều cần biết.
Bộ nhớ chung có thể chứa những thông tin như công ty, địa điểm, đội ngũ quản lý, kênh YouTube, phễu bán hàng và các công cụ đang sử dụng.
Trong khi đó, bộ nhớ riêng của từng Bot nên chứa những thông tin chỉ liên quan tới mối quan hệ hoặc công việc của Bot đó, chẳng hạn những ghi chú chỉ Klaus cần biết.
Khi đội ngũ càng lớn thì cách phân chia này càng quan trọng. Gmail hay Calendar có thể được nhiều Bot sử dụng, nhưng phần bối cảnh đi kèm vẫn phải được đặt đúng chỗ.
Có thể nói rõ cho Bot biết thông tin mới nên được lưu vào bộ nhớ chung hay bộ nhớ riêng.
Một tính năng khác cũng khá tiện là có thể biến bất kỳ tin nhắn quan trọng nào thành một thread riêng. Có thể đào sâu một ý tưởng với Klaus rồi quay lại cuộc trò chuyện chính mà không làm mọi thứ rối tung lên.
Kết nối các công cụ và theo dõi công việc
Hệ thống bắt đầu hữu ích hơn nhiều khi các Bot có thể dùng chung công cụ và ghi lại những gì chúng đang làm.
Mẹo #5: Dùng Composio để kết nối thêm ứng dụng
Grok Bot có sẵn khá nhiều Plugin, nhưng chắc chắn không thể có hết mọi công cụ.
Có thể dùng Composio khi cần kết nối với những dịch vụ như YouTube, Reddit, LinkedIn, GoHighLevel hay Perplexity.
Composio có hàng trăm tích hợp và Grok Bot có thể kết nối với Composio như một Plugin.
Nhờ vậy, các Bot có thêm một “cây cầu” để truy cập những ứng dụng mà chúng không thể dùng trực tiếp.
Thông tin này cũng có thể được lưu vào bộ nhớ chung để tất cả Bot biết rằng YouTube, Perplexity, LinkedIn và những kết nối sau này đều có thể truy cập thông qua Composio.
Mẹo #6: Ghi lại công việc của Bot vào ClickUp
Khi bắt đầu giao việc cho Bot từ cả điện thoại lẫn máy tính, mọi thứ rất dễ trở nên lộn xộn.
Một Skill có tên “Log Grok Bot Work to ClickUp” có thể giải quyết chuyện này. Ví dụ khi yêu cầu Klaus nghiên cứu 5 nhà cung cấp AI Voice Agent hàng đầu, nó sẽ tạo project trong ClickUp trước rồi mới giao phần research cho Eyes.
Trên ClickUp có thể theo dõi project đang chạy hay đã hoàn thành.
Trong từng task còn có thể xem ai phụ trách, thời gian bắt đầu, ghi chú tiến độ, link tới kết quả và Bot đang chờ điều gì.
Nhờ vậy, công việc không còn biến mất trong một cuộc chat mà sau đó chẳng ai nhớ mở lại.
Dạy một lần rồi tự động hóa
Mẹo #7: Dạy Bot bằng cách làm mẫu
Có những workflow thiên về thao tác trực quan và rất khó giải thích bằng lời.
Các Bot của Grok có thể dùng chung một máy tính trên đám mây. Giao diện desktop có thể khác nhau, nhưng bên dưới chúng vẫn đang làm việc trên cùng một máy.
Có thể mở chiếc máy tính đó, chọn Teach a task rồi thực hiện quy trình để Grok Bot ghi lại màn hình.
Ví dụ như tìm hình ảnh trên Google Images, lưu một số file cụ thể, thao tác với một giao diện khó hoặc xử lý một công việc phụ thuộc vào những gì đang hiển thị trên màn hình.
Sau khi dừng ghi hình, Grok Bot sẽ phân tích thao tác vừa thực hiện và biến nó thành một Skill có thể tái sử dụng.
Mẹo #8: Tạo Routine
Ứng dụng Grok Bot trên điện thoại khá tiện khi đang ở ngoài, nhưng Routine mới là thứ giúp công việc tự chạy mà không cần mở app.
Routine là một công việc lặp lại mà Bot sẽ chạy theo lịch hoặc theo một sự kiện nhất định. Chỉ cần đặt tên, viết yêu cầu rồi chỉ định Skill cần chạy hoặc Bot nào cần được gọi.
Lịch có thể chạy theo giờ, mỗi ngày, theo khoảng thời gian tùy chỉnh hoặc dựa trên một số sự kiện được hỗ trợ. Hiện có 6 loại sự kiện, trong đó có tin nhắn Slack, hoạt động trên Git và tin nhắn Microsoft Teams.
Vì công việc chạy trên cloud của Grok nên Routine vẫn có thể tiếp tục chạy ngay cả khi điện thoại, máy tính và ứng dụng Grok Bot đều đang tắt.
Mẹo #9: Lưu profile máy tính của Bot
Máy tính của Agent trở nên hữu ích hơn nhiều nếu nó có thể sử dụng lại một profile trình duyệt đã đăng nhập.
Ví dụ, có thể đăng nhập Klaus vào tài khoản Skool một lần.
Sau đó dạy nó cách tìm bài đăng trong cộng đồng và bấm thích, rồi kết nối Skill đó với một Routine chạy mỗi ngày hoặc mỗi tuần.
Thông tin đăng nhập được giữ trong profile đã lưu. Không cần mỗi lần chạy lại phải dán mật khẩu vào cuộc trò chuyện.
Dạy một lần. Lưu profile đã đăng nhập. Để Routine tự dùng lại cả hai.
Cuối cùng
Một hệ thống Grok Bot tốt không phải là hệ thống có nhiều Bot nhất.
Quan trọng hơn là mỗi Bot biết rõ vai trò của mình, được cung cấp đúng bối cảnh, biết báo cáo công việc và có thể biến một quy trình đã làm tốt thành thứ có thể dùng lại.
Đó mới là lúc những cuộc chat AI riêng lẻ bắt đầu trở thành một đội ngũ AI có thể phối hợp với nhau.