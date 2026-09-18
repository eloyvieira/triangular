import logging
import time

from threads import myThread
from utils import numberFormatPrecision, sorted_orderbook

logger = logging.getLogger("triangular-binance")

ROUTE_LOG_INTERVAL_SECONDS = 10.0
COLOR_GREEN = "\033[92m"
COLOR_RED = "\033[91m"
COLOR_RESET = "\033[0m"

class TriangularStrategy:
    """Analyzes and executes the BBA and BAA triangular arbitrage routes."""

    def __init__(self, ctx):
        self.ctx = ctx
        self._last_route_log_at = {}

    def _log_route_forecast(
            self,
            route,
            base,
            initial_value,
            final_value,
            profit_percentage,
    ):
        route_key = f"{route}:{base}"
        now = time.monotonic()

        last_log_at = self._last_route_log_at.get(route_key, 0.0)

        if now - last_log_at < ROUTE_LOG_INTERVAL_SECONDS:
            return

        self._last_route_log_at[route_key] = now

        is_profitable = (
                profit_percentage >= self.ctx.min_porcentagem
                and not self.ctx.desliga
        )

        color = COLOR_GREEN if is_profitable else COLOR_RED
        status = "PROFITABLE" if is_profitable else "BELOW TARGET"

        logger.info(
            "%s%s %s | initial=%.2f USDT | final=%.2f USDT | "
            "result=%+.4f%% | target=%.4f%% | %s%s",
            color,
            route,
            base,
            initial_value,
            final_value,
            profit_percentage,
            self.ctx.min_porcentagem,
            status,
            COLOR_RESET,
        )

    def can_emit_opportunity(self, route_key):
        now = time.monotonic()
        last_seen = self.ctx.last_opportunity_at.get(route_key, 0.0)

        if now - last_seen < self.ctx.OPPORTUNITY_COOLDOWN_SECONDS:
            return False

        self.ctx.last_opportunity_at[route_key] = now
        return True

    def _get_market_snapshot(self, market_book, validate_depth=False):
        """Returns prices and liquidity at the configured order-book level."""

        ordered_book = list(sorted_orderbook(market_book))
        book_length = len(ordered_book)

        if validate_depth and book_length < self.ctx.spread * 2:
            return None, ordered_book

        ask_price = ordered_book[self.ctx.spread - 1][1]
        ask_amount = market_book["asks", ask_price]
        ask_total = round(float(ask_price) * float(ask_amount), 8)

        bid_price = ordered_book[book_length - self.ctx.spread][1]
        bid_amount = market_book["bids", bid_price]
        bid_total = round(float(bid_price) * float(bid_amount), 8)

        snapshot = {
            "price": str(ask_price),
            "total": str(ask_total),
            "priceb": str(bid_price),
            "totalb": str(bid_total),
        }
        return snapshot, ordered_book

    def _get_execution_spread(self, market, side, expanded_fallback=False):
        spread_field = "spread_ask" if side == "buy" else "spread"
        configured_spread = self.ctx.info[market][spread_field]
        fallback_spread = (
            self.ctx.spread * 10 if expanded_fallback else self.ctx.spread
        )

        if configured_spread > 0:
            execution_spread = configured_spread
            if execution_spread < self.ctx.spread:
                execution_spread = fallback_spread
        else:
            execution_spread = fallback_spread

        return execution_spread

    def _get_execution_price(
        self,
        market,
        book_price,
        side,
        expanded_fallback=False,
    ):
        market_info = self.ctx.info[market]
        price = numberFormatPrecision(
            book_price,
            market_info["dec_precision"],
        )
        execution_spread = self._get_execution_spread(
            market,
            side,
            expanded_fallback,
        )

        side_label = "B" if side == "buy" else "A"
        orderbook_log = (
            f" {side_label}=> price: {price}"
            f" spread: {market_info['min_precision']} {execution_spread}"
        )

        price_change = float(market_info["min_precision"]) * execution_spread
        if side == "buy":
            price = float(price) + price_change
        else:
            price = float(price) - price_change

        price = numberFormatPrecision(price, market_info["dec_precision"])
        return price, orderbook_log

    def _get_trade_value(self, *liquidity_values):
        trade_value = min(float(value) for value in liquidity_values)

        if trade_value > self.ctx.balance:
            trade_value = self.ctx.balance

        return float(numberFormatPrecision(trade_value, 2))

    def _calculate_profit_percentage(self, initial_value, final_value):
        profit_percentage = (float(final_value) * 100 / float(initial_value)) - 100
        return float(numberFormatPrecision(profit_percentage, 2))

    def _start_order_thread(
        self,
        operation,
        orderbook_log,
        amount,
        market1,
        leg1,
        market2,
        leg2,
        market3,
        leg3,
    ):
        self.ctx.waiting = True
        order_thread = myThread(
            self.ctx,
            operation,
            "ORDER" + orderbook_log,
            amount,
            market1,
            leg1,
            market2,
            leg2,
            market3,
            leg3,
        )
        order_thread.start()

    def _analyze_bba(self, base):
        market1 = "BTCUSDT"
        market2 = base + "BTC"
        market3 = base + "USDT"

        if market1 not in self.ctx.markets:
            return False
        if market2 not in self.ctx.markets_btc:
            return False
        if market3 not in self.ctx.markets_usdt:
            return False
        if float(self.ctx.info[market2]["decimal"]) < 0:
            return False

        try:
            leg1, _leg1_orderbook = self._get_market_snapshot(
                self.ctx.markets[market1],
                validate_depth=True,
            )
            if leg1 is None:
                return False
            leg2, _leg2_orderbook = self._get_market_snapshot(
                self.ctx.markets_btc[market2]
            )
            leg3, leg3_orderbook = self._get_market_snapshot(
                self.ctx.markets_usdt[market3]
            )

            liquidity1 = float(leg1["total"])
            liquidity2 = float(leg2["total"]) * float(leg1["price"])
            liquidity3 = float(leg3["totalb"])
            trade_value = self._get_trade_value(
                liquidity1,
                liquidity2,
                liquidity3,
            )

            if trade_value < self.ctx.minamount:
                return False

            orderbook_log = ""

            price1, price_log = self._get_execution_price(
                market1,
                leg1["price"],
                "buy",
                expanded_fallback=True,
            )
            orderbook_log += price_log
            value1 = trade_value / float(price1)
            value1 = numberFormatPrecision(
                value1,
                self.ctx.info[market1]["decimal"],
            )

            price2, price_log = self._get_execution_price(
                market2,
                leg2["price"],
                "buy",
            )
            orderbook_log += price_log
            value2 = float(value1) / float(price2)
            value2 = numberFormatPrecision(
                value2,
                self.ctx.info[market2]["decimal"],
            )

            price3, price_log = self._get_execution_price(
                market3,
                leg3["priceb"],
                "sell",
            )
            orderbook_log += price_log
            final_value = float(value2) * float(price3)
            final_value *= self.ctx.FEE_FACTOR_3_LEGS

            profit_percentage = self._calculate_profit_percentage(
                trade_value,
                final_value,
            )
            self._log_route_forecast(
                route="BBA",
                base=base,
                initial_value=trade_value,
                final_value=final_value,
                profit_percentage=profit_percentage,
            )

            if (
                profit_percentage < self.ctx.min_porcentagem
                or self.ctx.desliga
            ):
                return False

            self.ctx._tempmarket = leg3_orderbook

            if self.can_emit_opportunity("BBA:" + base):
                logger.info(
                    "BBA Opportunity %s: entry=%.2f USDT"
                    "exit=%.2f USDT profit=%.2f%%",
                    base,
                    trade_value,
                    final_value,
                    profit_percentage,
                )

            if self.ctx.EXECUTE_ORDERS:
                self._start_order_thread(
                    "exec_order_BBA",
                    orderbook_log,
                    trade_value,
                    market1,
                    leg1,
                    market2,
                    leg2,
                    market3,
                    leg3,
                )

            return True
        except Exception as error:
            logger.exception(
                "Error parsing BBA route %s: %s",
                market1,
                error,
            )
            return False

    def _analyze_baa(self, base):
        market1 = base + "USDT"
        market2 = base + "BTC"
        market3 = "BTCUSDT"

        if market1 not in self.ctx.markets_usdt:
            return
        if market2 not in self.ctx.markets_btc:
            return
        if market3 not in self.ctx.markets:
            return
        if float(self.ctx.info[market2]["decimal"]) < 0:
            return

        try:
            leg1, _leg1_orderbook = self._get_market_snapshot(
                self.ctx.markets_usdt[market1],
                validate_depth=True,
            )
            if leg1 is None:
                return
            leg2, _leg2_orderbook = self._get_market_snapshot(
                self.ctx.markets_btc[market2]
            )
            leg3, _leg3_orderbook = self._get_market_snapshot(
                self.ctx.markets[market3]
            )

            liquidity1 = float(leg1["total"])
            liquidity2 = float(leg2["totalb"]) * float(leg3["priceb"])
            liquidity3 = float(leg3["totalb"])
            trade_value = self._get_trade_value(
                liquidity1,
                liquidity2,
                liquidity3,
            )

            if trade_value < self.ctx.minamount:
                return

            orderbook_log = ""

            price1, price_log = self._get_execution_price(
                market1,
                leg1["price"],
                "buy",
            )
            orderbook_log += price_log
            value1 = trade_value / float(price1)
            value1 = numberFormatPrecision(
                value1,
                self.ctx.info[market1]["decimal"],
            )

            price2, price_log = self._get_execution_price(
                market2,
                leg2["priceb"],
                "sell",
            )
            orderbook_log += price_log
            value1 = numberFormatPrecision(
                value1,
                self.ctx.info[market2]["decimal"],
            )
            value2 = float(value1) * float(price2)
            value2 = numberFormatPrecision(
                value2,
                self.ctx.info[market3]["decimal"],
            )

            price3, price_log = self._get_execution_price(
                market3,
                leg3["priceb"],
                "sell",
            )
            orderbook_log += price_log
            final_value = float(value2) * float(price3)
            final_value *= self.ctx.FEE_FACTOR_3_LEGS
            final_value = float(numberFormatPrecision(final_value, 2))

            profit_percentage = self._calculate_profit_percentage(
                trade_value,
                final_value,
            )

            self._log_route_forecast(
                route="BAA",
                base=base,
                initial_value=trade_value,
                final_value=final_value,
                profit_percentage=profit_percentage,
            )

            if (
                profit_percentage < self.ctx.min_porcentagem
                or self.ctx.desliga
            ):
                return

            if self.can_emit_opportunity("BAA:" + base):
                logger.info(
                    "BAA Opportunity %s: entry=%.2f USDT "
                    "exit=%.2f USDT profit=%.2f%%",
                    base,
                    trade_value,
                    final_value,
                    profit_percentage,
                )

            if self.ctx.EXECUTE_ORDERS:
                self._start_order_thread(
                    "exec_order_BAA",
                    orderbook_log,
                    trade_value,
                    market1,
                    leg1,
                    market2,
                    leg2,
                    market3,
                    leg3,
                )
        except Exception as error:
            logger.exception(
                "Error parsing BAA route %s: %s",
                market1,
                error,
            )

    def func_btc(self, base):
        if self.ctx.desliga:
            return

        bba_opportunity_found = self._analyze_bba(base)
        if not bba_opportunity_found:
            self._analyze_baa(base)
