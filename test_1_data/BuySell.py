# ib_trading.py

import threading
import time
import requests

from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order

# ─────────────────────────────────────────────────────────────────────────────
#  AlphaVantage price fetch (free)
ALPHA_KEY = "F1UXC7ZGHIEUFHUN"
def get_price_from_alpha(symbol: str, interval: str="1min", output_size: str="compact") -> float:
    url = "https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": interval,
        "apikey": ALPHA_KEY,
        "outputsize": output_size,
    }
    r = requests.get(url, params=params, timeout=5)
    data = r.json()
    ts = data.get(f"Time Series ({interval})")
    if not ts:
        raise RuntimeError(f"No intraday data for {symbol}")
    latest = sorted(ts.keys())[-1]
    return float(ts[latest]["4. close"])

# ─────────────────────────────────────────────────────────────────────────────
class IB(EWrapper, EClient):
    def __init__(self):
        EClient.__init__(self, self)
        self._nextOrderId = None
        self._positions = []
        self._pos_done = threading.Event()
        self._acct = {}
        self._acct_done = threading.Event()

    # -- connection/ID --------------------------------------
    def nextValidId(self, orderId: int):
        self._nextOrderId = orderId

    def connect_and_run(self, host, port, client_id):
        self.connect(host, port, client_id)
        t = threading.Thread(target=self.run, daemon=True)
        t.start()
        # wait for nextValidId()
        end = time.time() + 5
        while self._nextOrderId is None and time.time() < end:
            time.sleep(0.1)
        if self._nextOrderId is None:
            raise RuntimeError("no nextValidId from TWS")
        return t

    def disconnect_and_wait(self, thread):
        self.disconnect()
        thread.join(1)

    # -- positions callback --------------------------------
    def position(self, account, contract: Contract, pos, avgCost):
        self._positions.append({
            "account": account,
            "symbol": contract.symbol,
            "secType": contract.secType,
            "exchange": contract.exchange,
            "position": pos,
            "avgCost": avgCost
        })
    def positionEnd(self):
        self._pos_done.set()

    # -- account summary callback --------------------------
    def accountSummary(self, reqId, account, tag, value, currency):
        if tag == "ExcessLiquidity":
            self._acct["ExcessLiquidity"] = float(value)
    def accountSummaryEnd(self, reqId):
        self._acct_done.set()

    # -- suppress only real errors -------------------------
    def error(self, reqId, code, msg):
        if code >= 2000:
            print(f"[IB ERROR] reqId={reqId} code={code} msg={msg}")

# ─────────────────────────────────────────────────────────────────────────────
_ib: IB = None
_thread: threading.Thread = None

def connect(port:int=7497, client_id:int=100, host:str="127.0.0.1"):
    global _ib, _thread
    if _ib: return
    _ib = IB()
    _thread = _ib.connect_and_run(host, port, client_id)
    time.sleep(0.2)

def disconnect():
    global _ib, _thread
    if not _ib: return
    _ib.disconnect_and_wait(_thread)
    _ib = None

def _make_contract(symbol, exchange):
    c = Contract()
    c.symbol = symbol
    c.secType = "STK"
    c.currency = "USD"
    c.exchange = exchange or "SMART"
    return c

def _place_limit_order(action, symbol, quantity, exchange):
    global _ib
    # fetch most recent price
    price = get_price_from_alpha(symbol)
    oid = _ib._nextOrderId
    order = Order()
    order.orderId       = oid
    order.action        = action.upper()
    order.orderType     = "LMT"
    order.lmtPrice      = price
    order.totalQuantity = quantity
    order.tif           = "DAY"
    # clear any weird flags
    order.eTradeOnly    = False
    order.firmQuoteOnly = False
    order.outsideRth    = False

    _ib.placeOrder(oid, _make_contract(symbol, exchange), order)
    print(f">>> {action.upper()} {quantity}×{symbol} @LMT {price:.2f} (orderId={oid})")
    _ib._nextOrderId += 1

def buy(symbol:str, quantity:float, exchange:str="SMART"):
    _place_limit_order("BUY", symbol, quantity, exchange)

def sell(symbol:str, quantity:float, exchange:str="SMART"):
    _place_limit_order("SELL", symbol, quantity, exchange)

def close_buy(symbol:str, quantity:float, exchange:str="SMART"):
    sell(symbol, quantity, exchange)

def close_sell(symbol:str, quantity:float, exchange:str="SMART"):
    buy(symbol, quantity, exchange)

def get_positions(timeout:float=5.0):
    global _ib
    _ib._positions.clear()
    _ib._pos_done.clear()
    _ib.reqPositions()
    if not _ib._pos_done.wait(timeout):
        raise RuntimeError("timeout waiting for positions")
    _ib.cancelPositions()
    return list(_ib._positions)

def get_excess_liquidity(timeout:float=5.0):
    global _ib
    _ib._acct.clear()
    _ib._acct_done.clear()
    _ib.reqAccountSummary(0, "All", "ExcessLiquidity")
    if not _ib._acct_done.wait(timeout):
        raise RuntimeError("timeout waiting for account summary")
    _ib.cancelAccountSummary(0)
    return _ib._acct.get("ExcessLiquidity", None)
