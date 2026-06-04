import threading
from ibapi.client import EClient
from ibapi.wrapper import EWrapper
from ibapi.contract import Contract
from ibapi.order import Order
import json
import time

# This is the signals module, USED FOR CRYPTO 24h TRADING, NOT FOR STOCKS. For stocks, use the BuySell module.

class BuyApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)
    
    def nextValidId(self, orderId: int):
        with open('stock_data.json', 'r') as file:
            data_loaded = json.load(file)
        
        symbol = data_loaded["symbol"]
        quantity = data_loaded["quantity"]
        sec_type = data_loaded.get("secType", "STK")  # Default to "STK" if not provided
        
        if quantity < 1:
            print("Error: Fractional orders are not supported.")
            return

        # Define contract
        mycontract = Contract()
        mycontract.symbol = symbol
        mycontract.secType = sec_type
        if sec_type == "CRYPTO":
            mycontract.exchange = "PAXOS"
        else:
            mycontract.exchange = "SMART"
        mycontract.currency = "USD"

        # Define order
        myorder = Order()
        myorder.orderId = orderId
        myorder.totalQuantity = quantity
        myorder.action = "BUY"
        myorder.orderType = "MKT"

        self.placeOrder(orderId, mycontract, myorder)
        print(f"Order placed to BUY {quantity} units of {symbol} ({sec_type}).")

def buy(port):
    app = BuyApp()
    app.connect("127.0.0.1", port, clientId=100)
    
    # Run in a separate thread
    thread = threading.Thread(target=app.run)
    thread.start()
    
    # Disconnect after a delay
    time.sleep(2)
    app.disconnect()
    thread.join()
    print("Buy operation completed.")


class SellApp(EClient, EWrapper):
    def __init__(self):
        EClient.__init__(self, self)

    def nextValidId(self, orderId: int):
        with open('stock_data.json', 'r') as file:
            data_loaded = json.load(file)

        symbol = data_loaded["symbol"]
        quantity = data_loaded["quantity"]
        sec_type = data_loaded.get("secType", "STK")  # Default to "STK" if not provided

        # Define contract
        mycontract = Contract()
        mycontract.symbol = symbol
        mycontract.secType = sec_type
        if sec_type == "CRYPTO":
            mycontract.exchange = "PAXOS"
        else:
            mycontract.exchange = "SMART"
        mycontract.currency = "USD"

        # Define order
        myorder = Order()
        myorder.orderId = orderId
        myorder.totalQuantity = quantity
        myorder.action = "SELL"
        myorder.orderType = "MKT"

        self.placeOrder(orderId, mycontract, myorder)
        print(f"Order placed to SELL {quantity} units of {symbol} ({sec_type}).")

def sell(port):
    app = SellApp()
    app.connect("127.0.0.1", port, clientId=101)
    
    thread = threading.Thread(target=app.run)
    thread.start()
    
    # Disconnect after a delay
    time.sleep(2)
    app.disconnect()
    thread.join()
    print("Sell operation completed.")
