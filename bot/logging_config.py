"""Structured logging configuration for the trading bot."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class JsonFormatter(logging.Formatter):
    """Format log records as single-line JSON objects."""

    RESERVED = {
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "message",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
    }

    def format(self, record: logging.LogRecord) -> str:
        """Return a JSON representation of a log record."""

        payload: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key, value in record.__dict__.items():
            if key not in self.RESERVED and not key.startswith("_"):
                payload[key] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str, ensure_ascii=True)


def configure_logging(log_file: Path) -> logging.Logger:
    """Configure file logging and return the application logger."""

    log_file.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    return logger
