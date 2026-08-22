---
title: "AI code review không ai muốn tắt: vấn đề là độ chính xác, không phải năng lực"
description: "Một con bot review để lại ba mươi comment trên một pull request sẽ bị tắt trong vòng một tuần, và ba phát hiện thật chết chung với hai mươi bảy cái vụn vặt. Cách thiết kế cho precision: convention của chính repo thay vì best practice chung chung, giới hạn cứng số comment, mỗi finding phải bác bỏ được, một lượt phản biện đối kháng, và một chỉ số duy nhất để tinh chỉnh tất cả."
seoDescription: "Thiết kế AI code reviewer mà team chịu đọc: convention riêng của repo, context bám theo diff, ngưỡng severity kèm giới hạn cứng, finding bác bỏ được, lượt refute và tinh chỉnh theo action rate."
keywords:
  - ai code review
  - review pull request tự động
  - bot review code ci
  - ai review báo sai nhiều
  - github actions ai review
  - llm review code chính xác
category: "Hướng dẫn"
topic: "Developer Tooling"
level: "Trung cấp"
author: "Trung Hiếu"
publishDate: "2026-08-22"
emoji: "🔍"
tags: ["AI", "Code Review", "Developer Tools", "CI/CD"]
sources:
  - name: "GitHub Docs — GitHub Actions"
    url: "https://docs.github.com/en/actions"
  - name: "GitHub REST API — Pull request reviews"
    url: "https://docs.github.com/en/rest/pulls/reviews"
  - name: "GitHub Docs — Pull requests"
    url: "https://docs.github.com/en/pull-requests"
  - name: "Claude Code GitHub Action"
    url: "https://github.com/anthropics/claude-code-action"
  - name: "Dart — Linter rules"
    url: "https://dart.dev/tools/linter-rules"
related:
  - slug: "building-an-ai-agent-team-chief-of-staff-pattern"
    title: "Mô hình Chief of Staff: biến đống chat AI rời rạc thành một đội ngũ agent"
  - slug: "what-the-research-says-about-prompt-engineering"
    title: "Nghiên cứu thật sự nói gì về prompt engineering — kiểm chứng 5 tuyên bố đang lan truyền"
draft: false
---

Kịch bản hỏng lúc nào cũng giống nhau. Thứ Hai có người cắm một con AI reviewer vào CI. Nó để lại ba mươi comment trên pull request đầu tiên: hai mươi bảy cái là đặt tên biến, "cân nhắc tách đoạn này ra helper", và một gợi ý thêm test mà cái test đó đã nằm sẵn ở file cách đó hai bậc. Ba cái là thật, và một trong ba là bug mất dữ liệu thật sự nằm trong nhánh retry.

Không ai thấy ba cái đó. Đến thứ Tư mọi người lướt qua phần review của bot để xuống phần review của người. Đến thứ Hai tuần sau nó thành một check không chặn merge với thông báo đã tắt — một tích hợp chết nhưng vẫn đốt token mỗi lần push.

Con bot không dở trong việc tìm bug. Nó tìm ra bug rồi. Nó dở ở chỗ **không biết im lặng**, mà trong code review thì đó chính là toàn bộ công việc. Ngân sách của một reviewer không phải là compute, mà là mức độ sẵn lòng đọc tiếp của đồng đội — và niềm tin đó cập nhật rất nhanh. Nếu trong mười comment đầu tiên một developer đọc chỉ có một cái hữu ích, họ đã học được một quy tắc — *lướt qua thôi, thường chả có gì* — và quy tắc đó được áp lên comment thứ mười một, đúng cái bug mất dữ liệu. Bạn không thất bại ở khâu tìm ra nó. Bạn thất bại ở khâu làm cho nó được đọc.

Từ đó ra một sự bất đối xứng khó chịu nhưng chịu lực cho cả bài này: **bỏ sót một bug rẻ hơn là nói sai một câu.** Bỏ sót thì bạn quay về đúng chỗ trước khi có bot, tức là vẫn có người review. Nói sai một câu thì bạn mất sự chú ý và một phần niềm tin của người đọc, mất vĩnh viễn, và mất trên mọi comment về sau. Nên bài toán thiết kế ở đây là precision chứ không phải recall, và gần như mọi núm vặn đáng vặn đều là núm làm cho bot nói ít đi.

## Thứ gì công cụ tất định quyết được thì đừng bao giờ đưa tới model

Nguồn nhiễu lớn nhất là một model đi suy lại những ý kiến mà linter đã có sẵn, suy dở hơn và kém nhất quán hơn. Đẩy tất cả những gì quyết định được xuống cho một công cụ im lặng, nhanh, và báo ngay trong editor trước khi PR tồn tại.

| Câu hỏi | Ai nên trả lời |
| --- | --- |
| Code đã format đúng chưa? | `dart format` |
| Import thừa, code chết, thiếu `await`? | `dart analyze` |
| Chỗ `await` này có để `BuildContext` mất an toàn không? | lint `use_build_context_synchronously` |
| Đây có phải future không được await? | lint `unawaited_futures` |
| Cách đặt tên có khớp với repo không? | một analyzer rule hoặc plugin `custom_lint` |
| Nhánh retry có dùng lại idempotency key sau khi khởi động lại không? | model |

Cái gì viết được thành lint rule thì viết thành lint rule. Nó không bịa, và nó không tiêu tốn sự chú ý khi review, vì nó không bao giờ lên tới PR. Việc của model chỉ là dòng cuối cùng: những lỗi cần giữ hai file và một chuỗi sự kiện trong đầu cùng lúc.

## Best practice chung chung chính là cỗ máy sinh nhiễu

Một model không có context của repo sẽ rơi về mức trung bình của toàn bộ code nó từng thấy. Đó là lý do bạn nhận được "cân nhắc thêm xử lý lỗi" trên một hàm mà mục đích duy nhất của nó là đẩy lỗi lên cho caller xử lý.

Sửa bằng một file convention mà reviewer đọc ở mỗi lần chạy. Phần quan trọng không nằm ở các quy tắc — mà ở chỗ **mỗi quy tắc phải kèm một phản ví dụ tường minh**. Chính phần loại trừ đó mới mua được precision.

```markdown
## Error handling
Repository and data-source methods return `Result<T, AppError>`
(lib/core/result.dart). Throwing out of a repository method is a bug.
NOT A FINDING: `throw` inside a private helper the repository already
wraps, or anything under test/.

## Migrations
A change to a table under db/schema/ requires a paired file in
db/migrations/ in the same PR.
NOT A FINDING: a change to a view, or an index-only change.
```

Hãy rút các quy tắc này từ bằng chứng, không phải từ khẩu vị. Nguồn tốt nhất là chính lịch sử review của bạn: lấy vài trăm comment review của người thật trên các PR đã merge, gom cụm lại, giữ những cái lặp lại ở nhiều reviewer khác nhau. Một quy tắc mà người thật đã nhắc ba lần thì đáng tự động hoá. Một quy tắc chưa ai từng nhắc là quy tắc bạn tự nghĩ ra, và nó sẽ sinh nhiễu mãi mãi.

## Phạm vi: đúng phần diff, cộng đúng những gì diff chạm vào

Đưa nguyên file cho model là nguồn nhiễu lớn thứ hai, vì nó sẽ đi review cả phần không ai đụng vào. Reviewer ghét chuyện đó hơn cả ghét bị nói sai — comment thường đúng mà vẫn khó chịu, vì tác giả không viết dòng đó và cũng sẽ không sửa nó trong PR này.

Hãy lắp context có chủ đích: các hunk thay đổi dưới dạng unified diff; với mỗi symbol mà diff sửa, lấy định nghĩa hiện tại của nó và các call site cách một bậc; file test phủ file đã đổi nếu có; và file convention. Rồi nói thẳng với model rằng ngoài đó ra thì không có gì khác trong repository tồn tại, và code không đổi chỉ xuất hiện với vai trò context, không bao giờ là mục tiêu hợp lệ của một finding. Một câu lệnh đó loại bỏ được cả một lớp comment. Và hãy review phần diff **kể từ SHA đã review lần trước**, không phải toàn bộ PR lần nữa — nếu không thì mỗi lần force-push sẽ đăng lại đúng ba comment cũ và bản thân cái thread trở nên không đọc nổi.

## Một giới hạn cứng, một tầng bị xoá, và mỗi finding một mệnh đề bác bỏ được

Severity mà không có giới hạn thì chỉ là trang trí. Chính cái giới hạn mới ép model phải xếp hạng, và xếp hạng mới là hành vi bạn thật sự cần.

| Tầng | Nghĩa là gì | Xử lý thế nào |
| --- | --- | --- |
| **S1** | Mất dữ liệu, hỏng dữ liệu, vượt xác thực, credential lọt vào diff, crash trên đường đi có thể tới được | Comment inline |
| **S2** | Vỡ hợp đồng: API export ra ngoài, format serialize, hoặc đổi schema mà thiếu migration đi kèm | Comment inline |
| **S3** | Vi phạm một quy tắc đã viết trong file convention | Chỉ inline nếu giới hạn còn chỗ |
| **S4** | Mọi thứ còn lại — đặt tên, dễ đọc, "cân nhắc tách ra", cảm giác về hiệu năng, ý kiến về test | **Xoá** |

S4 bị xoá, chứ không gập vào một khối details. Một khối gập lại vẫn tập cho người ta thói quen mở nó ra, tức là vẫn tốn sự chú ý, mà đó lại đúng là chỗ nhiễu nằm. Nếu không đáng một comment inline thì cũng không đáng tồn tại.

Đặt giới hạn là một con số cố định nhỏ — năm là điểm khởi đầu hợp lý — và **đừng** cho nó co giãn theo kích thước diff. Giới hạn này áp lên sự chú ý của người đọc, mà sự chú ý đó không tự lớn lên vì PR của bạn to hơn. Nếu có hơn năm finding S1/S2 sống sót, hãy đăng năm cái và ghi rõ đã nén bao nhiêu cái: một PR có tám lỗi đúng nghĩa về tính đúng đắn thì cần được chẻ nhỏ, không phải cần một bài review dài hơn.

Rồi tới nửa sau của vấn đề. "Chỗ này có thể gây race condition" là một câu không bác bỏ được, mà comment không bác bỏ được là loại tệ nhất — người đọc không thể gạt đi mà không bỏ công, nên hoặc là họ bỏ công rồi bực, hoặc gạt đi rồi thấy áy náy mơ hồ. Hãy ép cấu trúc; bắt model xuất ra một object, không phải văn xuôi:

```json
{
  "file": "lib/sync/queue_flusher.dart",
  "line": 142,
  "severity": "S1",
  "claim": "Retried flushes generate a new idempotency key after the queue is re-hydrated from disk.",
  "trigger": "The app is killed mid-flush and restarts before the server's 2xx arrives.",
  "consequence": "The server treats the retry as a new request and creates a duplicate order.",
  "evidence": ["lib/sync/queue_flusher.dart:131-149", "lib/sync/queue_store.dart:88"],
  "falsifiable_by": "If QueueStore.hydrate() preserves item.idempotencyKey, this finding is wrong.",
  "confidence": 0.7
}
```

`falsifiable_by` là trường gánh phần việc chính: nó chỉ ra **một** thứ duy nhất cần kiểm tra. Reviewer mở một file, nhìn một method, rồi hoặc sửa một bug thật hoặc đóng comment trong mười giây mà không để lại dư âm gì. Trên thực tế, những finding không nặn ra nổi dòng đó chính là những finding mơ hồ — loại chúng ngay ở tầng schema là một khoản precision miễn phí. Khi render comment, hãy mở đầu bằng trigger chứ đừng mở đầu bằng khái niệm trừu tượng:

> **S1 — trùng đơn hàng khi app bị kill giữa lúc flush rồi khởi động lại.** Nếu app bị kill giữa lúc flush và khởi động lại trước khi nhận được 2xx, `hydrate()` dựng lại item mà không có idempotency key ban đầu, nên lần retry được gửi đi như một request mới.
> *Sai nếu:* `QueueStore.hydrate()` vốn đã khôi phục `item.idempotencyKey`.

## Đề xuất trước, rồi phản biện

Prompt của bên đề xuất phần lớn là một danh sách những điều cấm — đúng hình dạng cần có cho một công cụ đặt precision lên đầu.

```text
You are reviewing ONE pull request diff.

You are given:
  CONVENTIONS - the written rules of this repository.
  DIFF        - unified diff of the changed hunks only.
  CONTEXT     - for each changed symbol: its current definition, its
                callers one hop out, and its test file.
Nothing else in the repository exists as far as you are concerned.

Report a finding ONLY if all four hold:
  a. The defect is introduced or made reachable BY THIS DIFF.
  b. You can name a concrete trigger: an input, a sequence, a state.
  c. You can name the consequence in words an on-call engineer would use.
  d. Someone can prove you wrong by checking ONE thing that you name.

Never report:
  - anything `dart analyze` or `dart format` decides
  - style, naming, file layout, or "consider extracting"
  - missing tests, unless this diff changes a behaviour an existing test
    asserts and that test was not updated
  - performance, unless you can point at a loop bound or an allocation
    that scales with user-controlled input
  - anything on a line shown to you only as CONTEXT

Severity: S1 correctness/security, S2 contract break, S3 violates a rule
written in CONVENTIONS. Do not emit S4.

Output a JSON array, at most 8 objects, matching the schema below.
An empty array is a correct and common answer.
```

Dòng cuối cùng đó xứng đáng có mặt. Nếu không cho phép tường minh rằng "không tìm thấy gì" là một kết quả hợp lệ, model sẽ coi mảng rỗng là dấu hiệu mình chưa làm xong việc và sẽ nặn ra thứ gì đó để lấp chỗ trống.

Rồi tới thay đổi có đòn bẩy lớn nhất trong cả thiết kế này, đổi lại chỉ tốn thêm một lượt gọi cho mỗi finding: một lượt thứ hai mà nhiệm vụ duy nhất là phá huỷ các finding. Đưa cho nó finding và đúng cái context đó, nhưng **không** đưa lập luận của bên đề xuất và không đưa điểm confidence, để nó không bị neo theo phần biện hộ.

```text
You are the refuter. Below is a finding another reviewer proposed and the
exact context that reviewer was given. Your job is to KILL it.

Work through these in order:
1. Is the trigger reachable? Look for the guard that prevents it.
2. Is the consequence real, or handled downstream in the context shown?
3. Is the claim about a line this diff did not change?
4. Does CONVENTIONS explicitly permit this pattern?
5. Is the finding true but unverifiable from the context given - would
   checking it require reading code that is not here?

Return exactly: {"verdict": "KILL" | "SURVIVES", "reason": "..."}

Default to KILL. "I cannot verify this either way" is a KILL.
You are not scored on how many findings you let through.
```

Hai chi tiết còn quan trọng hơn cả câu chữ. **Mặc định phải là KILL** — một finding không kiểm chứng được thì chết, vì đăng nó lên nghĩa là bắt một con người đi làm phần kiểm chứng mà bạn không làm nổi. Và phải nói thẳng với bên phản biện rằng nó không được chấm điểm theo số finding cho qua; thiếu câu đó, model có xu hướng trôi dần về phía cho qua để tỏ ra dễ chịu. Trường hợp số 5 mới là cái làm nhiều người bất ngờ: những finding có vẻ đúng nhưng không kiểm chứng được từ context đã cho lại là loại comment đắt nhất bạn có thể đăng, vì nó đẻ ra một thread dài rồi kết thúc bằng câu "à cái đó không sao đâu, xem bên service kia".

## Nối vào CI mà không phát khoá cho thiên hạ

Bốn chặng, mỗi chặng một step riêng để khi có comment tệ lọt ra bạn còn mở được JSON trung gian ra soi.

```yaml
name: ai-review
on: pull_request

permissions:
  contents: read
  pull-requests: write

jobs:
  review:
    runs-on: ubuntu-latest
    env:
      MODEL_API_KEY: ${{ secrets.MODEL_API_KEY }}
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      - name: Collect diff and one-hop context
        run: |
          tools/review/collect.sh \
            "${{ github.event.pull_request.base.sha }}" \
            "${{ github.event.pull_request.head.sha }}" > /tmp/context.json
      - run: tools/review/propose.sh /tmp/context.json > /tmp/proposed.json
      - run: |
          tools/review/refute.sh /tmp/context.json /tmp/proposed.json \
            > /tmp/survivors.json
      - run: tools/review/post.sh /tmp/survivors.json --max 5
```

**Đăng một review, không phải N comment.** Endpoint reviews nhận một mảng `comments` trong cùng một request, nên tác giả nhận một thông báo thay vì năm. Gửi `"event": "COMMENT"`.

**Chống trùng qua các lần push.** Kết thúc mỗi comment bằng một marker vô hình — `<!-- rv:sha256(file + normalized_claim) -->` — đọc các comment đã có trước khi đăng, và bỏ qua những cái đã nằm sẵn ở đó. Hãy hash đường dẫn file cộng với phần claim đã chuẩn hoá, đừng hash số dòng, vì rebase phá vỡ mọi cách chống trùng dựa trên dòng.

**Đừng bao giờ checkout code từ fork bằng một token có đặc quyền.** Workflow được kích hoạt bởi `pull_request` từ một fork sẽ nhận `GITHUB_TOKEN` chỉ đọc và không có secret — đó chính là lớp bảo vệ bạn cần. Cách lách đầy cám dỗ là `pull_request_target`, vốn chạy với secret của repo gốc; ghép nó với một lệnh checkout code ở PR head là trao API key của bạn cho bất kỳ ai mở một pull request. Nếu cần phủ cả fork, hãy chạy model trong job bị hạn chế rồi đăng comment từ một job `workflow_run` riêng, job đó không bao giờ thực thi code của fork.

## Action rate là con số duy nhất giúp bạn tinh chỉnh được thứ gì

Số comment, số finding mỗi PR, hay "đã phát hiện bao nhiêu vấn đề" đều là chỉ số làm màu. Con số đáng quan tâm là tỷ lệ comment đã đăng dẫn tới một thay đổi trong code:

**Action rate** = (số comment mà vùng dòng nó neo vào có thay đổi trước khi merge, cộng với số comment được người thật trả lời đồng tình) ÷ tổng số comment đã đăng.

Đo nó là việc thuần cơ học. Mỗi comment vốn đã mang ID của finding trong cái marker chống trùng. Một job đi qua các PR mới merge, lấy review comment qua REST API, rồi với từng cái thì diff file được neo giữa commit lúc comment và commit merge để xem vùng bị gắn cờ có dịch chuyển không. Trạng thái resolve của thread lấy được qua GraphQL API của GitHub, nhưng hãy coi đó là tín hiệu yếu — người ta resolve thread để dọn giao diện, không phải để bày tỏ đồng tình.

Rồi tinh chỉnh theo nó. Action rate đang giảm: nâng ngưỡng lên — bỏ hẳn S3, hạ giới hạn số comment, nâng sàn confidence. Action rate cao nhưng bot gần như im bặt: bạn đang lọc quá tay, hạ sàn confidence xuống một nấc rồi xem cái gì quay lại. Số lượng tăng mà action rate vẫn giữ: file convention đang làm đúng việc của nó.

Con số tổng ít hữu ích hơn phần chi tiết. Hãy nhóm action rate **theo quy tắc convention đã sinh ra finding đó**, sắp tăng dần, rồi xoá quy tắc tệ nhất. Thường chỉ một số ít quy tắc sinh ra phần lớn nhiễu, và bỏ đi một quy tắc là khoản lợi về precision lớn hơn mọi lần chỉnh prompt. Ngưỡng của riêng mình, và đây là ý kiến chứ không phải số đo: nếu chưa tới một nửa số comment bạn đăng dẫn tới thay đổi, thì bạn đang tiêu niềm tin nhanh hơn kiếm được, và cách sửa là nói ít đi chứ không phải giải thích hay hơn.

## Đừng bao giờ để ai nói được câu "bot duyệt rồi mà"

Sự im lặng của reviewer có hai nguyên nhân khả dĩ: hoặc không có lỗi, hoặc lỗi nằm ngoài tầm nhìn của reviewer. Nhìn từ ngoài vào hai cái giống hệt nhau, và toàn bộ thiết kế ở trên làm cho nguyên nhân thứ hai trở nên phổ biến — bạn đã bó nó vào phần diff, chặn ở năm comment, và bảo bên phản biện giết mọi thứ nó không kiểm chứng được. Recall thấp là cái giá bạn đã đồng ý trả.

**Đừng để nó gửi `APPROVE`.** Reviews API nhận `APPROVE`, `REQUEST_CHANGES` hoặc `COMMENT`. Chỉ gửi `COMMENT`, luôn luôn. Một lượt approve là một tuyên bố mang tính xã hội — rằng có một người đủ năng lực đã xem và chấp nhận gắn tên mình vào kết quả — và công cụ không bảo chứng nổi điều đó. **Đừng để nó thoả mãn yêu cầu review**: giữ nguyên required reviewers và CODEOWNERS như cũ, vì nếu check của bot có thể làm PR chuyển xanh thì sớm muộn cũng có người ship dựa trên nó. Và **đừng để nó chặn merge**. Nhóm duy nhất có lý lẽ thật sự để chặn là credential bị commit vào diff, mà cái đó là việc của một secret scanner tất định chứ không phải của model. Nên trên thực tế, con bot không chặn gì cả.

Thứ nó nên trở thành là một đồng nghiệp rất tốt: đọc diff trước mọi người, mỗi quý nói ba câu cứu bạn khỏi mất một cuối tuần, và ngoài ra thì im lặng. Đó là một sản phẩm nhỏ hơn nhiều so với thứ người ta hay dựng, và cũng là phiên bản duy nhất còn được giữ lại sau sáu tháng.

## FAQ

**Chặn ở năm comment thì có bỏ sót bug thật không?**
Có, đôi khi. Đó là đánh đổi có chủ ý: bỏ sót một finding thì bạn quay về đúng chỗ trước khi có bot, còn nói sai một câu thì làm hỏng vĩnh viễn cách người ta đọc câu tiếp theo. Bạn không thay thế review của con người, nên sàn không phải là số không — người thật vẫn còn đó.

**Có cần model đầu bảng cho việc này không?**
Bên đề xuất hưởng lợi nhiều nhất từ model mạnh, vì phần khó là nhìn ra lỗi trình tự trải qua nhiều file. Bên phản biện là nhiệm vụ hẹp hơn nhiều — đọc một mệnh đề, đối chiếu với context được cấp, mặc định là không — nên đó là chỗ hợp lý để dùng model nhỏ hơn. Hãy đo action rate trước và sau khi hạ cấp từng bên thay vì đoán.

**Lấy convention ở đâu nếu team chưa từng viết ra?**
Từ chính các PR đã merge. Export comment review của người thật vài tháng gần nhất, gom cụm theo chủ đề, giữ những gì lặp lại ở nhiều reviewer khác nhau. Viết mỗi cái thành một quy tắc kèm ít nhất một phản ví dụ "NOT A FINDING" tường minh, rồi sau vài tuần thì xoá quy tắc nào có action rate kém.

**PR rất lớn hoặc monorepo thì sao?**
Bó context theo đường dẫn CODEOWNERS sở hữu các file đã đổi, và giữ giới hạn tính theo PR chứ không theo package. Nếu có hơn năm finding S1/S2 thật sự sống sót qua lượt phản biện, kết quả trung thực là năm comment cộng một dòng nói rằng PR này quá lớn để review cho tử tế.

---

*Thang severity, con số giới hạn năm comment và ngưỡng action rate năm mươi phần trăm là ý kiến của mình, không phải kết quả đo đạc — hãy coi chúng là điểm khởi đầu để tinh chỉnh theo số liệu của chính bạn. Các hành vi của GitHub Actions được mô tả ở đây (giới hạn token với fork, các giá trị `event` của endpoint reviews, gộp comment vào một review) đều có trong tài liệu, nhưng nền tảng CI vẫn thay đổi; hãy đối chiếu phần permissions và hình dạng API với tài liệu GitHub hiện hành trước khi đưa lên production.*
