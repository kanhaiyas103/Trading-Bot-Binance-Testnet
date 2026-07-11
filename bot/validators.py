"""Input validation helpers for order placement."""

from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from enum import StrEnum


SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{5,20}$")


class Side(StrEnum):
    """Supported order sides."""

    BUY = "BUY"
    SELL = "SELL"


class OrderType(StrEnum):
    """Supported Binance Futures order types."""

    MARKET = "MARKET"
    LIMIT = "LIMIT"


@dataclass(frozen=True)
class ValidatedOrderInput:
    """Validated order parameters ready for the order layer."""

    symbol: str
    side: Side
    order_type: OrderType
    quantity: Decimal
    price: Decimal | None = None


def _parse_positive_decimal(value: str, field_name: str) -> Decimal:
    """Parse a positive Decimal from a CLI string."""

    try:
        parsed = Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"{field_name} must be a valid decimal number.") from exc

    if parsed <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")

    return parsed


def validate_order_input(
    symbol: str,
    side: str,
    order_type: str,
    quantity: str,
    price: str | None = None,
) -> ValidatedOrderInput:
    """Validate raw CLI input and normalize it for Binance."""

    normalized_symbol = symbol.strip().upper()
    normalized_side = side.strip().upper()
    normalized_type = order_type.strip().upper()

    if not SYMBOL_PATTERN.fullmatch(normalized_symbol):
        raise ValueError("symbol must be 5-20 uppercase letters or numbers, for example BTCUSDT.")

    try:
        parsed_side = Side(normalized_side)
    except ValueError as exc:
        raise ValueError("side must be BUY or SELL.") from exc

    try:
        parsed_type = OrderType(normalized_type)
    except ValueError as exc:
        raise ValueError("order type must be MARKET or LIMIT.") from exc

    parsed_quantity = _parse_positive_decimal(quantity, "quantity")

    parsed_price: Decimal | None = None
    if parsed_type is OrderType.LIMIT:
        if price is None or not price.strip():
            raise ValueError("price is required for LIMIT orders.")
        parsed_price = _parse_positive_decimal(price, "price")
    elif price is not None and price.strip():
        raise ValueError("price is only accepted for LIMIT orders.")

    return ValidatedOrderInput(
        symbol=normalized_symbol,
        side=parsed_side,
        order_type=parsed_type,
        quantity=parsed_quantity,
        price=parsed_price,
    )
