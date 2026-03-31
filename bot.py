import requests
import time
import hmac
import hashlib
import json
import os

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

BASE_URL = "https://api.delta.exchange"
QTY = 1

positions = []

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def sign(method, path, body, timestamp):
    msg = method + timestamp + path + body
    return hmac.new(API_SECRET.encode(), msg.encode(), hashlib.sha256).hexdigest()

def request(method, path, body=None):
    timestamp = str(int(time.time()))
    body_str = json.dumps(body) if body else ""
    
    headers = {
        "api-key": API_KEY,
        "timestamp": timestamp,
        "signature": sign(method, path, body_str, timestamp),
        "Content-Type": "application/json"
    }

    url = BASE_URL + path
    if method == "GET":
        return requests.get(url, headers=headers).json()
    else:
        return requests.post(url, headers=headers, data=body_str).json()

def get_spot():
    data = requests.get(BASE_URL + "/v2/tickers").json()
    for i in data['result']:
        if i['symbol'] == "BTCUSD":
            return float(i['mark_price'])

def get_strikes(spot):
    return round(spot * 1.07, -2), round(spot * 0.93, -2)

def get_option(strike, opt_type):
    data = requests.get(BASE_URL + "/v2/products").json()
    for i in data['result']:
        if str(strike) in i['symbol'] and opt_type in i['symbol']:
            return i['id'], i['symbol']

def get_price(symbol):
    data = requests.get(BASE_URL + "/v2/tickers").json()
    for i in data['result']:
        if i['symbol'] == symbol:
            return float(i['mark_price'])

def order(product_id, side, symbol):
    body = {
        "product_id": product_id,
        "size": QTY,
        "side": side,
        "order_type": "market"
    }
    res = request("POST", "/v2/orders", body)
    send_telegram(f"{side.upper()} {symbol}")
    print(res)

def run():
    send_telegram("🚀 Bot Started")

    spot = get_spot()
    call, put = get_strikes(spot)

    ce_id, ce_symbol = get_option(call, "C")
    pe_id, pe_symbol = get_option(put, "P")

    ce_price = get_price(ce_symbol)
    pe_price = get_price(pe_symbol)

    order(ce_id, "sell", ce_symbol)
    order(pe_id, "sell", pe_symbol)

    positions.append({"id": ce_id, "symbol": ce_symbol, "sell": ce_price})
    positions.append({"id": pe_id, "symbol": pe_symbol, "sell": pe_price})

    while True:
        for p in positions[:]:
            price = get_price(p["symbol"])

            if "min_price" not in p:
                p["min_price"] = p["sell"]

            if price < p["min_price"]:
                p["min_price"] = price

            # Add
            if price >= p["sell"] * 1.05:
                order(p["id"], "sell", p["symbol"])
                positions.append({"id": p["id"], "symbol": p["symbol"], "sell": price})

            # Trailing Exit
            elif price >= p["min_price"] * 1.05:
                send_telegram(f"EXIT {p['symbol']}")
                order(p["id"], "buy", p["symbol"])
                positions.remove(p)

        time.sleep(3)
try:
    # आपका पूरा trading logic यहाँ
    print("Bot running...")

except Exception as e:
    print("Error:", str(e))

import requests

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": msg}
    requests.post(url, data=data)

send_telegram("Bot Started ✅")

run()
