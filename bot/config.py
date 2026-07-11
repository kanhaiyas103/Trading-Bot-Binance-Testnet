"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"
DEFAULT_LOG_FILE = PROJECT_ROOT / "logs" / "trading_bot.log"
BINANCE_FUTURES_TESTNET_BASE_URL = "https://testnet.binancefuture.com"


@dataclass(frozen=True)
class Settings:
    """Runtime settings required to connect to Binance Futures Testnet."""

    api_key: str
    api_secret: str
    base_url: str = BINANCE_FUTURES_TESTNET_BASE_URL
    log_file: Path = DEFAULT_LOG_FILE


class ConfigurationError(ValueError):
    """Raised when required configuration is missing or invalid."""


def load_settings() -> Settings:
    """Load settings from `.env` and validate required values."""

    load_dotenv(ENV_FILE)

    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()
    base_url = os.getenv("BINANCE_FUTURES_TESTNET_BASE_URL", BINANCE_FUTURES_TESTNET_BASE_URL).strip()
    log_file = Path(os.getenv("TRADING_BOT_LOG_FILE", str(DEFAULT_LOG_FILE))).expanduser()

    missing = []
    if not api_key:
        missing.append("BINANCE_API_KEY")
    if not api_secret:
        missing.append("BINANCE_API_SECRET")

    if missing:
        joined = ", ".join(missing)
        raise ConfigurationError(f"Missing required environment variable(s): {joined}")

    if base_url.rstrip("/") != BINANCE_FUTURES_TESTNET_BASE_URL:
        raise ConfigurationError(
            "BINANCE_FUTURES_TESTNET_BASE_URL must be "
            f"{BINANCE_FUTURES_TESTNET_BASE_URL!r} for this testnet bot."
        )

    return Settings(
        api_key=api_key,
        api_secret=api_secret,
        base_url=base_url.rstrip("/"),
        log_file=log_file,
    )
