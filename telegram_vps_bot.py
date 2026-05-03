#!/usr/bin/env python3
"""
Bot Telegram quan ly VPS trong mot file duy nhat.

Cach dung nhanh:
1. Cai thu vien:
   pip install python-telegram-bot psutil
2. Sua cac bien cau hinh o dau file nay:
   - BOT_TOKEN
   - ADMIN_IDS
   - ALLOWED_SERVICES
3. Chay:
   python3 telegram_vps_bot.py
"""

from __future__ import annotations

import html
import logging
import platform
import shutil
import subprocess
import time
from dataclasses import dataclass
from functools import wraps
from pathlib import Path
from typing import Awaitable, Callable, Iterable, Sequence

import psutil
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes


# =========================
# Cau hinh - sua tai day
# =========================
BOT_TOKEN = "PUT_YOUR_TELEGRAM_BOT_TOKEN_HERE"
ADMIN_IDS = {123456789}
ALLOWED_SERVICES = {"nginx", "ssh", "docker", "redis-server", "postgresql"}
ALLOWED_IMAGE_DIR = "/root/images"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
IMAGE_LIST_LIMIT = 50
MAX_IMAGE_SIZE_MB = 20

COMMAND_TIMEOUT_SECONDS = 20
DEFAULT_LOG_LINES = 100
MAX_LOG_LINES = 300
USE_SUDO = False
ALLOW_REBOOT = False
ALLOW_DOCKER_COMMANDS = True


LOGGER = logging.getLogger(__name__)
MAX_OUTPUT_CHARS = 3500
HandlerFn = Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[None]]


@dataclass(slots=True)
class CommandResult:
    success: bool
    command: str
    output: str
    exit_code: int = 0


class VPSBot:
    def __init__(self) -> None:
        self.bot_token = BOT_TOKEN.strip()
        self.admin_ids = {int(user_id) for user_id in ADMIN_IDS}
        self.allowed_services = {service.strip() for service in ALLOWED_SERVICES if service.strip()}
        self.allowed_image_dir = Path(ALLOWED_IMAGE_DIR).expanduser().resolve()
        self.image_extensions = {extension.lower() for extension in IMAGE_EXTENSIONS}
        self.image_list_limit = max(int(IMAGE_LIST_LIMIT), 1)
        self.max_image_size_bytes = max(int(MAX_IMAGE_SIZE_MB), 1) * 1024 * 1024
        self.command_timeout_seconds = max(int(COMMAND_TIMEOUT_SECONDS), 5)
        self.default_log_lines = max(int(DEFAULT_LOG_LINES), 1)
        self.max_log_lines = max(int(MAX_LOG_LINES), self.default_log_lines)
        self.use_sudo = bool(USE_SUDO)
        self.allow_reboot = bool(ALLOW_REBOOT)
        self.allow_docker_commands = bool(ALLOW_DOCKER_COMMANDS)

        if not self.bot_token or self.bot_token == "PUT_YOUR_TELEGRAM_BOT_TOKEN_HERE":
            raise ValueError("Ban can sua BOT_TOKEN trong file telegram_vps_bot.py")
        if not self.admin_ids:
            raise ValueError("Ban can sua ADMIN_IDS trong file telegram_vps_bot.py")

    def hostname(self) -> str:
        return platform.node()

    def overview(self) -> CommandResult:
        boot_time = psutil.boot_time()
        uptime_seconds = int(time.time() - boot_time)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        load_avg = getattr(psutil, "getloadavg", lambda: (0.0, 0.0, 0.0))()
        cpu_percent = psutil.cpu_percent(interval=1)

        lines = [
            f"Host: {platform.node()}",
            f"Platform: {platform.platform()}",
            f"CPU usage: {cpu_percent:.1f}%",
            f"Load average: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}",
            (
                "Memory: "
                f"{self._bytes_to_human(memory.used)} / "
                f"{self._bytes_to_human(memory.total)} "
                f"({memory.percent:.1f}%)"
            ),
            (
                "Disk /: "
                f"{self._bytes_to_human(disk.used)} / "
                f"{self._bytes_to_human(disk.total)} "
                f"({disk.percent:.1f}%)"
            ),
            f"Uptime: {self._format_duration(uptime_seconds)}",
        ]
        return CommandResult(success=True, command="status", output="\n".join(lines))

    def uptime(self) -> CommandResult:
        boot_time = psutil.boot_time()
        uptime_seconds = int(time.time() - boot_time)
        return CommandResult(True, "uptime", f"Uptime: {self._format_duration(uptime_seconds)}", 0)

    def cpu_usage(self) -> CommandResult:
        load_avg = getattr(psutil, "getloadavg", lambda: (0.0, 0.0, 0.0))()
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count() or 1
        output = "\n".join(
            [
                f"CPU usage: {cpu_percent:.1f}%",
                f"CPU cores: {cpu_count}",
                f"Load average: {load_avg[0]:.2f}, {load_avg[1]:.2f}, {load_avg[2]:.2f}",
            ]
        )
        return CommandResult(True, "cpu", output, 0)

    def memory_usage(self) -> CommandResult:
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        output = "\n".join(
            [
                (
                    "Memory: "
                    f"{self._bytes_to_human(memory.used)} / "
                    f"{self._bytes_to_human(memory.total)} "
                    f"({memory.percent:.1f}%)"
                ),
                (
                    "Swap: "
                    f"{self._bytes_to_human(swap.used)} / "
                    f"{self._bytes_to_human(swap.total)} "
                    f"({swap.percent:.1f}%)"
                ),
            ]
        )
        return CommandResult(True, "memory", output, 0)

    def disk_usage(self) -> CommandResult:
        partitions: list[str] = []
        for partition in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(partition.mountpoint)
            except PermissionError:
                continue

            partitions.append(
                (
                    f"{partition.mountpoint}: "
                    f"{self._bytes_to_human(usage.used)} / "
                    f"{self._bytes_to_human(usage.total)} "
                    f"({usage.percent:.1f}%)"
                )
            )

        if not partitions:
            partitions.append("No mounted partitions found.")
        return CommandResult(True, "disk", "\n".join(partitions), 0)

    def list_services(self) -> CommandResult:
        if not self.allowed_services:
            return CommandResult(True, "services", "Chua cau hinh service nao.", 0)
        output = "\n".join(f"- {service}" for service in sorted(self.allowed_services))
        return CommandResult(True, "services", output, 0)

    def list_images(self, keyword: str | None = None) -> CommandResult:
        if not self.allowed_image_dir.exists():
            return CommandResult(
                False,
                "images",
                f"Thu muc anh khong ton tai: {self.allowed_image_dir}",
                2,
            )
        if not self.allowed_image_dir.is_dir():
            return CommandResult(
                False,
                "images",
                f"ALLOWED_IMAGE_DIR khong phai thu muc: {self.allowed_image_dir}",
                2,
            )

        keyword_text = keyword.strip().lower() if keyword else ""
        matches: list[str] = []
        for path in sorted(self.allowed_image_dir.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in self.image_extensions:
                continue
            relative_path = path.relative_to(self.allowed_image_dir)
            if keyword_text and keyword_text not in str(relative_path).lower():
                continue

            size_text = self._bytes_to_human(path.stat().st_size)
            matches.append(f"- {relative_path} ({size_text})")
            if len(matches) >= self.image_list_limit:
                break

        if not matches:
            if keyword_text:
                return CommandResult(
                    True,
                    "images",
                    f"Khong tim thay anh nao trong {self.allowed_image_dir} voi tu khoa '{keyword}'.",
                    0,
                )
            return CommandResult(
                True,
                "images",
                f"Khong tim thay file anh nao trong {self.allowed_image_dir}.",
                0,
            )

        header = [
            f"Thu muc anh: {self.allowed_image_dir}",
            f"Toi da hien {self.image_list_limit} file.",
            "",
        ]
        return CommandResult(True, "images", "\n".join(header + matches), 0)

    def resolve_image(self, requested_path: str) -> Path | CommandResult:
        cleaned = requested_path.strip()
        if not cleaned:
            return CommandResult(False, "sendimage", "Thieu ten file anh.", 2)
        if not self.allowed_image_dir.exists() or not self.allowed_image_dir.is_dir():
            return CommandResult(
                False,
                "sendimage",
                f"Thu muc anh khong hop le: {self.allowed_image_dir}",
                2,
            )

        candidate = (self.allowed_image_dir / cleaned).expanduser().resolve()
        try:
            candidate.relative_to(self.allowed_image_dir)
        except ValueError:
            return CommandResult(
                False,
                "sendimage",
                "File nam ngoai thu muc duoc phep.",
                2,
            )

        if not candidate.exists() or not candidate.is_file():
            return CommandResult(
                False,
                "sendimage",
                f"Khong tim thay file: {cleaned}",
                2,
            )
        if candidate.suffix.lower() not in self.image_extensions:
            return CommandResult(
                False,
                "sendimage",
                "File nay khong phai anh duoc phep gui.",
                2,
            )
        if candidate.stat().st_size > self.max_image_size_bytes:
            return CommandResult(
                False,
                "sendimage",
                (
                    "File qua lon de gui. Gioi han hien tai la "
                    f"{MAX_IMAGE_SIZE_MB} MB."
                ),
                2,
            )
        return candidate

    def service_action(self, action: str, service: str) -> CommandResult:
        validated = self._validate_service(service)
        if isinstance(validated, CommandResult):
            return validated

        normalized_action = action.lower()
        if normalized_action == "status":
            return self._run_command(self._systemctl_command(["status", validated, "--no-pager"]))

        if normalized_action not in {"start", "stop", "restart"}:
            return CommandResult(
                False,
                "service",
                "Action phai la: status, start, stop, restart.",
                2,
            )

        return self._run_command(self._systemctl_command([normalized_action, validated]))

    def service_logs(self, service: str, limit: int | None = None) -> CommandResult:
        validated = self._validate_service(service)
        if isinstance(validated, CommandResult):
            return validated

        lines = self.default_log_lines if limit is None else limit
        safe_lines = min(max(lines, 1), self.max_log_lines)
        command: list[str] = []
        if self.use_sudo:
            command.append("sudo")
        command.extend(["journalctl", "-u", validated, "-n", str(safe_lines), "--no-pager"])
        return self._run_command(command)

    def docker_status(self) -> CommandResult:
        if not self.allow_docker_commands:
            return CommandResult(False, "docker ps", "Lenh docker dang bi tat.", 2)
        if shutil.which("docker") is None:
            return CommandResult(False, "docker ps", "Docker khong duoc cai tren VPS nay.", 127)
        return self._run_command(
            ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Image}}"]
        )

    def reboot(self) -> CommandResult:
        if not self.allow_reboot:
            return CommandResult(
                False,
                "reboot",
                "Lenh reboot dang bi tat. Hay bat ALLOW_REBOOT=True neu can.",
                2,
            )

        command: list[str] = []
        if self.use_sudo:
            command.append("sudo")
        command.extend(["shutdown", "-r", "now"])
        return self._run_command(command)

    def _validate_service(self, service: str) -> str | CommandResult:
        cleaned = service.strip()
        if not cleaned:
            return CommandResult(False, "service", "Thieu ten service.", 2)
        if cleaned not in self.allowed_services:
            return CommandResult(
                False,
                "service",
                f"Service '{cleaned}' khong nam trong ALLOWED_SERVICES.",
                2,
            )
        return cleaned

    def _systemctl_command(self, args: Sequence[str]) -> list[str]:
        command: list[str] = []
        if self.use_sudo:
            command.append("sudo")
        command.extend(["systemctl", *args])
        return command

    def _run_command(self, command: Sequence[str]) -> CommandResult:
        command_display = " ".join(command)
        try:
            completed = subprocess.run(
                list(command),
                capture_output=True,
                text=True,
                timeout=self.command_timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return CommandResult(
                False,
                command_display,
                f"Command bi timeout sau {self.command_timeout_seconds} giay.",
                124,
            )
        except FileNotFoundError as exc:
            return CommandResult(False, command_display, str(exc), 127)

        output = (completed.stdout or completed.stderr or "").strip()
        if not output:
            output = "Command chay xong nhung khong co output."
        output = self._truncate(output)
        return CommandResult(completed.returncode == 0, command_display, output, completed.returncode)

    @staticmethod
    def _bytes_to_human(value: float) -> str:
        size = float(value)
        for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
            if size < 1024 or unit == "PB":
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} PB"

    @staticmethod
    def _format_duration(seconds: int) -> str:
        days, remainder = divmod(seconds, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, secs = divmod(remainder, 60)
        parts: list[str] = []
        if days:
            parts.append(f"{days}d")
        if hours:
            parts.append(f"{hours}h")
        if minutes:
            parts.append(f"{minutes}m")
        if secs or not parts:
            parts.append(f"{secs}s")
        return " ".join(parts)

    @staticmethod
    def _truncate(value: str) -> str:
        if len(value) <= MAX_OUTPUT_CHARS:
            return value
        return value[: MAX_OUTPUT_CHARS - 18] + "\n...[truncated]"


BOT: VPSBot | None = None


def admin_only(handler: HandlerFn) -> HandlerFn:
    @wraps(handler)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if BOT is None:
            if update.effective_message:
                await update.effective_message.reply_text(
                    "Bot chua duoc cau hinh. Hay sua BOT_TOKEN va ADMIN_IDS trong file telegram_vps_bot.py"
                )
            return
        user = update.effective_user
        if user is None or user.id not in BOT.admin_ids:
            LOGGER.warning(
                "Unauthorized access attempt by user_id=%s",
                getattr(user, "id", None),
            )
            if update.effective_message:
                await update.effective_message.reply_text("Ban khong co quyen su dung bot nay.")
            return
        await handler(update, context)

    return wrapper


async def send_result(update: Update, title: str, result: CommandResult) -> None:
    if not update.effective_message:
        return
    message = (
        f"<b>{html.escape(title)}</b>\n"
        f"<pre>{html.escape(result.output)}</pre>\n"
        f"Exit code: <code>{result.exit_code}</code>"
    )
    await update.effective_message.reply_text(message, parse_mode=ParseMode.HTML)


def _parse_limit(args: Iterable[str], default: int) -> int:
    try:
        value = int(next(iter(args), str(default)))
    except ValueError as exc:
        raise ValueError("So dong log phai la so nguyen.") from exc
    if value <= 0:
        raise ValueError("So dong log phai lon hon 0.")
    return value


@admin_only
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message:
        return
    if BOT is None:
        await update.effective_message.reply_text(
            "Bot chua duoc cau hinh. Hay sua BOT_TOKEN va ADMIN_IDS trong file telegram_vps_bot.py"
        )
        return
    services = ", ".join(sorted(BOT.allowed_services)) if BOT.allowed_services else "chua khai bao"
    text = (
        "Bot quan ly VPS da san sang.\n\n"
        f"Hostname: {BOT.hostname()}\n"
        f"Allowed services: {services}\n\n"
        "Lenh co san:\n"
        "/status\n"
        "/uptime\n"
        "/cpu\n"
        "/memory\n"
        "/disk\n"
        "/services\n"
        "/service <status|restart|start|stop> <ten-service>\n"
        "/logs <ten-service> [so-dong]\n"
        "/images [tu-khoa]\n"
        "/sendimage <duong-dan-tuong-doi>\n"
        "/docker\n"
        "/reboot confirm"
    )
    await update.effective_message.reply_text(text)


@admin_only
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start(update, context)


@admin_only
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_result(update, "Tong quan VPS", BOT.overview())


@admin_only
async def uptime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_result(update, "Uptime", BOT.uptime())


@admin_only
async def cpu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_result(update, "CPU", BOT.cpu_usage())


@admin_only
async def memory(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_result(update, "Memory", BOT.memory_usage())


@admin_only
async def disk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_result(update, "Disk", BOT.disk_usage())


@admin_only
async def services(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_result(update, "Danh sach service", BOT.list_services())


@admin_only
async def images(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    keyword = " ".join(context.args).strip() if context.args else None
    await send_result(update, "Danh sach anh", BOT.list_images(keyword or None))


@admin_only
async def sendimage(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message:
        return
    if not context.args:
        await update.effective_message.reply_text(
            "Cach dung: /sendimage <duong-dan-tuong-doi-trong-thu-muc-anh>"
        )
        return

    image_path = " ".join(context.args).strip()
    resolved = BOT.resolve_image(image_path)
    if isinstance(resolved, CommandResult):
        await send_result(update, "Gui anh", resolved)
        return

    caption = f"Image: {resolved.relative_to(BOT.allowed_image_dir)}"
    with resolved.open("rb") as image_file:
        if resolved.suffix.lower() in {".jpg", ".jpeg", ".png", ".webp"}:
            await update.effective_message.reply_photo(photo=image_file, caption=caption)
        else:
            await update.effective_message.reply_document(
                document=image_file,
                caption=caption,
            )


@admin_only
async def service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message:
        return
    if len(context.args) != 2:
        await update.effective_message.reply_text(
            "Cach dung: /service <status|restart|start|stop> <ten-service>"
        )
        return

    action, service_name = context.args[0].lower(), context.args[1]
    await send_result(
        update,
        f"Service {action}: {service_name}",
        BOT.service_action(action, service_name),
    )


@admin_only
async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message:
        return
    if not context.args:
        await update.effective_message.reply_text("Cach dung: /logs <ten-service> [so-dong]")
        return

    service_name = context.args[0]
    try:
        limit = _parse_limit(context.args[1:], BOT.default_log_lines)
    except ValueError as exc:
        await update.effective_message.reply_text(str(exc))
        return

    await send_result(update, f"Logs: {service_name}", BOT.service_logs(service_name, limit))


@admin_only
async def docker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_result(update, "Docker", BOT.docker_status())


@admin_only
async def reboot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message:
        return
    if not context.args or context.args[0].lower() != "confirm":
        await update.effective_message.reply_text(
            "Lenh nay rat nhay cam. Dung /reboot confirm de xac nhan."
        )
        return
    await send_result(update, "Reboot", BOT.reboot())


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    LOGGER.exception("Unhandled exception", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text("Da xay ra loi. Kiem tra log bot de biet them chi tiet.")


def build_application() -> Application:
    if BOT is None:
        raise ValueError("Ban can sua BOT_TOKEN va ADMIN_IDS trong file telegram_vps_bot.py")
    application = Application.builder().token(BOT.bot_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("uptime", uptime))
    application.add_handler(CommandHandler("cpu", cpu))
    application.add_handler(CommandHandler("memory", memory))
    application.add_handler(CommandHandler("disk", disk))
    application.add_handler(CommandHandler("services", services))
    application.add_handler(CommandHandler("images", images))
    application.add_handler(CommandHandler("sendimage", sendimage))
    application.add_handler(CommandHandler("service", service))
    application.add_handler(CommandHandler("logs", logs))
    application.add_handler(CommandHandler("docker", docker))
    application.add_handler(CommandHandler("reboot", reboot))
    application.add_error_handler(error_handler)
    return application


def main() -> None:
    global BOT
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    BOT = VPSBot()
    application = build_application()
    application.run_polling(allowed_updates=["message"])


if __name__ == "__main__":
    main()
