---
title: "Key trong Flutter: một quy tắc duy nhất giải thích mọi trường hợp"
description: "Key không phải tối ưu hóa, cũng không phải đồ trang trí. Chúng tồn tại vì việc tái dùng element được quyết định bằng vị trí và kiểu runtime — và quyết định đó sai đúng vào lúc danh sách con của bạn có thể đổi thứ tự, chèn thêm hay bị xóa."
seoDescription: "Khi nào dùng ValueKey, ObjectKey, UniqueKey và GlobalKey trong Flutter, vì sao state widget nhảy sang dòng khác nếu thiếu key, và vì sao PageStorageKey là chuyện khác."
keywords:
  - key trong flutter
  - khi nào dùng valuekey flutter
  - flutter globalkey và valuekey
  - state nhảy sai dòng listview flutter
  - pagestoragekey flutter
  - widget canupdate flutter
category: "Chuyên sâu"
topic: "Flutter"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-09-06"
emoji: "🔑"
tags: ["Flutter", "Widgets", "State", "Elements", "Debugging"]
sources:
  - name: "Flutter — Architectural overview"
    url: "https://docs.flutter.dev/resources/architectural-overview"
  - name: "Key — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/foundation/Key-class.html"
  - name: "GlobalKey — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/GlobalKey-class.html"
  - name: "Widget.canUpdate — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/Widget/canUpdate.html"
  - name: "PageStorageKey — tài liệu Flutter API"
    url: "https://api.flutter.dev/flutter/widgets/PageStorageKey-class.html"
  - name: "Flutter — When to use keys (Widget of the Week)"
    url: "https://www.youtube.com/watch?v=kn0EOS-ZiIc"
related:
  - slug: "flutter-build-context-explained"
    title: "BuildContext chính là element: đọc hiểu những thông báo lỗi có nhắc tới nó"
  - slug: "flutter-lists-performance-builder"
    title: "Vì sao ListView của bạn chậm, và bốn cách sửa thật sự có tác dụng"
draft: false
---

Có một con bug rất cụ thể dạy cho tất cả mọi người về key. Bạn có một danh sách các dòng có trạng thái — mỗi dòng một checkbox, hoặc một expansion tile, hoặc một ô nhập liệu. Bạn xóa dòng thứ hai. Dòng đó biến mất đúng như mong đợi, nhưng **dấu tích** vốn thuộc về nó giờ lại nằm trên một dòng khác. Dữ liệu chẳng có gì sai. Tải lại trang thì mọi thứ bình thường.

Đó không phải lỗi của Flutter. Đó là framework làm đúng những gì được bảo, và cách sửa chỉ dài một từ. Nhưng cách sửa chỉ thật sự dính lại nếu bạn hiểu quy tắc bên dưới, vì cùng quy tắc đó giải thích vì sao đôi khi key chẳng làm gì cả, vì sao `GlobalKey` đắt, và vì sao `PageStorageKey` không thật sự là key theo cùng nghĩa.

## Ba cây, và cái cây giữ state của bạn

Flutter duy trì ba cấu trúc song song. **Cây widget** là kết quả `build` của bạn: các đối tượng cấu hình bất biến, bị vứt đi và tạo lại liên tục. **Cây render** lo layout và vẽ. Nằm giữa hai cái đó là **cây element**, và đây mới là cái quan trọng ở bài này, vì một `Element` sống lâu và — với `StatefulWidget` — chính nó sở hữu đối tượng `State`.

Khi có một lượt rebuild, Flutter đi song song cây element cũ và cây widget mới, và tại mỗi vị trí hỏi đúng một câu:

```dart
static bool canUpdate(Widget oldWidget, Widget newWidget) {
  return oldWidget.runtimeType == newWidget.runtimeType
      && oldWidget.key == newWidget.key;
}
```

Toàn bộ cơ chế chỉ có vậy. Nếu câu trả lời là có, element hiện tại (cùng `State` và render object của nó) được **giữ lại** và nhận widget mới. Nếu là không, element cũ bị hủy kích hoạt và một element mới được dựng lên.

Hãy để ý phép so sánh đó **không** bao gồm dữ liệu của bạn. Hai widget `TodoRow` mang hai todo hoàn toàn khác nhau vẫn thay thế được cho nhau dưới góc nhìn của `canUpdate`, miễn cả hai có `key == null`. Và để ý phép so sánh được thực hiện **theo vị trí trong danh sách con**. Con số 0 so với con số 0.

Từ đó ra quy tắc, và đó là quy tắc duy nhất:

> Flutter ghép các con theo vị trí và kiểu. Một key thay "theo vị trí" bằng "theo danh tính".

Mọi thứ còn lại đều là hệ quả.

## Con bug đó diễn ra thế nào, quay chậm

```dart
Column(
  children: [
    for (final todo in todos) TodoRow(todo: todo),   // không key
  ],
)
```

Trước khi xóa, cây element là `[TodoRow#0, TodoRow#1, TodoRow#2]`, giữ state `[chưa tick, đã tick, chưa tick]`. Bạn bỏ `todos[1]` và rebuild. Danh sách widget mới có hai phần tử. Flutter so vị trí 0 với vị trí 0 — cùng kiểu, hai key đều null, `canUpdate` đúng, giữ element #0 và đưa cho nó `todos[0]`. Vị trí 1 so với vị trí 1 — cùng kiểu, key null, đúng — nên element #1, đang giữ **trạng thái đã tick vốn thuộc về dòng vừa bị xóa**, được giữ lại và nhận `todos[2]`. Element #2 bị hủy.

Kết quả: các dòng hiển thị đúng chữ, vì chữ đến từ widget. Nhưng state nằm sai dòng, vì state đến từ element. Thêm key vào là vị trí thôi làm căn cứ ghép:

```dart
Column(
  children: [
    for (final todo in todos) TodoRow(key: ValueKey(todo.id), todo: todo),
  ],
)
```

Giờ `canUpdate` so `ValueKey('b')` với `ValueKey('c')` ở vị trí 1 và trả về sai. Flutter đi tìm trong đám con cũ một element có key khớp, tìm thấy element #2, và di chuyển nó. State đi theo danh tính.

## Khi nào cần key, khi nào không

Bỏ qua key khi:

- Các con **không có state ở bất kỳ tầng nào**. Không `State`, không `AnimationController`, không vị trí cuộn, không gì để đi lạc chỗ. Một danh sách `Text` không bao giờ cần key.
- Danh sách không bao giờ đổi thứ tự, và phần tử chỉ được thêm vào cuối. Ghép theo vị trí lúc đó là đúng.
- Bạn định gắn key cho **bản thân** `ListView.builder`. Các con của nó đã có key ngầm theo chỉ số cho mục đích của sliver child delegate; thứ bạn cần là key trên widget của từng item, không phải trên danh sách.

Dùng key khi **bất kỳ** điều nào sau đây đúng:

- Các con có state **và** tập hợp có thể đổi thứ tự, bị lọc, hoặc bị xóa phần tử ở vị trí không phải cuối.
- Bạn đang tráo giữa hai widget cùng kiểu và muốn một `State` mới tinh — `UniqueKey` buộc element cũ bị vứt bỏ.
- Bạn đang animate phần tử vào/ra bằng `AnimatedList`, `AnimatedSwitcher` hoặc một implicit animation cần phân biệt "cùng một widget, đã đổi" với "một widget khác".

Trường hợp `AnimatedSwitcher` hay làm người ta vấp:

```dart
AnimatedSwitcher(
  duration: const Duration(milliseconds: 300),
  child: Text('$counter', key: ValueKey(counter)),   // không có key: không animation
)
```

Cả hai con đều là `Text`. Không key thì `canUpdate` đúng, element được tái dùng, và `AnimatedSwitcher` kết luận rằng chẳng có gì thay đổi. Key chính là thứ khiến sự thay đổi trở nên nhìn thấy được với framework.

## Chọn giữa các loại key

| Loại | So sánh dựa trên | Dùng khi |
| --- | --- | --- |
| `ValueKey<T>` | Giá trị bạn đưa vào (`==`) | Bạn có id ổn định: `ValueKey(todo.id)` |
| `ObjectKey` | **Danh tính** của đối tượng bạn truyền | Model không có id nhưng instance thì ổn định |
| `UniqueKey` | Không gì cả — không bao giờ bằng ai | Bạn muốn ép dựng lại từ đầu |
| `GlobalKey` | Danh tính, nhưng duy nhất trong toàn app | Bạn phải với tới element hoặc state từ bên ngoài |
| `PageStorageKey` | Một giá trị, dùng để lưu vị trí cuộn | Giữ scroll offset khi điều hướng qua lại |

Hai cái bẫy trong bảng đó.

**`ValueKey` đặt lên sai giá trị.** `ValueKey(index)` là lỗi phổ biến nhất, vì chỉ số chính là thông tin vị trí mà bạn đang cố thoát khỏi. Xóa một phần tử là mọi chỉ số phía sau dịch đi, key dịch theo, và bạn quay về ghép theo vị trí. Hãy đặt key theo thứ gì đó thuộc về bản thân phần tử — id trong cơ sở dữ liệu, một UUID, một tên tệp.

**`UniqueKey` viết trong `build`.** Một `UniqueKey` tạo ra trong lúc `build` sẽ khác nhau ở mỗi lượt rebuild, nên `canUpdate` luôn sai, nên element cùng toàn bộ state và cây con của nó bị hủy và dựng lại ở mỗi frame. Thứ này tạo ra widget reset trông thấy được, animation không bao giờ chạy xong, và một cái giá hiệu năng thật. `UniqueKey` thuộc về một trường của lớp, hoặc một hành động "reset form này" có chủ đích.

## `GlobalKey` đắt hơn vẻ ngoài của nó

`GlobalKey` cho bạn `key.currentState`, `key.currentContext` và `key.currentWidget` từ bất cứ đâu. Cách dùng chuẩn mực là với `Form`:

```dart
final _formKey = GlobalKey<FormState>();          // một trường, không phải biến cục bộ

// ...
if (_formKey.currentState!.validate()) {
  _formKey.currentState!.save();
}
```

Chỗ đó chính đáng. Thứ không miễn phí là:

- Framework duy trì một **sổ đăng ký toàn cục** từ key tới element, được kiểm tra và cập nhật ở mỗi lần mount và unmount.
- Di chuyển một widget mang `GlobalKey` sang vị trí mới kích hoạt trọn một vòng deactivate/reactivate cho cây con đó — một cuộc tìm kiếm **toàn cục** thay vì so sánh cục bộ giữa các anh em.
- Hai widget cùng một `GlobalKey` được mount cùng lúc là lỗi, và chuyện đó rất dễ xảy ra khi `GlobalKey` được tạo trong `build` còn widget thì xuất hiện hai lần.

Trước khi với tay lấy một cái, hãy kiểm tra xem bạn có thật sự cần thò **vào trong** một cây con không, hay state đó đáng lẽ nên nằm cao hơn một tầng. Phần lớn cách dùng `GlobalKey` không phải cho `Form` hay để cầm `Scaffold`/`Navigator` đều là vấn đề đặt sai chỗ state được ngụy trang — hãy nâng state lên, hoặc truyền callback xuống.

## `PageStorageKey` là một giống loài khác

```dart
ListView(
  key: const PageStorageKey<String>('feed'),
  children: [ /* ... */ ],
)
```

Nó là một `Key`, nên có tham gia vào `canUpdate`, nhưng việc thật sự của nó là đặt tên cho một ô trong `PageStorage`, nơi vị trí cuộn được ghi lại. Đó là thứ giúp vị trí cuộn của một tab sống sót khi bạn chuyển đi rồi quay lại, hoặc giúp danh sách khôi phục offset sau một lượt `Navigator.push` rồi `pop`.

Hai hệ quả. Chuỗi đó phải **ổn định qua các lượt rebuild** và **duy nhất giữa các scrollable anh em** — hai tab dùng chung `'feed'` sẽ dùng chung một scroll offset, nhìn như bị ma ám. Và `PageStorageKey` chỉ hoạt động ở nơi có một `PageStorage` phía trên, thứ mà `MaterialApp` và `Navigator` cung cấp sẵn.

## Gỡ lỗi: làm sao biết đây là vấn đề về key

Kiểu triệu chứng đủ đặc trưng để chẩn đoán chỉ bằng hành vi. Hãy nghi ngờ key khi **dữ liệu thì đúng mà thứ gắn với dữ liệu thì sai**: chữ đúng, checkbox sai; xóa đúng phần tử nhưng dòng animate ra lại là dòng khác; ô nhập liệu vẫn giữ nội dung cũ sau khi bạn đổi bản ghi đang sửa; video vẫn chạy tiếp sau khi bạn đã tráo phần tử.

Xác nhận trong một phút:

```dart
@override
void initState() {
  super.initState();
  debugPrint('initState cho ${widget.todo.id} trên $hashCode');
}

@override
void didUpdateWidget(TodoRow old) {
  super.didUpdateWidget(old);
  debugPrint('${old.todo.id} -> ${widget.todo.id} trên $hashCode');
}
```

Nếu bạn thấy `didUpdateWidget` báo id đổi trên cùng một `hashCode`, tức là một element đang bị tái dùng cho hai phần tử logic khác nhau. Đó chính là bug, và một `ValueKey` tử tế là cách sửa. Flutter Inspector cho thấy đúng điều đó bằng hình ảnh — chọn một dòng trước và sau khi thay đổi rồi xem danh tính element có dịch chỗ không.

## Câu hỏi thường gặp

**Đặt key ở đâu — trên item hay trên thứ gì đó bên trong nó?**

Trên widget **ngoài cùng** trả về cho item đó, ở đúng tầng mà các anh em được đem ra so sánh. Key đặt trên một con nằm bên trong dòng thì không giúp gì, vì việc ghép sai đã xảy ra ở tầng trên rồi.

**Rắc key khắp nơi có hại hiệu năng không?**

`ValueKey` và `ObjectKey` rất rẻ: thêm một phép `==` trong lúc đối chiếu. Key trên một danh sách lớn thậm chí có thể **nhanh hơn** khi đổi thứ tự, vì element được di chuyển thay vì dựng lại. `GlobalKey` mới là cái có chi phí thật.

**Vì sao thêm key rồi mà vẫn không hết lỗi?**

Thường là giá trị key không ổn định — `ValueKey(index)`, `ValueKey(DateTime.now())`, hoặc key dựng từ một trường thay đổi mỗi khi item được sửa. Hãy in key ra trước và sau lượt thay đổi rồi kiểm tra xem chúng có chỉ đúng cùng một phần tử logic không.

**Trong `ListView.builder` có cần key không?**

Có, vì đúng những lý do trên, nếu phần tử có state và tập hợp thay đổi. Chỉ số của builder là thông tin vị trí; nó không cấp danh tính cho widget item của bạn.

**`Key` khác `LocalKey` chỗ nào?**

`Key` là kiểu gốc. `LocalKey` là nhánh chỉ cần duy nhất giữa các anh em — `ValueKey`, `ObjectKey`, `UniqueKey`, `PageStorageKey` đều kế thừa nó. `GlobalKey` là nhánh còn lại, duy nhất trong toàn bộ ứng dụng.

---

*Hành vi đối chiếu mô tả ở đây chính là `Widget.canUpdate` và phần logic cập nhật element trong framework Flutter đã dẫn ở trên. Phần nhận định về việc khi nào `GlobalKey` là dấu hiệu state bị đặt sai chỗ, cùng công thức gỡ lỗi, là của tôi. Hãy đối chiếu tài liệu API của đúng SDK bạn đang ship — các loại key thì ổn định, còn widget quanh chúng thì không.*
