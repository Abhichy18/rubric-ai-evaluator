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

# ── Load .env file (for local development) ───────────────────────────────────
load_dotenv()

# ── API Key ──────────────────────────────────────────────────────────────────
# Try .env first (local), then st.secrets (Streamlit Cloud)
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

if not NVIDIA_API_KEY:
    try:
        import streamlit as st
        NVIDIA_API_KEY = st.secrets.get("NVIDIA_API_KEY")
    except Exception:
        pass

if not NVIDIA_API_KEY:
    raise ValueError(
        "\n"
        "╔══════════════════════════════════════════════════════════════╗\n"
        "║  ERROR: NVIDIA_API_KEY not found!                            ║\n"
        "║                                                            ║\n"
        "║  For local: Create a .env file with your key               ║\n"
        "║  For cloud: Add key in Streamlit secrets                   ║\n"
        "╚══════════════════════════════════════════════════════════════╝\n"
    )

# ── Model Configuration ─────────────────────────────────────────────────────
#
# WHY TWO MODELS?
#   If the primary model is down, the fallback model keeps the app working.
#
# WHY THESE SPECIFIC MODELS?
#
#   FAST_MODEL: meta/llama-3.3-70b-instruct
#     - Fast and reliable
#     - Great general-purpose reasoning model
#
#   REASONING_MODEL: deepseek-ai/deepseek-v4-pro
#     - Very strong reasoning and instruction following
#     - Slower, but better for complex tasks
#
# ─────────────────────────────────────────────────────────────────────────────
FAST_MODEL = "meta/llama-3.3-70b-instruct"
REASONING_MODEL = "deepseek-ai/deepseek-v4-pro"

# ── NVIDIA NIM API Settings ─────────────────────────────────────────────────
#
# NVIDIA NIM uses the same API format as OpenAI (chat completions).
# ─────────────────────────────────────────────────────────────────────────────
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

NVIDIA_HEADERS = {
    "Authorization": f"Bearer {NVIDIA_API_KEY}",
    "Content-Type": "application/json",
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
