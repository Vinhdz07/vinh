from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


def _parse_csv(value: str | None) -> tuple[str, ...]:
    if not value:
        return ()
    return tuple(item.strip() for item in value.split(",") if item.strip())


def _parse_admin_ids(value: str | None) -> tuple[int, ...]:
    raw_values = _parse_csv(value)
    if not raw_values:
        raise ValueError("Missing TELEGRAM_ADMIN_IDS in environment.")

    try:
        return tuple(sorted({int(item) for item in raw_values}))
    except ValueError as exc:
        raise ValueError("TELEGRAM_ADMIN_IDS must contain only integers.") from exc


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True, slots=True)
class Settings:
    telegram_bot_token: str
    telegram_admin_ids: tuple[int, ...]
    allowed_services: tuple[str, ...]
    command_timeout_seconds: int
    default_log_lines: int
    max_log_lines: int
    use_sudo: bool
    allow_reboot: bool
    allow_docker_commands: bool

    @property
    def admin_ids(self) -> set[int]:
        return set(self.telegram_admin_ids)


def load_settings() -> Settings:
    load_dotenv()

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise ValueError("Missing TELEGRAM_BOT_TOKEN in environment.")

    command_timeout_seconds = int(os.getenv("COMMAND_TIMEOUT_SECONDS", "20"))
    default_log_lines = int(os.getenv("DEFAULT_LOG_LINES", "100"))
    max_log_lines = int(os.getenv("MAX_LOG_LINES", "300"))

    if command_timeout_seconds < 5:
        raise ValueError("COMMAND_TIMEOUT_SECONDS must be at least 5.")
    if default_log_lines < 1:
        raise ValueError("DEFAULT_LOG_LINES must be greater than 0.")
    if max_log_lines < default_log_lines:
        raise ValueError("MAX_LOG_LINES must be >= DEFAULT_LOG_LINES.")

    return Settings(
        telegram_bot_token=token,
        telegram_admin_ids=_parse_admin_ids(os.getenv("TELEGRAM_ADMIN_IDS")),
        allowed_services=_parse_csv(os.getenv("ALLOWED_SERVICES")),
        command_timeout_seconds=command_timeout_seconds,
        default_log_lines=default_log_lines,
        max_log_lines=max_log_lines,
        use_sudo=_get_bool("USE_SUDO", default=False),
        allow_reboot=_get_bool("ALLOW_REBOOT", default=False),
        allow_docker_commands=_get_bool("ALLOW_DOCKER_COMMANDS", default=True),
    )
