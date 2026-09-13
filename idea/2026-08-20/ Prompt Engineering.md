Khoa học đằng sau Prompt Engineering
Nguồn: The science behind prompt engineering - Ruben Hassid
Không có trường lớp nào dạy một công thức cố định để hỏi AI cho đúng. Mà AI thì đổi quá nhanh, nên mấy mẹo từng hiệu quả cách đây một hai năm chưa chắc còn xài ngon với ChatGPT hay Claude bây giờ.
Hồi trước, có một câu được truyền đi rất nhiều là: “Hãy hít một hơi thật sâu và làm từng bước một.” Câu này không phải tự nhiên mà có, nó từng được ủng hộ bởi một nghiên cứu về prompt từ năm 2023. Nhưng nghiên cứu đó được làm trên PaLM 2-L của Google. Từ đó tới giờ, năng lực của các model đã thay đổi rất nhiều.
Vậy muốn biết cách viết prompt nào còn hiệu quả với AI mới thì phải làm sao? Cách chắc ăn nhất là coi những nghiên cứu mới, nhưng mỗi ngày có hàng trăm paper AI mới thì chắc không ai rảnh tới mức ngồi đọc hết.
Từ một loạt nghiên cứu gần đây, có 5 chuyện khá đáng chú ý.
Đừng hỏi AI kiểu “đúng không?”
Một nghiên cứu của Cornell Tech thử 45 AI khác nhau và chỉ thay đổi một vài từ trong câu hỏi. Kết quả cho thấy nếu hỏi kiểu “X là lựa chọn tốt hơn, đúng không?”, AI có xu hướng bị cách hỏi dẫn dắt. Đổi thành “X có lẽ là lựa chọn tốt hơn?” thì mức độ đồng ý lại thay đổi đáng kể.
Nói đơn giản, nếu mình đã hỏi theo kiểu “mớm đáp án” cho AI thì đừng bất ngờ khi nó đi theo hướng đó.
Ví dụ thay vì hỏi: “Mua nhà là lựa chọn tốt hơn, đúng không?”, hãy hỏi: “Hãy so sánh việc mua và thuê nhà dựa trên tình hình của tôi.”
Giống như hỏi một người bạn vậy. Muốn nghe lời khuyên thật thì đừng hỏi theo kiểu đã có sẵn câu trả lời trong đầu.
Không phải lúc nào cũng cần “suy nghĩ từng bước”
IBM đã chạy hơn 430.000 lượt đánh giá trên 8 cách viết prompt khác nhau. Và một kết quả khá ngược đời là câu “Hãy suy nghĩ từng bước” nổi tiếng lại thua cách hỏi bình thường.
Cách làm hiệu quả nhất trong thử nghiệm này khá đơn giản: đưa câu hỏi ra, rồi thêm một vai trò ngắn cho AI, chẳng hạn “với góc nhìn của một kỹ sư độ tin cậy.”
Điều này không có nghĩa cứ thấy chữ “step by step” là phải bỏ. Chỉ là với các model mới, việc nhét thêm thật nhiều chỉ dẫn vào prompt không đồng nghĩa với kết quả sẽ tốt hơn.
AI nói tự tin không có nghĩa là AI nói đúng
Microsoft từng kiểm tra 2,6 triệu nguồn tham khảo trong các paper AI tại những hội nghị lớn. Một kết quả khá đáng sợ là khoảng 1/4 paper NeurIPS 2025 được kiểm tra có ít nhất một trích dẫn bị AI bịa ra, dù những paper đó đã qua vòng phản biện của chuyên gia.
Vậy nên đừng nhìn cách AI nói chuyện rất chắc chắn rồi nghĩ rằng thông tin đó chắc chắn đúng.
AI có thể đưa cho mình một câu trả lời rất mạch lạc, có số liệu, có link, có tên paper đầy đủ… nhưng nguồn vẫn có thể sai.
Những chuyện quan trọng thì cứ mở nguồn ra kiểm tra. Đừng lấy độ tự tin của AI làm thước đo độ chính xác.
Đừng nhét cả đống luật vô một prompt
Meta thử nhiều model như GPT-5.5, Claude Opus, Gemini Pro và 12 model khác với prompt có từ 1 tới 12 yêu cầu.
Khi có 8 yêu cầu, model chỉ làm đúng từng yêu cầu khoảng 41% số lần. Còn để đáp ứng đúng cả 8 yêu cầu cùng lúc thì chỉ khoảng 5,7%. Có tới 12/15 model không giữ được ổn định khi phải xử lý hơn 3 yêu cầu.
Cái này khá giống giao việc ngoài đời. Một lần quăng cho người ta 10 việc rồi đòi họ nhớ hết từng chi tiết thì kiểu gì cũng sót.
Thay vì vậy, cứ chia ra. Lần đầu cho AI làm phần chính với vài yêu cầu quan trọng. Sau đó đưa bản nháp cho nó kiểm tra từng điều kiện còn lại rồi sửa.
Prompt không cần dài. Quan trọng nhất là mục tiêu phải rõ.
Mục tiêu quan trọng hơn việc đưa một đống ví dụ
Một nghiên cứu từ EPFL, Apple và Mistral AI còn cho thấy việc đưa quá nhiều ví dụ vào prompt đôi khi làm AI làm tệ hơn.
Trong một thử nghiệm với Mistral, prompt có ví dụ đạt 74%, nhưng khi bỏ ví dụ đi và chỉ nói rõ mục tiêu, kết quả tăng lên 83,8%.
Thay vì quăng cho AI vài bài mẫu rồi nói “viết giống vậy”, thử nói rõ mình đang muốn đạt cái gì, tình hình hiện tại ra sao và AI cần giải quyết vấn đề nào.
Ví dụ, thay vì đưa 3 newsletter mẫu rồi bắt AI viết theo, có thể nói: “Tỷ lệ mở newsletter của tôi giảm từ X% xuống Y% trong 3 tháng. Tôi vẫn gửi vào thứ Ba và không đổi format hay thời gian gửi. Hãy tìm những nguyên nhân có khả năng nhất và hỏi tôi những dữ liệu cần thiết trước khi kết luận.”
Lúc này AI có một bài toán để giải, chứ không phải một đống văn mẫu để bắt chước.
Vậy Prompt Engineering rốt cuộc là gì?
Càng coi nhiều nghiên cứu mới, càng thấy prompt engineering chủ yếu là nói cho AI biết mình muốn đạt được cái gì, đưa đủ bối cảnh và để nó tự tìm cách giải quyết.
Đừng hỏi theo kiểu đã mớm sẵn câu trả lời. Đừng nhồi 10–20 luật vào một lần. Đừng thấy AI nói chắc nịch rồi tin ngay. Và cũng đừng mặc định một mẹo từng hiệu quả với model cũ thì giờ vẫn còn hiệu quả.
Model thay đổi thì cách làm việc với model cũng phải thay đổi.