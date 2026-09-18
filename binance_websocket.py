import asyncio
import json
import logging
import random
import time
from decimal import Decimal

import websockets

logger = logging.getLogger("triangular-binance")

class BinanceWebSocket:
    def __init__(self, ctx):
        self.ctx = ctx

    def books_are_fresh(self, base):
        now = time.monotonic()
        required = ("BTCUSDT", base + "BTC", base + "USDT")
        return all(
            symbol in self.ctx.market_updated_at
            and (now - self.ctx.market_updated_at[symbol]) <= self.ctx.WS_STALE_SECONDS
            for symbol in required
        )

    def handle_binance_partial_depth(self, stream_name, payload):
        if self.ctx.desliga or self.ctx.waiting:
            return
        symbol = stream_name.split("@", 1)[0].upper()
        update_id = int(payload.get("lastUpdateId", 0))
        if update_id and update_id <= self.ctx.market_update_id.get(symbol, -1):
            return
        bids = payload.get("bids", payload.get("b", []))
        asks = payload.get("asks", payload.get("a", []))
        if not bids or not asks:
            return

        book = {}
        for price, amount in bids:
            if Decimal(str(amount)) > 0:
                book["bids", str(price)] = str(amount)
        for price, amount in asks:
            if Decimal(str(amount)) > 0:
                book["asks", str(price)] = str(amount)

        if symbol in self.ctx.dyn_markets:
            # BTCUSDT
            self.ctx.markets[symbol] = book

        elif symbol in self.ctx.dyn_market_btc:
            # ETHBTC, SOLBTC, LTCBTC...
            self.ctx.markets_btc[symbol] = book

        elif symbol in self.ctx.dyn_market_usdt:
            # ETHUSDT, SOLUSDT, LTCUSDT...
            self.ctx.markets_usdt[symbol] = book

        else:
            return

        self.ctx.market_update_id[symbol] = update_id
        self.ctx.market_updated_at[symbol] = time.monotonic()
        if symbol.endswith("USDT") and symbol != "BTCUSDT":
            base = symbol[:-4]
            if self.books_are_fresh(base):
                self.ctx.strategy.func_btc(base)

    async def stream_binance_group(self, stream_symbols, connection_number):
        streams = [
            symbol.lower() + "@depth" + str(self.ctx.WS_DEPTH) + "@" + self.ctx.WS_UPDATE_SPEED
            for symbol in stream_symbols
        ]
        backoff = 1.0
        while not self.ctx.desliga:
            try:
                async with websockets.connect(
                    self.ctx.WS_URL,
                    ping_interval=20,
                    ping_timeout=60,
                    close_timeout=10,
                    max_queue=4096,
                ) as websocket:
                    await websocket.send(json.dumps({
                        "method": "SET_PROPERTY",
                        "params": ["combined", True],
                        "id": "combined-" + str(connection_number),
                    }))
                    await websocket.send(json.dumps({
                        "method": "SUBSCRIBE",
                        "params": streams,
                        "id": connection_number,
                    }))
                    logger.info("Binance WebSocket #%s connected with %s streams", connection_number, len(streams))
                    backoff = 1.0
                    async for raw_message in websocket:
                        message = json.loads(raw_message)
                        if "result" in message:
                            continue
                        payload = message.get("data", message)
                        stream_name = message.get("stream")
                        if stream_name is None:
                            continue
                        self.handle_binance_partial_depth(stream_name, payload)
            except asyncio.CancelledError:
                raise
            except Exception as error:
                logger.exception(
                    "Binance WebSocket #%s disconnected; reconnecting in %.1fs: %s",
                    connection_number,
                    backoff,
                    error,
                )
                await asyncio.sleep(backoff + random.uniform(0, backoff * 0.2))
                backoff = min(backoff * 2, 30.0)

    async def stream_binance_orderbooks(self):
        groups = [
            self.ctx.symbols[index:index + self.ctx.WS_STREAMS_PER_CONNECTION]
            for index in range(0, len(self.ctx.symbols), self.ctx.WS_STREAMS_PER_CONNECTION)
        ]
        await asyncio.gather(*(
            self.stream_binance_group(group, index + 1)
            for index, group in enumerate(groups)
        ))

    def run(self):
        if self.ctx.desliga is False:
            asyncio.run(self.stream_binance_orderbooks())

