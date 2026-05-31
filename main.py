import yfinance as yf
import requests
import json
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_IDS = [
    chat_id.strip()
    for chat_id in os.getenv("CHAT_ID", "").split(",")
    if chat_id.strip()
]

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
    "WIPRO.NS",

    "ABB.NS",
    "ABCAPITAL.NS",
    "ABFRL.NS",
    "ALKEM.NS",
    "AMBUJACEM.NS",
    "ASHOKLEY.NS",
    "ASTRAL.NS",
    "AUROPHARMA.NS",
    "BANKBARODA.NS",
    "BOSCHLTD.NS",
    "BPCL.NS",
    "BRITANNIA.NS",
    "CANBK.NS",
    "CGPOWER.NS",
    "CHOLAFIN.NS",
    "COLPAL.NS",
    "CONCOR.NS",
    "CUMMINSIND.NS",
    "DABUR.NS",
    "DLF.NS",
    "DMART.NS",
    "GAIL.NS",
    "GODREJCP.NS",
    "HAVELLS.NS",
    "ICICIGI.NS",
    "ICICIPRULI.NS",
    "INDIGO.NS",
    "INDUSTOWER.NS",
    "IRCTC.NS",
    "JINDALSTEL.NS",
    "LICI.NS",
    "LODHA.NS",
    "LUPIN.NS",
    "MARICO.NS",
    "MOTHERSON.NS",
    "NAUKRI.NS",
    "NHPC.NS",
    "OBEROIRLTY.NS",
    "PAGEIND.NS",
    "PATANJALI.NS",
    "PEL.NS",
    "PIDILITIND.NS",
    "PNB.NS",
    "RECLTD.NS",
    "SAIL.NS",
    "SIEMENS.NS",
    "TORNTPHARM.NS",
    "TVSMOTOR.NS",
    "UNITDSPR.NS",
    "VEDL.NS"
]

# Alert thresholds based on 52-week high drop
THRESHOLDS = [15, 25, 35, 50]

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

    for chat_id in CHAT_IDS:

        payload = {
            "chat_id": chat_id,
            "text": message
        }

        try:

            response = requests.post(
                url,
                data=payload,
                timeout=10
            )

            print(
                f"Message sent to {chat_id}: "
                f"{response.status_code}"
            )

        except Exception as e:

            print(
                f"Telegram error for "
                f"{chat_id}: {e}"
            )# Determine highest threshold crossed
def get_threshold(drop_percent):

    crossed = 0

    for threshold in THRESHOLDS:

        if drop_percent >= threshold:

            crossed = threshold

    return crossed

print("Starting NIFTY 50 scan...")

for stock in NIFTY50:

    try:

        print(f"Checking {stock}")

        ticker = yf.Ticker(stock)

        # LAST 1 YEAR DATA
        hist = ticker.history(period="1y")

        if hist.empty:

            print(f"No data for {stock}")

            continue

        # 52-WEEK HIGH
        high_52_week = hist["High"].max()

        # CURRENT PRICE
        current = hist["Close"].iloc[-1]

        # DROP FROM 52-WEEK HIGH
        fall_percent = (
            (high_52_week - current)
            / high_52_week
        ) * 100

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
🚨 NIFTY 100 ALERT 🚨

Stock: {stock}

52W High: ₹{high_52_week:.2f}
Current: ₹{current:.2f}

Drop From 52W High: {fall_percent:.2f}%

New Threshold Crossed: {current_threshold}%
Previous Threshold: {previous_threshold}%
"""

            send_telegram(message)

            alerted[stock] = current_threshold

            print(f"Alert sent for {stock}")

        # RESET IF STOCK RECOVERS
        elif current_threshold == 0 and previous_threshold != 0:

            alerted[stock] = 0

            print(f"Reset alert state for {stock}")

    except Exception as e:

        print(f"Error with {stock}: {e}")

# Save alert state
with open(ALERT_FILE, "w") as f:

    json.dump(alerted, f)

print("NIFTY 50 scan completed.")
