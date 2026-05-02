# Telegram Userbot admin-only

Userbot nay duoc viet bang Python + Telethon. Bot se dang nhap bang tai khoan Telegram cua ban va chi cho phep cac `ADMIN_IDS` da khai bao duoc dung lenh.

## Tinh nang san co

- Chi cho phep admin ID dung lenh
- Ho tro command prefix tuy chon, mac dinh la `.`
- Co cac lenh mau:
  - `.help`
  - `.ping`
  - `.id`
  - `.whois`
  - `.chatinfo`
  - `.uptime`
  - `.echo <noi_dung>`
  - `.admins`
  - `.allowhere`
  - `.disallowhere`
  - `.groups`
  - `.mygroups [so_luong]`
  - `.broadcastdry <noi_dung>`
  - `.broadcast <noi_dung>`

## 1. Tao API Telegram

Ban vao trang:

`https://my.telegram.org`

Sau do:

1. Dang nhap bang so dien thoai Telegram
2. Vao `API development tools`
3. Tao app de lay:
   - `API_ID`
   - `API_HASH`

## 2. Cai dat

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Neu may bao loi thieu `python3-venv`, ban co the cai nhanh bang cach:

```bash
python3 -m pip install --user -r requirements.txt
cp .env.example .env
```

Sua file `.env`:

```env
API_ID=123456
API_HASH=your_api_hash_here
SESSION_NAME=userbot
BOT_PREFIX=.
ADMIN_IDS=123456789,987654321
ALLOWED_GROUPS_FILE=allowed_groups.json
BROADCAST_DELAY_SECONDS=3
BROADCAST_MAX_TARGETS=20
MYGROUPS_LIMIT=15
```

## 3. Lay Telegram user ID

De lay ID admin, ban co the:

- Dung bot nhu `@userinfobot`
- Hoac chay userbot, sau do dung lenh `.id`

`ADMIN_IDS` la danh sach ID duoc phep dung lenh, ngan cach bang dau phay.

## 4. Chay userbot

```bash
python3 userbot.py
```

Lan dau chay, Telethon se hoi:

- so dien thoai
- ma code Telegram gui ve
- neu co thi nhap them mat khau 2FA

Sau khi dang nhap thanh cong, file session se duoc tao trong may.

## Cach dung

- Tu tai khoan nam trong `ADMIN_IDS`, gui lenh trong chat bat ky:
  - `.help`
  - `.ping`
  - `.echo xin chao`
- Neu mot ID khong nam trong danh sach admin thi lenh se bi bo qua.

## Broadcast an toan theo allowlist

Userbot nay **khong** duoc thiet ke de phat tan tin nhan dai tra hoac tu dong join group hang loat. Thay vao do, no ho tro gui thong bao den danh sach nhom ban tu chon truoc:

- `.allowhere`
  - Dung trong group hien tai de them group do vao allowlist
- `.disallowhere`
  - Xoa group hien tai khoi allowlist
- `.groups`
  - Xem cac group dang duoc phep nhan broadcast
- `.mygroups [so_luong]`
  - Liet ke mot so nhom/kenh dang tham gia de lay ID nhanh
- `.broadcastdry <noi_dung>`
  - Xem truoc so dich, delay va noi dung truoc khi gui that
- `.broadcast <noi_dung>`
  - Gui noi dung toi cac group trong allowlist, co delay mac dinh 3 giay moi group

File `allowed_groups.json` se duoc tao tu dong de luu danh sach group da cho phep.

Ban co the chinh cac bien sau trong `.env`:

- `ALLOWED_GROUPS_FILE`: file luu allowlist
- `BROADCAST_DELAY_SECONDS`: so giay cho giua moi lan gui
- `BROADCAST_MAX_TARGETS`: so dich toi da duoc phep gui trong 1 lan
- `MYGROUPS_LIMIT`: so nhom/kenh mac dinh khi dung `.mygroups`

## Ghi chu

- Day la **userbot**, khong phai BotFather bot token.
- Userbot dung session dang nhap cua tai khoan that, vi vay hay bao mat file `.session` va `.env`.
- Neu ban muon, co the mo rong them cac lenh nhu:
  - xoa tin nhan
  - tag all
  - auto reply
  - download/upload media
  - quan ly group
