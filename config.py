# config.py
# ──────────────────────────────────────────────────────────────────────────────
# ⚙️ CONFIGURATION — API Keys, Model Settings, and Constants
# ──────────────────────────────────────────────────────────────────────────────
#
# WHAT IS THIS?
#   Central configuration file that loads secrets from .env file and defines
#   which AI models to use. All other files import settings from HERE,
#   so if you need to change anything, you only change ONE file.
#
# SECURITY:
#   - API key lives in .env (never committed to GitHub)
#   - config.py reads it at startup and validates it exists
#   - If key is missing, app crashes immediately with a clear error
#     (better than crashing mid-evaluation with a confusing error)
# ──────────────────────────────────────────────────────────────────────────────

import os
from dotenv import load_dotenv

# ── Load .env file ───────────────────────────────────────────────────────────
# load_dotenv() searches for a .env file in the current directory (and parents)
# and loads all KEY=VALUE pairs into the environment.
#
# Example .env file:
#   OPENROUTER_API_KEY=sk-or-v1-your-key-here
#
# After load_dotenv(), you can access it with os.getenv("OPENROUTER_API_KEY")
# ─────────────────────────────────────────────────────────────────────────────
load_dotenv()

# ── API Key ──────────────────────────────────────────────────────────────────
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError(
        "\n"
        "╔══════════════════════════════════════════════════════════════╗\n"
        "║  ERROR: OPENROUTER_API_KEY not found!                      ║\n"
        "║                                                            ║\n"
        "║  Steps to fix:                                             ║\n"
        "║  1. Go to https://openrouter.ai/keys                      ║\n"
        "║  2. Create a free API key                                  ║\n"
        "║  3. Create a .env file in the project root                 ║\n"
        "║  4. Add: OPENROUTER_API_KEY=sk-or-v1-your-key-here        ║\n"
        "╚══════════════════════════════════════════════════════════════╝\n"
    )

# ── Model Configuration ─────────────────────────────────────────────────────
#
# WHY TWO MODELS?
#   Free-tier AI models sometimes fail (rate limits, server overload, etc.)
#   Having a fallback model means our app stays working even when the
#   primary model is down. This is called "resilience" in production systems.
#
# WHY THESE SPECIFIC MODELS?
#
#   PRIMARY: Google Gemma-3-27B
#     - Strong reasoning and instruction following
#     - Good at structured JSON output
#     - Free on OpenRouter
#
#   FALLBACK: Llama-3.3-70B-Instruct
#     - Fast and reliable
#     - Good JSON compliance
#     - Largest free model available — great backup
#
# Note: Model availability on free tier changes over time.
# Run this to check current free models:
#   python -c "import requests; r=requests.get('https://openrouter.ai/api/v1/models'); [print(m['id']) for m in r.json()['data'] if ':free' in m['id']]"
#
# ─────────────────────────────────────────────────────────────────────────────
PRIMARY_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"
FALLBACK_MODEL = "openrouter/auto"

# ── OpenRouter API Settings ─────────────────────────────────────────────────
#
# OpenRouter uses the same API format as OpenAI (chat completions),
# but with a different base URL and some extra required headers.
#
# REQUIRED HEADERS FOR FREE TIER:
#   HTTP-Referer: Where your app is hosted (OpenRouter tracks this)
#   X-Title:      Your app name (shows in your OpenRouter dashboard)
#
# Without these headers, free-tier requests will be rejected.
# ─────────────────────────────────────────────────────────────────────────────
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

OPENROUTER_HEADERS = {
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    "Content-Type": "application/json",
    "HTTP-Referer": "http://localhost:8501",     # Streamlit default port
    "X-Title": "Mini Answer Evaluator",          # Shows in OpenRouter dashboard
}

# ── Evaluation Settings ─────────────────────────────────────────────────────
#
# TEMPERATURE: Controls how "creative" the AI is.
#   0.0 = completely deterministic (same input → same output every time)
#   1.0 = very creative/random (same input → different output each time)
#   0.1 = almost deterministic but with tiny variation
#
#   WHY 0.1?
#   For grading, we want CONSISTENCY. The same answer should always get
#   the same marks. Temperature 0.1 gives us that while allowing the
#   AI slight flexibility in how it phrases its feedback.
#
# MAX_TOKENS: Maximum length of AI's response.
#   Our JSON response is typically 300-800 tokens.
#   1200 gives plenty of room for detailed criterion breakdowns.
#   600 is enough for the simpler "without rubric" evaluation.
#
# REQUEST_TIMEOUT: How long to wait for AI response (seconds).
#   Free-tier models can be slow during peak hours.
#   60 seconds is generous but prevents infinite hangs.
#
# ─────────────────────────────────────────────────────────────────────────────
LLM_TEMPERATURE = 0.1
MAX_TOKENS_WITH_RUBRIC = 1200
MAX_TOKENS_WITHOUT_RUBRIC = 600
REQUEST_TIMEOUT = 60
