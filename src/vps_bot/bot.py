"""Telegram application wiring for VPS control commands."""

from __future__ import annotations

import html
import logging
from functools import wraps
from typing import Awaitable, Callable, Iterable

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

from .config import Settings
from .system_ops import CommandResult, SystemOperator

LOGGER = logging.getLogger(__name__)
HandlerFn = Callable[[Update, ContextTypes.DEFAULT_TYPE], Awaitable[None]]


def admin_only(handler: HandlerFn) -> HandlerFn:
    @wraps(handler)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        settings: Settings = context.application.bot_data["settings"]
        user = update.effective_user

        if user is None or user.id not in settings.admin_ids:
            LOGGER.warning(
                "Unauthorized access attempt by user_id=%s",
                getattr(user, "id", None),
            )
            if update.effective_message:
                await update.effective_message.reply_text(
                    "Ban khong co quyen su dung bot nay."
                )
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

    settings: Settings = context.application.bot_data["settings"]
    operator: SystemOperator = context.application.bot_data["operator"]
    services = (
        ", ".join(settings.allowed_services)
        if settings.allowed_services
        else "chua khai bao"
    )
    text = (
        "Bot quan ly VPS da san sang.\n\n"
        f"Hostname: {operator.hostname()}\n"
        f"Allowed services: {services}\n\n"
        "Dung /help de xem danh sach lenh."
    )
    await update.effective_message.reply_text(text)


@admin_only
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message:
        return

    help_text = (
        "Lenh ho tro:\n"
        "/status - Tong quan he thong\n"
        "/uptime - Xem thoi gian uptime\n"
        "/cpu - Xem tai CPU\n"
        "/memory - Xem RAM va swap\n"
        "/disk - Xem dung luong dia\n"
        "/services - Liet ke service duoc phep quan ly\n"
        "/service <status|restart|start|stop> <ten-service>\n"
        "/logs <ten-service> [so-dong]\n"
        "/docker - Xem docker ps\n"
        "/reboot confirm - Khoi dong lai VPS neu da bat cho phep"
    )
    await update.effective_message.reply_text(help_text)


@admin_only
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    operator: SystemOperator = context.application.bot_data["operator"]
    await send_result(update, "Tong quan VPS", operator.overview())


@admin_only
async def uptime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    operator: SystemOperator = context.application.bot_data["operator"]
    await send_result(update, "Uptime", operator.uptime())


@admin_only
async def cpu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    operator: SystemOperator = context.application.bot_data["operator"]
    await send_result(update, "CPU", operator.cpu_usage())


@admin_only
async def memory(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    operator: SystemOperator = context.application.bot_data["operator"]
    await send_result(update, "Memory", operator.memory_usage())


@admin_only
async def disk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    operator: SystemOperator = context.application.bot_data["operator"]
    await send_result(update, "Disk", operator.disk_usage())


@admin_only
async def services(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    operator: SystemOperator = context.application.bot_data["operator"]
    await send_result(update, "Danh sach service", operator.list_services())


@admin_only
async def service(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message:
        return

    operator: SystemOperator = context.application.bot_data["operator"]
    args = context.args
    if len(args) != 2:
        await update.effective_message.reply_text(
            "Cach dung: /service <status|restart|start|stop> <ten-service>"
        )
        return

    action, service_name = args[0].lower(), args[1]
    await send_result(
        update,
        f"Service {action}: {service_name}",
        operator.service_action(action, service_name),
    )


@admin_only
async def logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message:
        return

    operator: SystemOperator = context.application.bot_data["operator"]
    settings: Settings = context.application.bot_data["settings"]
    args = context.args
    if not args:
        await update.effective_message.reply_text(
            "Cach dung: /logs <ten-service> [so-dong]"
        )
        return

    service_name = args[0]
    try:
        limit = _parse_limit(args[1:], default=settings.default_log_lines)
    except ValueError as exc:
        await update.effective_message.reply_text(str(exc))
        return

    await send_result(
        update,
        f"Logs: {service_name}",
        operator.service_logs(service_name, limit=limit),
    )


@admin_only
async def docker(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    operator: SystemOperator = context.application.bot_data["operator"]
    await send_result(update, "Docker", operator.docker_status())


@admin_only
async def reboot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message:
        return

    operator: SystemOperator = context.application.bot_data["operator"]
    args = context.args
    if not args or args[0].lower() != "confirm":
        await update.effective_message.reply_text(
            "Lenh nay rat nhay cam. Dung /reboot confirm de xac nhan."
        )
        return

    await send_result(update, "Reboot", operator.reboot())


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    LOGGER.exception("Unhandled exception", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "Da xay ra loi khong mong muon. Kiem tra log cua bot de biet them chi tiet."
        )


def build_application(settings: Settings) -> Application:
    application = Application.builder().token(settings.telegram_bot_token).build()
    operator = SystemOperator(settings)

    application.bot_data["settings"] = settings
    application.bot_data["operator"] = operator

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("uptime", uptime))
    application.add_handler(CommandHandler("cpu", cpu))
    application.add_handler(CommandHandler("memory", memory))
    application.add_handler(CommandHandler("disk", disk))
    application.add_handler(CommandHandler("services", services))
    application.add_handler(CommandHandler("service", service))
    application.add_handler(CommandHandler("logs", logs))
    application.add_handler(CommandHandler("docker", docker))
    application.add_handler(CommandHandler("reboot", reboot))
    application.add_error_handler(error_handler)
    return application
