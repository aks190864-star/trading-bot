import requests
import os

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


# 🔹 Telegram Alert
def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": msg}
        requests.post(url, data=data)
    except:
        print("Telegram error")


# 🔹 Spot Price Fetch
def get_spot():
    try:
        url = "https://api.delta.exchange/v2/tickers/BTCUSD"
        res = requests.get(url).json()
        spot = float(res['result']['last_price'])
        return spot
    except Exception as e:
        print("Spot error:", e)
        return 67000   # fallback


# 🔹 Strike Calculation
def get_strikes(spot):
    call = round(spot * 1.07, -2)
    put = round(spot * 0.93, -2)
    return call, put


# 🔹 Main Bot Logic
def run():
    try:
        spot = get_spot()
        print("Spot:", spot)

        call, put = get_strikes(spot)

        msg = f"""
🚀 BOT STARTED
Spot: {spot}

Sell CALL: {call}
Sell PUT: {put}

Qty: 20
Strategy:
+5% move → Sell more
-13% → Buy back
"""

        print(msg)
        send_telegram(msg)

    except Exception as e:
        print("Main error:", e)


# 🔹 Run
if __name__ == "__main__":
    run()
