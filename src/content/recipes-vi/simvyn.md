---
title: "simvyn: một bảng điều khiển cho mọi simulator, emulator và thiết bị"
package: "simvyn"
repo: "pranshuchittora/simvyn"
githubUrl: "https://github.com/pranshuchittora/simvyn"
category: "Library/Tooling"
stars: 351
forks: 24
lastUpdate: "2026-08-05"
pubDev: ""
youtube: "https://www.youtube.com/results?search_query=simvyn+ios+simulator+android+emulator"
priority: "High"
phase: "P1"
trendRank: 0
description: "simvyn gom iOS Simulator, Android Emulator và thiết bị USB về một dashboard web và một CLI — log, GPS, database, file, push, ảnh chụp — mà không cần mở Xcode hay Android Studio."
seoDescription: "simvyn là công cụ devtool đa nền tảng cho iOS Simulator, Android Emulator và máy thật. Trình xem database, trình xem log, giả lập vị trí và CLI đầy đủ, chỉ với npx simvyn."
keywords:
  - simvyn
  - quản lý ios simulator
  - dashboard android emulator
  - công cụ thiết bị flutter
  - xem sqlite flutter
  - devtools di động cli
topics:
  - devtools
  - simulator
  - cli
summary:
  - "**simvyn** là một dashboard và một CLI cho iOS Simulator, Android Emulator và cả thiết bị thật cắm USB."
  - "Chạy bằng `npx simvyn` — không cần cài, không cần cấu hình, thiết bị được tự động nhận diện."
  - "Phần bạn sẽ dùng hằng ngày: trình xem SQLite và SharedPreferences, log realtime có tìm kiếm regex, phát lại lộ trình GPS, và duyệt file trong sandbox của app."
  - "**351★**, cần Node 22+, macOS để hỗ trợ đầy đủ hoặc Linux thì chỉ có Android."
related:
  - slug: tapflow
    title: "tapflow: stream simulator tự host cho cả nhóm"
  - slug: flutter-skill
    title: "flutter-skill: cho AI agent điều khiển ứng dụng đang chạy"
  - slug: simutil
    title: "simutil: hướng dẫn giao diện & thành phần UI trong Flutter"
faq:
  - q: Có cần cài simvyn không?
    a: "Không. `npx simvyn` khởi động server cục bộ, mở dashboard trong trình duyệt và tự phát hiện mọi simulator, emulator, thiết bị USB đang kết nối. Nếu dùng hằng ngày thì có thể cài toàn cục bằng `npm install -g simvyn`."
  - q: simvyn có chạy trên Windows không?
    a: "Không. Nó cần macOS để hỗ trợ đầy đủ iOS và Android, hoặc Linux thì chỉ có Android. Điều khiển iOS Simulator phụ thuộc công cụ dòng lệnh của Xcode, thứ không tồn tại ngoài macOS."
  - q: simvyn có dành riêng cho Flutter không?
    a: "Không, và đó mới là điểm hay. Nó điều khiển simulator và thiết bị chứ không phải framework, nên cùng một dashboard dùng được cho app Flutter, React Native, SwiftUI native và Jetpack Compose."
  - q: Nó xem được database cục bộ của app không?
    a: "Có. Trình xem database duyệt bảng SQLite và chạy câu truy vấn SQL, đồng thời đọc SharedPreferences trên Android và NSUserDefaults trên iOS. Với app Flutter dùng sqflite hay Drift, đó chính là toàn bộ kho dữ liệu cục bộ, không cần thêm mã debug nào."
datePublished: "2026-08-28"
dateModified: "2026-08-28"
draft: false
---

[`simvyn`](https://github.com/pranshuchittora/simvyn) là một dashboard và một CLI cho mọi thiết bị bạn phát triển trên đó — iOS Simulator, Android Emulator và máy thật qua USB. **351★**, cập nhật lần cuối **2026-08-05**. Chạy bằng một lệnh, không cần cấu hình.

## simvyn là gì?

Phát triển di động khiến việc điều khiển thiết bị bị phân mảnh qua quá nhiều công cụ. Khởi động simulator thì mở Xcode. Xóa sạch emulator thì mở Android Studio. Đọc log thì `adb logcat` ở một cửa sổ và Console.app ở cửa sổ khác. Đặt vị trí GPS giả thì mỗi nền tảng một hộp thoại. Xem file SQLite của app thì phải kéo thủ công ra khỏi thiết bị.

simvyn gom tất cả về một dashboard web, và ánh xạ mọi tính năng sang CLI để chạy được cả khi không có giao diện:

```bash
npx simvyn
```

Lệnh đó khởi động server cục bộ, mở dashboard và tự phát hiện mọi thứ đang kết nối — simulator, emulator, thiết bị USB.

## Vì sao lập trình viên Flutter nên quan tâm

Flutter đã trừu tượng hóa phần *ứng dụng* qua các nền tảng. simvyn trừu tượng hóa phần *thiết bị*, nửa còn lại mà Flutter chưa bao giờ động tới. `flutter run` chọn thiết bị nhưng không giúp gì cho những việc xung quanh.

Ba tính năng có giá trị ngay trong quy trình Flutter:

**Trình xem database.** Duyệt bảng SQLite và chạy truy vấn SQL, thêm SharedPreferences trên Android và NSUserDefaults trên iOS. Nếu app dùng `sqflite`, Drift hay `shared_preferences`, đó chính là toàn bộ lớp lưu trữ cục bộ, xem được mà không phải viết màn hình debug.

**Trình duyệt file.** Duyệt sandbox của app, tải file lên/xuống, sửa văn bản ngay tại chỗ. Tái hiện lỗi cache hỏng không còn là công việc khảo cổ.

**Giả lập vị trí.** Đặt tọa độ, hoặc phát lại lộ trình GPX/KML kèm điều chỉnh tốc độ. Thử tính năng bản đồ hay giao hàng không còn nghĩa là đi vòng quanh văn phòng.

Ngoài ra: log realtime có lọc theo mức và tìm kiếm regex, chụp ảnh và quay màn hình có lưu lịch sử, mở deep link kèm danh sách yêu thích, gửi payload thông báo đẩy tới iOS Simulator, đọc/ghi clipboard, log crash, và đẩy ảnh/video vào thư viện của máy.

Tính năng Collections là thứ dễ bị bỏ qua. Gói một chuỗi thao tác thiết bị — đặt ngôn ngữ, bật chế độ tối, gieo vị trí, cài bản build — rồi áp cho nhiều thiết bị cùng lúc. Đó là quy trình chuẩn bị QA của bạn được đóng thành một đối tượng dùng lại được.

## Khi nào nên dùng simvyn?

- bạn liên tục chuyển qua lại giữa iOS và Android và chán phải mở hai IDE chỉ để làm việc vặt với thiết bị
- bạn cần xem trạng thái trên máy — bảng dữ liệu, preferences, file sandbox — mà không phải dựng giao diện debug
- bạn thử vị trí, deep link hay push và muốn việc đó lặp lại được thay vì làm tay
- bạn muốn một AI agent điều khiển thiết bị; chính bề mặt CLI đầy đủ khiến điều đó khả thi

## Điểm còn hạn chế

Không có Windows. macOS cho bạn cả iOS lẫn Android; Linux chỉ có Android. Với nhóm Flutter dùng Windows thì đây là điểm chặn, và không cấu hình nào cứu được — điều khiển iOS Simulator cần công cụ dòng lệnh của Xcode.

Yêu cầu Node 22.12 trở lên, mới hơn mức mặc định trên nhiều máy.

Repo cũng không có file giấy phép, điều đáng lưu ý với một công cụ bạn chạy trên các bản build nội bộ trước khi đưa vào quy trình chung của nhóm. Đó là thiếu sót giấy tờ hơn là kỹ thuật, nhưng lại đúng loại thiếu sót khiến khâu rà soát bảo mật phải dừng lại.

## Các lựa chọn đáng so sánh

- [tapflow: stream simulator tự host cho cả nhóm](/vi/recipes/tapflow/) — phiên bản nhiều người dùng của cùng bài toán
- [flutter-skill: cho AI agent điều khiển ứng dụng đang chạy](/vi/recipes/flutter-skill/) — điều khiển ứng dụng thay vì thiết bị
- [simutil: hướng dẫn giao diện & thành phần UI trong Flutter](/vi/recipes/simutil/) — TUI nhẹ hơn nếu bạn chỉ cần khởi động thiết bị

## Câu hỏi thường gặp

### Có cần cài simvyn không?

Không. `npx simvyn` khởi động server cục bộ, mở dashboard trong trình duyệt và tự phát hiện mọi simulator, emulator, thiết bị USB đang kết nối. Nếu dùng hằng ngày thì có thể cài toàn cục bằng `npm install -g simvyn`.

### simvyn có chạy trên Windows không?

Không. Nó cần macOS để hỗ trợ đầy đủ iOS và Android, hoặc Linux thì chỉ có Android. Điều khiển iOS Simulator phụ thuộc công cụ dòng lệnh của Xcode, thứ không tồn tại ngoài macOS.

### simvyn có dành riêng cho Flutter không?

Không, và đó mới là điểm hay. Nó điều khiển simulator và thiết bị chứ không phải framework, nên cùng một dashboard dùng được cho app Flutter, React Native, SwiftUI native và Jetpack Compose.

### Nó xem được database cục bộ của app không?

Có. Trình xem database duyệt bảng SQLite và chạy câu truy vấn SQL, đồng thời đọc SharedPreferences trên Android và NSUserDefaults trên iOS. Với app Flutter dùng `sqflite` hay Drift, đó chính là toàn bộ kho dữ liệu cục bộ, không cần thêm mã debug nào.

## Tài nguyên & liên kết

- **GitHub:** [pranshuchittora/simvyn](https://github.com/pranshuchittora/simvyn)
- **npm:** [simvyn](https://www.npmjs.com/package/simvyn)

---

*Thuộc [FlutterCook](/vi/recipes/) — hướng dẫn thực hành về các thư viện, UI kit và ứng dụng Flutter mã nguồn mở tốt nhất. Xem [xu hướng GitHub](/vi/trends/) hoặc [hướng dẫn YouTube](/vi/youtube/).*
