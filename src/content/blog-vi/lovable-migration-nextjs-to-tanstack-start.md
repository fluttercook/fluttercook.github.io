---
title: "Lovable rời Next.js sau 6 tháng: những con số và phần bạn thật sự dùng lại được"
description: "Lovable chuyển toàn bộ sản phẩm từ Next.js trên Vercel sang TanStack Start trên Cloudflare workerd trong 6 tháng. TTFB giảm 49%, dev server nhẹ đi hơn 5 lần — và một sự cố OOM 11 phút. Phân tích cái gì đáng học, cái gì đừng bắt chước."
seoDescription: "Phân tích cuộc di trú của Lovable từ Next.js sang TanStack Start trên Cloudflare workerd: 6 tháng, 5 nhóm route, TTFB median giảm 49%, giới hạn 128 MB mỗi isolate, và bài học rút ra cho đội nhỏ."
keywords:
  - lovable next.js tanstack start
  - migration next.js sang tanstack
  - tanstack start cloudflare workers
  - v8 isolate 128mb
  - kiến trúc framework-agnostic
  - ttfb cloudflare workerd
category: "Phân tích"
topic: "Web Engineering"
level: "Nâng cao"
author: "Trung Hiếu"
publishDate: "2026-08-21"
emoji: "🚚"
tags: ["Web", "Next.js", "TanStack", "Cloudflare", "Kiến trúc"]
sources:
  - name: "Lovable — How we migrated lovable.dev away from Next.js"
    url: "https://lovable.dev/blog/how-we-migrated-lovable-dev-away-from-nextjs"
  - name: "TanStack Start"
    url: "https://tanstack.com/start"
  - name: "Cloudflare Workers — giới hạn (bộ nhớ, CPU, isolate)"
    url: "https://developers.cloudflare.com/workers/platform/limits/"
  - name: "MDN — View Transition API"
    url: "https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API"
draft: false
---

Đội Lovable vừa công bố nhật ký cuộc di trú của họ: rời Next.js trên Vercel để sang **TanStack Start chạy trên Cloudflare workerd**. Sáu tháng cho phần code, thêm hai tháng cho phần rollout, trên một sản phẩm đang phục vụ hàng chục triệu lượt truy cập.

Bài gốc đáng đọc nguyên văn — [How we migrated lovable.dev away from Next.js](https://lovable.dev/blog/how-we-migrated-lovable-dev-away-from-nextjs). Bài này không dịch lại nó. Tôi tóm những con số đã được công bố, rồi tách ra hai thứ mà một bài "chúng tôi đã đổi framework" thường trộn lẫn: **phần chỉ đúng ở quy mô của họ**, và **phần một đội năm người cũng dùng lại được ngay tuần sau**.

## Vì sao họ đổi, và vì sao lý do đó không phải là "Next.js tệ"

Ba động cơ, không cái nào là chê framework:

1. **Ăn đồ mình nấu.** Lovable sinh ra ứng dụng cho người dùng, và những ứng dụng đó chạy trên hạ tầng worker của chính họ. Sản phẩm chính lại chạy trên một stack khác. Mỗi lần nền tảng hở chỗ nào, đội làm sản phẩm không phải người đầu tiên đau.
2. **Quy mô một-ứng-dụng.** Trang chính là một ứng dụng lớn duy nhất chịu tải rất cao — khác hẳn bài toán "60 triệu ứng dụng nhỏ" mà nền tảng của họ đã giải xong.
3. **Gộp stack.** Hai runtime, hai mô hình deploy, hai bộ công cụ nội bộ. Chi phí đó không nằm ở hóa đơn mà nằm ở đầu người.

Điểm đáng chú ý về kiến trúc phía nền tảng: mỗi ứng dụng người dùng xuất bản chạy như **một worker riêng trong một V8 isolate**, có một worker cổng vào phân phối theo hostname, và isolate được tái sử dụng theo cơ chế LRU. Chính con số hiệu suất của mô hình này là thứ khiến việc kéo sản phẩm chính về cùng runtime trở nên hấp dẫn.

## Những con số

Đây là phần dễ trích dẫn sai nhất, nên tôi để nguyên dạng đã công bố:

| Chỉ số | Trước | Sau |
| --- | --- | --- |
| Thời gian build | 12+ phút | 6–9 phút |
| TTFB (median) | — | **giảm 49%** |
| TTFB (p90) | — | ban đầu **tệ gấp đôi**, chốt lại giảm 16% |
| RAM dev server | ~8 GB | ~1,5 GB |
| Khởi động dev server | ~70 giây | ~10 giây |
| Request phục vụ được trên mỗi isolate | dưới 10 | 500 – 10.000 |
| Quy mô codebase | 350K dòng | 910K dòng |
| Plugin build tự viết | 0 (Next.js lo sẵn) | **17** |

Hai dòng cuối là hai dòng trung thực nhất trong bảng, và cũng là hai dòng hay bị bỏ qua khi người ta kể lại câu chuyện này.

**p90 ban đầu tệ gấp đôi.** Median đẹp ngay, nhưng cái đuôi phân phối thì xấu đi trước khi tốt lên. Nếu bạn chỉ gắn median vào dashboard rồi mở van, bạn sẽ tuyên bố thắng lợi trong lúc nhóm người dùng chậm nhất đang chịu trận.

**17 plugin build.** Đây là cái giá thật của việc rời một framework "pin kèm sẵn". Bạn không xóa độ phức tạp, bạn chuyển nó từ chỗ có người khác bảo trì sang chỗ bạn bảo trì. Với Lovable, đổi lại là quyền kiểm soát runtime — họ cần nó. Với phần lớn đội khác, đó là 17 thứ mới có thể hỏng vào 2 giờ sáng.

## Cách họ làm: cắt theo hành trình người dùng, không cắt theo thư mục

Đây là phần kỹ thuật đáng học nhất, và nó gần như không liên quan gì tới việc framework nào thắng.

**Một proxy worker đứng trước tất cả.** Nó định tuyến theo route *và* theo người dùng, nghĩa là cùng một URL có thể rơi vào stack cũ hoặc stack mới tùy bạn là ai. Đó là điều kiện cần để có rollout theo phần trăm mà không cần fork toàn bộ ứng dụng.

**Năm nhóm route, chia theo hành trình người dùng.** Không chia theo "trang nào dễ port nhất" mà theo "chuyển cả một luồng người dùng qua bờ bên kia". Điều này giữ cho một người dùng trong một phiên phần lớn thời gian nằm gọn ở một stack.

**Khoảng 90% code bị đẩy ra khỏi framework.** Toàn bộ phần dùng chung nằm sau một alias `#shared/`, và **lint rule** cấm nó import ngược lên các API riêng của framework. Đây là chi tiết tôi thích nhất: ranh giới kiến trúc không được giữ bằng lời hứa trong file `CONTRIBUTING.md`, mà bằng thứ chặn được CI.

**Phần phụ thuộc nền tảng được bọc thành adapter.** Interface + dependency injection, nối bằng TS path alias. Framework trở thành lớp vỏ mỏng gọi vào lõi, thay vì lõi mọc rễ vào framework.

**Những thứ dính chặt được thay sớm.** `next/font`, `next/image`, auth, i18n — bốn thứ này bị gỡ ngay từ đầu, khi còn đang chạy Next.js. Rất khôn: chúng là loại phụ thuộc mà nếu để đến cuối sẽ biến ngày cuối cùng thành một vụ big-bang.

**Feature flag phải xác định (deterministic).** Cùng một người dùng luôn nhận cùng một quyết định. Nếu flag là ngẫu nhiên theo request, người dùng sẽ nhảy qua lại giữa hai stack giữa chừng một luồng.

**View Transitions API để che vết nối.** Điều hướng giữa hai stack là hard navigation — trình duyệt tải lại thật. View Transitions làm cho cú nhảy đó trông như một chuyển cảnh trong SPA. Đây là mẹo dùng được cho mọi cuộc di trú dần dần, kể cả di trú từ Rails sang cái gì đó.

**AI agent được giao việc theo lô có trần.** Kế hoạch bị chặn ở 12 PR, mỗi PR khoảng 800–1600 dòng. Con số đó không phải để agent chạy nhanh hơn — nó là kích thước mà **con người còn review nổi**.

## Bộ nhớ là ràng buộc thật, không phải CPU

Phần này là phần khác biệt nhất so với thế giới Node truyền thống, và cũng là phần tôi nghĩ nhiều người sẽ đọc lướt qua rồi trả giá sau.

Trong mô hình isolate, **giới hạn bộ nhớ mỗi isolate là 128 MB**, và isolate được tái sử dụng cho nhiều request. Nghĩa là mọi thứ bạn giữ ở phạm vi module đều nằm lại đó — nhân với số ứng dụng đang chia nhau isolate.

Ba chiến thuật họ nêu, xếp theo mức thu về:

- **Parse JSON lớn bên trong request handler, đừng parse ở top-level module.** Cùng một dữ liệu, chỉ khác chỗ đặt, giảm 2–12 lần bộ nhớ. Vì object ở module scope sống mãi, còn object trong handler được thu hồi.
- **Cắt các field API không dùng.** Bạn trả tiền bộ nhớ cho từng field mình fetch về rồi bỏ xó.
- **Đuổi bundle chỉ dành cho client ra khỏi server.** Ví dụ họ đưa ra rất đắt: TypeScript compiler nặng 9 MB code nhưng chiếm khoảng **18 MB bộ nhớ** khi được nạp.

Và rồi sự cố:

> Ở mức rollout 20% cho dashboard, tỉ lệ lỗi vọt lên 50%. Nguyên nhân không phải code mới — một file JSON tĩnh không liên quan đã đẩy các isolate vượt ngưỡng 128 MB. Khắc phục trong 11 phút.

Đọc kỹ hình dạng của sự cố này. Thay đổi gây ra nó **không nằm trong phần được rollout**. Bộ nhớ là tài nguyên dùng chung trong isolate, nên nó phá vỡ giả định quen thuộc rằng "chỉ 20% người dùng chịu rủi ro từ 20% rollout". 11 phút là con số của một đội có sẵn dashboard đúng chỗ và một nút tắt thật.

## Còn chuyện AI code tốt hơn trên TanStack Start?

Họ nói agent làm việc trên codebase mới ít ảo giác hơn, và quy nguyên nhân cho tính nhất quán: Next.js đã đi qua nhiều thế hệ API rất khác nhau (pages router, app router, các thay đổi lớn qua từng major), nên tập dữ liệu huấn luyện chứa đầy các mẫu code mâu thuẫn nhau cho cùng một câu hỏi.

Tôi cho rằng lập luận này đúng về cơ chế nhưng dễ bị suy rộng quá tay. Cái làm agent sai không phải "Next.js", mà là **nhiều cách làm cùng tồn tại cho cùng một việc**. Một codebase Next.js nhất quán, chỉ dùng app router, có lint rule chặn các mẫu cũ, sẽ cho agent kết quả tốt hơn nhiều so với một codebase TanStack Start viết theo năm phong cách. Đây là biến số bạn kiểm soát được mà không cần đổi framework.

Nói cách khác: nếu bạn đang định đổi stack *để AI viết code đỡ sai*, hãy thử dọn tính nhất quán trước. Rẻ hơn sáu tháng rất nhiều.

## Bạn có nên làm giống họ không? Gần như chắc chắn là không

Điều kiện khiến quyết định này hợp lý với Lovable:

- Họ **đã** vận hành hạ tầng worker cho hàng chục triệu ứng dụng người dùng. Runtime đích không phải thứ mới với họ.
- Sản phẩm chính chạy trên một stack khác với thứ họ bán — một chi phí chiến lược thật, không phải chuyện thẩm mỹ.
- Họ có đủ người để nuôi 17 plugin build và một proxy layer trong lúc vẫn ship tính năng.

Nếu ba điều đó không đúng với bạn, phép tính đảo chiều ngay. Sáu tháng của một đội sản phẩm là một quý rưỡi không có tính năng mới, đổi lấy một khoản cải thiện TTFB mà người dùng của bạn có thể không đo được.

## Phần dùng lại được, kể cả khi bạn không đổi gì

Đây là bốn thứ tôi nghĩ đáng lấy ra khỏi bài này ngay hôm nay:

1. **Dựng ranh giới `#shared/` và cưỡng chế bằng lint.** Đây là bảo hiểm rẻ nhất chống lại việc bị khóa vào framework. Bạn không cần biết trước mình sẽ đi đâu — chỉ cần lõi không mọc rễ vào bất cứ đâu. Làm được trong một sprint, có giá trị dù bạn có di trú hay không.
2. **Bọc phụ thuộc nền tảng sau interface.** Storage, auth, image, email. Không phải để "dễ đổi provider" theo nghĩa marketing, mà để phần logic của bạn test được mà không cần dựng cả thế giới.
3. **Rollout theo hành trình người dùng và theo flag xác định.** Đúng với mọi thay đổi rủi ro, không riêng di trú framework. Cộng thêm: gắn **p90 và p99** vào dashboard, đừng chỉ median.
4. **Coi bộ nhớ là ràng buộc hàng đầu nếu bạn chạy trên edge/serverless.** Quy tắc "parse trong handler, đừng parse ở module scope" là thứ áp dụng được ngay trên Cloudflare Workers, Vercel Edge, Deno Deploy — bất kỳ chỗ nào tái sử dụng isolate.

Và một quan sát cuối, không có trong bài gốc: codebase đi từ 350K lên 910K dòng. Một phần là tính năng mới trong sáu tháng đó, nhưng không thể là toàn bộ. Rời một framework có sẵn pin nghĩa là bạn tự viết những cục pin đó. Con số 910K là hình dạng thật của cái giá phải trả, và nó xứng đáng được đặt cạnh con số "TTFB giảm 49%" mỗi khi ai đó kể lại câu chuyện này.

## Câu hỏi thường gặp

**TanStack Start có thay thế được Next.js cho dự án mới không?**
Với ứng dụng thiên về client, cần kiểm soát runtime và muốn deploy lên edge — có, đáng cân nhắc nghiêm túc. Đổi lại bạn nhận ít quy ước sẵn hơn và tự lo nhiều thứ hơn. Lovable phải viết 17 plugin build; con số đó là dấu hiệu tốt về mức "tự lắp ráp" mà bạn nên chuẩn bị tinh thần.

**Giới hạn 128 MB mỗi isolate có phải con số cứng không?**
Đó là ngưỡng bộ nhớ của một Worker isolate trên Cloudflare. Hãy kiểm lại tài liệu giới hạn của Cloudflare cho gói bạn đang dùng trước khi thiết kế dựa trên nó — giới hạn nền tảng thay đổi theo thời gian.

**Di trú dần dần có luôn tốt hơn viết lại một lần không?**
Khi vạch đích còn dịch chuyển — tức sản phẩm vẫn phải ship tính năng trong lúc di trú — thì có. Viết lại một lần chỉ thắng khi bạn đóng băng được sản phẩm, và rất ít đội làm được điều đó trong sáu tháng.

**Vì sao p90 lại xấu đi trong khi median cải thiện?**
Median phản ánh trường hợp ấm (isolate đã sẵn sàng, cache đã nóng). Đuôi phân phối phản ánh cold start, isolate bị đuổi khỏi LRU, và những route chưa được tối ưu. Chuyển runtime cải thiện đường ấm trước, đường lạnh sau.

---

*Toàn bộ số liệu trong bài là theo công bố của Lovable trong [bài viết gốc](https://lovable.dev/blog/how-we-migrated-lovable-dev-away-from-nextjs); phần phân tích, phản biện và khuyến nghị là của tôi. Giới hạn nền tảng của Cloudflare thay đổi theo thời gian — hãy kiểm lại tài liệu chính chủ trước khi thiết kế dựa trên bất kỳ con số nào ở đây.*
