---
title: "dart-lang/ai: bộ gói MCP chính thức của Dart"
package: "dart_mcp"
repo: "dart-lang/ai"
githubUrl: "https://github.com/dart-lang/ai"
category: "AI/ML"
stars: 279
forks: 73
lastUpdate: "2026-08-28"
pubDev: "https://pub.dev/packages/dart_mcp"
youtube: "https://www.youtube.com/results?search_query=dart+mcp+server+flutter"
priority: "High"
phase: "P1"
trendRank: 0
description: "Repo chính thức của nhóm Dart cho các gói AI và GenAI: dart_mcp để dựng server/client MCP, dart_mcp_server mở công cụ Dart cho mô hình AI, và skills để quản lý skill của agent."
seoDescription: "dart-lang/ai chứa các gói MCP chính thức của Dart — dart_mcp, dart_mcp_server và skills. Mỗi gói làm gì, cách gắn dart_mcp_server vào Claude Code hay Cursor, và khi nào nên tự viết server."
keywords:
  - dart mcp
  - dart_mcp_server
  - flutter mcp server
  - model context protocol dart
  - công cụ ai cho flutter
  - gói ai của dart
topics:
  - mcp
  - ai
  - dart
summary:
  - "**dart-lang/ai** là nơi nhóm Dart đặt các gói AI và GenAI chính thức, duy trì dưới tổ chức `dart-lang`."
  - "Repo có ba gói: `dart_mcp` (dựng server và client MCP), `dart_mcp_server` (mở công cụ phát triển Dart cho mô hình AI) và `skills` (CLI quản lý skill trong package hoặc git repo)."
  - "`dart_mcp_server` là thứ đa số lập trình viên Flutter muốn dùng trước — nó cho AI agent quyền truy cập thật vào analyzer, test và pub."
  - "**279★**, BSD-3-Clause, phát triển tích cực với 81 issue đang mở cho cả ba gói."
related:
  - slug: flutter-skill
    title: "flutter-skill: cho AI agent điều khiển ứng dụng đang chạy"
  - slug: agent-plugins
    title: "agent-plugins: hướng dẫn thư viện & công cụ trong Flutter"
  - slug: genui
    title: "genui: hướng dẫn giao diện & thành phần UI trong Flutter"
  - slug: flutter-zero
    title: "Flutter Zero: Flutter khi bỏ đi dart:ui"
faq:
  - q: dart_mcp và dart_mcp_server khác nhau thế nào?
    a: "dart_mcp là thư viện — bạn dùng nó để tự viết server và client MCP bằng Dart. dart_mcp_server là một server hoàn chỉnh dựng từ thư viện đó, mở công cụ phát triển Dart và Flutter cho mô hình AI. Muốn agent phân tích và chạy test dự án thì dùng dart_mcp_server; muốn mở nghiệp vụ của riêng bạn cho agent thì dùng dart_mcp."
  - q: Đây có phải dự án chính thức của nhóm Dart không?
    a: "Đúng. Nó nằm trong tổ chức dart-lang cùng SDK và các gói lõi, cả ba gói đều xuất bản lên pub.dev với cùng giấy phép BSD-3-Clause như phần còn lại của Dart."
  - q: Những công cụ AI nào dùng được dart_mcp_server?
    a: "Bất kỳ client MCP nào nói chuyện qua stdio. README hướng dẫn thiết lập cho Gemini CLI, Gemini Code Assist, Cursor và GitHub Copilot trong VS Code, nhưng giao thức mới là giao diện — server không quan tâm client nào kết nối, miễn là hỗ trợ Tools và Resources."
  - q: Gói skills dùng để làm gì?
    a: "Đó là CLI quản lý các skill đóng gói trong package hoặc kéo về từ git repo. Nó mới nhất trong ba gói và cũng ít ổn định nhất, nên hãy đọc README của chính nó trước khi phụ thuộc vào giao diện."
datePublished: "2026-08-28"
dateModified: "2026-08-28"
draft: false
---

[`dart-lang/ai`](https://github.com/dart-lang/ai) là nơi nhóm Dart đặt phần việc AI và GenAI của mình. Không phải framework, cũng chẳng phải sản phẩm — đây là monorepo gồm ba gói gọn ghẽ, và một trong số đó có lẽ là thứ đáng cài nhất năm nay với lập trình viên Flutter. **279★**, BSD-3-Clause, cập nhật lần cuối **2026-08-28**.

## Trong repo có gì?

Ba gói đã xuất bản, mỗi gói một phạm vi riêng:

| Gói | Làm gì |
| --- | --- |
| [`dart_mcp`](https://pub.dev/packages/dart_mcp) | Thư viện để dựng server *và* client MCP bằng Dart |
| [`dart_mcp_server`](https://pub.dev/packages/dart_mcp_server) | Server MCP hoàn chỉnh, mở công cụ dự án Dart cho mô hình AI |
| [`skills`](https://pub.dev/packages/skills) | CLI quản lý skill đóng trong package và từ git repo |

Model Context Protocol là phần đường ống cho phép trợ lý AI gọi công cụ thật thay vì đoán mò. `dart_mcp` là bản hiện thực Dart cho cả hai nửa của giao thức đó.

## Vì sao đáng quan tâm trong năm 2026

Phần lớn thiết lập "AI trong editor" hiện vẫn chỉ làm việc với văn bản. Mô hình đọc file, đoán xem analyzer sẽ nói gì, và sai đủ thường xuyên để gây khó chịu. Một server MCP khép vòng lặp đó lại: agent thôi đoán kết quả của analyzer và bắt đầu *chạy* nó.

`dart_mcp_server` là phiên bản thực dụng của điều đó cho Dart và Flutter. Trỏ agent vào nó và agent có quyền truy cập thật vào công cụ của dự án chứ không phải một ấn tượng nghe hợp lý. Lỗi phân tích là lỗi phân tích thật. Kết quả test là kết quả test thật.

Việc nó đến từ `dart-lang` chứ không phải bên thứ ba quan trọng hơn ta tưởng. Công cụ gọi ra ngoài tới `dart` và `flutter` sẽ vỡ mỗi khi SDK đổi định dạng output. Một server được duy trì ngay cạnh SDK không gặp vấn đề đó.

## Bắt đầu như thế nào

Server là thứ đa số muốn trước, và bạn không phải cài gì cả — nó đi kèm trong Dart SDK từ bản 3.9 trở đi và chạy bằng `dart mcp-server`. Việc của bạn chỉ là khai báo nó với client. Với Gemini CLI hoặc Cursor, đó là một khối trong `.gemini/settings.json` hoặc `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "dart": {
      "command": "dart",
      "args": ["mcp-server"]
    }
  }
}
```

Với GitHub Copilot trong VS Code có lối tắt — một thiết lập, và extension Dart tự đăng ký server cho bạn:

```json
"dart.mcpServer": true
```

Bất kỳ client MCP nào nói stdio đều dùng được; server cần hỗ trợ Tools và Resources, và chạy tốt nhất khi có Roots. Sau khi kết nối, thường bạn chỉ cần bảo agent kết nối tới app đang chạy — nó sẽ tự tìm các instance Dart Tooling Daemon trên máy và các ứng dụng Flutter/Dart đăng ký với chúng.

Muốn tự viết server, hãy thêm thư viện:

```bash
dart pub add dart_mcp
```

## Khi nào nên dùng?

- bạn muốn agent lập trình chạy analyzer và bộ test thật, thay vì tưởng tượng ra chúng
- bạn xây công cụ Dart hoặc Flutter và muốn client AI điều khiển nó qua một giao thức chuẩn
- bạn duy trì công cụ nội bộ và muốn mở nó một lần qua MCP thay vì viết tích hợp cho từng trợ lý
- bạn đóng gói skill dùng lại cho agent và muốn chúng được đánh phiên bản cùng package sở hữu

## Điểm còn hạn chế

Ba gói ở ba mức trưởng thành rất khác nhau, và chính README của server mở đầu bằng việc tự nhận là thử nghiệm và sẽ còn thay đổi nhanh. Hãy hiểu đúng nghĩa đen: danh sách tool và các cờ vẫn dịch chuyển giữa các bản phát hành. `skills` còn mới hơn và ít ổn định nhất — hãy đọc README của nó thay vì giả định giao diện sẽ giữ nguyên.

Repo cũng có 81 issue đang mở, phản ánh tốc độ thay đổi của bề mặt MCP hơn là sự bỏ bê. Nếu bạn có ghim phiên bản ở đâu, hãy ghim ở đây.

Và một lưu ý phạm vi: đây là công cụ AI cho *Dart*, không phải công cụ AI cho *giao diện Flutter*. Muốn sinh giao diện từ mô hình, xem [genui](/vi/recipes/genui/); muốn điều khiển app đang chạy, xem [flutter-skill](/vi/recipes/flutter-skill/).

## Các lựa chọn đáng so sánh

- [flutter-skill: cho AI agent điều khiển ứng dụng đang chạy](/vi/recipes/flutter-skill/) — MCP cho runtime thay vì cho toolchain
- [agent-plugins: hướng dẫn thư viện & công cụ trong Flutter](/vi/recipes/agent-plugins/)
- [genui: hướng dẫn giao diện & thành phần UI trong Flutter](/vi/recipes/genui/)

## Câu hỏi thường gặp

### dart_mcp và dart_mcp_server khác nhau thế nào?

`dart_mcp` là thư viện — bạn dùng nó để tự viết server và client MCP bằng Dart. `dart_mcp_server` là một server hoàn chỉnh dựng từ thư viện đó, mở công cụ phát triển Dart và Flutter cho mô hình AI. Muốn agent phân tích và chạy test dự án thì dùng `dart_mcp_server`; muốn mở nghiệp vụ của riêng bạn cho agent thì dùng `dart_mcp`.

### Đây có phải dự án chính thức của nhóm Dart không?

Đúng. Nó nằm trong tổ chức `dart-lang` cùng SDK và các gói lõi, cả ba gói đều xuất bản lên pub.dev với cùng giấy phép BSD-3-Clause như phần còn lại của Dart.

### Những công cụ AI nào dùng được dart_mcp_server?

Bất kỳ client MCP nào nói chuyện qua stdio. README hướng dẫn thiết lập cho Gemini CLI, Gemini Code Assist, Cursor và GitHub Copilot trong VS Code, nhưng giao thức mới là giao diện — server không quan tâm client nào kết nối, miễn là hỗ trợ Tools và Resources.

### Gói skills dùng để làm gì?

Đó là CLI quản lý các skill đóng gói trong package hoặc kéo về từ git repo. Nó mới nhất trong ba gói và cũng ít ổn định nhất, nên hãy đọc README của chính nó trước khi phụ thuộc vào giao diện.

## Tài nguyên & liên kết

- **GitHub:** [dart-lang/ai](https://github.com/dart-lang/ai)
- **pub.dev:** [dart_mcp](https://pub.dev/packages/dart_mcp) · [dart_mcp_server](https://pub.dev/packages/dart_mcp_server) · [skills](https://pub.dev/packages/skills)
- **Giao thức:** [modelcontextprotocol.io](https://modelcontextprotocol.io/)

---

*Thuộc [FlutterCook](/vi/recipes/) — hướng dẫn thực hành về các thư viện, UI kit và ứng dụng Flutter mã nguồn mở tốt nhất. Xem [xu hướng GitHub](/vi/trends/) hoặc [hướng dẫn YouTube](/vi/youtube/).*
