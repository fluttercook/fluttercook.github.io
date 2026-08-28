---
title: "MaidKit: bộ công cụ SSH viết bằng Flutter để quản trị server"
package: "MaidKit"
repo: "Solsynth/MaidKit"
githubUrl: "https://github.com/Solsynth/MaidKit"
category: "App/Template"
stars: 426
forks: 35
lastUpdate: "2026-08-26"
pubDev: ""
youtube: "https://www.youtube.com/results?search_query=maidkit+ssh+flutter"
priority: "High"
phase: "P1"
trendRank: 0
description: "MaidKit là trình quản lý server qua SSH đa nền tảng viết bằng Flutter — terminal, SFTP, systemd, tường lửa, container và một AI agent, tất cả qua SSH thuần mà không cài gì lên máy chủ."
seoDescription: "MaidKit là ứng dụng Flutter giấy phép AGPL-3.0 dùng để quản trị server: terminal SSH chia khung, SFTP hai khung, Docker và Podman, cơ sở dữ liệu, két mật khẩu AES-GCM và một MCP server cục bộ."
keywords:
  - maidkit
  - flutter ssh client
  - trình quản lý server mã nguồn mở
  - ví dụ ứng dụng flutter desktop
  - ứng dụng terminal ssh flutter
  - quản lý docker trên di động
topics:
  - ssh
  - devops
  - desktop
summary:
  - "**MaidKit** quản trị server qua SSH thuần — không cài agent nào lên máy, trừ khi bạn tự chọn dùng daemon MaidCafe."
  - "Terminal chia khung, SFTP hai khung, systemd, nginx/Caddy, tường lửa, crontab, gói phần mềm, Docker/Podman, sao lưu Postgres/MySQL."
  - "Thông tin đăng nhập nằm trong két AES-GCM 256 với PBKDF2 310.000 vòng lặp và mở khóa sinh trắc học."
  - "**426★**, giấy phép AGPL-3.0, Flutter SDK `^3.12.2`. Đây là một ứng dụng chứ không phải gói thư viện — `publish_to: none`."
related:
  - slug: flutter-server-box
    title: "flutter_server_box: hướng dẫn thư viện & công cụ trong Flutter"
  - slug: droiddesk
    title: "DroidDesk: hướng dẫn thư viện & công cụ trong Flutter"
  - slug: denial
    title: "Denial: trình quản lý cửa sổ Wayland đặt Flutter làm nền móng"
faq:
  - q: MaidKit có cài gì lên server của tôi không?
    a: "Với công việc hằng ngày thì không — việc quản trị hoàn toàn dựa trên SSH và được thiết kế để không xâm lấn. Daemon MaidCafe tùy chọn bổ sung chỉ số cho cả dàn máy, tác vụ theo lịch và cảnh báo đẩy; nó chỉ kết nối ra ngoài nên không mở cổng vào nào."
  - q: MaidKit có trên pub.dev không?
    a: "Không. File pubspec đặt `publish_to: \"none\"` vì đây là một ứng dụng chứ không phải gói thư viện. Hãy tải bản build từ solsynth.dev hoặc tự build bằng Flutter SDK."
  - q: Thông tin đăng nhập SSH được lưu thế nào?
    a: "Trong một két AES-GCM 256 bit với hàm dẫn xuất khóa PBKDF2 chạy 310.000 vòng lặp, kèm mở khóa sinh trắc học, đồng bộ đám mây đã mã hóa (tùy chọn) và file sao lưu `.mkb` đã mã hóa. Access token GitHub cũng nằm trong cùng két đó."
  - q: AI agent thật sự làm được gì?
    a: "Nó vận hành server của bạn thông qua các công cụ, dùng nhà cung cấp AI của chính bạn hoặc Solar Network AI, mở rộng bằng MCP server và skill. Ở chế độ rà soát, mọi hành động được đề xuất đều phải được phê duyệt trước khi chạy, và lịch sử hội thoại nằm trên máy, ngoài két."
datePublished: "2026-08-28"
dateModified: "2026-08-28"
draft: false
---

[`MaidKit`](https://github.com/Solsynth/MaidKit) là trình quản lý server qua SSH đa nền tảng viết bằng Flutter, phủ từ terminal chia khung cho tới sao lưu Postgres. **426★**, giấy phép AGPL-3.0, cập nhật lần cuối **2026-08-26**.

## MaidKit là gì?

MaidKit là bộ công cụ tác giả tự làm để bảo trì server — cái tên đến từ ý "làm người giúp việc cho server". Ràng buộc chủ đạo của nó là việc quản trị hằng ngày phải **hoàn toàn dựa trên SSH và không cài gì lên máy chủ**. Phần lớn bảng điều khiển quản trị server đều muốn có một agent trên mọi máy; mặc định của MaidKit là server của bạn vẫn nguyên như cũ.

Đổi lại, từ một ứng dụng Flutter trên desktop hoặc di động, bạn có:

- bảng điều khiển server với trạng thái trực tiếp, độ trễ mạng và độ trễ đi về của SSH, tải, bộ nhớ và thời gian hoạt động, có nhóm và gắn thẻ
- terminal SSH đầy đủ với chia khung, kéo thả tab, bảng lệnh, hỗ trợ clipboard OSC 52 và các bảng màu
- trình duyệt SFTP hai khung với truyền file kéo thả, trình soạn thảo ngay trong app và phím tắt
- unit systemd, cấu hình nginx và Caddy, crontab, gói phần mềm (apt, dnf và hơn nữa), tiến trình
- quản lý tường lửa trên UFW, firewalld, nftables và iptables
- chuyển tiếp cổng với các preset tự khởi động khi kết nối, proxy HTTP CONNECT/SOCKS5, và jump host
- container Docker và Podman có gom nhóm theo dự án compose
- xem xét PostgreSQL, MySQL và MariaDB, sao lưu/phục hồi logic và pgBackRest
- Tailscale qua một node nhúng — không cần cài ứng dụng Tailscale

Nếu bạn cần nhiều hơn những gì SSH cho được, daemon **MaidCafe** tùy chọn bổ sung chỉ số cho cả dàn máy truyền qua SSE, tác vụ theo lịch, xem log container theo thời gian thực và ngưỡng cảnh báo. Nó chỉ kết nối ra ngoài nên không mở cổng vào nào.

## Vì sao lập trình viên Flutter nên đọc

Có hai lý do, và lý do thứ nhất là MaidKit là một mẫu vật hiếm có của một ứng dụng Flutter desktop *nghiêm túc*. Terminal chia khung, kéo thả sắp xếp tab, quản lý file hai khung có phím tắt, bảng lệnh, bộ kết xuất terminal chọn được (libghostty-vt của Ghostty hoặc xterm), và một thư viện native được biên dịch từ mã nguồn để đưa lên iOS App Store. Phần lớn ví dụ "ứng dụng Flutter desktop" chỉ là một thanh bên và một danh sách. Đây thì không.

Mô hình bảo mật cũng đáng nghiên cứu: két thông tin đăng nhập AES-GCM 256 bit, PBKDF2 310.000 vòng lặp, mở khóa sinh trắc học, đồng bộ đám mây tùy chọn chỉ với dữ liệu đã mã hóa, và file sao lưu `.mkb` đã mã hóa. Thậm chí còn có tùy chọn "ẩn địa chỉ server khi chia sẻ màn hình", điều cho thấy đã có người thật sự demo cái này trong một cuộc họp.

Lý do thứ hai là phần AI, được thiết kế cẩn thận hơn mặt bằng chung. Agent của MaidKit vận hành server thông qua các công cụ với nhà cung cấp của chính bạn, mở rộng bằng MCP server và skill, và **ở chế độ rà soát thì hành động được đề xuất phải được phê duyệt** trước khi chạy. Ở chiều ngược lại, MaidKit phơi bày một *MCP server cục bộ* để Claude Desktop hay bất kỳ client MCP nào khác chạm tới các server SSH, đoạn lệnh và skill của nó. Cả hai chiều, và chiều nguy hiểm thì luôn có con người ở giữa.

## Bắt đầu

MaidKit là một ứng dụng chứ không phải gói thư viện — pubspec của nó ghi `publish_to: "none"`. Tải bản build từ [solsynth.dev](https://solsynth.dev/products/maid-kit), hoặc tự build:

```bash
flutter pub get
flutter run
```

Nó cần Flutter SDK `^3.12.2`. Các điều kiện tiên quyết theo nền tảng là có thật:

- **Linux:** `ninja-build`, `libgtk-3-dev`, `libayatana-appindicator3-dev`, `keybinder-3.0`, `libnotify-dev`
- **Windows:** NASM, do native asset của `webcrypto` yêu cầu
- **Đóng gói cho iOS App Store:** Zig 0.15 (`brew install zig@0.15`) cho phần Ghostty đi kèm — mã nguồn Ghostty hiện tại không build được với Zig 0.16

Để phân phối trên Linux có sẵn script tạo AppImage:

```bash
flutter build linux
bash buildtools/build-appimage.sh
```

## Khi nào nên tìm hiểu MaidKit?

- bạn quản trị vài server và muốn một ứng dụng duy nhất lo cả terminal, file, dịch vụ và container
- bạn nhất định không cài agent quản trị lên máy chủ production
- bạn muốn một codebase Flutter desktop thật, lớn, đang được phát triển tích cực để học
- bạn muốn một AI agent có quyền truy cập server nhưng biết hỏi trước khi làm

## Điểm còn hạn chế

**AGPL-3.0** là thứ đầu tiên cần kiểm tra. Với việc dùng ứng dụng thì nó không thay đổi gì. Với việc mượn code vào sản phẩm của bạn — mà phần terminal, két mật khẩu và SFTP thì thật sự hấp dẫn — đó là nghĩa vụ copyleft mạnh, mở rộng cả qua mạng. Hãy đọc kỹ trước khi sao chép bất cứ thứ gì.

Khâu build có những chỗ gai góc. Một phiên bản Zig ghim cứng cho iOS, NASM trên Windows, năm gói apt trên Linux: đây là ứng dụng Flutter có phần đuôi native, và việc dựng CI không phải chuyện năm phút.

Tầng MaidCafe, nơi có những tính năng quản lý dàn máy thú vị nhất, gắn với tài khoản Solarpass và workspace của Solar Network. Cài đặt có hỗ trợ endpoint tự host, nhưng con đường trơn tru thì đi qua dịch vụ của tác giả — đáng biết trước khi bạn dựng quy trình làm việc trên nó.

Và danh sách tính năng thì khổng lồ so với tuổi đời dự án. Bề rộng như vậy thường đồng nghĩa với chiều sâu không đều; hãy kiểm chứng đúng phần bạn quan tâm thay vì mặc định cả bề mặt đều vững như nhau.

## Các lựa chọn đáng so sánh

- [flutter_server_box: hướng dẫn thư viện & công cụ trong Flutter](/vi/recipes/flutter-server-box/) — bản tương đương gần nhất trong hệ Flutter, nhẹ hơn và hẹp hơn
- Termius, Royal TSX — các client SSH thương mại đã chín
- [DroidDesk: hướng dẫn thư viện & công cụ trong Flutter](/vi/recipes/droiddesk/) — một desktop Linux trên điện thoại, thay vì một trình quản lý cho máy ở xa

## Câu hỏi thường gặp

### MaidKit có cài gì lên server của tôi không?

Với công việc hằng ngày thì không — việc quản trị hoàn toàn dựa trên SSH và được thiết kế để không xâm lấn. Daemon MaidCafe tùy chọn bổ sung chỉ số cho cả dàn máy, tác vụ theo lịch và cảnh báo đẩy; nó chỉ kết nối ra ngoài nên không mở cổng vào nào.

### MaidKit có trên pub.dev không?

Không. File pubspec đặt `publish_to: "none"` vì đây là một ứng dụng chứ không phải gói thư viện. Hãy tải bản build từ solsynth.dev hoặc tự build bằng Flutter SDK.

### Thông tin đăng nhập SSH được lưu thế nào?

Trong một két AES-GCM 256 bit với hàm dẫn xuất khóa PBKDF2 chạy 310.000 vòng lặp, kèm mở khóa sinh trắc học, đồng bộ đám mây đã mã hóa (tùy chọn) và file sao lưu `.mkb` đã mã hóa. Access token GitHub cũng nằm trong cùng két đó.

### AI agent thật sự làm được gì?

Nó vận hành server của bạn thông qua các công cụ, dùng nhà cung cấp AI của chính bạn hoặc Solar Network AI, mở rộng bằng MCP server và skill. Ở chế độ rà soát, mọi hành động được đề xuất đều phải được phê duyệt trước khi chạy, và lịch sử hội thoại nằm trên máy, ngoài két.

## Tài nguyên & liên kết

- **GitHub:** [Solsynth/MaidKit](https://github.com/Solsynth/MaidKit)
- **Tải về:** [solsynth.dev/products/maid-kit](https://solsynth.dev/products/maid-kit)

---

*Thuộc [FlutterCook](/vi/recipes/) — hướng dẫn thực hành về các thư viện, UI kit và ứng dụng Flutter mã nguồn mở tốt nhất. Xem [xu hướng GitHub](/vi/trends/) hoặc [hướng dẫn YouTube](/vi/youtube/).*
