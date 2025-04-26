import ssl, smtplib
from email.message import EmailMessage
from datetime import datetime
import pytz
from src.config import SMTP_SERVER, SMTP_PORT, EMAIL_SENDER, EMAIL_PASS, EMAIL_RCPT, TIMEZONE

def email_signal(payload: str):
    """Send the JSON payload as an email to your inbox."""
    now = datetime.now(pytz.timezone(TIMEZONE)).strftime("%Y-%m-%d %H:%M")
    msg = EmailMessage()
    msg["Subject"] = f"[Trading‑Bot] Signal @ {now}"
    msg["From"]    = EMAIL_SENDER
    msg["To"]      = EMAIL_RCPT
    msg.set_content(payload)

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=ctx) as smtp:
        smtp.login(EMAIL_SENDER, EMAIL_PASS)
        smtp.send_message(msg)
