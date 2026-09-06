---
title: "Đường ống ảnh trong Flutter: từ một URL tới pixel trên màn hình"
description: "Image.network giấu năm giai đoạn riêng biệt — khoá, tải, giải mã, cache, vẽ. Mọi lỗi ảnh bạn gặp (nháy khi rebuild, trắng khi cuộn ngược, bộ nhớ vọt lên) đều là một giai đoạn cụ thể đang hoạt động sai."
seoDescription: "Cách Flutter nạp ảnh: ImageProvider và khoá cache, cache bộ nhớ so với cache đĩa, cacheWidth và ResizeImage, precacheImage, placeholder và hiệu ứng mờ dần, xử lý lỗi, và các mô hình cho thư viện ảnh."
keywords:
  - cache ảnh flutter
  - cách dùng precacheimage flutter
  - flutter cached_network_image
  - flutter imageprovider resize
  - ảnh flutter bị nháy khi rebuild
  - flutter image error builder
category: "Chuyên sâu"
topic: "Flutter"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-29"
emoji: "🖼️"
tags: ["Flutter", "Hình ảnh", "Cache", "Hiệu năng", "UI"]
sources:
  - name: "ImageProvider — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/painting/ImageProvider-class.html"
  - name: "ImageCache — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/painting/ImageCache-class.html"
  - name: "precacheImage — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/precacheImage.html"
  - name: "ResizeImage — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/painting/ResizeImage-class.html"
  - name: "Image — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/Image-class.html"
  - name: "Gói cached_network_image"
    url: "https://pub.dev/packages/cached_network_image"
related:
  - slug: "flutter-memory-leaks-devtools"
    title: "Tìm rò rỉ bộ nhớ trong Flutter: năm loại đối tượng không bao giờ được dispose"
  - slug: "flutter-lists-performance-builder"
    title: "Vì sao ListView của bạn chậm, và bốn cách sửa thật sự có tác dụng"
draft: false
---

`Image.network(url)` là một trong những API thân thiện nhất của Flutter và cũng là một trong những cái dễ đánh bại bạn nhất. Nó chạy được ngay, rồi một tháng sau bạn có những tấm ảnh loé trắng mỗi lần rebuild, một thư viện ảnh tải lại khi cuộn ngược, và 400 MB bộ nhớ trên một máy 3 GB.

Cả ba đều là cùng một hiểu nhầm: `Image` là widget, nhưng việc cache và giải mã diễn ra trong một đối tượng mà nó uỷ thác — `ImageProvider`. Biết đối tượng đó đánh khoá theo cái gì, và cache cái gì, sẽ giải thích được tất cả.

## Năm giai đoạn

1. **Khoá.** `ImageProvider` sinh ra một khoá — với `NetworkImage` là URL cộng với scale. Hai provider có khoá bằng nhau là cùng một ảnh dưới góc nhìn của cache.
2. **Tải.** Byte đến từ mạng, từ asset bundle, từ file, hoặc từ bộ nhớ.
3. **Giải mã.** Byte đã nén trở thành một `dart:ui.Image`: pixel thô, `rộng × cao × 4` byte.
4. **Cache.** Ảnh đã giải mã đi vào `PaintingBinding.instance.imageCache`, đánh khoá theo bước 1.
5. **Vẽ.** Widget vẽ nó ra, áp dụng `fit`, `alignment`, và mọi bộ lọc màu.

Hệ quả quan trọng nhất: **cache lưu pixel đã giải mã, và nó đánh khoá theo provider, không theo widget**. Một widget rebuild sẽ không tải lại; một widget có khoá provider thay đổi thì có.

## Vì sao ảnh nháy khi rebuild

```dart
// Rebuild tạo ra một NetworkImage bằng nhau — chuyện này ổn.
Image.network(user.avatarUrl)

// Danh tính provider mới mỗi lần build — cũng thường ổn, vì
// NetworkImage cài đặt == theo (url, scale).
Image(image: NetworkImage(user.avatarUrl))

// Không ổn: khoá đổi khi `size` đổi, nên nó giải mã lại.
Image(image: ResizeImage(NetworkImage(url), width: size.round()))
```

`NetworkImage` và các anh em cài đặt `==` cùng `hashCode` theo đầu vào, nên tạo mới mỗi lần build vẫn trúng đúng mục cache cũ. Các trường hợp nháy là khi có thứ gì đó trong khoá thật sự thay đổi: một URL có tham số phá cache, một URL đã ký mà token xoay vòng, hoặc một `ResizeImage` có kích thước lấy từ layout dao động một pixel.

Hãy sửa cái khoá, đừng sửa widget. Hãy bỏ những tham số truy vấn hay thay đổi trước khi dựng provider, và làm tròn kích thước `ResizeImage` về những mốc ổn định thay vì truyền thẳng ràng buộc layout.

## Kích thước giải mã là cần gạt bộ nhớ

Điều này đáng nêu riêng vì nó lấn át mọi cân nhắc khác trong một ứng dụng nhiều media:

| Nguồn | Trên đĩa | Sau giải mã trong bộ nhớ |
| --- | --- | --- |
| JPEG 4000×3000 | ~2 MB | ~48 MB |
| JPEG 1200×900 | ~300 KB | ~4,3 MB |
| Thumbnail 400×300 | ~40 KB | ~0,5 MB |

Nếu bạn hiển thị một thumbnail rộng 400 pixel từ nguồn 4000 pixel, bạn đang trả khoảng một trăm lần lượng bộ nhớ cần thiết. `cacheWidth` và `cacheHeight` thay đổi chính quá trình giải mã:

```dart
Image.network(url, cacheWidth: 400, width: 200, fit: BoxFit.cover)
```

Chú ý hai con số. `width: 200` là layout — pixel logic. `cacheWidth: 400` là giải mã — pixel vật lý, tức khoảng chiều rộng logic nhân tỉ lệ pixel thiết bị. Truyền chiều rộng logic vào `cacheWidth` sẽ cho ảnh mờ trên màn hình 2x hay 3x; truyền chiều rộng gốc thì mất hết ý nghĩa.

```dart
final dpr = MediaQuery.devicePixelRatioOf(context);
Image.network(url, cacheWidth: (200 * dpr).round(), width: 200)
```

`ResizeImage` là cùng cơ chế nhưng ở dạng provider tường minh, hữu ích khi bạn đang ghép các provider thay vì dùng constructor của `Image`.

## Cache bộ nhớ so với cache đĩa

`ImageCache` dựng sẵn của Flutter **chỉ ở bộ nhớ**. Không có tầng đĩa nào: tắt ứng dụng là mọi ảnh mạng phải tải lại. Nó cũng có giới hạn, và mặc định khá khiêm tốn — một số mục tối đa và một hạn mức byte, cả hai đều nâng hoặc hạ được:

```dart
PaintingBinding.instance.imageCache
  ..maximumSize = 200
  ..maximumSizeBytes = 100 << 20;
```

Nâng những con số này làm thư viện ảnh mượt hơn và làm việc bị giết vì hết bộ nhớ dễ xảy ra hơn. Hãy hạ chúng trên thiết bị eo hẹp bộ nhớ thay vì mặc định nâng ở mọi nơi.

Để dữ liệu sống qua các lần khởi động, bạn cần một package. `cached_network_image` là lựa chọn phổ biến, cho bạn cache đĩa, `placeholder`, `errorWidget`, và cặp `memCacheWidth`/`maxWidthDiskCache` phản chiếu `cacheWidth`:

```dart
CachedNetworkImage(
  imageUrl: url,
  memCacheWidth: 800,
  placeholder: (context, url) => const _ShimmerBox(),
  errorWidget: (context, url, error) => const Icon(Icons.broken_image),
  fadeInDuration: const Duration(milliseconds: 150),
)
```

Đánh đổi ở đây rất sòng phẳng: cache đĩa nghĩa là một thư mục sẽ phình ra, một chính sách loại bỏ mà bạn nên cấu hình, và ảnh cũ nếu URL của bạn không đánh địa chỉ theo nội dung. Nếu URL ảnh chứa hash hoặc số phiên bản, cache đĩa gần như miễn phí; nếu chúng là đường dẫn có thể đổi như `/avatars/42.jpg`, bạn cần một chiến lược phá cache, nếu không người dùng sẽ thấy avatar cũ mãi.

## `precacheImage`, và khi nào nó giúp ích

```dart
@override
void didChangeDependencies() {
  super.didChangeDependencies();
  precacheImage(const AssetImage('assets/hero.webp'), context);
}
```

`precacheImage` phân giải và giải mã một ảnh vào cache trước khi nó được hiển thị, để widget hiện nó về sau vẽ ra ngay thay vì mờ dần vào. Nó thật sự hữu ích ở ba chỗ:

- **Ảnh hero của màn hình kế tiếp**, nạp trước trong khi người dùng còn ở màn hình hiện tại.
- **Các slide onboarding**, nạp trước trong lúc slide đầu tiên đang hiển thị.
- **Asset nằm trên đường tới hạn**, nạp trước lúc splash — kèm lưu ý từ việc đo khởi động rằng nó cộng thêm vào thời gian tới frame đầu nếu bạn await nó.

Nó không hữu ích, và còn có hại, khi áp cho một danh sách: nạp trước bốn mươi ảnh nghĩa là giải mã bốn mươi ảnh, đúng cái đỉnh bộ nhớ mà bạn đang muốn tránh. Hãy nạp trước thứ bạn sắp hiện, không phải thứ người dùng có thể cuộn tới.

Lưu ý `precacheImage` cần `BuildContext` nên không gọi trực tiếp từ `initState` được — `didChangeDependencies` là chỗ thường dùng.

## Placeholder, hiệu ứng mờ dần, và độ ổn định layout

Chất lượng cảm nhận của một màn hình nhiều ảnh chủ yếu nằm ở chuyện xảy ra *trước khi* ảnh đến nơi.

**Giữ chỗ sẵn.** Một tấm ảnh đến nơi rồi đẩy nội dung xuống là khiếm khuyết giao diện dễ thấy nhất. Nếu bạn biết tỉ lệ khung, hãy bọc bằng `AspectRatio`; nếu bạn biết kích thước, hãy cấp cho nó. Nếu không biết cả hai, hãy hỏi API — hầu hết API media đều trả về kích thước, và dùng nó chính là khác biệt giữa một danh sách đứng yên và một danh sách nhảy loạn.

**Mờ dần, nhưng ngắn.** `FadeInImage` và `frameBuilder` trên `Image` đều cho phép chuyển mờ từ placeholder. Hãy giữ ngắn — 100–200 ms. Một hiệu ứng dài đọc thành sự chậm chạp.

```dart
Image.network(
  url,
  frameBuilder: (context, child, frame, wasSynchronouslyLoaded) {
    if (wasSynchronouslyLoaded) return child;
    return AnimatedOpacity(
      opacity: frame == null ? 0 : 1,
      duration: const Duration(milliseconds: 150),
      child: child,
    );
  },
)
```

`wasSynchronouslyLoaded` là chi tiết người ta hay bỏ sót: một ảnh đã nằm trong cache sẽ vẽ ngay ở frame đầu tiên, và cho nó mờ dần vào sẽ khiến ảnh đã cache trông chậm hơn ảnh chưa cache ở lần xem thứ hai.

**Xử lý thất bại.** `errorBuilder` không phải tuỳ chọn trong ứng dụng thật — mạng hỏng, URL trả 404, và mặc định là một exception trong console cộng một ô trống.

```dart
Image.network(
  url,
  errorBuilder: (context, error, stack) => const _AvatarFallback(),
)
```

Cũng đáng nghĩ tới việc thử lại. `Image` dựng sẵn không tự thử lại; `cached_network_image` và các package tương tự cho bạn một điểm móc thử lại, hoặc bạn có thể ép một lần bằng cách đổi khoá provider.

## Những mô hình cho thư viện ảnh trụ được

Với một lưới hoặc một dòng tin, bốn quy tắc bao phủ gần hết:

1. `cacheWidth` đặt theo kích thước ô, không theo kích thước nguồn.
2. `GridView.builder` / `ListView.builder`, để ô ngoài màn hình không bị dựng.
3. Một `imageCache` có giới hạn chọn theo thiết bị yếu nhất bạn hỗ trợ.
4. Giải mã độ phân giải đầy đủ **chỉ** ở màn hình chi tiết, từ một URL riêng nếu API có cấp.

Điều cuối là khác biệt giữa một thư viện ảnh chạy được trên máy 2 GB và một cái thì không. Một lưới không bao giờ nên giải mã tấm ảnh mà màn hình chi tiết hiển thị.

## Câu hỏi thường gặp

**`Image.network` có cache xuống đĩa không?**

Không. Cache của framework chỉ ở bộ nhớ và không sống qua lần khởi động lại. Hãy dùng package nếu cần cache đĩa.

**Vì sao ảnh asset của tôi vẫn tải chậm?**

Asset được đọc từ bundle, việc đó nhanh, nhưng giải mã vẫn tốn. Một file PNG asset khổng lồ giải mã chậm y như một ảnh mạng khổng lồ — `cacheWidth` áp dụng cho cả asset.

**Cái gì xoá cache ảnh?**

`imageCache.clear()` dọn sạch; `imageCache.evict(provider)` gỡ một mục, và đó là cách đúng để ép tải lại một ảnh cụ thể sau khi người dùng vừa tải lên.

**Tôi có nên nâng `maximumSizeBytes` không?**

Chỉ sau khi đã đo, và chỉ khi đã xác định mức thiết bị sàn. Nó đánh đổi độ mượt lấy rủi ro hết bộ nhớ, và rủi ro đó rơi vào nhóm người dùng máy yếu nhất, cũng là nhóm ít có khả năng báo lỗi nhất.

**`Image.asset` hay `SvgPicture`?**

Asset vector tránh hẳn bài toán độ phân giải và rất nhẹ trên đĩa, đổi lại phải rasterise lúc chạy ở mỗi kích thước khác nhau. Với icon và minh hoạ phẳng, vector thường là đánh đổi tốt hơn; với ảnh chụp thì nó không phải lựa chọn.

---

*Hành vi của provider, cache, `precacheImage` và `ResizeImage` mô tả ở đây được ghi trong các trang API painting và widget của Flutter đã dẫn. Cách chia giai đoạn, bảng kích thước giải mã (số học từ rộng × cao × 4), hướng dẫn nạp trước và các quy tắc cho thư viện ảnh là đánh giá riêng của tôi từ việc dựng những màn hình nhiều media. Giá trị mặc định của cache và API của package thay đổi giữa các phiên bản — hãy đối chiếu với SDK và package bạn phát hành.*
