---
title: "Bloc: kiến trúc nhàm chán nhưng scale được"
description: "Event vào, state ra — vì sao bloc vẫn là mặc định của team Flutter lớn."
seoDescription: "Kiến trúc Flutter bloc: event state dự đoán được, test app lớn, state management scale."
keywords:
  - flutter bloc architecture
  - bloc state management
  - flutter scalable architecture
  - flutter event state
  - bloc testing
tags: ["Flutter", "OpenSource", "Architecture", "StateManagement"]
sources:
  - name: "Bloc GitHub"
    url: "https://github.com/felangel/bloc"
  - name: "Bloc docs"
    url: "https://bloclibrary.dev/"
related:
  - slug: "oss-flutter-deer"
    title: "Flutter Deer"
  - slug: "oss-serverpod"
    title: "Serverpod"
category: "Deep Dive"
topic: "Open Source"
level: "Intermediate"
author: "Trung Hieu"
publishDate: "2026-09-10"
emoji: "🧱"
draft: false
---

Xu hướng xoay vòng; team production vẫn ship với Bloc vì nó **dự đoán được**. UI gửi event; bloc emit state; widget rebuild từ state.

![Sơ đồ: Bloc Architecture](/blog/images/oss-bloc-architecture.svg)



## Vì sao scale được

1. Event log debug được.
2. Test bloc không cần pump cả app.
3. Biên sở hữu feature rõ ràng.

## Mẹo dùng hiện đại

- Ưu tiên builder/selector của `flutter_bloc` hơn rebuild cả trang.
- Giữ bloc không dính side-effect điều hướng `BuildContext`.
- Ghép tầng repository — bloc không phải data layer.

## Cạm bẫy

God-bloc ôm cả app. Chia theo feature và lifecycle. Cũng đừng map 1:1 mọi thay đổi field thành event.

Nếu team cần architecture mặc định năm 2026, Bloc vẫn là câu trả lời bảo vệ được.
