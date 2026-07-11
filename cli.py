"""Command-line interface for the Binance Futures Testnet trading bot."""

from __future__ import annotations

import argparse
import sys

from binance.exceptions import BinanceAPIException, BinanceRequestException
from requests.exceptions import RequestException

from bot.client import BinanceFuturesClient
from bot.config import ConfigurationError, load_settings
from bot.logging_config import configure_logging
from bot.orders import average_price_from_response, place_order
from bot.validators import OrderType, ValidatedOrderInput, validate_order_input


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""

    parser = argparse.ArgumentParser(
        description="Place MARKET and LIMIT orders on Binance USDT-M Futures Testnet.",
    )
    parser.add_argument("--symbol", required=True, help="Trading pair symbol, for example BTCUSDT.")
    parser.add_argument("--side", required=True, choices=["BUY", "SELL", "buy", "sell"], help="Order side.")
    parser.add_argument(
        "--type",
        required=True,
        choices=["MARKET", "LIMIT", "market", "limit"],
        dest="order_type",
        help="Order type.",
    )
    parser.add_argument("--quantity", required=True, help="Order quantity, for example 0.001.")
    parser.add_argument("--price", help="Limit price. Required for LIMIT orders and rejected for MARKET orders.")
    return parser


def print_request_summary(order: ValidatedOrderInput) -> None:
    """Print a readable order summary before submission."""

    print("Order request summary")
    print(f"  Symbol:   {order.symbol}")
    print(f"  Side:     {order.side.value}")
    print(f"  Type:     {order.order_type.value}")
    print(f"  Quantity: {order.quantity}")
    if order.order_type is OrderType.LIMIT:
        print(f"  Price:    {order.price}")
    print()


def print_order_response(response: dict[str, object]) -> None:
    """Print important fields from the Binance order response."""

    print("Order response")
    print(f"  orderId:      {response.get('orderId', 'N/A')}")
    print(f"  status:       {response.get('status', 'N/A')}")
    print(f"  executedQty:  {response.get('executedQty', 'N/A')}")
    print(f"  averagePrice: {average_price_from_response(response) or 'N/A'}")
    print()
    print("Success: order submitted to Binance Futures Testnet.")


def main(argv: list[str] | None = None) -> int:
    """Run the CLI application."""

    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        order = validate_order_input(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )
        settings = load_settings()
        logger = configure_logging(settings.log_file)
        print_request_summary(order)

        client = BinanceFuturesClient(settings=settings, logger=logger)
        response = place_order(client, order)
        print_order_response(response)
        return 0
    except ConfigurationError as exc:
        print(f"Failure: configuration error - {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"Failure: invalid input - {exc}", file=sys.stderr)
        return 2
    except BinanceAPIException as exc:
        print(f"Failure: Binance API error ({exc.code}) - {exc.message}", file=sys.stderr)
        return 1
    except BinanceRequestException as exc:
        print(f"Failure: Binance request error - {exc}", file=sys.stderr)
        return 1
    except RequestException as exc:
        print(f"Failure: network error - {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"Failure: unexpected error - {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
