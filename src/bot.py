# src/bot.py

import time
import logging
import traceback
import schedule

from src.screenshot import grab_chart
from src.vision_client import analyze_chart    # ← updated import
from src.mailer import email_signal

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)

def run_cycle():
    try:
        shot   = grab_chart()
        report = analyze_chart(shot)             # ← call analyze_chart
        logging.info("Analysis report:\n%s", report)
        email_signal(report)
    except Exception as e:
        logging.error("Cycle error: %s\n%s", e, traceback.format_exc())

# schedule every 30 minutes
schedule.every(30).minutes.do(run_cycle)

if __name__ == "__main__":
    logging.info("Starting TradingView Mail‑Bot…")
    run_cycle()                                 # first run immediately
    while True:
        schedule.run_pending()
        time.sleep(5)
