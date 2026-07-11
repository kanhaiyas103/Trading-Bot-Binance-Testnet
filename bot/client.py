"""Binance Futures Testnet client wrapper."""

from __future__ import annotations

import logging
from typing import Any

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException
from requests.exceptions import RequestException

from bot.config import Settings


class BinanceFuturesClient:
    """Small wrapper around python-binance for USDT-M Futures Testnet."""

    def __init__(self, settings: Settings, logger: logging.Logger) -> None:
        """Create a configured python-binance client."""

        self._logger = logger
        try:
            self._client = Client(settings.api_key, settings.api_secret, testnet=True, ping=False)
        except TypeError:
            self._client = Client(settings.api_key, settings.api_secret, testnet=True)
        futures_url = f"{settings.base_url}/fapi"
        self._client.FUTURES_URL = futures_url
        self._client.API_URL = f"{settings.base_url}/api"

    def create_order(self, params: dict[str, Any]) -> dict[str, Any]:
        """Create a futures order and return the Binance response."""

        safe_params = {key: value for key, value in params.items() if key not in {"apiKey", "signature"}}
        self._logger.info(
            "Submitting futures order",
            extra={"event": "binance_request", "params": safe_params},
        )

        try:
            response = self._client.futures_create_order(**params)
        except BinanceAPIException as exc:
            self._logger.error(
                "Binance API rejected order",
                extra={
                    "event": "binance_api_error",
                    "status_code": exc.status_code,
                    "error_code": exc.code,
                    "error_message": exc.message,
                    "params": safe_params,
                },
            )
            raise
        except BinanceRequestException as exc:
            self._logger.error(
                "Binance request failed",
                extra={"event": "binance_request_error", "error_message": str(exc), "params": safe_params},
            )
            raise
        except RequestException as exc:
            self._logger.error(
                "Network error while contacting Binance",
                extra={"event": "network_error", "error_message": str(exc), "params": safe_params},
            )
            raise

        self._logger.info(
            "Received futures order response",
            extra={"event": "binance_response", "response": response},
        )
        return response
