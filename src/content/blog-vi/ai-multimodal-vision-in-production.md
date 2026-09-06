---
title: "Mô hình thị giác trong sản phẩm thật: những phần bản demo bỏ qua"
description: "Đưa một ảnh cho mô hình chỉ tốn một dòng mã. Quyết định gửi độ phân giải nào, xử lý một PDF quét 40 trang ra sao, làm gì khi câu trả lời sai một cách đầy tự tin, và tất cả tốn bao nhiêu — đó mới là dự án thật."
seoDescription: "Kỹ thuật thực tế cho tính năng LLM đa phương thức: độ phân giải ảnh và chi phí token, xử lý tài liệu và PDF, trích xuất có cấu trúc theo schema, chiến lược kiểm chứng, độ trễ và quyền riêng tư."
keywords:
  - llm da phuong thuc san pham
  - mo hinh thi giac trich xuat tai lieu
  - chi phi token anh llm
  - ocr hay mo hinh thi giac
  - trich xuat co cau truc tu anh
  - xu ly pdf bang llm
category: "Hướng dẫn"
topic: "AI"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-05"
emoji: "👁️"
tags: ["AI", "Đa phương thức", "Thị giác máy", "OCR", "Sản phẩm"]
sources:
  - name: "Vision — tài liệu Anthropic API"
    url: "https://docs.anthropic.com/en/docs/build-with-claude/vision"
  - name: "Images and vision — tài liệu OpenAI API"
    url: "https://platform.openai.com/docs/guides/images-vision"
  - name: "PDF support — tài liệu Anthropic API"
    url: "https://docs.anthropic.com/en/docs/build-with-claude/pdf-support"
  - name: "Tesseract OCR — tài liệu"
    url: "https://tesseract-ocr.github.io/"
  - name: "Pillow — tài liệu thư viện xử lý ảnh Python"
    url: "https://pillow.readthedocs.io/"
  - name: "JSON Schema specification"
    url: "https://json-schema.org/"
related:
  - slug: "ai-chunking-strategies-that-matter"
    title: "Chia nhỏ tài liệu cho truy hồi: quyết định âm thầm chặn trần chất lượng RAG"
  - slug: "ai-synthetic-data-for-evals"
    title: "Dữ liệu tổng hợp cho eval: xây bộ kiểm thử mà bạn tin được"
draft: false
---

Bản demo chạy ngon ngay lần đầu: chụp một hoá đơn, nhận về JSON có cấu trúc với tên cửa hàng, ngày và tổng tiền. Rồi bạn đưa nó ra sản phẩm, và người dùng gửi cho bạn một hoá đơn chụp nghiêng trong ánh sáng tệ với ngón tay che mất tổng tiền, một hợp đồng quét 40 trang, một ảnh chụp màn hình bảng tính, và một tấm ảnh mờ chụp lại một màn hình khác đang hiển thị hoá đơn.

Mô hình xử lý được nhiều hơn bạn tưởng, và những phần nó không xử lý được mới là thứ quyết định tính năng này có dùng được hay không.

## Độ phân giải là cái núm chi phí

Ảnh trở thành token, và số lượng tỉ lệ với diện tích điểm ảnh. Công thức chính xác khác nhau tuỳ nhà cung cấp, nhưng hình dạng thì phổ quát: một ảnh lớn có thể tốn hơn cả một trang văn bản, và dù sao đa số nhà cung cấp cũng thu nhỏ ảnh vượt quá một kích thước tối đa trước khi xử lý.

Hai hệ quả theo sau.

**Gửi một tấm ảnh điện thoại ở độ phân giải đầy đủ thường là lãng phí.** Ảnh 12 megapixel sẽ bị nhà cung cấp thu nhỏ, nên bạn đã trả tiền để tải lên những điểm ảnh bị vứt đi. Hãy đổi kích thước trước khi gửi:

```python
from PIL import Image

def prepare(path, max_dim=1568):
    img = Image.open(path)
    img = img.convert("RGB")
    if max(img.size) > max_dim:
        ratio = max_dim / max(img.size)
        img = img.resize((int(img.width * ratio), int(img.height * ratio)),
                         Image.LANCZOS)
    return img
```

Hãy kiểm tra kích thước tối đa mà nhà cung cấp của bạn công bố trước khi cố định hằng số đó — con số này thay đổi và khác nhau giữa các API.

**Nhưng chữ nhỏ thì cần điểm ảnh.** Thu nhỏ một trang hợp đồng dày chữ quá mức và mô hình sẽ đọc ra những từ sai nhưng trông hợp lý. Với công việc trên tài liệu, nước đi hữu ích lại ngược với việc thu nhỏ: **hãy cắt và gửi từng vùng ở độ phân giải cao** thay vì gửi cả trang ở độ phân giải thấp. Một cái bảng bạn quan tâm, gửi đi như một ảnh riêng, được đọc chính xác hơn hẳn so với cũng cái bảng đó khi nó chỉ chiếm một phần mười hai trang.

## Tài liệu không phải là ảnh

PDF quét là đầu vào thực tế phổ biến nhất, và coi nó như "một danh sách ảnh" sẽ cho bạn một hệ thống vừa đắt vừa quên sạch mọi thứ khi qua ranh giới trang.

Những gì đã hiệu quả với tôi, theo thứ tự:

1. **Nếu PDF có lớp văn bản, hãy dùng nó.** Một tỉ lệ rất lớn các PDF "quét" thật ra được sinh ra bằng phần mềm và chứa văn bản hoàn hảo. Hãy trích xuất và bỏ qua thị giác hoàn toàn. Riêng phép kiểm tra này gỡ bỏ phần lớn chi phí của phần lớn đường ống xử lý tài liệu.
2. **Nếu không có, hãy chọn giữa OCR và mô hình thị giác.** OCR truyền thống rẻ hơn nhiều trên mỗi trang và cho bạn vị trí ở mức ký tự; mô hình thị giác hiểu bố cục, xử lý chữ viết tay và bản quét kém tốt hơn, và trả lời được câu hỏi trực tiếp. Chạy OCR trước rồi đưa cho mô hình cả ảnh lẫn văn bản OCR thường tốt hơn dùng riêng cái nào.
3. **Xử lý từng trang, mang theo một bản tóm tắt đang chạy.** Gửi bốn mươi ảnh trang trong một yêu cầu thì tốn kém và làm loãng sự chú ý. Hãy trích xuất từng trang thành một bản ghi có cấu trúc, rồi đối chiếu.
4. **Xử lý tường minh những bảng trải dài qua nhiều trang.** Không có công cụ tổng quát nào làm đúng việc này; bạn phải tự phát hiện phần nối tiếp và ghép các dòng lại.

## Hãy yêu cầu cấu trúc, và kiểm tra nó

Câu trả lời dạng văn xuôi về một tấm ảnh vừa khó dùng vừa khó đánh giá. Hãy định nghĩa một schema và bắt buộc dùng nó:

```json
{
  "merchant_name": "string | null",
  "date": "YYYY-MM-DD | null",
  "total": "number | null",
  "currency": "mã ISO 4217 | null",
  "line_items": [{"description": "string", "amount": "number"}],
  "unreadable_fields": ["string"],
  "notes": "string"
}
```

Hai trường trong schema đó là quan trọng nhất và thường vắng mặt trong lần thử đầu tiên của mọi người.

**Cho phép null ở mọi trường.** Một mô hình được yêu cầu đưa ra tổng tiền sẽ đưa ra tổng tiền. Nếu tổng tiền bị ngón tay che, việc ép trường không được null nghĩa là bạn nhận về một con số bịa ra thay vì một lời thừa nhận. Null phải hợp lệ và prompt phải nói rõ điều đó.

**Một danh sách `unreadable_fields`.** Nó cho mô hình một chỗ để đặt sự bất định thay vì nhét vào giá trị. Theo kinh nghiệm của tôi đây là phần bổ sung hiệu quả nhất cho một schema trích xuất, vì nó biến lỗi âm thầm thành lỗi được gắn cờ — và đó là khác biệt giữa một tính năng tự động hoá được với một tính năng thì không.

Sau đó hãy kiểm tra: phân tích JSON, kiểm tra kiểu, kiểm tra ngày có phải ngày thật, kiểm tra tổng các dòng có xấp xỉ tổng tiền không. **Kiểm chứng bằng số học là miễn phí và bắt được một phần lớn lỗi trích xuất**, và một chỗ lệch là tín hiệu để đẩy lên cho người xem chứ không phải lý do để vứt bỏ dữ liệu.

## Kiểm chứng, vì độ tự tin không được hiệu chỉnh

Mô hình thị giác không trả về một xác suất để bạn đặt ngưỡng, và nó không rào đón theo cách bạn phân tích được. Câu trả lời sai đầy tự tin trông y hệt câu trả lời đúng đầy tự tin. Hãy dựng khâu kiểm chứng ngay trong đường ống:

- **Đối chiếu chéo bên trong dữ liệu.** Tổng số, ngày nằm trong khoảng hợp lý, mã định danh khớp định dạng đã biết, tổng tiền khớp tổng các dòng.
- **Đối chiếu với hệ thống của chính bạn.** Nếu cửa hàng trích xuất được không có trong danh sách nhà cung cấp, hoặc số hoá đơn đã tồn tại, hãy gắn cờ.
- **Hai lần trích xuất độc lập** cho những trường quan trọng — một lượt thứ hai với prompt diễn đạt khác, và khi hai lượt bất đồng thì chuyển cho con người. Cách này nhân đôi chi phí cho vài trường quan trọng, không phải cho cả tài liệu.
- **Luôn giữ ảnh gốc bên cạnh kết quả trích xuất**, có liên kết và xem được. Mọi quy trình soát xét đều cần nó, và thêm vào sau nghĩa là phải xử lý lại từ đầu.

Hãy thiết kế bước có con người ngay từ đầu. Một tính năng trích xuất đúng 90% số trường là xuất sắc nếu 10% còn lại rơi vào hàng đợi soát xét, và vô dụng nếu chúng rơi âm thầm vào cơ sở dữ liệu của bạn.

## Độ trễ, và những gì người dùng nhìn thấy

Yêu cầu có ảnh chậm hơn yêu cầu chỉ có văn bản — việc tải lên, mã hoá và xử lý đều cộng dồn, và một tài liệu nhiều trang nhân nó lên. Điều đó định hình trải nghiệm người dùng hơn bất cứ thứ gì khác:

- Hãy đổi kích thước **ngay trên thiết bị**. Nó cắt thời gian tải lên trên mạng di động rất nhiều và chẳng tốn gì.
- Hiển thị tiến độ theo từng trang, không phải một vòng xoay cho cả tài liệu.
- Trả kết quả từng phần khi chúng xong. Người dùng thấy dữ liệu trang đầu trong lúc trang bảy đang xử lý sẽ cảm nhận đây là hệ thống nhanh.
- Xử lý bất đồng bộ với một ID công việc cho bất cứ tài liệu nào hơn vài trang. Một yêu cầu đồng bộ mất chín mươi giây sẽ đụng vào một cái timeout nào đó trong hệ thống của bạn.

## Quyền riêng tư, thứ không phải tuỳ chọn ở đây

Ảnh mang theo nhiều hơn nội dung của nó. Một tấm ảnh chụp hoá đơn có thể chứa số thẻ lọt vào khung hình, một người ở hậu cảnh, và toạ độ GPS trong EXIF.

- **Loại bỏ EXIF trước khi tải lên.** Vị trí, mã định danh thiết bị và dấu thời gian nằm sẵn trong đó, và người dùng không hề nghĩ là mình đang gửi chúng đi.
- **Nói rõ cho người dùng biết cái gì rời khỏi thiết bị**, một cách thẳng thắn, ngay tại thời điểm chụp.
- **Đặt thời hạn lưu cho ảnh tải lên** và thực thi nó. "Chúng tôi giữ lại để gỡ lỗi" sẽ biến thành một kho lưu trữ vô thời hạn tài liệu của người dùng.
- **Cân nhắc tiền xử lý trên thiết bị** để phát hiện và làm mờ những vùng bạn không cần — số thẻ đầy đủ, một khuôn mặt — trước khi bất cứ thứ gì được truyền đi.
- Hãy kiểm tra điều khoản lưu trữ dữ liệu của nhà cung cấp có khớp với những gì bạn nói với người dùng không. Đây là một cam kết bằng văn bản, không phải chi tiết kỹ thuật.

## Câu hỏi thường gặp

**Mô hình thị giác có tốt hơn OCR chuyên dụng không?**

Với việc hiểu bố cục, chữ viết tay, bản quét kém và trả lời câu hỏi thì nhìn chung là có. Với trích xuất văn bản thuần khối lượng lớn ở chi phí thấp thì OCR vẫn thắng. Kết hợp cả hai thường là lựa chọn mạnh nhất.

**Tôi gửi nhiều ảnh trong một yêu cầu được không?**

Được, và nó giúp ích khi chúng liên quan với nhau — so sánh hai trang, hoặc một tài liệu kèm một bản tham chiếu. Nó tốn bằng tổng số token của chúng, nên hãy gộp một cách có chủ ý chứ đừng mặc định làm vậy.

**Xử lý ảnh bị xoay hoặc ngược thế nào?**

Hãy phát hiện và chỉnh hướng trước khi gửi. Mô hình chịu được một mức xoay nhất định, nhưng độ chính xác giảm và bạn đã có công cụ tất định rẻ tiền cho việc này.

**Còn video thì sao?**

Hãy lấy mẫu khung hình và coi chúng như ảnh, trừ khi nhà cung cấp của bạn hỗ trợ video trực tiếp. Việc chọn khung hình — chứ không phải chất lượng mô hình — thường mới là thứ quyết định kết quả.

**Tôi có cần tinh chỉnh mô hình không?**

Hiếm khi. Prompt tốt hơn, khung cắt tốt hơn và schema chặt hơn sẽ sửa phần lớn vấn đề trích xuất với công sức chỉ bằng một phần nhỏ.

---

*Cách xử lý ảnh, cách tính token, giới hạn kích thước và hỗ trợ PDF khác nhau tuỳ nhà cung cấp và thay đổi theo thời gian; hãy đọc tài liệu API liên kết bên trên để lấy con số áp dụng cho tích hợp của bạn thay vì dựa vào các giá trị ở đây. Thứ tự các bước trong đường ống, khuyến nghị về schema bao gồm `unreadable_fields`, các chiến lược kiểm chứng và danh sách kiểm tra quyền riêng tư là đánh giá riêng của tôi từ việc xây các tính năng xử lý tài liệu.*
