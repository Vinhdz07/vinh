# Telegram VPS Bot - 1 file Python

Project nay da duoc rut gon thanh **1 file duy nhat**:

- `telegram_vps_bot.py`

## Cach dung

### 1. Cai thu vien

```bash
pip install python-telegram-bot psutil
```

### 2. Sua cau hinh trong file

Mo file `telegram_vps_bot.py` va sua:

- `BOT_TOKEN`
- `ADMIN_IDS`
- `ALLOWED_SERVICES`

Vi du:

```python
BOT_TOKEN = "123456:ABCDEF"
ADMIN_IDS = {123456789}
ALLOWED_SERVICES = {"nginx", "ssh", "redis-server"}
```

Neu can:

```python
USE_SUDO = True
ALLOW_REBOOT = False
ALLOW_DOCKER_COMMANDS = True
```

### 3. Chay bot

```bash
python3 telegram_vps_bot.py
```

## Lenh Telegram

- `/start`
- `/help`
- `/status`
- `/uptime`
- `/cpu`
- `/memory`
- `/disk`
- `/services`
- `/service status nginx`
- `/service restart nginx`
- `/logs nginx 50`
- `/docker`
- `/reboot confirm`

## Luu y

- Bot khong cho chay shell tuy y
- Chi admin trong `ADMIN_IDS` moi duoc dung
- Chi service trong `ALLOWED_SERVICES` moi duoc phep thao tac
