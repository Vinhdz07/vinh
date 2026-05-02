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

Sua file `.env`:

```env
API_ID=123456
API_HASH=your_api_hash_here
SESSION_NAME=userbot
BOT_PREFIX=.
ADMIN_IDS=123456789,987654321
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

## Ghi chu

- Day la **userbot**, khong phai BotFather bot token.
- Userbot dung session dang nhap cua tai khoan that, vi vay hay bao mat file `.session` va `.env`.
- Neu ban muon, co the mo rong them cac lenh nhu:
  - xoa tin nhan
  - tag all
  - auto reply
  - download/upload media
  - quan ly group
