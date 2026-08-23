# Triển khai bộ sync lên server

Mục này dựng một dịch vụ nhỏ trên server nội dung: định kỳ kéo repo về, build lại
site, rồi mirror những bài chưa có sang ba blog Blogger — cộng một trang admin để
xem trạng thái và bấm đẩy bài ngay, khỏi phải SSH.

Bài viết vẫn được soạn trong repo và merge vào `main` như cũ. Server chỉ lo phần
đưa lên Blogger, nhả dần theo hạn mức thay vì đổ một lượt.

```
                 GitHub main
                      │  git reset --hard
                      ▼
  ┌───────────────────────────────────────────────┐
  │ /opt/fluttercook            (checkout)        │
  │ /var/lib/fluttercook        (state + log)     │
  └───────────────────────────────────────────────┘
        │ systemd timer 08:20 & 20:20        │ admin_server.py :8787
        ▼                                    ▼
   deploy/sync.sh ──► Blogger API      nginx ──► https://jo.fighttech.vn
```

## Có gì trong này

| File | Việc của nó |
|---|---|
| `sync.sh` | một lượt sync: cập nhật repo → `npm run build` → publish → làm mới báo cáo |
| `admin_server.py` | API + dashboard, thư viện chuẩn của Python, không cần cài thêm |
| `admin/index.html` | giao diện dashboard (một file, không tải gì từ ngoài) |
| `install.sh` | dựng máy mới trên Debian/Ubuntu, chạy lại được nhiều lần |
| `fluttercook-sync.{service,timer}` | lịch chạy |
| `fluttercook-admin.service` | dashboard chạy nền |
| `nginx.conf.example` | vhost cho `jo.fighttech.vn`, TLS + giới hạn tần suất |
| `crontab.example` | phương án thay thế nếu máy không dùng systemd |
| `env.example` | mọi tuỳ chọn, kèm giải thích |

## Cài lần đầu

```bash
git clone https://github.com/fluttercook/fluttercook.github.io.git /tmp/fc
sudo bash /tmp/fc/deploy/install.sh --host jo.fighttech.vn
```

`install.sh` cài Node 22, Python + PyYAML, nginx; tạo user hệ thống `fluttercook`;
clone repo vào `/opt/fluttercook`; tạo `/var/lib/fluttercook`; sinh admin token;
bật systemd timer và dịch vụ admin; dựng vhost nginx.

Nó **cố ý không làm** hai việc, vì cả hai đều hướng ra ngoài và nên là quyết định
của người vận hành: không tự xin chứng chỉ TLS, và không tự chạy sync lần nào.
Cuối script in ra đúng lệnh cho cả hai.

### Credentials

Token OAuth **không nằm trong git** và không bao giờ nên nằm trong đó. Chép tay:

```bash
scp -r .app_dist you@fighttech.vn:/tmp/app_dist
```
```bash
sudo mv /tmp/app_dist /opt/fluttercook/.app_dist && sudo chown -R fluttercook:fluttercook /opt/fluttercook/.app_dist && sudo chmod -R go-rwx /opt/fluttercook/.app_dist
```

`sync.sh` dừng ngay nếu không thấy `.app_dist`, thay vì chạy tiếp rồi hỏng giữa chừng.

### TLS

Trỏ bản ghi A của `jo.fighttech.vn` về máy này rồi:

```bash
sudo certbot --nginx -d jo.fighttech.vn
```

Trước khi có chứng chỉ, dashboard vẫn vào được qua HTTP — **đừng dán token trước lúc đó**.

### Chạy thử trước khi bật lịch

```bash
sudo -u fluttercook /opt/fluttercook/deploy/sync.sh --dry-run --no-pull
```

Dry run vẫn build đầy đủ và dựng nguyên payload sẽ gửi, ghi ra `/tmp/blogger-dry-run/`,
nhưng không gọi API ghi nào cả.

## Trang admin

```bash
sudo cat /var/lib/fluttercook/admin_token
```

Mở `https://jo.fighttech.vn/`, dán token. Trang này cho:

- trạng thái từng blog: đã đăng bao nhiêu / tổng, quyền hiện tại, số bài đang live
- commit mà server đang đứng
- **Chạy sync** — chọn hạn mức, chọn blog, tuỳ chọn dry run
- **Chỉ cập nhật status** — chỉ dò lại API, không đăng gì
- log chạy trực tiếp, tự cuộn theo khi job đang chạy
- lịch sử 15 lần chạy gần nhất, bấm vào xem lại log
- danh sách bài còn chờ đăng

Token nằm trong `sessionStorage`, gửi qua header `Authorization`. Không có cookie
nên không có bề mặt CSRF: một form từ site khác không đặt được header đó.
Server chỉ nghe `127.0.0.1`, nginx lo TLS và giới hạn 30 request/phút mỗi IP.

Đổi token:

```bash
sudo sh -c 'python3 -c "import secrets;print(secrets.token_urlsafe(32))" > /var/lib/fluttercook/admin_token' && sudo systemctl restart fluttercook-admin
```

## Lịch và hạn mức

Mặc định 08:20 và 20:20 hàng ngày, `SYNC_LIMIT=3`. Hạn mức tính theo **mỗi tổ hợp
blog × mục × ngôn ngữ**: 3 blog × 2 mục × 2 ngôn ngữ × 3 bài = tối đa 36 bài mỗi
lượt, 72 bài mỗi ngày nếu có sẵn từng đó bài chưa đăng. Thực tế thấp hơn nhiều vì
`--skip-existing` bỏ qua bài đã lên.

Sửa trong `/etc/fluttercook/sync.env`, rồi `sudo systemctl restart fluttercook-admin`.
Đổi giờ thì sửa `fluttercook-sync.timer` và `sudo systemctl daemon-reload`.

## Vì sao state nằm ngoài checkout

`sync.sh` chạy `git reset --hard origin/main`, nên mọi thứ nó ghi vào repo sẽ mất ở
lượt sau. Bản đồ slug → postId mà mất thì lượt kế tiếp không tìm ra bài cũ và **tạo
bản sao của mọi bài**. Vì vậy `BLOGGER_SYNC_STATE`, `BLOGGER_STATUS_JSON` và
`BLOGGER_STATUS_MD` đều trỏ vào `/var/lib/fluttercook/`.

Lần đầu, chép bản đồ hiện có sang chứ đừng để nó tự tạo mới:

```bash
sudo -u fluttercook cp /opt/fluttercook/data/blogger_sync.json /var/lib/fluttercook/blogger_sync.json
```

Sao lưu duy nhất cần quan tâm cũng là file này.

## Khi có trục trặc

```bash
sudo systemctl status fluttercook-admin fluttercook-sync.timer
```
```bash
sudo journalctl -u fluttercook-sync -n 100 --no-pager
```
```bash
sudo ls -t /var/lib/fluttercook/logs | head
```

| Hiện tượng | Nguyên nhân thường gặp |
|---|---|
| `author-cannot-create` | tài khoản mới có quyền AUTHOR; Blogger yêu cầu ADMIN mới `posts.insert` được |
| `token-dead` | refresh token bị thu hồi — tạo lại rồi chép `.app_dist` sang |
| `astro build failed` | sync dừng trước bước publish, không đẩy `dist/` cũ lên |
| `every target failed` | credentials hoặc mạng; đây là trường hợp duy nhất script trả về exit 1 |

Một blog hỏng riêng lẻ chỉ là cảnh báo và script vẫn trả 0 — đó là trạng thái bình
thường khi đang chờ cấp quyền, không đáng để timer báo động mỗi 12 tiếng.

## Chưa làm

- Chưa dùng thử trên chính `fighttech.vn`. Toàn bộ `sync.sh`, `admin_server.py` và
  dashboard đã chạy thật ở máy dev; riêng `install.sh` và `nginx.conf.example` mới
  chỉ kiểm cú pháp, vì cần một máy Debian/Ubuntu để xác nhận.
- Chưa có cảnh báo ra ngoài (email/Telegram) khi sync hỏng — hiện phải tự xem dashboard.
