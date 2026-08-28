---
title: "Denial: trình quản lý cửa sổ Wayland đặt Flutter làm nền móng"
package: "Denial"
repo: "denialwm/denial"
githubUrl: "https://github.com/denialwm/denial"
category: "Framework/Core"
stars: 501
forks: 15
lastUpdate: "2026-08-27"
pubDev: ""
youtube: "https://www.youtube.com/results?search_query=denial+wayland+compositor+flutter"
priority: "High"
phase: "P1"
trendRank: 0
description: "Denial là một compositor Wayland gốc Flutter: shell viết bằng Dart chạy AOT ngay trong tiến trình compositor, client Wayland đến dưới dạng texture ngoài, và Impeller kết xuất thẳng xuống KMS."
seoDescription: "Denial nhúng Flutter Engine qua Embedder API native và kết xuất cả một desktop Linux bằng Impeller vào một atlas GBM dùng chung. Rust và Smithay nắm trạng thái Wayland; Flutter nắm chính sách desktop."
keywords:
  - denial wayland compositor
  - flutter linux desktop
  - flutter wayland
  - impeller compositor
  - smithay rust flutter
  - môi trường desktop flutter
topics:
  - wayland
  - linux
  - compositor
summary:
  - "**Denial** không phải một ứng dụng Flutter chạy trên desktop — nó *chính là* desktop, nhúng Flutter Engine vào bên trong tiến trình compositor."
  - "Rust và Smithay nắm giao thức Wayland, đầu vào, DRM/KMS; Flutter nắm bố cục shell, chuyển động và cách ghép cửa sổ."
  - "Impeller kết xuất cả desktop vào một atlas GBM dùng chung mà mỗi màn hình quét ra trực tiếp — không có lượt ghép thứ hai."
  - "**501★**, giấy phép GPLv3, đang ở public beta. Có gói x86-64 đã ký cho Arch, Debian 13, Ubuntu 24.04 và Fedora 44."
related:
  - slug: flutter-zero
    title: "Flutter Zero: Flutter khi bỏ đi dart:ui"
  - slug: pangolin-desktop
    title: "pangolin_desktop: hướng dẫn giao diện & thành phần UI trong Flutter"
  - slug: maidkit
    title: "MaidKit: bộ công cụ SSH viết bằng Flutter để quản trị server"
faq:
  - q: Denial có phải một ứng dụng Flutter chạy trên compositor Wayland không?
    a: "Không, và đó chính là điểm mấu chốt. `deniald` nhúng Flutter Engine qua Embedder API native của nó và chạy shell Dart đã biên dịch AOT ngay trong tiến trình compositor. Nó không phải client Wayland và không cần một compositor nào khác bên dưới."
  - q: Ứng dụng Wayland được vẽ ra bằng cách nào?
    a: "Bộ đệm phía client vẫn là tài nguyên native. Denial nhập nội dung đó vào dưới dạng texture ngoài và đặt vào cùng một scene Flutter với giao diện shell, rồi scene ấy kết xuất vào một atlas GBM trải toàn desktop để mỗi màn hình quét ra qua KMS."
  - q: Có hot reload được shell của desktop không?
    a: "Trên Arch thì có. Gói `denial-ui-development` cùng lệnh `denialctl ui setup` cho bạn một shell chạy JIT với hot reload mỗi khi lưu file. Việc gỡ lỗi cố tình không cho tạm dừng — dừng isolate gốc đồng nghĩa với việc đóng băng chính cái desktop bạn đang dùng."
  - q: Denial đã dùng làm desktop hằng ngày được chưa?
    a: "Nó đang ở public beta. Nó đã chạy được như một phiên Wayland đầy đủ với Xwayland, trình chiếu nhiều màn hình và chia sẻ màn hình qua portal, nhưng các API native, hợp đồng gói Flutter, cấu hình và giao thức truyền vẫn có thể thay đổi trước 1.0."
datePublished: "2026-08-28"
dateModified: "2026-08-28"
draft: false
---

[`Denial`](https://github.com/denialwm/denial) là một compositor Wayland gốc Flutter — Flutter không chạy *trên* desktop, nó là một phần nền móng của compositor. **501★**, giấy phép GPLv3, cập nhật lần cuối **2026-08-27**.

## Denial là gì?

Một ứng dụng Flutter desktop bình thường xin một cửa sổ từ compositor có sẵn. Denial đi xuống thấp hơn một tầng. `deniald` nhúng thẳng Flutter Engine qua Embedder API native của nó, và shell Dart chạy ở dạng biên dịch AOT ngay trong tiến trình compositor. Không có Hyprland hay Mutter nào bên dưới cả.

Trách nhiệm được chia rất gọn theo ranh giới Rust/Dart:

- **Rust**, dựng trên [Smithay](https://github.com/Smithay/smithay), nắm trạng thái giao thức Wayland, bộ đệm client, thiết bị nhập, tiêu điểm và grab, cấu hình màn hình, khâu trình chiếu DRM/KMS và vòng đời tài nguyên native.
- **Flutter** nắm *chính sách* desktop: bố cục shell, cửa sổ, các bề mặt hệ thống, cài đặt, chuyển động, cử chỉ, và vùng nào tham gia tương tác với shell.

Client Wayland không bao giờ đưa pixel cho Dart. Bộ đệm của chúng vẫn ở dạng native; Denial nhập nội dung vào dưới dạng texture ngoài và thả vào cùng scene Flutter với giao diện shell:

```text
Client Wayland ──> Rust / Smithay ──> texture ngoài ──> scene Flutter
       nhập liệu <──── định tuyến native <──── vùng chạm shell <─────┘
                                                                    │
Màn hình <────────────── DRM / KMS <────────────── atlas GBM dùng chung
```

## Vì sao điều này thú vị về mặt kỹ thuật

Câu chuyện Impeller là phần đáng đọc hai lần. Impeller được thiết kế để kết xuất *một ứng dụng bên trong một cửa sổ*. Denial bắt nó kết xuất cả một desktop vào các framebuffer GBM luân phiên do compositor sở hữu. Nhánh Flutter đã khóa phiên bản của họ nối thẳng đường GLES của Impeller vào atlas KMS dùng chung — trình chiếu FBO ở tầng embedder, xử lý khung hình không có đích, giữ nguyên vùng hư hại từng phần, hàng rào đồng bộ native, vòng đời texture ngoài. Mỗi màn hình quét trực tiếp phần của mình trong atlas đó. Không có lượt ghép thứ hai trên một khung hình đã xong.

Skia/Ganesh vẫn nằm trong cùng thế hệ engine như một phương án dự phòng, chọn bằng `--flutter-renderer skia` hoặc `DENIA_FLUTTER_RENDERER=skia`.

Cầu nối giữa Rust và Dart cũng cố ý được giữ hẹp. Nó chỉ mang trạng thái scene bất biến và các lệnh có giới hạn; Dart không bao giờ sở hữu file descriptor, đối tượng Wayland, ảnh EGL hay bộ đệm KMS. Ứng dụng Cài đặt là một tiến trình Wayland thông thường riêng biệt, nói chuyện với `deniald` qua một socket điều khiển Unix có đánh phiên bản, nên khối lượng kết xuất của nó không thể làm nghẽn engine của compositor. Ranh giới gói đó cũng là con đường dự tính cho các shell của bên thứ ba: một khi hợp đồng tương thích ổn định, một gói tương thích sẽ có thể thay thế shell tham chiếu mà không cần thay compositor.

## Bắt đầu

Denial phát hành các kho x86-64 chính chủ đã ký. Hãy xem [script cài đặt](https://github.com/denialwm/denial/blob/main/install.sh) trước — nó xác minh vân tay khóa phát hành và thêm kho, nhưng không cài gì cả:

```bash
curl -fsSL https://install.denialwm.org | sh
```

Rồi tùy bản phân phối của bạn:

```bash
sudo pacman -Syu denial
```

```bash
sudo apt update && sudo apt install denial
```

```bash
sudo dnf install denial
```

Gói x86-64 đã ký phủ Arch và CachyOS, Debian 13, Ubuntu 24.04 LTS, Fedora 44, cùng Alpine 3.24 qua GitHub Releases. NixOS và Void đã được thử nhưng chưa đóng gói; ARM64 được hỗ trợ đầy đủ nhưng chỉ khi tự build từ mã nguồn.

Để nghịch phần shell trên Arch có một gói riêng:

```bash
sudo pacman -S denial-ui-development
denialctl ui setup
```

Lệnh đó tạo một bản checkout mã nguồn và khởi động shell chạy JIT — mở `dart_shell/` trong trình soạn thảo là bạn có hot reload mỗi lần lưu trong khi các ứng dụng Wayland vẫn chạy. `denialctl ui restore` đưa shell tối ưu đóng gói sẵn trở lại nếu bản sửa của bạn khiến không còn cửa sổ nào dùng được.

## Khi nào nên tìm hiểu Denial?

- bạn viết Flutter và từng tự hỏi nó có thể đi xuống sâu tới đâu bên dưới tầng ứng dụng
- bạn muốn một desktop Linux mà phần shell hot reload được
- bạn quan tâm tới Embedder API, texture ngoài, hay Impeller ở ngoài bối cảnh "ứng dụng trong một cửa sổ"
- bạn đang dùng Arch, Debian 13, Ubuntu 24.04 hoặc Fedora 44 trên x86-64 và thích chạy desktop bản beta

## Điểm còn hạn chế

Đây là public beta, và README nói thẳng: API native, hợp đồng gói Flutter, cấu hình và giao thức truyền đều còn có thể đổi trước 1.0. Đây là một compositor — khi nó hỏng, nó không hỏng gọn trong một cửa sổ.

Nó phụ thuộc vào một **nhánh Flutter đã khóa** với thế hệ engine ghim cứng. Điều đó là không tránh khỏi với những gì nó làm trên đường trình chiếu của Impeller, nhưng cũng nghĩa là engine của Denial đi theo lịch của Denial, không phải của Flutter.

Độ phủ hẹp hơn vẻ ngoài của bảng bản phân phối: ARM64 chạy được nhưng không có bản nhị phân công bố, NixOS và Void không có gói chính chủ, còn Alpine chỉ có file tải về đã ký chứ không có kho. Khả năng gỡ lỗi cũng bị giới hạn có chủ ý — bộ điều hợp gỡ lỗi trong trình soạn thảo không thể tạm dừng, đặt breakpoint hay đánh giá biểu thức, vì dừng isolate gốc sẽ đóng băng chính cái desktop bạn đang ngồi trước mặt.

Và giấy phép là GPLv3, một lựa chọn đúng cho một compositor nhưng đáng biết trước khi bạn định làm bất cứ thứ gì phái sinh.

## Các lựa chọn đáng so sánh

- [Flutter Zero: Flutter khi bỏ đi dart:ui](/vi/recipes/flutter-zero/) — dự án còn lại đang hỏi Flutter thật sự là gì bên dưới framework
- [pangolin_desktop: hướng dẫn giao diện & thành phần UI trong Flutter](/vi/recipes/pangolin-desktop/) — một *môi trường* desktop viết bằng Flutter thay vì một compositor
- Hyprland, Sway, niri — các compositor Wayland đã chín, nếu bạn muốn một desktop chứ không phải một thí nghiệm

## Câu hỏi thường gặp

### Denial có phải một ứng dụng Flutter chạy trên compositor Wayland không?

Không, và đó chính là điểm mấu chốt. `deniald` nhúng Flutter Engine qua Embedder API native của nó và chạy shell Dart đã biên dịch AOT ngay trong tiến trình compositor. Nó không phải client Wayland và không cần một compositor nào khác bên dưới.

### Ứng dụng Wayland được vẽ ra bằng cách nào?

Bộ đệm phía client vẫn là tài nguyên native. Denial nhập nội dung đó vào dưới dạng texture ngoài và đặt vào cùng một scene Flutter với giao diện shell, rồi scene ấy kết xuất vào một atlas GBM trải toàn desktop để mỗi màn hình quét ra qua KMS.

### Có hot reload được shell của desktop không?

Trên Arch thì có. Gói `denial-ui-development` cùng lệnh `denialctl ui setup` cho bạn một shell chạy JIT với hot reload mỗi khi lưu file. Việc gỡ lỗi cố tình không cho tạm dừng — dừng isolate gốc đồng nghĩa với việc đóng băng chính cái desktop bạn đang dùng.

### Denial đã dùng làm desktop hằng ngày được chưa?

Nó đang ở public beta. Nó đã chạy được như một phiên Wayland đầy đủ với Xwayland, trình chiếu nhiều màn hình và chia sẻ màn hình qua portal, nhưng các API native, hợp đồng gói Flutter, cấu hình và giao thức truyền vẫn có thể thay đổi trước 1.0.

## Tài nguyên & liên kết

- **GitHub:** [denialwm/denial](https://github.com/denialwm/denial)
- **Website:** [denialwm.org](https://denialwm.org)

---

*Thuộc [FlutterCook](/vi/recipes/) — hướng dẫn thực hành về các thư viện, UI kit và ứng dụng Flutter mã nguồn mở tốt nhất. Xem [xu hướng GitHub](/vi/trends/) hoặc [hướng dẫn YouTube](/vi/youtube/).*
