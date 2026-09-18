# Triangular

A Python-based triangular arbitrage engine designed to detect and optionally execute arbitrage opportunities on Binance.

The project uses real-time WebSocket market data, modular trading logic, multithreaded processing, and MySQL persistence to monitor triangular trading paths and identify potential BBA and BAA arbitrage opportunities.

## Features

* Real-time Binance WebSocket market data
* Triangular arbitrage detection
* BBA and BAA trading flows
* Optional live order execution
* MySQL persistence
* Multithreaded order and database processing
* Centralized runtime state and configuration
* External JSON configuration with no credentials stored in the repository

## Architecture

```text
main.py
├── runtime_context.py       # Shared application state
├── config.py                # Configuration management
├── binance_websocket.py     # Binance WebSocket integration
├── strategy.py              # Arbitrage calculations and strategy logic
├── order_functions.py       # BBA / BAA execution flow
├── threads.py               # Order and database workers
├── mysql_functions.py       # MySQL persistence
└── utils.py                 # Shared utilities
```

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/triangular.git
cd triangular
```

Create and activate the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Copy the example configuration file and configure the required values:

```bash
cp config.example.json config.json
export TRIANGULAR_CONFIG=/path/to/config.json
```

Then start the engine:

```bash
python3 main.py
```

## Order Execution

Live order execution is controlled through:

```text
triangular.execute_orders
```

The default value is `false`.

With this configuration, the engine detects arbitrage opportunities without submitting real orders. Live execution must be explicitly enabled.

## Disclaimer

This project is intended for software engineering, market research, and educational purposes. Trading cryptocurrencies involves financial risk. Test thoroughly before enabling live order execution.
