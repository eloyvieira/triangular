import json
import time
from datetime import datetime

import ccxt

from threads import mysqlThread, orderThread
from utils import numberFormatPrecision, sorted_orderbook

MAX_ORDER_ATTEMPTS = 9
ORDER_RETRY_DELAY_SECONDS = 0.5
RETRYABLE_EXCHANGE_ERRORS = (
    ccxt.ExchangeError,
    ccxt.AuthenticationError,
    ccxt.ExchangeNotAvailable,
)

class OrderFunctions:
    """Executes the three legs of the BBA and BAA triangular arbitrage routes."""

    def __init__(self, ctx):
        self.ctx = ctx

    @staticmethod
    def _utc_now():
        return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    def _start_mysql_thread(self, operation, data):
        connection = self.ctx.mySQLConnectionPool.connection()
        log_thread = mysqlThread(
            self.ctx,
            operation,
            connection,
            data,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            None,
            self._utc_now(),
        )
        log_thread.start()

    def _create_order_with_retry(
        self,
        market,
        side,
        amount,
        order_type="market",
        price=None,
    ):
        """Creates an order while preserving the original nine-attempt retry logic."""
        symbol = self.ctx.info[market]["symbol"]
        error_message = ""

        for _attempt in range(MAX_ORDER_ATTEMPTS):
            try:
                if price is None:
                    order = self.ctx.exchange.create_order(
                        symbol,
                        order_type,
                        side,
                        amount,
                    )
                else:
                    order = self.ctx.exchange.create_order(
                        symbol,
                        order_type,
                        side,
                        amount,
                        price,
                    )
                return order, error_message
            except RETRYABLE_EXCHANGE_ERRORS as error:
                error_message = str(error)
                time.sleep(ORDER_RETRY_DELAY_SECONDS)

        return None, error_message

    def _best_ask_price(self, market):
        orderbook = sorted_orderbook(self.ctx.markets_usdt[market])
        return orderbook, list(orderbook)[0][1]

    def _calculate_final_sell_price(
        self,
        market1,
        amount1,
        market3,
        amount3,
        executed_value1,
    ):
        target_value = float(executed_value1) * (
            1 + (self.ctx.porcentagem_gain / 100)
        )

        try:
            orderbook, sell_price = self._best_ask_price(market3)
            current_value = float(sell_price) * float(amount3)
            change_sell_price = float(executed_value1) > current_value

            if change_sell_price:
                sell_price = target_value / float(amount3)
        except Exception:
            orderbook = []
            change_sell_price = True
            sell_price = target_value / float(amount3)

        if self.ctx.lastorder_limit and not change_sell_price:
            sell_price = self.ctx.lastorder[market1 + str(amount1)]

        return orderbook, sell_price

    def _create_final_sell_order(self, market, amount, sell_price):
        if self.ctx.lastorder_limit:
            return self._create_order_with_retry(
                market,
                "sell",
                amount,
                order_type="limit",
                price=sell_price,
            )

        return self._create_order_with_retry(market, "sell", amount)

    def exec_order_BBA(
        self,
        thread_name,
        minimum_value,
        market1,
        buy1,
        market2,
        buy2,
        market3,
        sell3,
    ):
        buy1_amount = float(minimum_value) / float(buy1["price"])
        buy1_amount = numberFormatPrecision(
            buy1_amount,
            self.ctx.info[market1]["decimal"],
        )

        buy2_amount = float(buy1_amount) / float(buy2["price"])
        buy2_amount = numberFormatPrecision(
            buy2_amount,
            self.ctx.info[market2]["decimal"],
        )

        sell3_amount = numberFormatPrecision(
            float(buy2_amount),
            self.ctx.info[market3]["decimal"],
        )
        sell3_value = float(sell3_amount) * float(sell3["priceb"])

        self.ctx.lastorder[market1 + str(buy1_amount)] = sell3["priceb"]

        operation_data = (
            f"BBA___{market1}___{minimum_value}"
            f"___buy1_price={buy1['price']}"
            f"___buy2_price={buy2['price']}"
            f"___sell3_price={sell3['priceb']}"
            f"___{market1}={buy1_amount}"
            f"___{market2}={buy2_amount}"
            f"____{market3}={sell3_value} ::: {thread_name}"
        )

        next_thread = orderThread(
            self.ctx,
            "order_buy1",
            operation_data,
            market1,
            buy1_amount,
            market2,
            buy2_amount,
            market3,
            sell3_value,
            None,
            None,
            None,
        )
        next_thread.start()

    def order_buy1(
        self,
        thread_name,
        market1,
        amount1,
        market2,
        amount2,
        market3,
        amount3,
        executed_value1,
        executed_value2,
        executed_value3,
    ):
        order, error_message = self._create_order_with_retry(
            market1,
            "buy",
            amount1,
        )

        if order is not None:
            next_thread = orderThread(
                self.ctx,
                "order_buy2",
                thread_name + "|||" + json.dumps(order),
                market1,
                amount1,
                market2,
                order["amount"],
                market3,
                amount3,
                order["cost"],
                None,
                None,
            )
            next_thread.start()
            return

        error_data = (
            f"ERROR___order_buy1___{self.ctx.info[market1]['symbol']}"
            f"___market___buy___{amount1}___{error_message}"
        )
        self._start_mysql_thread("log", error_data)

    def order_buy2(
        self,
        thread_name,
        market1,
        amount1,
        market2,
        amount2,
        market3,
        amount3,
        executed_value1,
        executed_value2,
        executed_value3,
    ):
        order = None
        error_message = ""
        buy_price = None
        buy2_amount = None

        # The price is calculated for each attempt, just like in the original code.
        for _attempt in range(MAX_ORDER_ATTEMPTS):
            try:
                orderbook = sorted_orderbook(self.ctx.markets_btc[market2])
                buy_price = list(orderbook)[0][1]
                buy2_amount = float(amount2) / float(buy_price)
                buy2_amount = numberFormatPrecision(
                    buy2_amount,
                    self.ctx.info[market2]["decimal"],
                )
                order = self.ctx.exchange.create_order(
                    self.ctx.info[market2]["symbol"],
                    "market",
                    "buy",
                    buy2_amount,
                )
                break
            except RETRYABLE_EXCHANGE_ERRORS as error:
                error_message = str(error)
                time.sleep(ORDER_RETRY_DELAY_SECONDS)

        if order is not None:
            next_thread = orderThread(
                self.ctx,
                "order_sell1",
                thread_name + "|||" + json.dumps(order),
                market1,
                amount1,
                market2,
                amount2,
                market3,
                order["amount"],
                executed_value1,
                order["cost"],
                None,
            )
            next_thread.start()
            return

        error_data = (
            f"ERROR___order_buy2___{self.ctx.info[market2]['symbol']}"
            f"___market___buy___{buy2_amount}___{amount2}"
            f"___{buy_price}___{error_message}"
        )
        self._start_mysql_thread("log", error_data)

    def order_sell1(
        self,
        thread_name,
        market1,
        amount1,
        market2,
        amount2,
        market3,
        amount3,
        executed_value1,
        executed_value2,
        executed_value3,
    ):
        orderbook, sell_price = self._calculate_final_sell_price(
            market1,
            amount1,
            market3,
            amount3,
            executed_value1,
        )
        amount3 = numberFormatPrecision(
            amount3,
            self.ctx.info[market3]["decimal"],
        )

        order, error_message = self._create_final_sell_order(
            market3,
            amount3,
            sell_price,
        )

        current_orderbook = sorted_orderbook(self.ctx.markets_usdt[market3])

        if order is not None:
            operation_data = (
                thread_name
                + "|||"
                + json.dumps(order)
                + "|||markets_usdt:"
                + str(current_orderbook)
                + "|||lastorder:"
                + str(self.ctx.lastorder)
                + "|||markets_usdt_math:"
                + str(self.ctx._tempmarket)
            )
            self._start_mysql_thread("orders", operation_data)
            return

        error_data = (
            f"ERROR___order_sell1___{self.ctx.info[market3]['symbol']}"
            f"___market___sell___{amount3}___{sell_price}___{error_message}"
            f"|||markets_usdt:{current_orderbook}"
            f"|||lastorder:{self.ctx.lastorder}"
            f"|||markets_usdt_math:{self.ctx._tempmarket}"
        )
        self._start_mysql_thread("log", error_data)

    def exec_order_BAA(
        self,
        thread_name,
        minimum_value,
        market1,
        buy1,
        market2,
        sell2,
        market3,
        sell3,
    ):
        buy1_amount = float(minimum_value) / float(buy1["price"])
        buy1_amount = numberFormatPrecision(
            buy1_amount,
            self.ctx.info[market1]["decimal"],
        )

        sell2_amount = numberFormatPrecision(
            float(buy1_amount),
            self.ctx.info[market2]["decimal"],
        )
        sell2_value = float(sell2_amount) * float(sell2["priceb"])
        sell2_value = numberFormatPrecision(
            sell2_value,
            self.ctx.info[market2]["dec_precision"],
        )

        sell3_value = float(sell2_value) * float(sell3["priceb"])
        sell3_value = numberFormatPrecision(
            sell3_value,
            self.ctx.info[market3]["decimal"],
        )

        self.ctx.lastorder[market1 + str(buy1_amount)] = sell3["priceb"]

        operation_data = (
            f"BAA___{market1}___{minimum_value}"
            f"___buy1_price={buy1['price']}"
            f"___sell2_price={sell2['price']}"
            f"___sell3_price={sell3['priceb']}"
            f"___{market1}={buy1_amount}"
            f"___{market2}={sell2_value}"
            f"____{market3}={sell3_value} ::: {thread_name}"
        )

        next_thread = orderThread(
            self.ctx,
            "baa_order_buy1",
            operation_data,
            market1,
            buy1_amount,
            market2,
            sell2_value,
            market3,
            sell3_value,
            None,
            None,
            None,
        )
        next_thread.start()

    def baa_order_buy1(
        self,
        thread_name,
        market1,
        amount1,
        market2,
        amount2,
        market3,
        amount3,
        executed_value1,
        executed_value2,
        executed_value3,
    ):
        order, error_message = self._create_order_with_retry(
            market1,
            "buy",
            amount1,
        )

        if order is not None:
            next_thread = orderThread(
                self.ctx,
                "baa_order_sell1",
                thread_name + "|||" + json.dumps(order),
                market1,
                amount1,
                market2,
                order["amount"],
                market3,
                amount3,
                order["cost"],
                None,
                None,
            )
            next_thread.start()
            return

        error_data = (
            f"ERROR___baa_order_buy1___{self.ctx.info[market1]['symbol']}"
            f"___market___buy___{amount1}___{error_message}"
        )
        self._start_mysql_thread("log", error_data)

    def baa_order_sell1(
        self,
        thread_name,
        market1,
        amount1,
        market2,
        amount2,
        market3,
        amount3,
        executed_value1,
        executed_value2,
        executed_value3,
    ):
        sell2_amount = numberFormatPrecision(
            amount1,
            self.ctx.info[market2]["decimal"],
        )

        order, error_message = self._create_order_with_retry(
            market2,
            "sell",
            sell2_amount,
        )

        if order is not None:
            next_thread = orderThread(
                self.ctx,
                "baa_order_sell2",
                thread_name + "|||" + json.dumps(order),
                market1,
                amount1,
                market2,
                sell2_amount,
                market3,
                order["cost"],
                executed_value1,
                None,
                None,
            )
            next_thread.start()
            return

        error_data = (
            f"ERROR___baa_order_sell1___{self.ctx.info[market2]['symbol']}"
            f"___market___sell___{sell2_amount}___{error_message}"
        )
        self._start_mysql_thread("log", error_data)

    def baa_order_sell2(
        self,
        thread_name,
        market1,
        amount1,
        market2,
        amount2,
        market3,
        amount3,
        executed_value1,
        executed_value2,
        executed_value3,
    ):
        _orderbook, sell_price = self._calculate_final_sell_price(
            market1,
            amount1,
            market3,
            amount3,
            executed_value1,
        )
        amount3 = numberFormatPrecision(
            amount3,
            self.ctx.info[market3]["decimal"],
        )

        order, error_message = self._create_final_sell_order(
            market3,
            amount3,
            sell_price,
        )

        if order is not None:
            operation_data = thread_name + "|||" + json.dumps(order)
            self._start_mysql_thread("orders", operation_data)
            return

        error_data = (
            f"ERROR___baa_order_sell2___{self.ctx.info[market3]['symbol']}"
            f"___market___sell___{amount3}___{error_message}"
        )
        self._start_mysql_thread("log", error_data)
