from pathlib import Path
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env", override=True)

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Anthropic
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Email
SMTP_SERVER  = os.getenv("SMTP_SERVER")
SMTP_PORT    = int(os.getenv("SMTP_PORT", 465))
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_PASS   = os.getenv("EMAIL_PASSWORD")
EMAIL_RCPT   = os.getenv("EMAIL_RECEIVER")

# Other
TIMEZONE    = os.getenv("TIMEZONE", "UTC")
SCREEN_DIR  = ROOT / "screens"
SCREEN_DIR.mkdir(exist_ok=True)