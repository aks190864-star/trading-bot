import requests
import os

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


# 🔹 Telegram Alert
def send_telegram(msg):
    try:
        if not BOT_TOKEN or not CHAT_ID:
            print("Telegram not configured")
            return

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": msg}
        requests.post(url, data=data)

    except Exception as e:
        print("Telegram error:", e)


# 🔹 Spot Price Fetch
def get_spot():
    try:
        url = "https://api.delta.exchange/v2/tickers/BTCUSD"
        res = requests.get(url, timeout=10).json()

        # 🔥 safe parsing
        if 'result' in res and 'last_price' in res['result']:
            return float(res['result']['last_price'])

        else:
            print("Invalid API response:", res)
            return 67000

    except Exception as e:
        print("Spot error:", e)
        return 67000   # fallback


# 🔹 Strike Calculation
def get_strikes(spot):
    try:
        call = round(spot * 1.07, -2)
        put = round(spot * 0.93, -2)
        return call, put
    except Exception as e:
        print("Strike error:", e)
        return 72000, 62000


# 🔹 Main Bot Logic
def run():
    try:
        # 🔥 spot पहले define होगा
        spot = get_spot()

        if spot is None:
            print("Spot is None, using fallback")
            spot = 67000

        print("Current Spot:", spot)

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
