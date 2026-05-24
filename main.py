import yfinance as yf
import requests
import json
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

ALERT_FILE = "alerted.json"

# NIFTY 50 STOCKS
NIFTY50 = [

    "ADANIENT.NS",
    "ADANIPORTS.NS",
    "APOLLOHOSP.NS",
    "ASIANPAINT.NS",
    "AXISBANK.NS",
    "BAJAJ-AUTO.NS",
    "BAJFINANCE.NS",
    "BAJAJFINSV.NS",
    "BEL.NS",
    "BHARTIARTL.NS",
    "CIPLA.NS",
    "COALINDIA.NS",
    "DRREDDY.NS",
    "EICHERMOT.NS",
    "ETERNAL.NS",
    "GRASIM.NS",
    "HCLTECH.NS",
    "HDFCBANK.NS",
    "HDFCLIFE.NS",
    "HEROMOTOCO.NS",
    "HINDALCO.NS",
    "HINDUNILVR.NS",
    "ICICIBANK.NS",
    "INDUSINDBK.NS",
    "INFY.NS",
    "ITC.NS",
    "JIOFIN.NS",
    "JSWSTEEL.NS",
    "KOTAKBANK.NS",
    "LT.NS",
    "M&M.NS",
    "MARUTI.NS",
    "NESTLEIND.NS",
    "NTPC.NS",
    "ONGC.NS",
    "POWERGRID.NS",
    "RELIANCE.NS",
    "SBILIFE.NS",
    "SBIN.NS",
    "SHRIRAMFIN.NS",
    "SUNPHARMA.NS",
    "TATACONSUM.NS",
    "TATAMOTORS.NS",
    "TATASTEEL.NS",
    "TCS.NS",
    "TECHM.NS",
    "TITAN.NS",
    "TRENT.NS",
    "ULTRACEMCO.NS",
    "WIPRO.NS"
]

# Alert thresholds
THRESHOLDS = [20, 30, 40, 50]

# Load previous alerts safely
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

        response = requests.post(
            url,
            data=payload,
            timeout=10
        )

        print(response.text)

    except Exception as e:

        print(f"Telegram error: {e}")

# Determine highest crossed threshold
def get_threshold(drop_percent):

    crossed = 0

    for threshold in THRESHOLDS:

        if drop_percent >= threshold:

            crossed = threshold

    return crossed

print("Starting scan...")

for stock in NIFTY50:

    try:

        print(f"Checking {stock}")

        ticker = yf.Ticker(stock)

        hist = ticker.history(period="max")

        if hist.empty:

            print(f"No data for {stock}")

            continue

        ath = hist["High"].max()

        current = hist["Close"].iloc[-1]

        fall_percent = ((ath - current) / ath) * 100

        current_threshold = get_threshold(fall_percent)

        previous_threshold = alerted.get(stock, 0)

        print(
            f"{stock} | "
            f"Drop: {fall_percent:.2f}% | "
            f"Previous: {previous_threshold}% | "
            f"Current: {current_threshold}%"
        )

        # NEW THRESHOLD CROSSED
        if current_threshold > previous_threshold:

            message = f"""
🚨 NIFTY ATH ALERT 🚨

Stock: {stock}

ATH: ₹{ath:.2f}
Current: ₹{current:.2f}

Drop: {fall_percent:.2f}%

New Threshold Crossed: {current_threshold}%
Previous Threshold: {previous_threshold}%
"""

            send_telegram(message)

            alerted[stock] = current_threshold

            print(f"Alert sent for {stock}")

        # RESET IF RECOVERED BELOW 20%
        elif current_threshold == 0 and previous_threshold != 0:

            alerted[stock] = 0

            print(f"Reset alert state for {stock}")

    except Exception as e:

        print(f"Error with {stock}: {e}")

# Save state
with open(ALERT_FILE, "w") as f:

    json.dump(alerted, f)

print("Scan completed.")
