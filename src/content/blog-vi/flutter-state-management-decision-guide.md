---
title: "Riverpod, Bloc, signals hay setState: chọn cách quản lý state Flutter và sống chung với nó"
description: "Một màn hình danh sách với loading, error, data và pull-to-refresh, viết bốn lần — setState, ValueNotifier, Riverpod và Bloc — để bạn so sánh code thật thay vì so sánh tính từ. Kèm mốc mà setState thật sự hết đủ dùng."
seoDescription: "Cùng một màn hình Flutter viết bằng setState, ValueNotifier, Riverpod và Bloc, kèm bảng quyết định theo quy mô team, nhu cầu test và tỉ lệ async."
keywords:
  - quản lý state flutter
  - riverpod hay bloc
  - flutter setstate và provider
  - valuenotifier flutter
  - hướng dẫn flutter_bloc
  - package signals flutter
category: "Hướng dẫn"
topic: "Flutter"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-22"
emoji: "🧩"
tags: ["Flutter", "State Management", "Riverpod", "Bloc", "Kiến trúc"]
sources:
  - name: "Flutter — Danh sách các cách quản lý state"
    url: "https://docs.flutter.dev/data-and-backend/state-mgmt/options"
  - name: "Flutter — Phân biệt ephemeral state và app state"
    url: "https://docs.flutter.dev/data-and-backend/state-mgmt/ephemeral-vs-app"
  - name: "Flutter — Kiến trúc ứng dụng"
    url: "https://docs.flutter.dev/app-architecture"
  - name: "ValueNotifier — tài liệu API Flutter"
    url: "https://api.flutter.dev/flutter/foundation/ValueNotifier-class.html"
  - name: "ValueListenableBuilder — tài liệu API Flutter"
    url: "https://api.flutter.dev/flutter/widgets/ValueListenableBuilder-class.html"
  - name: "RefreshIndicator — tài liệu API Flutter"
    url: "https://api.flutter.dev/flutter/material/RefreshIndicator-class.html"
  - name: "Dart — Patterns"
    url: "https://dart.dev/language/patterns"
  - name: "Dart — Class modifiers"
    url: "https://dart.dev/language/class-modifiers"
  - name: "flutter_riverpod trên pub.dev"
    url: "https://pub.dev/packages/flutter_riverpod"
  - name: "flutter_bloc trên pub.dev"
    url: "https://pub.dev/packages/flutter_bloc"
  - name: "provider trên pub.dev"
    url: "https://pub.dev/packages/provider"
  - name: "signals trên pub.dev"
    url: "https://pub.dev/packages/signals"
related:
  - slug: "flutter-introduction-2026"
    title: "Flutter là gì: đọc một game 3D dựng trong 15 phút để hiểu cả framework"
  - slug: "creating-a-custom-progress-indicator"
    title: "Tạo progress indicator tùy chỉnh trong Flutter với CustomPaint"
draft: false
---

Mọi bài so sánh quản lý state trong Flutter đều là một danh sách tính năng. Riverpod có provider an toàn ở compile time. Bloc có luồng dữ liệu một chiều kèm event log. signals có reactivity chi tiết tới từng giá trị. Đúng hết, và vô dụng hết — danh sách tính năng cho bạn biết một thư viện *có gì*, không bao giờ cho biết nó *tốn gì* khi người bảo trì đoạn code đó không phải là bạn.

Cách nhìn hữu ích hơn: mỗi thư viện đang trả lời một câu hỏi khác nhau. Nếu câu hỏi đó không phải câu hỏi app của bạn đang đặt ra, thì tính năng của nó chỉ là chi phí bạn trả bằng thời gian review và thời gian onboard người mới. Nên thay vì liệt kê tính từ, bài này viết **cùng một tính năng bốn lần** — một màn hình load danh sách, hiển thị trạng thái loading, error, data và hỗ trợ pull-to-refresh — rồi đọc phần khác nhau.

Nói luôn phần không được lòng ai: `setState` cộng với `ValueNotifier` và `InheritedWidget` là đủ cho rất nhiều app production, và tài liệu chính thức của Flutter cũng vạch ranh giới theo hướng đó. Có một mốc thật sự mà nó hết đủ dùng. Mốc đó không phải "app to lên". Nó cụ thể hơn nhiều, và được gọi tên ở cuối bài.

## Mỗi thư viện đang trả lời một câu hỏi khác nhau

Hãy đọc những dòng dưới như câu hỏi thiết kế, không phải quảng cáo:

- **`setState`** trả lời *"widget nào cần build lại?"* — chỉ vậy thôi. Nó không có quan điểm gì về việc state nằm ở đâu, sống bao lâu, hay ai khác nhìn thấy nó.
- **`ValueNotifier` + `InheritedWidget`** trả lời *"làm sao một giá trị đi từ nơi nó nằm tới nơi nó được đọc, và làm sao bên đọc biết nó đã thay đổi?"* Đây là câu trả lời có sẵn của Flutter cho việc truyền dữ liệu. Nó không trả lời gì về vòng đời.
- **`provider`** trả lời *"làm sao đặt một object lên phía trên widget cần nó, và dispose đúng lúc?"* Nó là phần plumbing của `InheritedWidget` kèm sẵn cơ chế dispose.
- **Riverpod** trả lời *"ai sở hữu state này, nó được tạo khi nào, bị hủy khi nào, và cái gì tính lại khi nó đổi?"* Nó là một đồ thị phụ thuộc có vòng đời. Cache và invalidation mới là sản phẩm chính; dependency injection chỉ là hệ quả.
- **Bloc** trả lời *"chuyện gì đã xảy ra, và chuyện đó sinh ra cái gì?"* Sản phẩm của nó là một hình dạng thống nhất, kiểm toán được, grep được, mà mọi tính năng đều tuân theo bất kể ai viết.
- **signals** trả lời *"đúng chiếc lá nào trong cây widget cần build lại khi giá trị này đổi?"* Phụ thuộc được ghi nhận ngay lúc bạn đọc, nên bạn không bao giờ phải khai báo.

Chỉ hai trong số đó thật sự nói về state. Riverpod nói về *vòng đời*. Bloc nói về *quy ước*. Nếu nỗi đau của bạn không phải vòng đời cũng không phải quy ước, bạn đang đi nhầm quầy hàng.

## Cùng một tính năng, viết bốn lần

Một màn hình, bốn trạng thái: loading, failure, data, đang refresh. Các kiểu dữ liệu dùng chung cho mọi phiên bản:

```dart
class Recipe {
  const Recipe({required this.id, required this.title});
  final String id;
  final String title;
}

abstract interface class RecipeRepository {
  Future<List<Recipe>> fetchRecipes();
}
```

Mọi phiên bản dưới đây còn dùng hai widget trình bày không chứa logic state: `RecipeList(recipes)`, một `ListView.builder` gồm các `ListTile`, và `ErrorView(message, onRetry:)`, một dòng thông báo kèm nút thử lại. Cả bốn phiên bản dùng y hệt nhau nên tôi lược đi để phần khác biệt được thật.

Và, cho ba phiên bản mô hình hóa state một cách tường minh, một cây sealed class. Đây là phần người ta hay bỏ qua, và là phần quan trọng nhất — **mô hình state giống hệt nhau ở mọi thư viện.** Cái thay đổi chỉ là ai được phép dịch chuyển nó.

```dart
sealed class RecipeListState { const RecipeListState(); }

final class RecipeListLoading extends RecipeListState { const RecipeListLoading(); }

final class RecipeListFailure extends RecipeListState {
  const RecipeListFailure(this.error);
  final Object error;
}

final class RecipeListSuccess extends RecipeListState {
  const RecipeListSuccess(this.recipes);
  final List<Recipe> recipes;
}
```

Vì class là `sealed`, một `switch` trên nó là exhaustive: thêm trạng thái thứ tư thì mọi màn hình render nó sẽ không compile được cho tới khi bạn xử lý. Riêng tính năng Dart 3 đó đã xóa đi một phần lớn lý do người ta từng mua một thư viện state.

### Phiên bản 1 — `setState`, để lộ hết chỗ dễ sai

```dart
class _RecipeListPageState extends State<RecipeListPage> {
  RecipeListState _state = const RecipeListLoading();

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _state = const RecipeListLoading());
    try {
      final recipes = await widget.repository.fetchRecipes();
      if (!mounted) return;
      setState(() => _state = RecipeListSuccess(recipes));
    } catch (error) {
      if (!mounted) return;
      setState(() => _state = RecipeListFailure(error));
    }
  }

  @override
  Widget build(BuildContext context) => switch (_state) {
        RecipeListLoading() => const Center(child: CircularProgressIndicator()),
        RecipeListFailure(error: final e) => ErrorView('$e', onRetry: _load),
        RecipeListSuccess(recipes: final recipes) =>
          RefreshIndicator(onRefresh: _load, child: RecipeList(recipes)),
      };
}
```

Khoảng ba mươi dòng, và thật sự đúng — nhiều hơn những gì khá nhiều code Bloc làm được. Có ba điểm đáng gọi tên.

`if (!mounted) return;` không phải tùy chọn. Thiếu nó, người dùng bấm back giữa lúc request đang chạy sẽ nhận `setState() called after dispose()`. Mọi giải pháp state bất đồng bộ đều phải giải quyết chuyện này; ở đây bạn giải quyết bằng tay, hai lần, trong mỗi method có `await`.

`RefreshIndicator.onRefresh` cần một `Future` hoàn tất khi việc refresh xong, và `_load` tình cờ đúng là như vậy. Nhớ điểm này — đây là chỗ duy nhất `setState` *dễ hơn* Bloc.

Và giới hạn thật sự: **`_load` không unit test được.** Logic bị hàn chặt vào một object `State`, nên muốn test phải dùng `pumpWidget` và dựng cả cây widget. Ổn với một màn hình. Không ổn với bốn mươi màn hình.

### Phiên bản 2 — `ValueNotifier`, cùng logic nhưng nhấc ra ngoài

```dart
class RecipeListController extends ValueNotifier<RecipeListState> {
  RecipeListController(this._repository) : super(const RecipeListLoading());

  final RecipeRepository _repository;

  Future<void> load() async {
    value = const RecipeListLoading();
    try {
      value = RecipeListSuccess(await _repository.fetchRecipes());
    } catch (error) {
      value = RecipeListFailure(error);
    }
  }
}
```

```dart
class _RecipeListPageState extends State<RecipeListPage> {
  late final _controller = RecipeListController(widget.repository)..load();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<RecipeListState>(
      valueListenable: _controller,
      builder: (context, state, _) => switch (state) {
        RecipeListLoading() => const Center(child: CircularProgressIndicator()),
        RecipeListFailure(error: final e) =>
          ErrorView('$e', onRetry: _controller.load),
        RecipeListSuccess(recipes: final recipes) => RefreshIndicator(
            onRefresh: _controller.load,
            child: RecipeList(recipes),
          ),
      },
    );
  }
}
```

Không có gì được thêm vào. Có thứ bị *bỏ đi*: logic không còn chạm tới `BuildContext`, nên nó là một object Dart thuần mà bạn test được bằng `test()` bình thường với một repository giả. Không `pumpWidget`, không phải pump frame.

Hai cái bẫy không ai cảnh báo. **Gán `value` sau khi `dispose()` sẽ ném lỗi.** Vấn đề `mounted` không biến mất, nó chỉ dời chỗ — nếu route bị pop trong lúc `fetchRecipes()` đang chạy, `load()` chạy tiếp và gán vào một notifier đã bị dispose. Chặn bằng một cờ `bool _disposed` bạn set trong `dispose()` override, hoặc giữ controller ở nơi sống lâu hơn route.

**`ValueNotifier` bỏ qua thông báo khi giá trị mới `==` giá trị cũ.** Với `const RecipeListLoading()` ở cả hai phía, Dart canonicalise chúng thành cùng một instance, nên Loading → Loading không phát ra gì. Ở đây vô hại. Rất không vô hại vào ngày bạn thêm `Equatable` vào một class state rồi tự hỏi vì sao một state trông y hệt lại không render lại danh sách bạn vừa sửa tại chỗ.

Với một màn hình cỡ này, phiên bản 2 là chỗ rất nhiều app nên dừng lại. Không package nào, test được, và mọi developer Flutter đang sống đều đọc hiểu.

## Riverpod: state có chủ sở hữu và có vòng đời

Điểm bán hàng của Riverpod không phải "ít boilerplate hơn". Nó là: một mẩu state được khai báo một lần, ở top level, với vòng đời tường minh, và bất cứ thứ gì đọc nó sẽ tự tính lại khi nó đổi.

Các đoạn dưới đây nhắm tới **Riverpod 3.x với `flutter_riverpod`, không dùng code generation**, vì cú pháp đó ổn định qua nhiều major version. Kiểu annotation `@riverpod` của `riverpod_generator` sinh ra đúng những provider này với ít chữ hơn.

```dart
final recipeRepositoryProvider = Provider<RecipeRepository>((ref) {
  return HttpRecipeRepository();
});

final recipeListProvider = FutureProvider<List<Recipe>>((ref) async {
  return ref.watch(recipeRepositoryProvider).fetchRecipes();
});
```

Đó là toàn bộ tính năng. Không có `RecipeListState` — `FutureProvider` trả về một `AsyncValue`, chính là cây sealed ba trạng thái đã được viết sẵn cho bạn, cộng thêm hai trường hợp mà code tự viết tay thường quên: *đã có data nhưng đang refresh*, và *đã có lỗi nhưng vẫn còn data cũ dùng được*.

```dart
class RecipeListPage extends ConsumerWidget {
  const RecipeListPage({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return ref.watch(recipeListProvider).when(
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, stack) => ErrorView(
            '$error',
            onRetry: () => ref.invalidate(recipeListProvider),
          ),
          data: (list) => RefreshIndicator(
            onRefresh: () => ref.refresh(recipeListProvider.future),
            child: RecipeList(list),
          ),
        );
  }
}
```

`ref.refresh(recipeListProvider.future)` trả về một `Future`, đúng thứ `RefreshIndicator` cần — chỗ vướng víu mà bạn sắp thấy ở phiên bản Bloc không tồn tại ở đây. App được bọc một lần trong `ProviderScope`.

Vấn đề hủy request và `mounted` biến mất, không phải vì Riverpod khôn ngoan về `async`, mà vì *widget không còn sở hữu request nữa*. Provider sở hữu nó, và vòng đời của provider thuộc về scope. Khi listener cuối cùng biến mất, một provider auto-dispose sẽ tự dọn; còn nếu không auto-dispose thì kết quả nằm lại trong cache, và màn hình tiếp theo watch nó sẽ nhận danh sách đã cache thay vì gọi mạng lần hai. **Hành vi cache đó mới là lý do thật sự để chọn Riverpod**, và nó cũng là thứ tốn công nhất nếu làm bằng tay.

Test không cần widget nào cả:

```dart
test('recipeListProvider resolves from the repository', () async {
  final container = ProviderContainer(
    overrides: [recipeRepositoryProvider.overrideWithValue(FakeRepository())],
  );
  addTearDown(container.dispose);

  expect(await container.read(recipeListProvider.future), hasLength(3));
});
```

Khi bạn cần method trên state chứ không chỉ một future trần — ví dụ xóa lạc quan (optimistic delete) — bạn lên `AsyncNotifier`, nơi `AsyncValue.guard` gói trọn khối try/catch của phiên bản 1 thành một lời gọi:

```dart
class RecipeListNotifier extends AsyncNotifier<List<Recipe>> {
  @override
  Future<List<Recipe>> build() =>
      ref.watch(recipeRepositoryProvider).fetchRecipes();

  Future<void> reload() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(
      () => ref.read(recipeRepositoryProvider).fetchRecipes(),
    );
  }
}

final recipeListProvider =
    AsyncNotifierProvider<RecipeListNotifier, List<Recipe>>(RecipeListNotifier.new);
```

Nếu bạn đang ở một major version khác, hãy đối chiếu tên các class notifier với tài liệu hiện hành trước khi copy — phần API đó có thay đổi giữa các bản phát hành, trong khi `FutureProvider` và `ref.watch` thì không.

## Bloc: mọi thay đổi đều có tên và ghi log được

Bloc dùng lại đúng cây `RecipeListState` ở trên và thêm một cây thứ hai cho đầu vào. Việc nhân đôi đó là cái giá, và nó mua về một thứ rất cụ thể. Các đoạn dưới nhắm tới `flutter_bloc` 9.x.

```dart
sealed class RecipeListEvent { const RecipeListEvent(); }

final class RecipeListRequested extends RecipeListEvent { const RecipeListRequested(); }

final class RecipeListRefreshed extends RecipeListEvent { const RecipeListRefreshed(); }

class RecipeListBloc extends Bloc<RecipeListEvent, RecipeListState> {
  RecipeListBloc(this._repository) : super(const RecipeListLoading()) {
    on<RecipeListRequested>(_onLoad);
    on<RecipeListRefreshed>(_onLoad);
  }

  final RecipeRepository _repository;

  Future<void> _onLoad(
    RecipeListEvent event,
    Emitter<RecipeListState> emit,
  ) async {
    emit(const RecipeListLoading());
    try {
      emit(RecipeListSuccess(await _repository.fetchRecipes()));
    } catch (error) {
      emit(RecipeListFailure(error));
    }
  }
}
```

Phía widget tách làm hai, có chủ đích — nửa provider tạo bloc, nửa view chỉ đọc nó:

```dart
BlocProvider(
  create: (_) => RecipeListBloc(context.read<RecipeRepository>())
    ..add(const RecipeListRequested()),
  child: const RecipeListView(),
);
```

```dart
class RecipeListView extends StatelessWidget {
  const RecipeListView({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<RecipeListBloc, RecipeListState>(
      builder: (context, state) => switch (state) {
        RecipeListLoading() => const Center(child: CircularProgressIndicator()),
        RecipeListFailure(error: final e) => ErrorView(
            '$e',
            onRetry: () =>
                context.read<RecipeListBloc>().add(const RecipeListRequested()),
          ),
        RecipeListSuccess(recipes: final recipes) => RefreshIndicator(
            onRefresh: () {
              final bloc = context.read<RecipeListBloc>()
                ..add(const RecipeListRefreshed());
              return bloc.stream.firstWhere((s) => s is! RecipeListLoading);
            },
            child: RecipeList(recipes),
          ),
      },
    );
  }
}
```

Cái thân hàm `onRefresh` đó là cái giá thật thà của luồng dữ liệu một chiều. `add()` được thiết kế là bắn-rồi-quên, nhưng `RefreshIndicator` cần một `Future` hoàn tất khi công việc xong, nên bạn phải dựng lại nó bằng cách lắng nghe stream đầu ra. Codebase Bloc nào cũng có một biến thể của đoạn này; phần lớn giấu nó trong một helper rồi thôi để ý.

Cũng lưu ý `emit(const RecipeListLoading())` khi state khởi tạo đã là `const RecipeListLoading()`: `emit` bỏ qua state `==` với state hiện tại, nên lần emit đầu tiên đó không làm gì cả. Ở đây không thấy được, nhưng là nguồn bug thật khi state của bạn dùng `Equatable` và bạn emit lại một danh sách vừa sửa tại chỗ thay vì thay bằng danh sách mới.

Đổi lại bạn có `bloc_test`, đọc lên như một bản đặc tả:

```dart
blocTest<RecipeListBloc, RecipeListState>(
  'emits a success state when the repository returns',
  build: () => RecipeListBloc(FakeRepository()),
  act: (bloc) => bloc.add(const RecipeListRequested()),
  expect: () => [isA<RecipeListSuccess>()],
);
```

Và bạn có một thứ không lựa chọn nào khác trong danh sách này cho: **một hình dạng thống nhất.** Bốn mươi tính năng do mười hai người viết đều trông giống nhau. Điều đó đáng tiền thật ở một quy mô nhân sự nhất định, và không đáng gì cả ở dưới mức đó.

## signals: build lại đúng thứ nhỏ nhất vừa đổi

Package `signals` mang mô hình reactive primitive — ý tưởng đứng sau SolidJS và Preact signals — sang Dart. Bạn không khai báo phụ thuộc; chúng được ghi nhận ngay lúc bạn đọc.

```dart
final counter = signal(0);
final doubled = computed(() => counter.value * 2);

// In build():
Watch((context) => Text('${doubled.value}'));
```

`doubled` biết nó phụ thuộc `counter` vì nó đã đọc `counter`. Chỉ đúng cái `Watch` đã đọc `doubled` build lại — không phải widget bao ngoài, không phải cả route. Với màn hình có nhiều giá trị nhỏ độc lập (một form, một canvas editor, một dashboard cập nhật liên tục) thì đó là mức giảm phạm vi rebuild có thật so với một `setState` ở trên cùng.

Tôi cố ý không trình bày một bản async đầy đủ, vì phần API async của `signals` thay đổi giữa các bản phát hành nhiều hơn các primitive lõi, và một đoạn code gắn chặt vào một version sẽ nhanh lỗi thời. Hãy đọc tài liệu của package trước khi dùng.

Điểm chiến lược còn quan trọng hơn API: hệ sinh thái signals nhỏ hơn Riverpod hay Bloc, và tài liệu kiến trúc chính thức của Flutter viết quanh `Listenable`/`ChangeNotifier`. Đó không phải lý do để phản đối nó — đó là lý do để biết trước rằng bạn sẽ tự viết nhiều quy ước hơn và trả lời nhiều câu "sao chỗ này khác tutorial vậy?" hơn.

## Cái gì thật sự khác nhau khi app đã thật

Đếm số dòng cho một màn hình là thước đo tồi. Đây mới là những khác biệt lộ ra ở tháng thứ sáu:

| | setState + ValueNotifier | provider | Riverpod | Bloc |
| --- | --- | --- | --- | --- |
| Test logic không cần widget | Chỉ khi đã tách ra controller | Có | Có, qua `ProviderContainer` | Có, qua `bloc_test` |
| Cache dữ liệu server giữa các màn hình | Tự làm | Tự làm | Có sẵn | Tự làm ở tầng repository |
| Dispose đúng khi pop route | Bạn tự lo | Có sẵn | Có sẵn | Có sẵn |
| Thiếu dependency thì lỗi ở | — | Runtime | Compile time | Runtime |
| Thay dependency khi test | Tham số constructor | Override provider | Override provider | Tham số constructor |
| Truy "vì sao cái này đổi?" | Đọc code | Đọc code | Provider observer | Event log, theo thiết kế |
| Kết hợp `RefreshIndicator` | Tự nhiên | Tự nhiên | Tự nhiên | Cần vòng qua stream |
| Người mới làm được việc sau | Vài giờ | Vài giờ | Một hai ngày | Một ngày, rồi thành máy móc |

Dòng cuối là dòng các team hay xem nhẹ. Đường học của Bloc dốc ở đầu rồi phẳng — viết xong hai bloc là bạn đã viết được tất cả. Đường học của Riverpod thoải hơn lúc đầu và có một đoạn dốc thứ hai về sau, khi bạn gặp auto-dispose, family, và khác biệt giữa `ref.watch` với `ref.read` bên trong callback. Flutter thuần thì không có đường dốc nào, mà cũng không có trần: bạn cứ trả tiền đều đặn bằng plumbing viết tay.

## Một bảng quyết định bạn có thể cãi lại

Chọn dòng theo tín hiệu mạnh nhất, đừng cộng điểm.

| Nếu điều này đúng với app của bạn | Thì |
| --- | --- |
| Một hai người, chủ yếu state cục bộ/UI, vài lời gọi mạng | `setState` + `ValueNotifier`. Tách controller ra, khỏi cần package. |
| Làm một mình, nhưng cùng một object cần ở các màn hình không liên quan | `provider` với `ChangeNotifier`, hoặc Riverpod nếu bạn muốn phần cache. |
| Phần lớn màn hình dựa vào server, có cache và invalidation | Riverpod. Đây đúng là câu hỏi nó trả lời. |
| Từ sáu developer trở lên, nhiều squad, sản phẩm sống lâu | Bloc. Bạn đang mua sự đồng nhất, và đồng nhất tỉ lệ thuận với số người. |
| Compliance hoặc support cần dấu vết phát lại được của mọi thay đổi | Bloc. Không thứ nào khác cho bạn cái này mà không phải tự xây. |
| Vài màn hình có nhiều giá trị nhỏ độc lập nhau | signals, giới hạn trong đúng những màn hình đó. |
| Bạn đang migrate một codebase lớn sẵn có | Cái codebase đó đang dùng. Migrate nửa vời tệ hơn cả hai đầu. |

Hai điều bảng đó không nói. Thứ nhất, trộn lẫn là bình thường và lành mạnh: một app Riverpod vẫn dùng `setState` cho chuyện một cái card đang mở hay đóng, và tài liệu Flutter vạch đúng ranh giới đó giữa state *ephemeral* và *app state*. Thứ hai, chọn cái nào thì **class state sealed và interface repository vẫn y nguyên**, và đó là lý do việc chuyển đổi ít đau hơn Internet hay dọa. Bạn đang đổi cơ chế vận chuyển, không phải viết lại tính năng.

## Chỗ mà setState hết đủ dùng

Không phải "khi app to lên". Bốn mốc cụ thể, và bạn thường gặp theo đúng thứ tự này:

1. **Cùng một dữ liệu server được đọc bởi hai widget không có quan hệ cha–con.** Lúc này bạn hoặc phải nhấc state lên rồi khoan xuống qua một loạt constructor không liên quan, hoặc cần một cơ chế truyền dữ liệu thật. Đây là ngưỡng `InheritedWidget`/`provider`, và nó đến sớm.
2. **State phải sống lâu hơn widget đã tạo ra nó.** Người dùng rời màn hình rồi quay lại, và bạn fetch lại một danh sách không hề đổi. Mọi cách vá bên trong một object `State` đều là một cache bạn phải tự bảo trì — kèm invalidation, nửa khó của vấn đề.
3. **Bạn bắt đầu đếm số lần `if (!mounted)`.** Khi một file có nhiều lệnh kiểm tra `mounted` và cờ `_disposed` hơn số nhánh nghiệp vụ thật, framework đang nói với bạn rằng request không nên do widget sở hữu.
4. **Hai người bất đồng trong review về việc state của một tính năng nên nằm ở đâu, hơn một lần.** Đây là ngưỡng quy ước, và là mốc duy nhất thuần túy mang tính xã hội. Nó cũng là lý lẽ duy nhất ủng hộ Bloc mà tự nó đứng vững.

Mốc 1 và 2 chỉ về Riverpod. Mốc 3 chỉ về bất cứ thứ gì nắm vòng đời giúp bạn. Mốc 4 chỉ về Bloc. Nếu hôm nay codebase của bạn không dính mốc nào trong bốn mốc đó, thêm một package quản lý state chỉ làm app khó đọc hơn mà không đổi lại được gì.

## FAQ

**Tôi dùng nhiều hơn một cách trong cùng một app được không?**
Được, và phần lớn codebase lành mạnh đều làm vậy. `setState` cho state ephemeral của widget — đang mở, đang focus, đang hover — và một giải pháp dùng chung cho app state. Chỗ hỏng là khi có *hai* giải pháp dùng chung cho cùng một loại state, khiến người mới không đoán được tính năng nào đang dùng cái nào.

**`provider` chết rồi khi đã có Riverpod?**
Không. Nó vẫn được bảo trì và vẫn đang chạy trong production, và vẫn là cách ít nghi thức nhất để đưa một object lên trên các widget cần nó. Riverpod do chính tác giả đó viết để sửa những vấn đề cụ thể — lỗi không tìm thấy provider ở runtime, việc kết hợp provider vướng víu, khả năng test bên ngoài cây widget. Nếu bạn không gặp những vấn đề đó, `provider` chẳng tốn gì của bạn.

**Có bắt buộc dùng code generation với Riverpod không?**
Không. Mọi ví dụ ở đây là Dart thuần, không bước build nào. Package `riverpod_generator` bỏ bớt các tham số kiểu và suy ra loại provider từ chữ ký hàm, dễ chịu trên codebase lớn và thuần túy là chi phí thừa trên codebase nhỏ. Bạn có thể dùng sau mà không phải viết lại widget.

**Boilerplate của Bloc có đáng với một developer làm một mình không?**
Thường là không. Mỗi tương tác một class event chỉ đáng khi nhiều người cùng chạm vào một chỗ code và cần một pattern chung, hoặc khi bạn cần một log phát lại được của những gì đã xảy ra. Làm một mình, bạn trả đủ giá của một quy ước mà thu về rất ít lợi ích — và bạn luôn có thể thêm sau, vì các class state giữ nguyên không đổi.

**Chính team Flutter khuyến nghị gì?**
Tài liệu cố ý không nêu quan điểm về package nhưng rất có quan điểm về cấu trúc: tách ephemeral state khỏi app state, và theo một cách phân tầng kiểu MVVM với một tầng repository nằm giữa view model và nguồn dữ liệu. Chính cách phân tầng đó khiến lựa chọn trong bài này đảo ngược được. Làm đúng các tầng thì thư viện state chỉ còn là chi tiết cài đặt của một trong số chúng.

---

*Code trong bài nhắm tới Flutter 3.x với sealed class và pattern matching của Dart 3; các đoạn Riverpod nhắm tới cú pháp 3.x không dùng code generation và các đoạn Bloc nhắm tới `flutter_bloc` 9.x. Những phần API tôi đã đánh dấu là nhạy cảm theo version — các class notifier trong Riverpod, các helper async trong `signals` — chính là những chỗ cần đối chiếu với tài liệu package hiện hành trước khi copy. Toàn bộ bảng quyết định là đánh giá chủ quan của tôi từ các app đã ship, không phải số đo; các đánh đổi là thật nhưng con số của team bạn sẽ khác của tôi.*
