---
title: "Vì sao ListView của bạn chậm, và bốn cách sửa thật sự có tác dụng"
description: "Một danh sách giật gần như không bao giờ là lỗi của widget danh sách. Nó là một trong bốn thứ: bạn dựng tất cả cùng lúc, mỗi mục quá đắt, chiều dài cuộn chưa biết, hoặc bạn đang giải mã ảnh nguyên cỡ cho từng dòng."
seoDescription: "Sửa danh sách Flutter chậm: ListView.builder so với ListView, itemExtent và prototypeItem, const và RepaintBoundary, kích thước giải mã ảnh, key và keepAlive, và cách đo giật khi cuộn."
keywords:
  - hiệu năng listview flutter
  - listview builder so với listview
  - flutter itemextent prototypeitem
  - đo giật khi cuộn flutter
  - repaintboundary trong danh sách flutter
  - flutter keepalive danh sách
category: "Chuyên sâu"
topic: "Flutter"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-28"
emoji: "📜"
tags: ["Flutter", "Hiệu năng", "ListView", "Cuộn", "DevTools"]
sources:
  - name: "ListView — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/ListView-class.html"
  - name: "SliverChildBuilderDelegate — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/SliverChildBuilderDelegate-class.html"
  - name: "RepaintBoundary — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/RepaintBoundary-class.html"
  - name: "Flutter — Performance best practices"
    url: "https://docs.flutter.dev/perf/best-practices"
  - name: "AutomaticKeepAliveClientMixin — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/AutomaticKeepAliveClientMixin-mixin.html"
  - name: "Flutter — UI performance profiling"
    url: "https://docs.flutter.dev/perf/ui-performance"
related:
  - slug: "flutter-image-caching-precache"
    title: "Đường ống ảnh trong Flutter: từ một URL tới pixel trên màn hình"
  - slug: "flutter-slivers-custom-scroll"
    title: "Hiểu đúng về sliver: giao thức đứng sau mọi hiệu ứng cuộn trong Flutter"
draft: false
---

Đội Flutter nào cũng gặp chuyện này. Danh sách chạy ngon với hai mươi mục lúc phát triển, phát hành, rồi một người dùng có tám trăm mục đã lưu báo rằng cuộn bị khựng và ứng dụng cảm giác nặng nề. Phản xạ đầu tiên là đổ lỗi cho `ListView`, cho Flutter, hoặc cho cái máy.

`ListView` không có lỗi. Trong mọi danh sách chậm tôi từng phân tích, nguyên nhân là một trong bốn thứ, và phân biệt chúng mất khoảng mười phút.

## Trước tiên: xem luồng nào đang trễ

Trước khi đổi bất cứ thứ gì, hãy chạy ở **chế độ profile trên thiết bị thật** và mở performance view của DevTools. Mỗi frame được vẽ thành hai thanh:

- **Luồng UI dài** → build và layout đang đắt. `itemBuilder` của bạn làm quá nhiều việc.
- **Luồng raster dài** → vẽ đang đắt. Bóng đổ, làm mờ, lớp opacity, saveLayer, ảnh lớn.

Phân biệt đó loại bỏ ngay một nửa số cách sửa khả dĩ. Thêm `RepaintBoundary` vào một danh sách mà nút thắt nằm ở luồng UI chẳng có tác dụng gì; đơn giản hoá cấu trúc widget trong một danh sách mà luồng raster đang bão hoà vì `BackdropFilter` cũng vậy.

## Cách 1: dựng theo kiểu lười

```dart
// Dựng cả 800 con ngay lập tức, ở frame đầu tiên.
ListView(children: items.map(ItemTile.new).toList())

// Chỉ dựng những gì gần khung nhìn.
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, i) => ItemTile(items[i]),
)
```

`ListView(children: ...)` nhận một danh sách đã được dựng sẵn toàn bộ. Mọi widget con đều được khởi tạo, và mọi cái đều được layout, trước khi frame đầu tiên xuất hiện. Với hai mươi mục thì không thấy gì; với tám trăm mục thì đó là một cú khựng vài giây lúc mở và một khoản bộ nhớ thường trực.

`ListView.builder` dùng `SliverChildBuilderDelegate`, chỉ gọi builder của bạn cho những con nằm trong và gần khung nhìn, rồi huỷ những con cuộn ra đủ xa. Đây là nguyên nhân phổ biến nhất khiến danh sách chậm, và cách sửa chỉ là một dòng.

Điều tương tự áp dụng cho `Column` bên trong `SingleChildScrollView`: nó luôn dựng hết. Với danh sách dài, đó là công cụ sai bất kể các con được tạo ra thế nào. Với một màn hình ngắn, nội dung hỗn hợp, thì nó lại đúng — ranh giới đại khái là "cái này có vừa trong hai ba màn hình không".

## Cách 2: làm cho mỗi mục thật rẻ

Khi việc dựng đã lười, chi phí trên mỗi mục mới quan trọng. Những thủ phạm quen thuộc:

**Làm việc bên trong `itemBuilder`.** Định dạng ngày, phân tích chuỗi, sắp xếp, lọc, hay tính một giá trị dẫn xuất bên trong builder sẽ chạy cho mọi mục đang hiển thị, ở mọi frame có rebuild. Hãy làm một lần, ở phía trên:

```dart
// Sai: DateFormat được tạo cho từng mục, ở mỗi lần rebuild.
itemBuilder: (context, i) =>
    Text(DateFormat.yMMMd().format(items[i].date)),

// Đúng: tạo bộ định dạng một lần.
final _fmt = DateFormat.yMMMd();
itemBuilder: (context, i) => Text(_fmt.format(items[i].date)),
```

**Thiếu `const`.** Một widget `const` không bị dựng lại và không bị tạo lại. Trong một danh sách trăm dòng, những `const Icon`, `const SizedBox` và `const Divider` cộng dồn lại rất đáng kể.

**Lồng sâu không cần thiết.** Sáu `Container` lồng nhau với padding và decoration là sáu render object cho mỗi dòng. Một `Container` duy nhất với `EdgeInsets` và `BoxDecoration` làm đúng việc đó với một cái.

**Vẽ đắt.** `Opacity`, `ClipRRect`, `BackdropFilter` và `BoxShadow` mỗi cái đều tốn thời gian raster thật, và trong danh sách bạn trả phí theo từng dòng đang hiển thị. Riêng `Opacity` kích hoạt một `saveLayer`; nếu bạn chỉ cần một màu nhạt đi, `Color.withValues(alpha: ...)` rẻ hơn nhiều. Nếu bạn cần bo góc trên một màu đặc, `BoxDecoration(borderRadius: ...)` thắng `ClipRRect`.

**`RepaintBoundary` cho những mục có hoạt ảnh.** Nếu một dòng vẽ lại — thanh tiến trình, hiệu ứng shimmer, hoạt ảnh nút thích — mà không có ranh giới, nó có thể buộc cả lớp danh sách vẽ lại.

```dart
itemBuilder: (context, i) => RepaintBoundary(child: ItemTile(items[i])),
```

Đây là cách sửa cho luồng raster, không phải luồng UI. Rải nó khắp nơi theo mặc định sẽ thêm lớp và có thể làm mọi thứ tệ hơn; đặt đúng vào những dòng thật sự có hoạt ảnh thì đó là khoản thắng rõ ràng.

## Cách 3: nói cho danh sách biết mỗi mục cao bao nhiêu

Một scroll view phải biết tổng chiều dài của nó để vẽ đúng thanh cuộn và để nhảy tới một vị trí. Nếu chiều cao của mọi mục đều chưa biết, nó buộc phải layout để biết.

```dart
// Tốt nhất, khi mọi dòng cùng chiều cao:
ListView.builder(itemExtent: 72, ...)

// Khi các dòng đồng nhất nhưng bạn không muốn ghi cứng con số:
ListView.builder(prototypeItem: const ItemTile.placeholder(), ...)
```

`itemExtent` cho phép framework tính vị trí bằng số học thay vì layout. Trên danh sách dài, đó là khoản tiết kiệm đáng kể, và nó khiến `jumpTo` cùng thao tác kéo thanh cuộn trở nên chính xác thay vì xấp xỉ. `prototypeItem` đo một thể hiện rồi dùng chiều dài đó, tức là cùng tối ưu mà không có con số ma thuật.

Cả hai đều không dùng được nếu các dòng thật sự khác chiều cao. Khi đó, hãy chấp nhận chi phí — hoặc chuẩn hoá thiết kế để chúng không khác nhau, vốn thường là câu trả lời tốt hơn cho một dòng tin.

## Cách 4: đặt kích thước ảnh theo ô

Đây là cách biến một danh sách vốn đúng về kỹ thuật thành một thảm hoạ bộ nhớ.

```dart
itemBuilder: (context, i) => Image.network(
  items[i].thumbUrl,
  cacheWidth: 160,   // pixel vật lý, khớp với ô
  width: 56,
  height: 56,
  fit: BoxFit.cover,
),
```

Bộ nhớ ảnh sau giải mã là rộng × cao × 4 byte, bất kể kích thước file. Bốn mươi dòng, mỗi dòng giải mã một nguồn 3000 pixel, là hàng gigabyte pixel cho một màn hình hiển thị thumbnail 56 pixel. `cacheWidth` thay đổi quá trình giải mã chứ không chỉ phần hiển thị, và nó thường chính là khác biệt giữa một danh sách sống sót trên máy yếu và một cái thì không.

## Câu chuyện `keepAlive`

Mặc định, `ListView.builder` huỷ trạng thái của một mục khi mục đó cuộn ra ngoài phạm vi cache. Đó là thứ khiến nó tiết kiệm bộ nhớ — và cũng là lý do video ở dòng 3 dừng lại, hay ô nhập liệu đang gõ dở mất nội dung, khi bạn cuộn đi rồi cuộn về.

`addAutomaticKeepAlives` mặc định là true, nghĩa là những mục *yêu cầu* được giữ sống sẽ được giữ. Một mục yêu cầu bằng cách mixin `AutomaticKeepAliveClientMixin`:

```dart
class _VideoRowState extends State<VideoRow>
    with AutomaticKeepAliveClientMixin {
  @override
  bool get wantKeepAlive => _controller.value.isPlaying;

  @override
  Widget build(BuildContext context) {
    super.build(context); // mixin yêu cầu dòng này
    return VideoPlayer(_controller);
  }
}
```

Chú ý `wantKeepAlive` trả về một *điều kiện*, không phải hằng `true`. Giữ sống mọi dòng sẽ biến danh sách lười trở lại thành danh sách dựng sẵn, từng cú cuộn một — đó là cách sửa lặng lẽ tái tạo lại đúng vấn đề của cách 1.

Lựa chọn thay thế, và thường tốt hơn, là đưa hẳn trạng thái ra khỏi mục. Vị trí cuộn, trạng thái mở rộng, lựa chọn và bản nháp văn bản thuộc về tầng trạng thái của bạn, đánh khoá theo id của mục, chứ không thuộc về `State` của dòng.

## Key, và khi nào chúng quan trọng trong danh sách

Với danh sách tĩnh, không cần key. Với danh sách có sắp xếp lại, chèn hoặc xoá, và các mục có giữ trạng thái, key chính là thứ giúp Flutter ghép đúng element với đúng mục:

```dart
itemBuilder: (context, i) => ItemTile(key: ValueKey(items[i].id), items[i]),
```

Không có key, xoá mục đầu tiên sẽ khiến mọi element sau đó nhận dữ liệu của mục kế tiếp trong khi vẫn giữ trạng thái của mục trước — biểu hiện là một checkbox trông như bị dịch chỗ, hoặc một hoạt ảnh chạy trên nhầm dòng.

## Danh sách kiểm tra

1. Đo ở **chế độ profile** trên **thiết bị thật**. Ghi lại luồng nào dài.
2. `ListView.builder` (hoặc `.separated`) — không bao giờ dùng danh sách `children` dựng sẵn cho nội dung dài.
3. `itemExtent` hoặc `prototypeItem` nếu các dòng đồng nhất.
4. Đưa việc tính toán ra khỏi `itemBuilder`; thêm `const` ở mọi chỗ biên dịch được.
5. `cacheWidth`/`cacheHeight` cho mọi ảnh trong ô.
6. `RepaintBoundary` cho những dòng có hoạt ảnh — chỉ những dòng đó.
7. `ValueKey` cho các mục trong danh sách có thể thay đổi.
8. Đo lại. Nếu luồng raster vẫn dài, hãy tìm `Opacity`, `ClipRRect` và bóng đổ.

## Câu hỏi thường gặp

**`ListView.separated` có tốn hơn không?**

Nó dựng phần ngăn cách như những con bổ sung, nên danh sách *n* mục sẽ dựng khoảng 2n−1 con. Điều đó ổn — phần ngăn cách là widget `const` rẻ tiền nếu bạn làm cho nó như vậy.

**`cacheExtent` để làm gì?**

Nó điều khiển danh sách giữ các con đã dựng xa khung nhìn tới đâu. Nâng nó lên làm cuộn nhanh mượt hơn, đổi lại tốn bộ nhớ và công dựng; đó là một núm tinh chỉnh, không phải một cách sửa.

**`ListView` có chậm hơn danh sách native không?**

Phép so sánh hiếm khi đứng vững khi cả hai làm cùng khối lượng công việc. Một `ListView.builder` dựng đúng cách tái sử dụng như `RecyclerView`; một `ListView` dựng sẵn thì tương đương với việc thêm tám trăm view vào một `LinearLayout`, vốn cũng chậm trên Android.

**Tôi có nên phân trang không?**

Có, với bất cứ thứ gì không giới hạn. Dựng lười giải quyết chi phí kết xuất, chứ không giải quyết chi phí giữ tám trăm model đã phân tích trong bộ nhớ hay chi phí tải chúng qua mạng.

**Vì sao lần cuộn đầu bị giật còn các lần sau thì mượt?**

Thường là do biên dịch shader hoặc giải mã ảnh ở lần xuất hiện đầu tiên, không phải do logic danh sách. Hãy kiểm tra luồng raster ở đúng frame đó trước khi sửa code danh sách.

---

*Hành vi của các widget, ngữ nghĩa delegate và cơ chế keep-alive mô tả ở đây được ghi trong các trang API và hướng dẫn hiệu năng của Flutter đã dẫn. Cách chia bốn hướng sửa, thứ tự trong danh sách kiểm tra và khuyến nghị đưa trạng thái ra khỏi dòng là đánh giá riêng của tôi từ việc phân tích danh sách theo cách này. Hãy luôn xác nhận bằng bản trace ở chế độ profile của chính bạn — cách sửa đúng phụ thuộc vào luồng nào đang trễ.*
