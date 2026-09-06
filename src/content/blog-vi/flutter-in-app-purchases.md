---
title: "Mua hàng trong ứng dụng Flutter: những phần không nằm ở cái nút"
description: "Nối dây in_app_purchase mất một buổi chiều. Xử lý khôi phục, giao dịch bị gián đoạn, hoàn tiền, và việc xác thực biên nhận để một client bị sửa không mở khoá được mọi thứ thì mất lâu hơn nhiều — và đó mới là phần quan trọng."
seoDescription: "Mua hàng trong ứng dụng Flutter với in_app_purchase: luồng purchase stream, completePurchase, xác thực biên nhận phía máy chủ, khôi phục giao dịch, trạng thái gói đăng ký, và các tình huống hỏng mà store sẽ kiểm tra."
keywords:
  - mua hàng trong ứng dụng flutter
  - in_app_purchase flutter hướng dẫn
  - xác thực biên nhận máy chủ flutter
  - khôi phục giao dịch flutter
  - trạng thái đăng ký flutter
  - completepurchase pending flutter
category: "Hướng dẫn"
topic: "Flutter"
level: "Nâng cao"
author: "Trung Hiếu"
publishDate: "2026-08-20"
emoji: "💳"
tags: ["Flutter", "Monetization", "IAP", "Backend", "Mobile"]
sources:
  - name: "in_app_purchase — pub.dev"
    url: "https://pub.dev/packages/in_app_purchase"
  - name: "Mua hàng trong ứng dụng — tài liệu Flutter"
    url: "https://docs.flutter.dev/cookbook/in-app-purchases"
  - name: "App Store Server API — tài liệu Apple"
    url: "https://developer.apple.com/documentation/appstoreserverapi"
  - name: "Google Play Developer API — tài liệu Android"
    url: "https://developers.google.com/android-publisher"
  - name: "Thông báo thời gian thực cho nhà phát triển — tài liệu Google Play"
    url: "https://developer.android.com/google/play/billing/getting-ready#configure-rtdn"
  - name: "App Store server notifications — tài liệu Apple"
    url: "https://developer.apple.com/documentation/appstoreservernotifications"
related:
  - slug: "flutter-secure-storage-secrets"
    title: "Bí mật trong ứng dụng Flutter: cái gì lưu được, cái gì thì không"
  - slug: "flutter-error-handling-crash-reporting"
    title: "Xử lý lỗi trong Flutter: bắt được thứ thật sự tới tay người dùng"
draft: false
---

Phiên bản trong bài hướng dẫn của việc mua hàng trong ứng dụng là một cái nút, một lời gọi `buyNonConsumable`, và một callback thành công đặt `isPremium = true`. Phát hành thứ đó rồi bạn sẽ lần lượt phát hiện: người dùng cài lại thì mất sạch, một giao dịch bị cuộc gọi cắt ngang thì không bao giờ hoàn tất, người đã hoàn tiền vẫn giữ quyền truy cập mãi mãi, và bất kỳ ai có bản build đã sửa đều mở khoá ứng dụng miễn phí.

Không cái nào trong số đó là trường hợp biên. Chúng là điều kiện vận hành bình thường của một hệ thống thanh toán.

## Stream mới là API

`in_app_purchase` không hoạt động theo kiểu hỏi-đáp. Giao dịch đến trên một stream, bao gồm cả giao dịch bạn không khởi tạo trong phiên này — các lần khôi phục, giao dịch hoàn tất khi ứng dụng đã đóng, và giao dịch từ thiết bị khác cùng tài khoản.

```dart
final class PurchaseService {
  PurchaseService(this._iap, this._backend);

  final InAppPurchase _iap;
  final BackendApi _backend;

  StreamSubscription<List<PurchaseDetails>>? _sub;

  void start() {
    _sub = _iap.purchaseStream.listen(
      _onPurchases,
      onError: (Object e, StackTrace s) => reportError(e, s),
    );
  }

  Future<void> _onPurchases(List<PurchaseDetails> purchases) async {
    for (final purchase in purchases) {
      switch (purchase.status) {
        case PurchaseStatus.pending:
          _showPendingUi();

        case PurchaseStatus.error:
          _showError(purchase.error);
          await _iap.completePurchase(purchase);

        case PurchaseStatus.purchased:
        case PurchaseStatus.restored:
          final valid = await _backend.verify(
            productId: purchase.productID,
            source: purchase.verificationData.source,
            token: purchase.verificationData.serverVerificationData,
          );
          if (valid) await _grantEntitlement(purchase.productID);
          await _iap.completePurchase(purchase);

        case PurchaseStatus.canceled:
          await _iap.completePurchase(purchase);
      }
    }
  }

  void dispose() => _sub?.cancel();
}
```

Hai điều trong đó không thương lượng được.

**Bắt đầu lắng nghe trước khi hiển thị bất kỳ giao diện mua hàng nào**, tốt nhất là ngay lúc khởi động ứng dụng. Một giao dịch hoàn tất khi không có ai lắng nghe sẽ được giao ở lần lắng nghe kế tiếp — nhưng nếu bạn chỉ đăng ký khi mở màn hình trả phí, thì một giao dịch đã hoàn tất rồi bị gián đoạn sẽ nằm im cho tới khi người dùng tình cờ mở lại màn hình đó.

**`completePurchase` phải được gọi cho mọi trạng thái kết thúc**, kể cả lỗi và huỷ. Trên iOS, một giao dịch chưa hoàn tất vẫn nằm trong hàng đợi và được giao lại ở mỗi lần khởi chạy, mãi mãi. Người dùng thấy hộp thoại mua hàng hiện lại mỗi lần mở ứng dụng, và điều đó sinh ra ticket hỗ trợ cùng đánh giá một sao với tỉ lệ ngang nhau.

`PurchaseStatus.pending` không phải lỗi — trên Android nó bao gồm các phương thức thanh toán trả sau, nơi người dùng ra cửa hàng trả tiền mặt. Giao dịch có thể hoàn tất vài giờ sau, qua stream, với ứng dụng đã đóng ở giữa.

## Việc xác thực thuộc về máy chủ của bạn

Client không thể quyết định một giao dịch có thật hay không. `serverVerificationData` là một token bạn gửi tới backend, backend gọi API máy chủ của Apple hoặc Google và nhận câu trả lời có thẩm quyền.

```
App → token giao dịch → Backend của bạn → API App Store / Play
                              ↓
                        bản ghi quyền lợi
                              ↓
App ← trạng thái quyền lợi ← Backend của bạn
```

Quyền lợi nằm trong cơ sở dữ liệu của bạn, khoá theo id người dùng *của bạn*, không theo thiết bị và không nằm trong bộ nhớ cục bộ. Chỉ một lựa chọn thiết kế đó sửa cùng lúc ba vấn đề: cài lại vẫn chạy, nhiều thiết bị vẫn chạy, và một client bị sửa không thể tự cấp quyền cho mình vì máy chủ chưa bao giờ hỏi nó.

Lý do phải làm vậy ngay cả với ứng dụng nhỏ là hoàn tiền và huỷ đăng ký. Người đã hoàn tiền vẫn giữ một biên nhận cục bộ trông hợp lệ vô thời hạn. Chỉ máy chủ của store mới biết, và chỉ khi bạn hỏi — hoặc khi bạn đăng ký **thông báo từ máy chủ** (App Store Server Notifications, Play Real-time Developer Notifications), thứ đẩy sự kiện hoàn tiền, huỷ và sự cố thanh toán tới bạn ngay khi chúng xảy ra. Với gói đăng ký, chúng gần như bắt buộc; phương án còn lại là quét lại mọi biên nhận theo lịch, và cách đó không mở rộng được.

## Khôi phục

```dart
Future<void> restore() async {
  await _iap.restorePurchases();
  // Kết quả về trên purchaseStream với status == restored.
}
```

Apple yêu cầu có nút khôi phục nhìn thấy được cho sản phẩm mua vĩnh viễn, và người duyệt có kiểm tra thật. Ngoài chuyện tuân thủ, đó là cửa thoát khi cơ chế đồng bộ quyền lợi của chính bạn hỏng.

Lưu ý rằng khôi phục sẽ giao lại *mọi* giao dịch vĩnh viễn trong quá khứ, nên `_grantEntitlement` phải idempotent. Cấp hai lần phải là không làm gì thêm, không phải cộng đôi.

## Hàng tiêu hao cần hình dạng khác

Với hàng tiêu hao — xu, lượt, gói tăng lực dùng một lần — trình tự phải là:

1. Nhận giao dịch.
2. Xác thực phía máy chủ.
3. **Cộng số dư cho người dùng trên máy chủ.**
4. Chỉ sau đó mới gọi `completePurchase`.

Hoàn tất trước rồi sập trước khi cộng số dư thì giao dịch coi như mất: store xem như đã giao và sẽ không giao lại. Người dùng đã trả tiền mà không nhận được gì, và cách khắc phục duy nhất là hỗ trợ thủ công.

Trên Android, cũng lưu ý rằng hàng tiêu hao chưa được tiêu thụ thì không mua lại được, nên lỗi ở trình tự này lộ ra dưới dạng "người dùng không mua thêm xu được" chứ không phải một thông báo lỗi.

## Kiểm thử mà không tốn tiền

| Nền tảng | Cơ chế | Điều cần lưu ý |
| --- | --- | --- |
| iOS | File cấu hình StoreKit trong Xcode | Chạy được trên giả lập; không đi qua đường biên nhận thật |
| iOS | Tài khoản sandbox | Thời lượng gói đăng ký bị nén — một tháng có thể là năm phút |
| Android | License tester trong Play Console | Cần bản build đã tải lên một kênh test; ứng dụng phải cài từ Play |
| Cả hai | Thông báo từ máy chủ | Hãy kiểm thử tường minh; một webhook hỏng là vô hình cho tới khi có người hoàn tiền |

Thời lượng bị nén trong sandbox vừa hữu ích vừa gây hiểu lầm ngang nhau: logic gia hạn bạn test theo chu kỳ năm phút chưa bao giờ chạm tới đồng hồ thật hay ranh giới múi giờ thật.

## Những thứ bị người duyệt từ chối

Đáng biết trước khi nộp hơn là sau khi nộp:

- Màn hình trả phí không có nút khôi phục nhìn thấy được.
- Giá viết cứng trong giao diện thay vì đọc từ `ProductDetails` — store hiển thị tiền tệ địa phương, và chuỗi viết cứng sẽ sai với phần lớn thế giới.
- Bất kỳ nhắc tới phương thức thanh toán ngoài ứng dụng nào, ở những khu vực không cho phép.
- Gói đăng ký không nêu rõ thời hạn, giá và điều khoản gia hạn ngay cạnh nút mua.

Hãy đọc giá từ `queryProductDetails` và hiển thị `product.price`, thứ đã được định dạng sẵn cho cửa hàng của người dùng.

## Câu hỏi thường gặp

**Có nên dùng RevenueCat hoặc dịch vụ tương tự không?**

Nếu bạn không muốn tự xây và vận hành phần xác thực biên nhận cùng thông báo máy chủ thì có — đó chính xác là thứ họ bán. Kiến trúc ở trên là thứ bạn đang mua.

**Vì sao giao dịch thành công mà không tới listener của tôi?**

Thường là đăng ký stream sau khi giao dịch đã hoàn tất, hoặc một ngoại lệ trong handler đã giết stream. Hãy thêm `onError` và đừng bao giờ để handler ném lỗi.

**Kiểm tra trạng thái đăng ký khi ngoại tuyến thế nào?**

Cache câu trả lời của máy chủ kèm hạn dùng và một khoảng ân hạn. Tin cache trong thời gian ngắn; xác thực lại lúc khởi chạy và sau mỗi lần quay lại từ nền.

**Xử lý sao khi người dùng mua trên iOS rồi mở ứng dụng Android?**

Quyền lợi gắn với tài khoản của bạn, không gắn với store. Đây là một trong những lập luận mạnh nhất cho việc giữ quyền lợi ở máy chủ ngay cả với ứng dụng nhỏ.

**Có cần xử lý nâng và hạ cấp giữa các bậc đăng ký không?**

Có, và các nền tảng mô hình hoá việc chia tỉ lệ tiền khác nhau. Hãy thiết kế quyền lợi theo kiểu "ngay lúc này bậc nào đang hoạt động, theo máy chủ" thay vì theo lịch sử giao dịch.

---

*Mô hình stream của `in_app_purchase`, ngữ nghĩa `completePurchase`, hành vi khôi phục và sự tồn tại của thông báo máy chủ mô tả ở đây đều nằm trong tài liệu dẫn ở trên. Kiến trúc giữ quyền lợi ở máy chủ, quy tắc thứ tự cho hàng tiêu hao, danh sách lý do bị từ chối khi duyệt và cảnh báo về thời lượng sandbox bị nén là nhận định riêng của tôi từ việc phát hành ứng dụng có thu phí. Chính sách và API của store thay đổi thường xuyên — hãy kiểm tra yêu cầu hiện hành trong tài liệu nền tảng trước khi nộp.*
