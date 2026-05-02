import logging
import os
import re
from datetime import datetime, timezone

from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.errors import RPCError
from telethon.tl.types import User


load_dotenv()


logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
LOGGER = logging.getLogger("userbot")


def require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def parse_admin_ids(raw_value: str) -> set[int]:
    admin_ids: set[int] = set()
    for item in raw_value.split(","):
        candidate = item.strip()
        if not candidate:
            continue
        admin_ids.add(int(candidate))
    if not admin_ids:
        raise RuntimeError("ADMIN_IDS must contain at least one Telegram user id")
    return admin_ids


API_ID = int(require_env("API_ID"))
API_HASH = require_env("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME", "userbot")
BOT_PREFIX = os.getenv("COMMAND_PREFIX") or os.getenv("BOT_PREFIX", ".")
ADMIN_IDS = parse_admin_ids(require_env("ADMIN_IDS"))

START_TIME = datetime.now(timezone.utc)
client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
OWNER_ID: int | None = None


def format_duration(total_seconds: int) -> str:
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    parts: list[str] = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    parts.append(f"{seconds}s")
    return " ".join(parts)


async def is_authorized(event: events.NewMessage.Event) -> bool:
    sender = await event.get_sender()
    sender_id = getattr(sender, "id", None)
    if sender_id is None:
        return False
    return sender_id in ADMIN_IDS or sender_id == OWNER_ID


def command_handler(name: str):
    pattern = rf"^{re.escape(BOT_PREFIX)}{name}(?:\s+(.*))?$"

    def decorator(func):
        @client.on(events.NewMessage(outgoing=True, pattern=pattern))
        @client.on(events.NewMessage(incoming=True, pattern=pattern))
        async def wrapped(event: events.NewMessage.Event):
            if not await is_authorized(event):
                return
            try:
                await func(event)
            except RPCError as exc:
                LOGGER.exception("Telegram RPC error while handling %s", name)
                await event.reply(f"RPC error: {exc}")
            except Exception as exc:  # pragma: no cover - best effort reply
                LOGGER.exception("Unexpected error while handling %s", name)
                await event.reply(f"Error: {exc}")

        return wrapped

    return decorator


@command_handler("help")
async def help_command(event: events.NewMessage.Event) -> None:
    commands = [
        f"{BOT_PREFIX}help - hien thi danh sach lenh",
        f"{BOT_PREFIX}ping - kiem tra userbot co online hay khong",
        f"{BOT_PREFIX}id - lay ID cua nguoi/gui nhom",
        f"{BOT_PREFIX}whois [reply] - xem thong tin nguoi dung",
        f"{BOT_PREFIX}chatinfo - xem thong tin doan chat hien tai",
        f"{BOT_PREFIX}uptime - thoi gian userbot da chay",
        f"{BOT_PREFIX}echo <noi dung> - lap lai noi dung ban gui",
        f"{BOT_PREFIX}admins - xem danh sach admin ID duoc phep dung lenh",
    ]
    await event.reply("Danh sach lenh:\n" + "\n".join(commands))


@command_handler("ping")
async def ping_command(event: events.NewMessage.Event) -> None:
    start = datetime.now(timezone.utc)
    message = await event.reply("Pong...")
    latency_ms = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
    await message.edit(f"Pong! {latency_ms}ms")


@command_handler("id")
async def id_command(event: events.NewMessage.Event) -> None:
    sender = await event.get_sender()
    chat = await event.get_chat()
    lines = [
        f"Sender ID: {getattr(sender, 'id', 'unknown')}",
        f"Chat ID: {getattr(chat, 'id', 'unknown')}",
    ]
    if event.is_reply:
        replied = await event.get_reply_message()
        if replied is not None:
            lines.append(f"Reply target ID: {getattr(replied, 'sender_id', 'unknown')}")
    await event.reply("\n".join(lines))


@command_handler("whois")
async def whois_command(event: events.NewMessage.Event) -> None:
    target = await event.get_sender()
    if event.is_reply:
        replied = await event.get_reply_message()
        if replied is not None:
            target = await replied.get_sender()
    if not isinstance(target, User):
        await event.reply("Khong the lay thong tin nguoi dung tu tin nhan nay.")
        return
    name = " ".join(part for part in [target.first_name, target.last_name] if part)
    lines = [
        f"ID: {target.id}",
        f"Ten: {name or 'khong ro'}",
        f"Username: @{target.username}" if target.username else "Username: khong co",
        f"Bot: {'co' if target.bot else 'khong'}",
        f"Scam: {'co' if target.scam else 'khong'}",
        f"Verified: {'co' if target.verified else 'khong'}",
    ]
    await event.reply("\n".join(lines))


@command_handler("chatinfo")
async def chatinfo_command(event: events.NewMessage.Event) -> None:
    chat = await event.get_chat()
    lines = [
        f"Chat ID: {getattr(chat, 'id', 'unknown')}",
        f"Title: {getattr(chat, 'title', None) or getattr(chat, 'first_name', 'khong ro')}",
        f"Username: @{chat.username}" if getattr(chat, "username", None) else "Username: khong co",
    ]
    await event.reply("\n".join(lines))


@command_handler("uptime")
async def uptime_command(event: events.NewMessage.Event) -> None:
    seconds = int((datetime.now(timezone.utc) - START_TIME).total_seconds())
    await event.reply(f"Uptime: {format_duration(seconds)}")


@command_handler("echo")
async def echo_command(event: events.NewMessage.Event) -> None:
    payload = event.pattern_match.group(1)
    if not payload:
        await event.reply(f"Cach dung: {BOT_PREFIX}echo <noi dung>")
        return
    await event.reply(payload)


@command_handler("admins")
async def admins_command(event: events.NewMessage.Event) -> None:
    admin_lines = [str(admin_id) for admin_id in sorted(ADMIN_IDS)]
    if OWNER_ID is not None and OWNER_ID not in ADMIN_IDS:
        admin_lines.append(f"{OWNER_ID} (tai khoan userbot)")
    await event.reply("Admin IDs duoc phep:\n" + "\n".join(admin_lines))


async def main() -> None:
    global OWNER_ID
    me = await client.get_me()
    OWNER_ID = me.id
    LOGGER.info("Userbot started as %s (%s)", me.username or me.first_name, me.id)
    await client.run_until_disconnected()


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
