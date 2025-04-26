import base64
import logging
from openai import OpenAI, OpenAIError
from anthropic import Anthropic, AnthropicError
from src.config import OPENAI_API_KEY, ANTHROPIC_API_KEY

logger = logging.getLogger(__name__)

# Initialize clients
openai_client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None

# Analysis prompt
ANALYSIS_PROMPT = """
You are an expert trading analyst. The image I'm sending is a price chart (e.g. XAU/USD or any other instrument).
Please produce a report in this exact structure, replacing the example values:

1. SUMMARY
   Based on the chart you've shared, the price is currently around $<current_price> with <bullish/bearish/mixed> momentum.

2. SIGNAL
   **BUY SIGNAL** or **SELL SIGNAL** (choose one in all‑caps).

3. KEY OBSERVATIONS
   - Indicator 1: … (e.g. RSI is at 74.10, showing overbought).
   - Indicator 2: … (e.g. price above moving averages suggests…).
   - Price action: … (e.g. approaching support/resistance at $X).

4. TAKE PROFIT ZONES
   1. First take profit: $<level1> (nearest visible support/resistance)
   2. Second take profit: $<level2>
   3. Final take profit: $<level3>
"""

# Models to try
GPT_MODELS = ["gpt-4o-mini", "o3-mini"]
CLAUDE_MODELS = ["claude-3-opus-20240229", "claude-3-sonnet-20240229"]


def analyze_chart(image_path: str, provider: str = "GPT") -> str:
    """Send the screenshot for full text analysis and return the report."""
    # Read & encode image
    with open(image_path, "rb") as f:
        image_data = f.read()
        b64 = base64.b64encode(image_data).decode()
    
    if provider == "GPT":
        return analyze_with_gpt(b64)
    elif provider == "Claude":
        return analyze_with_claude(image_data)
    else:
        raise ValueError(f"Unknown provider: {provider}")


def analyze_with_gpt(b64_image: str) -> str:
    """Analyze using OpenAI GPT models"""
    if not openai_client:
        raise RuntimeError("OpenAI API key not configured")
    
    for model in GPT_MODELS:
        try:
            logger.info(f"Trying GPT model {model} for analysis")
            resp = openai_client.chat.completions.create(
                model=model,
                max_tokens=300,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{b64_image}",
                                    "detail": "high"
                                }
                            },
                            {"type": "text", "text": ANALYSIS_PROMPT}
                        ]
                    }
                ]
            )
            return resp.choices[0].message.content.strip()
        except OpenAIError as e:
            if "model_not_found" in str(e) or getattr(e, "code", "") == "model_not_found":
                logger.warning(f"GPT model {model} unavailable: {e}")
                continue
            raise
    
    raise RuntimeError(f"No available GPT models: {GPT_MODELS}")


def analyze_with_claude(image_data: bytes) -> str:
    """Analyze using Anthropic Claude models"""
    if not anthropic_client:
        raise RuntimeError("Anthropic API key not configured")
    
    for model in CLAUDE_MODELS:
        try:
            logger.info(f"Trying Claude model {model} for analysis")
            
            # Convert image to base64 for Claude
            b64_image = base64.b64encode(image_data).decode()
            
            message = anthropic_client.messages.create(
                model=model,
                max_tokens=300,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/png",
                                    "data": b64_image
                                }
                            },
                            {
                                "type": "text",
                                "text": ANALYSIS_PROMPT
                            }
                        ]
                    }
                ]
            )
            return message.content[0].text
        except AnthropicError as e:
            if "model_not_found" in str(e):
                logger.warning(f"Claude model {model} unavailable: {e}")
                continue
            raise
    
    raise RuntimeError(f"No available Claude models: {CLAUDE_MODELS}")