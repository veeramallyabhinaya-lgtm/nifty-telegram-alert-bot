import yfinance as yf
import requests
import json
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

NIFTY50 = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "SBIN.NS",
    "LT.NS",
    "ITC.NS",
    "HINDUNILVR.NS",
    "BHARTIARTL.NS"
]

ALERT_FILE = "alerted.json"

# Load existing alerts
if os.path.exists(ALERT_FILE):
    with open(ALERT_FILE, "r") as f:
        alerted = json.load(f)
else:
    alerted = {}

def send_telegram(message):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(url, data=payload)

for stock in NIFTY50:

    try:
        ticker = yf.Ticker(stock)

        hist = ticker.history(period="max")

        if hist.empty:
            continue

        ath = hist["High"].max()
        current = hist["Close"].iloc[-1]

        fall_percent = ((ath - current) / ath) * 100

        threshold_hit = fall_percent >= 30

        already_alerted = alerted.get(stock, False)

        if threshold_hit and not already_alerted:

            message = f"""
🚨 STOCK ALERT

Stock: {stock}

ATH: ₹{ath:.2f}
Current: ₹{current:.2f}

Down by: {fall_percent:.2f}% from ATH
"""

            send_telegram(message)

            alerted[stock] = True

        elif not threshold_hit:
            alerted[stock] = False

    except Exception as e:
        print(f"Error with {stock}: {e}")

with open(ALERT_FILE, "w") as f:
    json.dump(alerted, f)
