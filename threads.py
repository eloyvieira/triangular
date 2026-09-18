import threading


class orderThread(threading.Thread):
    """Dispatches an individual order leg to OrderFunctions."""

    _HANDLERS = {
        "order_buy1": "order_buy1",
        "order_buy2": "order_buy2",
        "order_sell1": "order_sell1",
        "baa_order_buy1": "baa_order_buy1",
        "baa_order_sell1": "baa_order_sell1",
        "baa_order_sell2": "baa_order_sell2",
    }

    def __init__(
        self,
        ctx,
        _type,
        _name,
        _market1,
        _amount1,
        _market2,
        _amount2,
        _market3,
        _amount3,
        _exec1,
        _exec2,
        _exec3,
    ):
        super().__init__()

        self.ctx = ctx
        self.operation_type = _type
        self.operation_name = _name
        self.market1 = _market1
        self.amount1 = _amount1
        self.market2 = _market2
        self.amount2 = _amount2
        self.market3 = _market3
        self.amount3 = _amount3
        self.executed_value1 = _exec1
        self.executed_value2 = _exec2
        self.executed_value3 = _exec3

        # Backward-compatible attributes used by the original implementation.
        self.type = _type
        self.name = _name
        self.exec1 = _exec1
        self.exec2 = _exec2
        self.exec3 = _exec3

    def run(self):
        handler_name = self._HANDLERS.get(self.operation_type)
        if handler_name is None:
            return

        handler = getattr(self.ctx.orders, handler_name)
        handler(
            self.operation_name,
            self.market1,
            self.amount1,
            self.market2,
            self.amount2,
            self.market3,
            self.amount3,
            self.executed_value1,
            self.executed_value2,
            self.executed_value3,
        )


class myThread(threading.Thread):
    """Dispatches a complete triangular route to OrderFunctions."""

    _HANDLERS = {
        "exec_order_BBA": "exec_order_BBA",
        "exec_order_BAA": "exec_order_BAA",
    }

    def __init__(
        self,
        ctx,
        type,
        name,
        _valminimal,
        market1,
        buy1,
        market2,
        buy2,
        market3,
        sell3,
    ):
        super().__init__()

        self.ctx = ctx
        self.operation_type = type
        self.operation_name = name
        self.minimum_value = _valminimal
        self.market1 = market1
        self.leg1 = buy1
        self.market2 = market2
        self.leg2 = buy2
        self.market3 = market3
        self.leg3 = sell3

        # Backward-compatible attributes used by the original implementation.
        self.type = type
        self.name = name
        self._valminimal = _valminimal
        self.buy1 = buy1
        self.buy2 = buy2
        self.sell3 = sell3

    def run(self):
        handler_name = self._HANDLERS.get(self.operation_type)
        if handler_name is None:
            return

        handler = getattr(self.ctx.orders, handler_name)
        handler(
            self.operation_name,
            self.minimum_value,
            self.market1,
            self.leg1,
            self.market2,
            self.leg2,
            self.market3,
            self.leg3,
        )


class mysqlThread(threading.Thread):
    """Dispatches asynchronous database writes to MysqlFunctions."""

    _SIMPLE_HANDLERS = {
        "lockunlock": "exec_lockunlock",
        "orders": "exec_orders",
        "log": "exec_log",
    }

    def __init__(
        self,
        ctx,
        type,
        dbConnection_in,
        side,
        market1,
        market2,
        market3,
        price1,
        price2,
        price3,
        amount1_in,
        amount1_out,
        perc1,
        amount2_in,
        amount2_out,
        perc2,
        date_creation,
    ):
        super().__init__()

        self.ctx = ctx
        self.operation_type = type
        self.db_connection = dbConnection_in
        self.side = side
        self.market1 = market1
        self.market2 = market2
        self.market3 = market3
        self.price1 = price1
        self.price2 = price2
        self.price3 = price3
        self.amount1_in = amount1_in
        self.amount1_out = amount1_out
        self.percentage1 = perc1
        self.amount2_in = amount2_in
        self.amount2_out = amount2_out
        self.percentage2 = perc2
        self.date_creation = date_creation

        # Backward-compatible attributes used by the original implementation.
        self.type = type
        self.dbConnection_in = dbConnection_in
        self.perc1 = perc1
        self.perc2 = perc2

    def run(self):
        if self.operation_type == "exec_mysql":
            self.ctx.mysql.exec_mysql(
                self.db_connection,
                self.side,
                self.market1,
                self.market2,
                self.market3,
                self.price1,
                self.price2,
                self.price3,
                self.amount1_in,
                self.amount1_out,
                self.percentage1,
                self.amount2_in,
                self.amount2_out,
                self.percentage2,
                self.date_creation,
            )
            return

        handler_name = self._SIMPLE_HANDLERS.get(self.operation_type)
        if handler_name is None:
            return

        handler = getattr(self.ctx.mysql, handler_name)
        handler(
            self.db_connection,
            self.side,
            self.date_creation,
        )

OrderThread = orderThread
StrategyThread = myThread
MySQLThread = mysqlThread
