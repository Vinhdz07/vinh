import asyncio
import json
import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path

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
ALLOWED_GROUPS_FILE = Path(os.getenv("ALLOWED_GROUPS_FILE", "allowed_groups.json"))
BROADCAST_DELAY_SECONDS = max(float(os.getenv("BROADCAST_DELAY_SECONDS", "3")), 0.0)
BROADCAST_MAX_TARGETS = max(int(os.getenv("BROADCAST_MAX_TARGETS", "20")), 1)
MYGROUPS_LIMIT = max(int(os.getenv("MYGROUPS_LIMIT", "15")), 1)

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


def load_allowed_groups() -> dict[str, dict[str, str | int]]:
    if not ALLOWED_GROUPS_FILE.exists():
        return {}
    with ALLOWED_GROUPS_FILE.open("r", encoding="utf-8") as handle:
        raw_data = json.load(handle)
    if not isinstance(raw_data, dict):
        raise RuntimeError("allowed_groups.json must contain an object")
    normalized: dict[str, dict[str, str | int]] = {}
    for chat_id, metadata in raw_data.items():
        if not isinstance(metadata, dict):
            continue
        normalized[str(chat_id)] = {
            "title": str(metadata.get("title", "khong ro")),
            "username": str(metadata.get("username", "")),
            "chat_type": str(metadata.get("chat_type", "unknown")),
        }
    return normalized


def save_allowed_groups(groups: dict[str, dict[str, str | int]]) -> None:
    with ALLOWED_GROUPS_FILE.open("w", encoding="utf-8") as handle:
        json.dump(groups, handle, ensure_ascii=True, indent=2, sort_keys=True)


def get_chat_type(chat) -> str:
    if getattr(chat, "megagroup", False):
        return "supergroup"
    if getattr(chat, "broadcast", False):
        return "channel"
    if getattr(chat, "title", None):
        return "group"
    if isinstance(chat, User):
        return "user"
    return "unknown"


def is_collective_chat(chat) -> bool:
    return get_chat_type(chat) in {"group", "supergroup", "channel"}


def describe_allowed_chat(chat_id: str, metadata: dict[str, str | int]) -> str:
    title = str(metadata.get("title", "khong ro"))
    username = str(metadata.get("username", "")).strip()
    chat_type = str(metadata.get("chat_type", "unknown"))
    username_part = f" | @{username}" if username else ""
    return f"- {title} ({chat_type}) | {chat_id}{username_part}"


async def is_authorized(event: events.NewMessage.Event) -> bool:
    sender = await event.get_sender()
    sender_id = getattr(sender, "id", None)
    if sender_id is None:
        return False
    return sender_id in ADMIN_IDS or sender_id == OWNER_ID


async def get_current_collective_chat(event: events.NewMessage.Event):
    chat = await event.get_chat()
    if not is_collective_chat(chat):
        await event.reply("Lenh nay chi dung trong nhom, supergroup hoac channel.")
        return None
    return chat


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
        f"{BOT_PREFIX}allowhere - them nhom hien tai vao allowlist broadcast",
        f"{BOT_PREFIX}disallowhere - xoa nhom hien tai khoi allowlist",
        f"{BOT_PREFIX}groups - xem danh sach nhom/kenh da duoc phep broadcast",
        f"{BOT_PREFIX}mygroups [so_luong] - liet ke cac nhom/kenh dang tham gia",
        f"{BOT_PREFIX}broadcastdry <noi dung> - xem truoc noi dung se gui di dau",
        f"{BOT_PREFIX}broadcast <noi dung> - gui thong bao toi cac nhom trong allowlist",
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


@command_handler("allowhere")
async def allowhere_command(event: events.NewMessage.Event) -> None:
    chat = await get_current_collective_chat(event)
    if chat is None:
        return
    groups = load_allowed_groups()
    chat_id = str(getattr(chat, "id", ""))
    groups[chat_id] = {
        "title": getattr(chat, "title", None) or getattr(chat, "first_name", "khong ro"),
        "username": getattr(chat, "username", "") or "",
        "chat_type": get_chat_type(chat),
    }
    save_allowed_groups(groups)
    await event.reply(
        "Da them vao allowlist:\n"
        + describe_allowed_chat(chat_id, groups[chat_id])
    )


@command_handler("disallowhere")
async def disallowhere_command(event: events.NewMessage.Event) -> None:
    chat = await get_current_collective_chat(event)
    if chat is None:
        return
    groups = load_allowed_groups()
    chat_id = str(getattr(chat, "id", ""))
    removed = groups.pop(chat_id, None)
    if removed is None:
        await event.reply("Nhom/kenh hien tai chua nam trong allowlist.")
        return
    save_allowed_groups(groups)
    await event.reply("Da xoa nhom/kenh hien tai khoi allowlist.")


@command_handler("groups")
async def groups_command(event: events.NewMessage.Event) -> None:
    groups = load_allowed_groups()
    if not groups:
        await event.reply(
            "Allowlist dang trong.\n"
            f"Dung {BOT_PREFIX}allowhere trong nhom/kenh muon nhan broadcast."
        )
        return
    lines = [describe_allowed_chat(chat_id, metadata) for chat_id, metadata in groups.items()]
    await event.reply("Danh sach nhom/kenh duoc phep broadcast:\n" + "\n".join(lines))


@command_handler("mygroups")
async def mygroups_command(event: events.NewMessage.Event) -> None:
    raw_limit = event.pattern_match.group(1)
    limit = MYGROUPS_LIMIT
    if raw_limit:
        try:
            limit = max(int(raw_limit.strip()), 1)
        except ValueError:
            await event.reply(f"Cach dung: {BOT_PREFIX}mygroups [so_luong]")
            return

    lines: list[str] = []
    async for dialog in client.iter_dialogs(limit=limit * 3):
        if not (dialog.is_group or dialog.is_channel):
            continue
        entity = dialog.entity
        username = getattr(entity, "username", None)
        username_part = f" | @{username}" if username else ""
        lines.append(f"- {dialog.name} | {dialog.id}{username_part}")
        if len(lines) >= limit:
            break

    if not lines:
        await event.reply("Khong tim thay nhom/kenh nao trong tai khoan nay.")
        return
    await event.reply("Mot so nhom/kenh hien co:\n" + "\n".join(lines))


def resolve_broadcast_text(event: events.NewMessage.Event) -> str | None:
    payload = event.pattern_match.group(1)
    if not payload:
        return None
    message = payload.strip()
    return message or None


@command_handler("broadcastdry")
async def broadcastdry_command(event: events.NewMessage.Event) -> None:
    message = resolve_broadcast_text(event)
    if not message:
        await event.reply(f"Cach dung: {BOT_PREFIX}broadcastdry <noi dung>")
        return

    groups = load_allowed_groups()
    if not groups:
        await event.reply(
            "Allowlist dang trong. Hay dung "
            f"{BOT_PREFIX}allowhere o nhom/kenh ban muon gui."
        )
        return

    preview_lines = [describe_allowed_chat(chat_id, metadata) for chat_id, metadata in groups.items()]
    await event.reply(
        "Broadcast dry-run\n"
        f"- So dich: {len(groups)} / toi da {BROADCAST_MAX_TARGETS}\n"
        f"- Delay: {BROADCAST_DELAY_SECONDS}s\n"
        "- Noi dung:\n"
        f"{message}\n\n"
        "Danh sach dich:\n"
        + "\n".join(preview_lines)
    )


@command_handler("broadcast")
async def broadcast_command(event: events.NewMessage.Event) -> None:
    message = resolve_broadcast_text(event)
    if not message:
        await event.reply(f"Cach dung: {BOT_PREFIX}broadcast <noi dung>")
        return

    groups = load_allowed_groups()
    if not groups:
        await event.reply(
            "Allowlist dang trong. Hay dung "
            f"{BOT_PREFIX}allowhere o nhom/kenh ban muon gui."
        )
        return

    if len(groups) > BROADCAST_MAX_TARGETS:
        await event.reply(
            "So dich hien tai vuot gioi han an toan.\n"
            f"Hien co: {len(groups)} | toi da: {BROADCAST_MAX_TARGETS}\n"
            f"Xoa bot nhom bang {BOT_PREFIX}disallowhere hoac tang BROADCAST_MAX_TARGETS trong .env."
        )
        return

    status_message = await event.reply(
        f"Bat dau broadcast toi {len(groups)} nhom/kenh, delay {BROADCAST_DELAY_SECONDS}s..."
    )
    success_count = 0
    failures: list[str] = []

    for index, (chat_id, metadata) in enumerate(groups.items(), start=1):
        try:
            await client.send_message(int(chat_id), message)
            success_count += 1
        except RPCError as exc:
            failures.append(f"{metadata.get('title', chat_id)}: {exc}")
        except Exception as exc:  # pragma: no cover - defensive
            failures.append(f"{metadata.get('title', chat_id)}: {exc}")

        if index < len(groups) and BROADCAST_DELAY_SECONDS > 0:
            await asyncio.sleep(BROADCAST_DELAY_SECONDS)

    summary = [
        "Broadcast xong.",
        f"Thanh cong: {success_count}",
        f"That bai: {len(failures)}",
    ]
    if failures:
        summary.append("Loi:")
        summary.extend(failures[:10])
    await status_message.edit("\n".join(summary))


async def main() -> None:
    global OWNER_ID
    me = await client.get_me()
    OWNER_ID = me.id
    LOGGER.info("Userbot started as %s (%s)", me.username or me.first_name, me.id)
    await client.run_until_disconnected()


if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(main())
