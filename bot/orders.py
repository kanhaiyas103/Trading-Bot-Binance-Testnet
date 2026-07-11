"""Order placement service for Binance Futures Testnet."""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from bot.client import BinanceFuturesClient
from bot.validators import OrderType, ValidatedOrderInput


def _decimal_to_binance(value: Decimal) -> str:
    """Convert Decimal values to Binance-friendly plain strings."""

    return format(value.normalize(), "f")


def build_order_params(order: ValidatedOrderInput) -> dict[str, Any]:
    """Build python-binance futures_create_order parameters."""

    params: dict[str, Any] = {
        "symbol": order.symbol,
        "side": order.side.value,
        "type": order.order_type.value,
        "quantity": _decimal_to_binance(order.quantity),
        "newOrderRespType": "RESULT",
    }

    if order.order_type is OrderType.LIMIT:
        if order.price is None:
            raise ValueError("LIMIT orders require a price.")
        params["price"] = _decimal_to_binance(order.price)
        params["timeInForce"] = "GTC"

    return params


def average_price_from_response(response: dict[str, Any]) -> str | None:
    """Return avgPrice from Binance or compute it from cumulative quote when possible."""

    avg_price = response.get("avgPrice")
    if avg_price not in (None, "", "0", "0.0", "0.00"):
        return str(avg_price)

    executed_qty = Decimal(str(response.get("executedQty", "0") or "0"))
    cumulative_quote = Decimal(str(response.get("cumQuote", "0") or "0"))

    if executed_qty > 0 and cumulative_quote > 0:
        return format((cumulative_quote / executed_qty).normalize(), "f")

    return None


def place_order(client: BinanceFuturesClient, order: ValidatedOrderInput) -> dict[str, Any]:
    """Place a validated futures order through the client wrapper."""

    params = build_order_params(order)
    return client.create_order(params)
