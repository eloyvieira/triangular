"""Synchronize Binance Spot market metadata with the local database."""

from decimal import Decimal, InvalidOperation

import ccxt
import pymysql

from config import load_config


def decimal_places(value: str) -> int:
    """Return the number of significant decimal places in a Binance filter."""
    try:
        decimal_value = Decimal(str(value)).normalize()
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"Invalid Binance decimal value: {value}") from exc

    return max(0, -decimal_value.as_tuple().exponent)


def get_filter(market_info: dict, filter_type: str) -> dict:
    """Return one filter from the raw Binance exchangeInfo response."""
    for market_filter in market_info.get("filters", []):
        if market_filter.get("filterType") == filter_type:
            return market_filter

    raise ValueError(
        f"Filter {filter_type} not found for {market_info.get('symbol', 'unknown')}"
    )


def create_database_connection(config: dict):
    """Create a database connection using the project's existing configuration."""
    mysql_config = config["mysql"]
    password = mysql_config.get("password", mysql_config.get("passwd"))

    if password is None:
        raise ValueError("MySQL password was not found in the configuration")

    return pymysql.connect(
        host=mysql_config["host"],
        port=int(mysql_config.get("port", 3306)),
        user=mysql_config["user"],
        password=password,
        database=mysql_config.get("database", mysql_config.get("db")),
        charset="utf8mb4",
        autocommit=False,
    )


def load_active_symbols(connection) -> list[str]:
    """Load enabled WebSocket symbols from binance_market."""
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id_symbol FROM binance_market "
            "WHERE status = 1 ORDER BY id_symbol ASC"
        )
        return [str(row[0]).upper() for row in cursor.fetchall()]


def synchronize_market(connection, market: dict) -> None:
    """Insert or update the precision metadata for one Binance Spot market."""
    market_info = market["info"]
    lot_size = get_filter(market_info, "LOT_SIZE")
    price_filter = get_filter(market_info, "PRICE_FILTER")

    amount_step = str(lot_size["stepSize"])
    minimum_amount = str(lot_size["minQty"])
    price_step = str(price_filter["tickSize"])

    values = (
        str(market["id"]).upper(),
        str(market["symbol"]),
        decimal_places(amount_step),
        minimum_amount,
        decimal_places(price_step),
        price_step,
        str(market["quote"]).upper(),
        1,
    )

    sql = """
        INSERT INTO binance (
            id_symbol,
            symbol,
            min_decimal,
            min_amount,
            dec_precision,
            min_precision,
            quote,
            spread,
            spread_ask,
            up,
            down,
            status,
            date_creation
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s,
            0, 0, 0, 0, %s, NOW()
        )
        ON DUPLICATE KEY UPDATE
            symbol = VALUES(symbol),
            min_decimal = VALUES(min_decimal),
            min_amount = VALUES(min_amount),
            dec_precision = VALUES(dec_precision),
            min_precision = VALUES(min_precision),
            quote = VALUES(quote),
            status = VALUES(status),
            date_update = NOW()
    """

    with connection.cursor() as cursor:
        cursor.execute(sql, values)

    print(
        f"Synchronized {market['id']}: "
        f"amount_step={amount_step}, min_amount={minimum_amount}, "
        f"price_step={price_step}"
    )


def main() -> None:
    config = load_config()
    connection = create_database_connection(config)

    try:
        active_symbols = load_active_symbols(connection)
        if not active_symbols:
            raise RuntimeError("No active symbols found in binance_market")

        exchange = ccxt.binance({"enableRateLimit": True})
        markets = exchange.load_markets()
        spot_markets_by_id = {
            str(market["id"]).upper(): market
            for market in markets.values()
            if market.get("spot") is True
        }

        unavailable_symbols = []

        for symbol_id in active_symbols:
            market = spot_markets_by_id.get(symbol_id)

            if market is None or market.get("active") is False:
                unavailable_symbols.append(symbol_id)
                print(f"Skipped {symbol_id}: market is unavailable or inactive")
                continue

            synchronize_market(connection, market)

        connection.commit()
        print(f"Metadata synchronized for {len(active_symbols) - len(unavailable_symbols)} markets")

        if unavailable_symbols:
            raise RuntimeError(
                "Unavailable Binance Spot markets: "
                + ", ".join(unavailable_symbols)
            )
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    main()
