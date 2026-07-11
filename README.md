# Binance Futures Testnet Trading Bot

A production-ready Python 3.11 CLI application for placing simple `MARKET` and `LIMIT` orders on the Binance USDT-M Futures Testnet using `python-binance`.

## Features

- Places `MARKET` and `LIMIT` futures orders
- Supports `BUY` and `SELL`
- Validates symbol, side, order type, quantity, and limit price before calling Binance
- Loads secrets from `.env` with `python-dotenv`
- Logs structured JSON request, response, and error events to `logs/trading_bot.log`
- Handles validation errors, Binance API errors, request errors, and network failures gracefully

## Project Structure

```text
bot/
  __init__.py
  client.py
  orders.py
  validators.py
  logging_config.py
  config.py
cli.py
README.md
requirements.txt
.gitignore
.env.example
logs/
```

## Prerequisites

- Python 3.11
- Binance Futures Testnet account
- Binance Futures Testnet API key and secret

Create testnet credentials at [Binance Futures Testnet](https://testnet.binancefuture.com).

## Setup

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Create your local environment file:

```powershell
Copy-Item .env.example .env
```

4. Edit `.env` and add your credentials:

```env
BINANCE_API_KEY=your_testnet_api_key
BINANCE_API_SECRET=your_testnet_api_secret
BINANCE_FUTURES_TESTNET_BASE_URL=https://testnet.binancefuture.com
TRADING_BOT_LOG_FILE=logs/trading_bot.log
```

Never commit `.env` or real API credentials.

## Usage

Run commands from the project root.

### Market Order

```powershell
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### Limit Order

```powershell
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 70000
```

The CLI prints:

- Order request summary
- `orderId`
- `status`
- `executedQty`
- Average price when Binance provides it or when it can be calculated
- Success or failure message

## Logging

Application logs are written as JSON lines to:

```text
logs/trading_bot.log
```

The log includes:

- Order request parameters
- Binance order responses
- Binance API errors
- Binance request errors
- Network errors

For the assignment deliverable, run at least one `MARKET` order and one `LIMIT` order so `logs/trading_bot.log` contains real testnet examples.

## Assumptions

- This bot is intentionally scoped to Binance USDT-M Futures Testnet.
- Only `MARKET` and `LIMIT` orders are implemented because they are the required order types.
- `LIMIT` orders use `GTC` time-in-force.
- The application does not include Docker, FastAPI, GUI, or unrelated trading features.

## Troubleshooting

- `Missing required environment variable`: confirm `.env` exists and contains `BINANCE_API_KEY` and `BINANCE_API_SECRET`.
- `price is required for LIMIT orders`: add `--price`.
- Binance precision or minimum notional errors: adjust quantity and price for the selected symbol's testnet rules.
- Authentication errors: regenerate Binance Futures Testnet credentials and update `.env`.
