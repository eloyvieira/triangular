import json
import os
import socket

CONFIG_PATH = os.getenv(
    "TRIANGULAR_CONFIG",
    "config.json",
)

def load_config():
    with open(CONFIG_PATH, encoding="utf-8") as json_data_file:
        return json.load(json_data_file)

def configure_context(ctx, config):
    ctx.config = config
    ws_config = config.get("binance_websocket", {})
    ctx.WS_URL = ws_config.get("url", "wss://stream.binance.com:9443/stream")
    ctx.WS_DEPTH = int(ws_config.get("depth", 20))
    ctx.WS_UPDATE_SPEED = str(ws_config.get("update_speed", "100ms"))
    ctx.WS_STALE_SECONDS = float(ws_config.get("stale_seconds", 3.0))
    ctx.WS_STREAMS_PER_CONNECTION = min(
        int(ws_config.get("streams_per_connection", 200)), 1024
    )

    strategy_config = config.get("triangular", {})
    ctx.EXECUTE_ORDERS = strategy_config.get("execute_orders", False) is True
    ctx.OPPORTUNITY_COOLDOWN_SECONDS = float(
        strategy_config.get("opportunity_cooldown_seconds", 2.0)
    )
    taker_fee_percent = float(strategy_config.get("taker_fee_percent", 0.1))
    ctx.FEE_FACTOR_3_LEGS = (1.0 - (taker_fee_percent / 100.0)) ** 3
    ctx.spread = int(strategy_config.get("book_level", 5))
    ctx.maxamount = float(strategy_config.get("max_amount_usdt", 150))
    ctx.minamount = float(strategy_config.get("min_amount_usdt", 100))
    ctx.min_porcentagem = float(strategy_config.get("min_profit_percent", 1.0))
    ctx.porcentagem_gain = float(
        strategy_config.get("last_order_gain_percent", 0.5)
    )
    ctx.balance = float(strategy_config.get("balance_limit_usdt", 1000))
    ctx.lastorder_limit = strategy_config.get("last_order_limit", True) is True
    ctx.ROUTE_LOG_INTERVAL_SECONDS = float(
        strategy_config.get("route_log_interval_seconds", 2.0)
    )
    if ctx.WS_DEPTH not in (5, 10, 20):
        raise ValueError("binance_websocket.depth It needs to be 5, 10, or 20.")

    hostname = socket.gethostname()
    return os.getenv(
        "ROBOT_PRIVATE_IP",
        config.get("robot_private_ip", socket.gethostbyname(hostname)),
    )

