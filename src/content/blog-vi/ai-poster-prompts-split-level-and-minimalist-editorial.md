---
title: "Hai hệ bố cục khiến poster AI nhìn như được thiết kế, không phải được sinh ra"
description: "Bố cục split-level và kiểu ảnh-chuyển-trừu-tượng: hai khung bố cục dùng lại được, kèm prompt điền chỗ trống và các tỷ lệ vùng khiến chúng hiệu quả."
seoDescription: "Prompt thiết kế poster bằng AI: bố cục split-level cho poster triển lãm và kiểu tách đôi ảnh thật với đồ họa trừu tượng. Kèm tỷ lệ vùng, giới hạn màu, phân cấp chữ và template copy-paste."
keywords:
  - prompt poster ai
  - bố cục split level
  - prompt thiết kế editorial
  - prompt poster tối giản
  - poster triển lãm ai
  - prompt nano banana poster
  - template prompt tạo ảnh
category: "Hướng dẫn"
topic: "AI Design"
level: "Cơ bản"
author: "Trung Hiếu"
publishDate: "2026-08-20"
emoji: "🖼️"
tags: ["AI", "Thiết kế", "Prompt Engineering", "Tạo ảnh", "Typography"]
sources:
  - name: "ZzzLc0405/photo-abstract-editorial — skill và prompt biến ảnh thành poster trừu tượng"
    url: "https://github.com/ZzzLc0405/photo-abstract-editorial"
  - name: "Müller-Brockmann, Grid Systems in Graphic Design"
    url: "https://en.wikipedia.org/wiki/Grid_(graphic_design)"
draft: false
---

Bảo model tạo ảnh vẽ "một cái poster", bạn sẽ nhận về một tấm ảnh có hình dạng poster: hình ở trên, chữ ở dưới, hai bên tranh nhau sự chú ý, chẳng có gì gắn chúng lại với nhau. Nó nhìn ra ngay là do AI sinh vì **bố cục** chung chung, chứ không phải vì chất lượng render kém.

Cách sửa không phải là đổi model xịn hơn. Mà là đưa cho model một hệ bố cục thay vì một chủ đề.

Dưới đây là hai hệ cho ra kết quả nhìn như có art director thật. Cả hai đều kèm template điền chỗ trống. Cả hai đều chạy được trên mọi model tạo ảnh hiện tại có nhận prompt dài — Nano Banana, Midjourney, Seedream, GPT Image, Flux.

## Vì sao chỉ dẫn bố cục ăn đứt tính từ mô tả phong cách

Đa số prompt làm poster là một đống tính từ: *tối giản, thanh lịch, cao cấp, chuyên nghiệp, đoạt giải*. Mấy từ đó đẩy model về phía trung bình cộng của tất cả những gì được gắn nhãn như vậy trong dữ liệu huấn luyện. Mà trung bình chính là thứ bạn đang muốn thoát khỏi.

Chỉ dẫn bố cục thì khác. **"Vùng thông tin phía dưới chiếm 25–40% chiều cao"** là ràng buộc mà model có thể thỏa hoặc không thỏa, và nó ràng buộc phần bố cục chứ không phải phần bề mặt. Nói bốn điều cụ thể về cấu trúc thì bạn nhận được một cấu trúc cụ thể.

Ba đòn bẩy làm được nhiều việc nhất:

| Đòn bẩy | Vì sao quan trọng |
| --- | --- |
| **Tỷ lệ vùng** | Chia không đều thì nhìn như có thiết kế; 50/50 thì nhìn như template |
| **Số lượng màu** | Đặt trần rõ ràng (3–5 màu) là đòn bẩy chất lượng lớn nhất |
| **Phân cấp chữ** | Gọi tên 3–4 cỡ chữ khác biệt giúp model không để mọi thứ cùng cỡ trung bình |

Mọi thứ bên dưới đều dựng trên ba cái đó.

## Hệ 1 — Bố cục split-level

**Hợp với:** poster triển lãm, bìa sách, đồ họa sự kiện và văn hóa, bất cứ thứ gì cần cảm giác được tuyển chọn kỹ.

Ý tưởng nghe thì hiển nhiên — chia khung thành phần trên và phần dưới — nhưng phiên bản hiệu quả có một điểm xoay rất cụ thể. Nó **không** phải "hình trên, chữ dưới". Nó là **hai hoặc ba vùng không đều nhau với vai trò khác nhau, rồi được nối lại bằng những thành phần vượt qua ranh giới.**

Cái sự vượt ranh giới đó mới là toàn bộ mẹo. Một cành hoa chạy xuyên qua đường chia, một tiêu đề đủ lớn để cưỡi lên nó, bờ vai của nhân vật phá qua vạch. Không có nó thì bạn có hai hình chữ nhật xếp chồng. Có nó thì bạn có chiều sâu.

### Công thức chia vùng

```text
┌─────────────────────────┐
│                         │
│   VÙNG HÌNH CHÍNH       │  50–65%
│   một chủ thể duy nhất  │
│                         │
├─────────────────────────┤
│  DẢI CHUYỂN TIẾP        │  8–15%
├─────────────────────────┤
│  VÙNG THÔNG TIN         │
│  tiêu đề / ngày / nơi   │  25–40%
│  tên đơn vị (rất nhỏ)   │
└─────────────────────────┘
```

Ba điều khiến nó thật sự hiệu quả chứ không chỉ gọn gàng:

**Dải chuyển tiếp không phải để trang trí.** Nó là một dải hẹp — một khối màu nhạt, một vạch mảnh, một hàng module thông tin nhỏ — có nhiệm vụ làm *thứ thứ ba* mà không vùng nào sở hữu. Thiếu nó, hai vùng đọc lên như không liên quan gì tới nhau. Nó tương đương một dấu phẩy trong thị giác.

**Một tiếng nói chính, vài tiếng thì thầm.** Giữ đúng một chủ thể chính. Sau đó rải vài chi tiết nhẹ ký vào khoảng trống: nét vẽ mảnh, phác thảo dở, một mảnh sơ đồ, chữ dựng đứng, mấy ký hiệu chú thích nhỏ. Chúng làm vùng trống có mật độ mà không cạnh tranh. Đây chính là khác biệt giữa "thoáng" và "trống".

**Tiêu đề tham gia vào bố cục.** Không phải một dòng chú thích nằm dưới hình — tiêu đề là một thành phần bố cục. Phóng to nó, dựng đứng nó, đặt lệch có chủ ý, hoặc cho nó chạy xuyên qua ranh giới vùng.

### Template

Điền vào các ngoặc vuông rồi dán nguyên cả khối:

```text
[Chủ đề]: ___
[Hình chính]: ___
[Tiêu đề chính]: ___
[Tiêu đề phụ / bản dịch]: ___
[Họa tiết bổ trợ]: ___
[Màu chủ đạo]: ___
[Màu nhấn]: ___
[Ngày và địa điểm]: ___
[Tỷ lệ khung]: 9:16

Thiết kế một poster theo ngôn ngữ editorial cao cấp và triển lãm
văn hóa, dựng trên bố cục split-level.

CẤU TRÚC — không tạo bố cục "hình trên, chữ dưới" thông thường.
Chia khung thành ba vùng ngang không đều nhau:
- vùng hình chính chiếm 50-65% chiều cao
- một dải chuyển tiếp hẹp chiếm 8-15%
- vùng thông tin chiếm 25-40%

VÙNG CHÍNH — chỉ một chủ thể duy nhất: [Hình chính]. Thêm hai tới ba
chi tiết phụ nhẹ ký vào khoảng trống (nét mảnh, phác thảo dở, một sơ
đồ nhỏ, chữ dựng đứng) để vùng trống có mật độ mà không lấn át chủ thể.

DẢI CHUYỂN TIẾP — nối hai vùng bằng một khối màu giảm bão hòa, một
vạch mảnh, hoặc một hàng module thông tin nhỏ. Dải này không thuộc
về vùng nào cả.

CHỮ — tiêu đề chính là một thành phần bố cục, không phải chú thích.
Phóng to, dựng đứng, đặt lệch, hoặc cho nó cắt ngang ranh giới vùng.
Đồng thời cho một phần chủ thể chính vượt qua ranh giới, để tách bạch
tiền cảnh và hậu cảnh.

PHÂN CẤP — bốn cỡ chữ khác biệt rõ ràng: tiêu đề chính cỡ lớn, rồi
tiêu đề phụ và ngày tháng, rồi phụ đề nhỏ, rồi thông tin đơn vị rất
nhỏ. Gom nhóm chữ nhỏ thật sát nhau; tuyệt đối không rải rác.

MÀU — tối đa 5 màu. [Màu chủ đạo] dẫn dắt, [Màu nhấn] chỉ xuất hiện
trên dưới 10% diện tích.

TINH THẦN — mỗi vùng có vai trò riêng, và các vùng được nối lại qua
chủ thể chính cùng phần chữ. Giàu chi tiết nhưng không rối, thoáng
nhưng không trống; đạt độ hoàn thiện của một poster bảo tàng thật
hoặc một catalogue nghệ thuật.
```

### Sửa khi ra chưa đúng

- **Không có gì vượt ranh giới.** Nói thẳng: *"chủ thể chính phải chồng lên ranh giới vùng khoảng 10–15% chiều cao của nó."* Model mặc định chia tách gọn gàng.
- **Chữ nhỏ rải khắp nơi.** Thêm: *"toàn bộ chữ dưới tiêu đề phụ phải nằm trong một khối duy nhất, sát nhau."*
- **Quá nhiều màu.** Hạ trần xuống 3 và gọi tên từng màu.
- **Các vùng ra bằng nhau.** Nhắc lại các tỷ lệ phần trăm ở cuối prompt — position bias là có thật, và chỉ dẫn cuối cùng thường sống sót.

## Hệ 2 — Ảnh chuyển thành đồ họa trừu tượng

**Hợp với:** biến một tấm ảnh sẵn có thành tác phẩm kiểu phòng trưng bày. Chân dung, kiến trúc, phong cảnh, ảnh sản phẩm.

Cấu trúc khác, triết lý giống. Khung được chia làm hai nửa: một nửa giữ nguyên **ảnh thật**, nửa còn lại là **bản rút gọn trừu tượng** của chính chủ thể đó. Đặt cạnh nhau, cặp đôi này đọc lên có chủ đích theo cách mà từng nửa riêng lẻ không có được.

Quy tắc theo hướng ảnh là thứ khiến nó bền:

| Ảnh gốc | Cách chia |
| --- | --- |
| Nằm ngang | Chia ngang — trên / dưới, xấp xỉ 50:50 |
| Dựng đứng | Chia dọc — trái / phải, xấp xỉ 50:50 |

Đây là ngoại lệ duy nhất cho nguyên tắc "tránh 50/50", và nó xứng đáng: hai nửa không cạnh tranh nhau, chúng là cùng một chủ thể ở hai thanh âm khác nhau, nên sự cân bằng đọc lên như một phép so sánh có chủ ý.

Có một skill mã nguồn mở triển khai cách này tại [ZzzLc0405/photo-abstract-editorial](https://github.com/ZzzLc0405/photo-abstract-editorial) nếu bạn muốn dùng như một công cụ tái sử dụng thay vì dán prompt mỗi lần.

### Nhiệm vụ của từng nửa

**Nửa ảnh — giữ nguyên, đừng diễn giải lại.** Đây là chỗ đa số thất bại. Model rất muốn stylize, mà ngay khi nó làm vậy thì cặp đôi sụp đổ. Hãy nói thẳng: giữ nguyên hình dáng, tỷ lệ, chất liệu thật, ánh sáng và bóng đổ tự nhiên, màu gốc của chủ thể. Chỉ chỉnh màu — nhẹ nhàng theo kiểu nhiếp ảnh nghệ thuật đương đại, không hơn. Nếu cần mở rộng khung cho vừa, chỉ mở rộng bầu trời, mặt đất hoặc môi trường xung quanh, tuyệt đối không đụng vào chủ thể.

**Nửa đồ họa — rút về đường bao.** Lấy đường viền dễ nhận ra nhất của chủ thể rồi dựng lại bằng hình học sạch, mảng màu phẳng, nét mảnh và khoảng trống rộng rãi. Không minh họa tả thực, không chi tiết vụn. Đích đến là *trừu tượng nhưng nhận ra ngay lập tức*.

**Lấy bảng màu từ chính tấm ảnh.** Đây là chỉ dẫn buộc hai nửa lại với nhau, và cũng là cái mọi người hay quên. Màu được lấy mẫu từ ảnh gốc mới là thứ khiến hai nửa nhìn như một tấm poster chứ không phải hai file ghép lại.

### Template

```text
Tạo một poster editorial tối giản cao cấp từ tấm ảnh được tải lên.
Khung dọc tỷ lệ 3:4.

CÁCH CHIA — nếu ảnh gốc nằm ngang, chia khung theo chiều ngang thành
hai nửa xấp xỉ bằng nhau (ảnh ở trên, đồ họa ở dưới). Nếu ảnh gốc
dựng đứng, chia theo chiều dọc thành hai nửa xấp xỉ bằng nhau (ảnh
một bên, đồ họa bên còn lại).

NỬA ẢNH — giữ nguyên ảnh gốc một cách trung thực: hình dáng, tỷ lệ,
chất liệu thật, ánh sáng và bóng đổ tự nhiên, cùng màu sắc gốc của
chủ thể. Chỉ áp dụng chỉnh màu chuyên nghiệp ở mức tiết chế, theo
đúng thanh âm của nhiếp ảnh nghệ thuật đương đại. Nếu buộc phải mở
rộng khung, chỉ mở rộng bầu trời, mặt đất hoặc môi trường xung quanh.
Không bóp méo, không đổi phong cách, không thay đổi chủ thể.

NỬA ĐỒ HỌA — diễn giải lại đường bao và cấu trúc dễ nhận ra nhất của
chủ thể thành một bố cục trừu tượng đơn giản: hình học sạch, mảng màu
phẳng, nét mảnh, khoảng trống rộng rãi. Không minh họa tả thực, không
chi tiết rườm rà. Kết quả phải trừu tượng nhưng vẫn nhận ra ngay đó
là cùng một chủ thể. Lấy toàn bộ bảng màu từ các màu có trong ảnh gốc.

NỀN — nền trung tính sáng (màu xương, ngà, xám ấm), lề rộng rãi và
bố cục cân bằng quanh trục giữa.

CHỮ — tối thiểu hoặc không có. Nhiều nhất là một tiêu đề ngắn và một
năm, đặt cỡ nhỏ.

ĐỊNH HƯỚNG — thiết kế editorial tối giản cao cấp, poster triển lãm
nghệ thuật đương đại, ngôn ngữ đồ họa kiến trúc, sang trọng tiết chế,
art direction chuẩn bảo tàng, khoảng trống rộng rãi.

TRÁNH — bố cục kiểu template, thiết kế thương mại rẻ tiền, phong cách
hoạt hình, render 3D, trang trí rườm rà, gradient, hiệu ứng neon,
minh họa rối rắm, và mọi hình thức bóp méo chủ thể trong ảnh.
```

### Sửa khi ra chưa đúng

- **Chọn ảnh có đường bao rõ ràng.** Muốn rút gọn thì phải có thứ để rút gọn. Cảnh rối rắm không có hình khối chủ đạo sẽ ra một mớ nhòe.
- **Nửa trừu tượng nhìn như đồ lại vụng về.** Đẩy mạnh phần rút gọn: *"không quá 5 hình khối riêng biệt."*
- **Nửa ảnh bị stylize mất.** Dời mệnh đề giữ nguyên xuống cuối prompt và thêm: *"phần ảnh phải giữ nguyên chất nhiếp ảnh."*
- **Hai nửa nhìn không liên quan.** Nhắc lại chỉ dẫn về bảng màu, và gọi tên hai ba màu bạn nhìn thấy trong ảnh gốc.

## Phần chuyển được sang mọi prompt poster khác

Bóc cả hai hệ ra thì bên dưới vẫn là bốn nước đi giống nhau:

**Nêu cấu trúc trước phong cách.** Phần trăm, số vùng, số lượng — những thứ này ràng buộc model theo cách tính từ không làm được. *"25–40% chiều cao"* là kiểm được; *"cân đối"* thì không.

**Đặt trần cho bảng màu.** Nếu chỉ đổi được một điều trong cách viết prompt tạo ảnh, hãy đổi cái này. Ba tới năm màu, nêu ra bằng một con số, là chỉ dẫn có đòn bẩy cao nhất trong cả prompt.

**Gọi tên phân cấp một cách rõ ràng.** Model mặc định làm phẳng phân cấp, vì dữ liệu huấn luyện lấy trung bình thì phẳng. Liệt kê bốn cỡ chữ khác biệt sẽ ép nó tách bạch ra.

**Cho các thành phần vượt khỏi khung của chúng.** Chiều sâu trong bố cục đến từ những thứ không chịu nằm yên trong ô của mình. Đây là chỉ dẫn hay bị thiếu nhất trong những prompt cho ra kết quả phẳng lì.

## Câu hỏi thường gặp

**Dùng được với model tạo ảnh nào?**
Bất kỳ model nào nhận prompt dài có cấu trúc — Nano Banana, Midjourney, Seedream, GPT Image, Flux. Model render chữ tốt sẽ xử lý phần phân cấp typography khá hơn; với model yếu chữ thì cứ tạo bố cục rồi tự đặt chữ vào sau.

**Dùng thương mại được không?**
Bản thân hệ bố cục là quy ước thiết kế, không phải tài sản của ai — split-level có từ trước AI hàng chục năm. Hãy kiểm tra điều khoản thương mại của chính model bạn dùng, và kiểm tra giấy phép của bất kỳ đoạn code hay skill nào bạn sử dụng.

**Làm sao để chữ trong poster đọc được?**
Viết ngắn, ghi rõ chuỗi chữ trong dấu ngoặc kép, và chuẩn bị tinh thần phải sửa. Với những thứ đưa cho khách hàng, hãy tạo bố cục bằng AI rồi dựng chữ thật bằng công cụ thiết kế đè lên trên.

**Bìa sách thì dùng hệ nào?**
Split-level. Vùng thông tin ánh xạ rất tự nhiên sang tên sách, tác giả và nhà xuất bản.

**Sao ở hệ 2 lại đảo ngược nguyên tắc 50/50?**
Vì hai nửa không tranh nhau sự chú ý — chúng là cùng một chủ thể được trình bày hai lần. Sự cân bằng ở đây đọc lên như một phép so sánh, chứ không phải sự do dự.

---

*Khung split-level trong bài được phóng tác từ một phân tích bố cục ghi nguồn Larus Canus, còn cách ảnh-chuyển-trừu-tượng từ một bài ghi nguồn VibeEverything, cả hai đang lan truyền trong cộng đồng thiết kế AI Việt Nam. Các template prompt phía trên được mình viết lại bằng ngôn từ của mình kèm phần giải thích lý do; skill mã nguồn mở triển khai hệ thứ hai đã được dẫn link ở phần nguồn.*
