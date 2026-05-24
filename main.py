import yfinance as yf
import requests
import json
import os
from nsepython import *

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

ALERT_FILE = "alerted.json"

# Safe JSON loading
try:
    if os.path.exists(ALERT_FILE):
        with open(ALERT_FILE, "r") as f:
            content = f.read().strip()
            alerted = json.loads(content) if content else {}
    else:
        alerted = {}
except:
    alerted = {}

# Telegram sender
def send_telegram(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"Telegram error: {e}")

# Dynamically fetch ONLY NIFTY 50 stocks
def get_nifty50_stocks():

    try:

        data = nse_get_index_quote("NIFTY 50")

        stocks = []

        for stock in data["data"]:

            symbol = stock["symbol"]

            stocks.append(symbol + ".NS")

        return stocks

    except Exception as e:

        print(f"NSE fetch error: {e}")

        return []

# Main logic
stocks = get_nifty50_stocks()

print(f"Found {len(stocks)} NIFTY 50 stocks")

for stock in stocks:

    try:

        ticker = yf.Ticker(stock)

        hist = ticker.history(period="max")

        if hist.empty:
            continue

        ath = hist["High"].max()

        current = hist["Close"].iloc[-1]

        fall_percent = ((ath - current) / ath) * 100

        already_alerted = alerted.get(stock, False)

        if fall_percent >= 30 and not already_alerted:

            message = f"""
🚨 ATH DROP ALERT 🚨

Stock: {stock}

ATH: ₹{ath:.2f}
Current: ₹{current:.2f}

Drop: {fall_percent:.2f}% from ATH
"""

            send_telegram(message)

            alerted[stock] = True

            print(f"Alert sent for {stock}")

        elif fall_percent < 30:

            alerted[stock] = False

    except Exception as e:

        print(f"Error with {stock}: {e}")

# Save state
with open(ALERT_FILE, "w") as f:
    json.dump(alerted, f)

print("Scan completed.")
