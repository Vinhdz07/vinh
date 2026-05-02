# Telegram VPS Manager Bot

Bot Telegram an toan de dieu khien va quan ly VPS cua ban. Project nay cung cap cac lenh da duoc gioi han de ban van hanh may chu tu Telegram ma khong mo ra mot cua hau "chay shell tuy y".

Bot ho tro:

- xem tong quan he thong
- kiem tra CPU, RAM, disk, uptime
- liet ke service duoc phep quan ly
- start/stop/restart/status service systemd
- doc log gan day cua service
- xem danh sach container Docker
- reboot VPS voi buoc xac nhan

## Vi sao bot nay an toan hon

Project **khong** ho tro lenh "run command" de thuc thi shell tuy y tu Telegram. Moi thao tac nguy hiem deu di qua:

- xac thuc Telegram admin IDs
- whitelist `ALLOWED_SERVICES`
- timeout cho lenh he thong
- gioi han so dong log
- tuy chon bat/tat reboot va Docker

## Cau truc project

```text
.
├── .env.example
├── pyproject.toml
├── requirements.txt
├── scripts/
│   └── install.sh
└── src/
    └── vps_bot/
        ├── __init__.py
        ├── bot.py
        ├── config.py
        ├── main.py
        └── system_ops.py
```

## Yeu cau

- Linux VPS co `systemd`
- Python 3.10+
- Bot token tu `@BotFather`
- Telegram user id cua ban

## Cai dat nhanh

```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

Hoac cai thu cong:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

## Cau hinh

Sao chep file mau:

```bash
cp .env.example .env
```

Chinh sua `.env`:

```env
TELEGRAM_BOT_TOKEN=123456789:replace_me
TELEGRAM_ADMIN_IDS=123456789
ALLOWED_SERVICES=nginx,ssh,docker,redis-server,postgresql
COMMAND_TIMEOUT_SECONDS=20
DEFAULT_LOG_LINES=100
MAX_LOG_LINES=300
USE_SUDO=false
ALLOW_REBOOT=false
ALLOW_DOCKER_COMMANDS=true
```

### Giai thich bien moi truong

- `TELEGRAM_BOT_TOKEN`: token bot Telegram
- `TELEGRAM_ADMIN_IDS`: danh sach Telegram user id duoc phep dung bot
- `ALLOWED_SERVICES`: whitelist service systemd duoc phep thao tac
- `COMMAND_TIMEOUT_SECONDS`: timeout cho lenh he thong
- `DEFAULT_LOG_LINES`: so dong mac dinh khi xem log
- `MAX_LOG_LINES`: gioi han so dong log toi da
- `USE_SUDO`: neu `true`, bot se them `sudo` vao `systemctl`, `journalctl`, `shutdown`
- `ALLOW_REBOOT`: bat/tat lenh reboot
- `ALLOW_DOCKER_COMMANDS`: bat/tat lenh `/docker`

## Cac lenh Telegram

- `/start` - thong tin bot va danh sach tinh nang
- `/help` - hien thi huong dan
- `/status` - tong quan CPU, RAM, disk, uptime
- `/uptime` - xem thoi gian hoat dong
- `/cpu` - xem CPU usage va load average
- `/memory` - xem RAM va swap
- `/disk` - xem dung luong dia
- `/services` - liet ke service duoc phep quan ly
- `/service status <ten-service>`
- `/service start <ten-service>`
- `/service stop <ten-service>`
- `/service restart <ten-service>`
- `/logs <ten-service> [so-dong]`
- `/docker` - xem Docker containers
- `/reboot confirm` - reboot VPS neu da bat `ALLOW_REBOOT=true`

Vi du:

```text
/status
/service restart nginx
/logs nginx 80
/docker
```

## Chay bot

### Cach 1: chay truc tiep

```bash
source .venv/bin/activate
vps-telegram-bot
```

Hoac:

```bash
python -m vps_bot.main
```

### Cach 2: chay bang systemd

Tao file `/etc/systemd/system/vps-telegram-bot.service`:

```ini
[Unit]
Description=Telegram VPS Manager Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/vps-telegram-bot
EnvironmentFile=/opt/vps-telegram-bot/.env
ExecStart=/opt/vps-telegram-bot/.venv/bin/vps-telegram-bot
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Sau do:

```bash
sudo systemctl daemon-reload
sudo systemctl enable vps-telegram-bot
sudo systemctl start vps-telegram-bot
sudo systemctl status vps-telegram-bot
```

## Cau hinh sudo an toan

Neu bot khong chay bang root ma van can quan ly service, hay cap sudo toi thieu.

Vi du file `/etc/sudoers.d/vps-telegram-bot`:

```sudoers
botuser ALL=(ALL) NOPASSWD: /bin/systemctl, /usr/bin/systemctl, /bin/journalctl, /usr/bin/journalctl, /sbin/shutdown, /usr/sbin/shutdown
```

**Khong** cap `NOPASSWD: ALL`.

## Lay Telegram user id

Ban co the dung `@userinfobot` de lay user id Telegram cua minh, sau do them vao `TELEGRAM_ADMIN_IDS`.

## Bao mat

- Khong chia se bot token
- Chi them nhung service can thiet vao `ALLOWED_SERVICES`
- Neu khong can reboot, giu `ALLOW_REBOOT=false`
- Neu khong can Docker, giu `ALLOW_DOCKER_COMMANDS=false`
- Han che quyen sudo toi muc toi thieu
- Nen dung bot trong chat rieng thay vi group

## Kiem tra nhanh

```bash
python -m compileall src
```

## Huong mo rong

Ban co the mo rong them:

- quan ly nhieu VPS qua mot bot trung tam
- thong bao CPU/RAM/disk dinh ky
- backup database
- deploy project
- hien thi nut bam inline trong Telegram
