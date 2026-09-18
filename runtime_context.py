class RuntimeContext:
    """Stores the state shared across the robot's modules."""

    def __init__(self):
        # External services
        self.exchange = None
        self.mySQLConnectionPool = None

        # Market configuration
        self.symbols = []
        self.info = {}

        # Enabled markets
        self.dyn_markets = {}
        self.dyn_market_btc = {}
        self.dyn_market_usdt = {}

        # Order books
        self.markets = {}
        self.markets_btc = {}
        self.markets_usdt = {}

        # Runtime state
        self.desliga = False
        self.waiting = False

        # Strategy configuration
        self.spread = 5
        self.maxamount = 150
        self.minamount = 100
        self.min_porcentagem = 1
        self.porcentagem_gain = 0.5
        self.balance = 0

        # Order execution
        self.lastorder = {}
        self.lastorder_limit = True
        self._tempmarket = {}

        # Opportunity control
        self.last_opportunity_at = {}
        self.EXECUTE_ORDERS = False
        self.OPPORTUNITY_COOLDOWN_SECONDS = 2.0
        self.FEE_FACTOR_3_LEGS = 1.0

        # Binance WebSocket
        self.WS_URL = "wss://stream.binance.com:9443/stream"
        self.WS_DEPTH = 20
        self.WS_UPDATE_SPEED = "100ms"
        self.WS_STALE_SECONDS = 3.0
        self.WS_STREAMS_PER_CONNECTION = 200

        # Order-book update control
        self.market_updated_at = {}
        self.market_update_id = {}

        # Application modules
        self.mysql = None
        self.orders = None
        self.strategy = None
        self.websocket = None