from __future__ import annotations

import platform
import shutil
import subprocess
import time
from dataclasses import dataclass
from typing import Sequence

import psutil

from .config import Settings


MAX_OUTPUT_CHARS = 3500


@dataclass(slots=True)
class CommandResult:
    success: bool
    command: str
    output: str
    exit_code: int = 0


class SystemOperator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

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
        return CommandResult(
            success=True,
            command="uptime",
            output=f"Uptime: {self._format_duration(uptime_seconds)}",
        )

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
        return CommandResult(success=True, command="cpu", output=output)

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
        return CommandResult(success=True, command="memory", output=output)

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
        return CommandResult(success=True, command="disk", output="\n".join(partitions))

    def list_services(self) -> CommandResult:
        if not self.settings.allowed_services:
            output = "No services configured in ALLOWED_SERVICES."
        else:
            output = "\n".join(f"- {service}" for service in self.settings.allowed_services)
        return CommandResult(success=True, command="services", output=output)

    def service_action(self, action: str, service: str) -> CommandResult:
        validated = self._validate_service(service)
        if isinstance(validated, CommandResult):
            return validated

        normalized_action = action.lower()
        if normalized_action == "status":
            return self._run_command(
                self._build_systemctl(["status", validated, "--no-pager"])
            )

        if normalized_action not in {"start", "stop", "restart"}:
            return CommandResult(
                success=False,
                command="service",
                output="Action must be one of: status, start, stop, restart.",
                exit_code=2,
            )

        return self._run_command(self._build_systemctl([normalized_action, validated]))

    def service_logs(self, service: str, limit: int | None = None) -> CommandResult:
        validated = self._validate_service(service)
        if isinstance(validated, CommandResult):
            return validated

        lines = self.settings.default_log_lines if limit is None else limit
        safe_lines = min(max(lines, 1), self.settings.max_log_lines)
        command: list[str] = []
        if self.settings.use_sudo:
            command.append("sudo")
        command.extend(
            [
                "journalctl",
                "-u",
                validated,
                "-n",
                str(safe_lines),
                "--no-pager",
            ]
        )
        return self._run_command(command)

    def docker_status(self) -> CommandResult:
        if not self.settings.allow_docker_commands:
            return CommandResult(
                success=False,
                command="docker ps",
                output="Docker commands are disabled by configuration.",
                exit_code=2,
            )

        if shutil.which("docker") is None:
            return CommandResult(
                success=False,
                command="docker ps",
                output="Docker is not installed on this VPS.",
                exit_code=127,
            )

        return self._run_command(
            ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}\t{{.Image}}"]
        )

    def reboot(self) -> CommandResult:
        if not self.settings.allow_reboot:
            return CommandResult(
                success=False,
                command="reboot",
                output="Reboot command is disabled. Set ALLOW_REBOOT=true to enable it.",
                exit_code=2,
            )

        command: list[str] = []
        if self.settings.use_sudo:
            command.append("sudo")
        command.extend(["shutdown", "-r", "now"])
        return self._run_command(command)

    def _validate_service(self, service: str) -> str | CommandResult:
        cleaned = service.strip()
        if not cleaned:
            return CommandResult(
                success=False,
                command="service",
                output="Service name is required.",
                exit_code=2,
            )

        if cleaned not in self.settings.allowed_services:
            return CommandResult(
                success=False,
                command="service",
                output=f"Service '{cleaned}' is not in ALLOWED_SERVICES.",
                exit_code=2,
            )
        return cleaned

    def _build_systemctl(self, args: Sequence[str]) -> list[str]:
        command: list[str] = []
        if self.settings.use_sudo:
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
                timeout=self.settings.command_timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return CommandResult(
                success=False,
                command=command_display,
                output=(
                    "Command timed out after "
                    f"{self.settings.command_timeout_seconds} seconds."
                ),
                exit_code=124,
            )
        except FileNotFoundError as exc:
            return CommandResult(
                success=False,
                command=command_display,
                output=str(exc),
                exit_code=127,
            )

        output = (completed.stdout or completed.stderr or "").strip()
        if not output:
            output = "Command completed without output."
        output = self._truncate(output)
        return CommandResult(
            success=completed.returncode == 0,
            command=command_display,
            output=output,
            exit_code=completed.returncode,
        )

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
