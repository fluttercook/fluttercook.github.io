---
title: "Form trong Flutter vượt khỏi ví dụ mẫu: validate bất đồng bộ, focus và autofill"
description: "Form và TextFormField đủ cho bài hướng dẫn. Form thật cần validate nói chuyện được với server, lỗi hiện đúng lúc, focus di chuyển theo đúng quy ước nền tảng, và bàn phím không che mất ô đang gõ."
seoDescription: "Dựng form Flutter thật sự: autovalidateMode, validate bất đồng bộ và chéo trường, FocusNode, TextInputFormatter, AutofillGroup và vòng đời controller."
keywords:
  - validate form flutter bất đồng bộ
  - autovalidatemode flutter
  - flutter focusnode chuyển ô kế tiếp
  - textinputformatter flutter ví dụ
  - flutter autofillgroup trình quản lý mật khẩu
  - texteditingcontroller dispose
category: "Hướng dẫn"
topic: "Flutter"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-09-04"
emoji: "📝"
tags: ["Flutter", "Forms", "Validation", "UX", "Accessibility"]
sources:
  - name: "Form — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/Form-class.html"
  - name: "FormField — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/FormField-class.html"
  - name: "TextFormField — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/material/TextFormField-class.html"
  - name: "Flutter cookbook — Build a form with validation"
    url: "https://docs.flutter.dev/cookbook/forms/validation"
  - name: "TextInputFormatter — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/services/TextInputFormatter-class.html"
  - name: "AutofillGroup — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/AutofillGroup-class.html"
related:
  - slug: "flutter-accessibility-semantics"
    title: "Trợ năng trong Flutter: cây semantics thật sự báo cáo những gì"
  - slug: "flutter-build-context-explained"
    title: "BuildContext chính là element: đọc hiểu những thông báo lỗi có nhắc tới nó"
draft: false
---

Bài cookbook về form của Flutter đưa bạn tới một màn hình đăng ký chạy được trong khoảng bốn mươi dòng. Rồi một designer nhìn vào, và bạn phát hiện lỗi hiện đỏ trước khi ai kịp gõ chữ nào, phím Enter chẳng làm gì, trình quản lý mật khẩu phớt lờ các ô, và trên điện thoại nhỏ thì bàn phím che mất đúng ô bạn đang sửa. Không cái nào trong đó là vấn đề validate. Chúng là những phần của "một form" mà bài hướng dẫn không mô hình hóa.

## Ba đối tượng, và mỗi cái sở hữu gì

`Form` là một bộ điều phối, không phải một layout. Nó giữ một `FormState` có thể `validate()`, `save()` và `reset()` mọi `FormField` nằm bên dưới nó trong cây. `FormField` sở hữu một giá trị, chuỗi lỗi của nó, và việc nó đã bị chạm tới hay chưa. `TextFormField` là một `FormField` bọc quanh một `TextField`.

```dart
final _formKey = GlobalKey<FormState>();

Form(
  key: _formKey,
  child: Column(children: [
    TextFormField(
      decoration: const InputDecoration(labelText: 'Email'),
      validator: (value) =>
          (value == null || !value.contains('@')) ? 'Email không hợp lệ' : null,
      onSaved: (value) => _draft.email = value!.trim(),
    ),
  ]),
);

if (_formKey.currentState!.validate()) {
  _formKey.currentState!.save();
  await api.signUp(_draft);
}
```

Một `validator` trả về `null` nghĩa là hợp lệ và trả về chuỗi nghĩa là không hợp lệ — phép đảo ngược đó làm ai cũng vấp một lần. `onSaved` chỉ chạy khi bạn gọi `save()`, khiến quy trình "validate rồi mới ghi" trở thành hai pha tự nhiên.

`GlobalKey` phải là một **trường của lớp**, không phải biến cục bộ trong `build`. Một key tạo lại mỗi lượt build là một danh tính mới mỗi frame, và `currentState` sẽ null hoặc cũ mèm đúng vào lúc bạn cần nó.

## Lỗi hiện lúc nào là quyết định UX, không phải giá trị mặc định

`autovalidateMode` có ba giá trị và chọn sai là lời than phiền phổ biến nhất về form:

| Giá trị | Validate lúc nào | Cảm giác |
| --- | --- | --- |
| `disabled` (mặc định) | Chỉ khi gọi `validate()` | Im lặng tới lúc submit — an toàn, hơi muộn |
| `onUserInteraction` | Sau khi người dùng đã sửa ô đó | Đúng thứ người ta mong đợi |
| `always` | Ở mọi lượt build, từ lần vẽ đầu | Lỗi đỏ trên một form còn trống |

`always` trên màn hình đăng ký mới toanh sẽ chào người dùng bằng ba lỗi cho những ô họ còn chưa nhìn. Hãy dùng `onUserInteraction` trên `Form` cho trường hợp thông thường, và để dành `always` cho form đã điền sẵn dữ liệu thật sự không hợp lệ.

Có một cải tiến đáng mười dòng code: validate lúc submit, nhưng khi một ô đã sai thì chuyển riêng ô đó sang validate theo từng thay đổi, để lỗi biến mất ngay khi người dùng sửa xong. `onUserInteraction` xấp xỉ điều này đủ tốt, nên phần lớn đội dừng ở đó.

## Quy tắc chéo trường cần giá trị, không cần widget

"Xác nhận mật khẩu phải trùng mật khẩu" không thể diễn đạt bằng một validator chỉ nhìn thấy giá trị của chính nó. Hãy giữ nguồn sự thật trong một controller và bắt lấy nó trong closure:

```dart
final _password = TextEditingController();

TextFormField(
  controller: _password,
  obscureText: true,
  validator: (v) => (v == null || v.length < 8) ? 'Tối thiểu 8 ký tự' : null,
),
TextFormField(
  obscureText: true,
  validator: (v) => v != _password.text ? 'Mật khẩu không khớp' : null,
),
```

Chỗ tinh tế là **khi nào** ô thứ hai validate lại. Nếu người dùng sửa ô thứ nhất, lỗi của ô thứ hai vẫn cũ cho tới khi có gì đó kích hoạt nó. Hoặc gọi `_formKey.currentState!.validate()` từ `onChanged` của ô thứ nhất, hoặc chấp nhận rằng lỗi chỉ biến mất lúc submit. Cách đầu tốn công hơn và tốt hơn.

Mọi `TextEditingController` và `FocusNode` bạn tạo đều phải được dispose:

```dart
@override
void dispose() {
  _password.dispose();
  _emailFocus.dispose();
  super.dispose();
}
```

Bỏ qua việc này là rò rỉ thật — controller giữ listener sống, và trên một app nhiều form thì nó lộ ra trong phần memory của DevTools dưới dạng số lượng `State` bị giữ lại cứ tăng dần.

## Validate bất đồng bộ không nhét vừa vào `validator`

`validator` là đồng bộ. Nó buộc phải vậy: nó chạy trong `validate()`, hàm trả về một `bool` mà nơi gọi hành động ngay. Nên "tên đăng nhập này có ai lấy chưa?" không thể sống ở đó. Hình dạng làm được là giữ kết quả bất đồng bộ trong state và để validator đồng bộ đọc nó:

```dart
String? _usernameError;
Timer? _debounce;

void _onUsernameChanged(String value) {
  _debounce?.cancel();
  setState(() => _usernameError = null);
  _debounce = Timer(const Duration(milliseconds: 400), () async {
    final taken = await api.isUsernameTaken(value);
    if (!mounted) return;
    setState(() => _usernameError = taken ? 'Tên này đã có người dùng' : null);
  });
}

TextFormField(
  onChanged: _onUsernameChanged,
  validator: (v) {
    if (v == null || v.isEmpty) return 'Bắt buộc';
    return _usernameError;                 // điều server nói lần gần nhất
  },
)
```

Ba thứ khiến nó hành xử đúng. Phép **debounce** ngăn mỗi lần gõ phím là một request. Phép kiểm tra `mounted` ngăn callback ghi vào một state đã bị hủy sau khi người dùng rời trang. Và việc xóa `_usernameError` ở đầu mỗi lần thay đổi nghĩa là form không hiện một chữ "đã có người dùng" cũ trong khi một lượt kiểm tra mới hơn đang bay.

Lỗ hổng còn lại là cuộc đua: submit trong lúc một lượt kiểm tra đang chờ thì `validate()` đọc câu trả lời cũ. Với bất cứ thứ gì quan trọng, server dù sao cũng phải kiểm tra lại lúc submit — validate bất đồng bộ phía client là một tiện ích trải nghiệm, không phải một bảo đảm.

## Focus là thành phần hạng nhất của form

Hai hành vi mà người dùng nhận ra ngay khi thiếu: phím Enter/Next chuyển sang ô kế tiếp, và loại bàn phím khớp với nội dung.

```dart
TextFormField(
  keyboardType: TextInputType.emailAddress,
  textInputAction: TextInputAction.next,
  onFieldSubmitted: (_) => FocusScope.of(context).nextFocus(),
),
TextFormField(
  obscureText: true,
  textInputAction: TextInputAction.done,
  onFieldSubmitted: (_) => _submit(),
),
```

`FocusScope.of(context).nextFocus()` đi theo thứ tự duyệt tự nhiên, nên thường bạn chẳng cần giữ một `FocusNode` cho từng ô. Hãy dùng node tường minh khi bạn cần **nhảy** tới đâu đó — hữu ích nhất là chuyển focus tới ô sai đầu tiên sau một lần submit thất bại, vừa là một thắng lợi về khả năng dùng vừa là yêu cầu về trợ năng, vì người dùng trình đọc màn hình nếu không sẽ chẳng biết cái gì sai.

`keyboardType` không phải chuyện trang trí. `TextInputType.emailAddress` đưa `@` lên bàn phím chính; `TextInputType.numberWithOptions(decimal: true)` cho bàn phím số. Hãy kết hợp với `textCapitalization` — `TextCapitalization.words` cho tên riêng, `none` cho email, nơi mà kiểu viết hoa đầu câu mặc định đang tích cực chống lại người dùng.

## Formatter định hình dữ liệu nhập; nó không validate

```dart
TextFormField(
  keyboardType: TextInputType.number,
  inputFormatters: [
    FilteringTextInputFormatter.digitsOnly,
    LengthLimitingTextInputFormatter(11),
  ],
)
```

Formatter chạy ở mỗi lần gõ phím và có thể viết lại giá trị. Hai quy tắc giữ chúng không thành nguồn sinh lỗi: đừng bao giờ dùng formatter để áp một quy tắc nghiệp vụ mà người dùng không nhìn thấy (âm thầm nuốt ký tự bị đọc là bàn phím hỏng), và hãy cẩn thận với formatter tùy chỉnh làm dịch con trỏ — một formatter chèn khoảng trắng vào số thẻ phải tính lại `TextEditingValue.selection`, nếu không thì gõ vào giữa sẽ khiến con trỏ nhảy về cuối.

`FilteringTextInputFormatter.digitsOnly` và `LengthLimitingTextInputFormatter` đáp ứng phần lớn nhu cầu thật. Thứ gì phức tạp hơn thường sáng sủa hơn khi tách thành một validator cộng một hàm định dạng lúc hiển thị.

## Autofill, để trình quản lý mật khẩu nhìn thấy các ô

Đây là vài dòng cải thiện tỉ lệ hoàn tất một cách rõ rệt mà lại liên tục bị bỏ qua:

```dart
AutofillGroup(
  child: Column(children: [
    TextFormField(
      autofillHints: const [AutofillHints.username, AutofillHints.email],
      keyboardType: TextInputType.emailAddress,
    ),
    TextFormField(
      autofillHints: const [AutofillHints.password],
      obscureText: true,
      onFieldSubmitted: (_) {
        TextInput.finishAutofillContext();     // mời lưu thông tin đăng nhập
        _submit();
      },
    ),
  ]),
)
```

`AutofillGroup` nói với nền tảng rằng các ô này thuộc về cùng một bộ thông tin đăng nhập. `autofillHints` nói mỗi ô là gì. `TextInput.finishAutofillContext()` là phần nhắc iOS hoặc Android **lưu** một mật khẩu mới — không có nó, luồng đăng ký không bao giờ mời lưu gì cả. Với form tạo tài khoản mới, hãy dùng `AutofillHints.newPassword` cho ô mật khẩu để trình quản lý gợi ý một mật khẩu sinh tự động thay vì một mật khẩu cũ.

## Bàn phím che mất ô đang gõ

Trên một form dài bên trong `Scaffold`, giá trị mặc định `resizeToAvoidBottomInset: true` thu nhỏ phần body khi bàn phím hiện ra — điều đó chẳng giúp gì nếu nội dung của bạn không cuộn được. Hãy đặt form trong một `SingleChildScrollView`, và framework sẽ tự cuộn ô đang focus vào tầm nhìn.

Vẫn còn hai chỗ hay hỏng. Một `Column` trong `SingleChildScrollView` trong một `Column` sinh lỗi chiều cao không giới hạn; hãy cho scroll view một cha có ràng buộc (`Expanded`, hoặc để nó làm `body` trực tiếp). Và các nút hành động dưới cùng cần luôn nhìn thấy thì thuộc về `bottomNavigationBar` hoặc một bottom sheet bọc `SafeArea`, chứ không phải cuối cột cuộn nơi bàn phím đẩy chúng khỏi tầm với.

## Câu hỏi thường gặp

**Nên dùng package form hay `Form` thuần?**

`Form` thuần là đủ cho phần lớn màn hình và không tốn thêm phụ thuộc. Một package đáng dùng khi form được sinh động theo schema, hoặc khi bạn muốn trạng thái các ô ở dạng stream để đưa vào tầng quản lý trạng thái.

**Vì sao `validate()` trả về true trong khi một ô rõ ràng đang sai?**

Hoặc ô đó không phải hậu duệ của `Form` kia trong cây element, hoặc validator chỉ trả về khác null trong một nhánh không được chạy tới. Hãy in log bên trong validator — nó được gọi đúng một lần cho mỗi ô ở mỗi `validate()`.

**Có cần `TextEditingController` cho mọi ô không?**

Không. `onSaved` cộng `initialValue` đã đủ cho việc đọc lúc submit. Hãy thêm controller khi bạn cần đọc hoặc đặt nội dung giữa các lượt build — validate chéo trường, xóa trắng một ô, hoặc nhập liệu bằng code.

**Làm sao hiện lỗi từ server lên đúng một ô sau khi submit?**

Giữ một `Map<String, String>` lỗi theo tên ô trong state, để mỗi validator tra vào đó, và gọi `validate()` sau khi có phản hồi. Cách đó tái dùng đúng đường vẽ với lỗi phía client thay vì nghĩ ra một đường thứ hai.

**`autovalidateMode` trên `Form` có đè lên các ô không?**

`autovalidateMode` của chính một ô sẽ thắng ở nơi nó được đặt. Đặt trên `Form` là cách mặc định tiện lợi; hãy ghi đè theo từng ô cho đúng cái ô cần thời điểm khác.

---

*Hành vi API ở đây lấy từ tài liệu widget và cookbook của Flutter đã dẫn ở trên. Các khuyến nghị — chọn `onUserInteraction` làm mặc định, coi validate bất đồng bộ phía client là tiện ích chứ không phải bảo đảm, và chuyển focus tới ô sai đầu tiên — là nhận định của tôi từ việc dựng những form mà người ta thật sự điền xong.*
