#!/usr/bin/python3

import logging
from datetime import datetime

import ccxt
import pymysql

try:
    from dbutils.pooled_db import PooledDB
except ImportError:
    from DBUtils.PooledDB import PooledDB

from binance_websocket import BinanceWebSocket
from config import configure_context, load_config
from mysql_functions import MysqlFunctions
from order_functions import OrderFunctions
from runtime_context import RuntimeContext
from strategy import TriangularStrategy

def main():
    config = load_config()
    logging.basicConfig(
        level=getattr(logging, str(config.get("log_level", "INFO")).upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(message)s",
    )
    logger = logging.getLogger("triangular-binance")
    ctx = RuntimeContext()
    ctx.logger = logger
    ip_address = configure_context(ctx, config)

    db = pymysql.connect(
        host=config["mysql"]["host"],
        user=config["mysql"]["user"],
        password=config["mysql"]["passwd"],
        database=config["mysql"]["db"],
    )
    cursor = db.cursor()

    try:

        # Confirm registered server information
        # Binance account API key and secret
        cursor.execute(
            "SELECT api_key, api_secret, api_uid, id FROM robot WHERE private_ip=%s AND version=%s AND exchanges=%s AND status=1 LIMIT 1", 
            (ip_address, "bot_binance_v20", "binance")
        )
        robot = cursor.fetchone()
        ctx.robot = robot
        if not robot:
            logger.error("Active robot not found for the IP %s", ip_address)
            return

        # It is also necessary to filter the query that constructs ctx.symbols.
        cursor.execute(
            "SELECT id_symbol "
            "FROM binance_market "
            "WHERE id_symbol = 'BTCUSDT' "
            "OR id_symbol LIKE '%BTC' "
            "OR id_symbol LIKE '%USDT' "
            "ORDER BY id_symbol ASC"
        )
        data = cursor.fetchall()
        if data:
            ctx.desliga = False
            ctx.symbols = sorted({str(row[0]).upper() for row in data})
            logger.info("Markets loaded for Binance WebSocket: %s", len(ctx.symbols))
        else:
            ctx.desliga = True
            logger.error("No market found in binance_market")

        # Retrieve data for each altcoin, including their specific details.
        cursor.execute(
            "SELECT id_symbol, symbol, min_decimal, min_amount, dec_precision,min_precision, quote, spread, spread_ask, up, down FROM binance ORDER BY id_symbol ASC"
        )
        for row in cursor.fetchall():
            ctx.info[row[0]] = {
                "symbol": row[1],
                "decimal": str(row[2]),
                "min_amount": str(row[3]),
                "dec_precision": str(row[4]),
                "min_precision": str(row[5]),
                "quote": row[6],
                "spread": float(row[7]),
                "spread_ask": float(row[8]),
                "up": float(row[9]),
                "down": float(row[10]),
            }

        # BTC: ETHBTC, SOLBTC, LTCBTC...
        ctx.dyn_markets["BTCUSDT"] = True
        cursor.execute(
            "SELECT id_symbol FROM binance_market WHERE id_symbol LIKE '%BTC' ORDER BY id_symbol ASC"
        )
        for row in cursor.fetchall():
            ctx.dyn_market_btc[row[0]] = True

        # USDT: ETHUSDT, SOLUSDT, LTCUSDT...
        cursor.execute(
            "SELECT id_symbol FROM binance_market WHERE (id_symbol LIKE '%USDT' AND id_symbol<>'BTCUSDT') ORDER BY id_symbol ASC"
        )
        for row in cursor.fetchall():
            ctx.dyn_market_usdt[row[0]] = True

        exchange_class = getattr(ccxt, "binance")
        ctx.exchange = exchange_class({
            "apiKey": robot[0],
            "secret": robot[1],
            "timeout": 30000,
            "enableRateLimit": True,
            "options": {"adjustForTimeDifference": True},
        })

        ctx.mySQLConnectionPool = PooledDB(
            creator=pymysql,
            host=config["mysql"]["host"],
            user=config["mysql"]["user"],
            password=config["mysql"]["passwd"],
            database=config["mysql"]["db"],
            autocommit=True,
            cursorclass=pymysql.cursors.DictCursor,
            blocking=False,
            maxconnections=20,
        )

        cursor.execute(
            "SELECT balance FROM balances_history WHERE robot=%s AND version=%s AND type=%s ORDER BY id DESC LIMIT 1",
            (robot[3], "bot_binance_v20", "USDT"),
        )
        balances_history = cursor.fetchone()

        if not balances_history:
            ctx.desliga = True
            logger.error(
                "Robot disabled: no USDT balance history found for robot ID %s",
                robot[3],
            )
        elif float(balances_history[0]) < 10:
            ctx.desliga = True
            logger.error(
                "Robot disabled: database balance is below 10 USDT: %.2f",
                float(balances_history[0]),
            )
        else:
            ctx.desliga = False
            logger.info(
                "Database balance validated: %.2f USDT",
                float(balances_history[0]),
            )

        if ctx.balance < ctx.minamount:
            logger.error(
                "Robot disabled: balance_limit_usdt %.2f is below "
                "min_amount_usdt %.2f",
                ctx.balance,
                ctx.minamount,
            )

        if ctx.balance >= ctx.minamount:
            if ctx.balance < ctx.maxamount:
                ctx.maxamount = ctx.balance
            if ctx.maxamount < ctx.minamount:
                ctx.minamount = ctx.maxamount
            ctx.balance = ctx.maxamount

            ctx.mysql = MysqlFunctions(ctx)
            ctx.orders = OrderFunctions(ctx)
            ctx.strategy = TriangularStrategy(ctx)
            ctx.websocket = BinanceWebSocket(ctx)
            ctx.websocket.run()

        try:
            dbConnection_in = ctx.mySQLConnectionPool.connection()
            sqlInsert = (
                "INSERT INTO log (robot, version, data, date_creation) "
                "VALUES (%s, %s, %s, %s)"
            )
            mySQLCursor = dbConnection_in.cursor()
            mySQLCursor.execute(
                sqlInsert,
                (1, "bot_slave15", "restart", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")),
            )
            mySQLCursor.close()
            dbConnection_in.close()
        except Exception as error:
            logger.exception("Failed to write restart log: %s", error)
    finally:
        cursor.close()
        db.close()

if __name__ == "__main__":
    main()

