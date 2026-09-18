import math
from decimal import Decimal

def numberFormatPrecision(f, n):
    _return = math.floor(float(f) * 10 ** float(n)) / 10 ** float(n)
    chk = str(_return)
    chk = chk[-2:]
    if chk == ".0":
        _return = str(_return).replace(".0", "")
    return _return

def sorted_orderbook(book):
    """Keeps asks before bids while sorting prices numerically."""
    return sorted(book, key=lambda item: (item[0], Decimal(str(item[1]))))

