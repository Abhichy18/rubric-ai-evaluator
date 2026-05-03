# app.py
# Streamlit UI for RubricAI — AI Answer Evaluator
# Clean, professional interface with rubric display, score visualization,
# per-criterion breakdown, and optional comparison mode.

import streamlit as st
from evaluator import evaluate, evaluate_without_rubric
from retriever import retrieve_rubric
from rubric_store import RUBRICS

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="RubricAI — AI Answer Evaluator",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS for polished look ─────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
    /* ═══════════════════════════════════════════════════════════════════════
       GLOBAL — Font, scrollbar, body
       ═══════════════════════════════════════════════════════════════════════ */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .block-container { max-width: 860px; padding-top: 1.8rem; }

    /* Custom scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(14,165,233,0.3);
        border-radius: 3px;
    }
    ::-webkit-scrollbar-thumb:hover { background: rgba(14,165,233,0.5); }

    /* Hide Streamlit branding */
    #MainMenu, footer, header { visibility: hidden; }

    /* ═══════════════════════════════════════════════════════════════════════
       HEADER — Animated gradient with glow
       ═══════════════════════════════════════════════════════════════════════ */
    @keyframes headerShift {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .main-header {
        background: linear-gradient(135deg, #0f172a, #134e4a, #164e63, #0f172a);
        background-size: 300% 300%;
        animation: headerShift 8s ease infinite;
        padding: 2.5rem 2.8rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        color: white !important;
        box-shadow: 0 12px 40px rgba(14,165,233,0.15),
                    0 4px 12px rgba(13,148,136,0.1);
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
        animation: headerShift 6s ease infinite reverse;
    }
    .main-header h1 {
        margin: 0; font-size: 2.2rem; font-weight: 800;
        color: white !important;
        letter-spacing: -0.02em;
        position: relative;
    }
    .main-header p {
        margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 0.95rem;
        color: white !important;
        letter-spacing: 0.01em;
        position: relative;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       TEXTAREAS — Glowing focus, custom border
       ═══════════════════════════════════════════════════════════════════════ */
    .stTextArea textarea {
        border: 1px solid rgba(128,128,128,0.2) !important;
        border-radius: 12px !important;
        transition: all 0.3s ease !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.92rem !important;
        line-height: 1.6 !important;
    }
    .stTextArea textarea:focus {
        border-color: #0ea5e9 !important;
        box-shadow: 0 0 0 3px rgba(14,165,233,0.15),
                    0 4px 16px rgba(14,165,233,0.1) !important;
    }
    .stTextArea label {
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        letter-spacing: 0.02em !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       EVALUATE BUTTON — Gradient with hover animation
       ═══════════════════════════════════════════════════════════════════════ */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0ea5e9, #0d9488) !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        letter-spacing: 0.03em !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(14,165,233,0.3) !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(14,165,233,0.4) !important;
    }
    .stButton > button[kind="primary"]:active {
        transform: translateY(0) !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       SCORE CONTAINER — Glassmorphism with radial glow
       ═══════════════════════════════════════════════════════════════════════ */
    .score-container {
        text-align: center;
        padding: 1.8rem 1.5rem;
        border-radius: 18px;
        border: 1px solid rgba(128,128,128,0.15);
        background: rgba(128,128,128,0.04);
        backdrop-filter: blur(12px);
        position: relative;
        overflow: hidden;
    }
    .score-container::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background: radial-gradient(circle, rgba(14,165,233,0.12) 0%, transparent 70%);
        pointer-events: none;
    }
    .score-big {
        font-size: 3.8rem;
        font-weight: 900;
        line-height: 1;
        position: relative;
        z-index: 1;
    }
    .score-max {
        font-size: 1.4rem;
        opacity: 0.5;
        font-weight: 500;
        position: relative;
        z-index: 1;
    }
    .score-pct {
        font-size: 1.05rem;
        font-weight: 700;
        margin-top: 0.3rem;
        position: relative;
        z-index: 1;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       PROGRESS BAR — Custom gradient
       ═══════════════════════════════════════════════════════════════════════ */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #0ea5e9, #14b8a6) !important;
        border-radius: 8px !important;
    }
    .stProgress > div > div > div {
        border-radius: 8px !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       CRITERION CARDS — Glassmorphism with colored left accents
       ═══════════════════════════════════════════════════════════════════════ */
    .criterion-card {
        border: 1px solid rgba(128,128,128,0.12);
        border-radius: 14px;
        padding: 1.1rem 1.4rem;
        margin-bottom: 0.65rem;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        background: rgba(128,128,128,0.03);
        backdrop-filter: blur(8px);
    }
    .criterion-card:hover {
        background: rgba(14,165,233,0.05);
        transform: translateX(6px);
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    }
    .criterion-card .criterion-name {
        font-weight: 700;
        font-size: 0.92rem;
        color: inherit;
        letter-spacing: -0.01em;
    }
    .criterion-card .criterion-reason {
        opacity: 0.72;
        font-size: 0.84rem;
        margin-top: 0.45rem;
        line-height: 1.6;
        color: inherit;
    }
    .criterion-card-full {
        border-left: 4px solid #22c55e;
        box-shadow: inset 4px 0 12px -4px rgba(34,197,94,0.15);
    }
    .criterion-card-partial {
        border-left: 4px solid #eab308;
        box-shadow: inset 4px 0 12px -4px rgba(234,179,8,0.15);
    }
    .criterion-card-zero {
        border-left: 4px solid #ef4444;
        box-shadow: inset 4px 0 12px -4px rgba(239,68,68,0.15);
    }

    /* ═══════════════════════════════════════════════════════════════════════
       FEEDBACK BOX — Accent border with subtle glow
       ═══════════════════════════════════════════════════════════════════════ */
    .feedback-box {
        border-radius: 14px;
        padding: 1.3rem 1.6rem;
        margin: 1rem 0;
        font-size: 0.9rem;
        line-height: 1.75;
        border-left: 4px solid #0ea5e9;
        background: rgba(14,165,233,0.06);
        box-shadow: inset 4px 0 16px -4px rgba(14,165,233,0.12);
        color: inherit;
    }
    .feedback-box strong { color: #38bdf8; }

    /* ═══════════════════════════════════════════════════════════════════════
       EXPANDER — Custom styling
       ═══════════════════════════════════════════════════════════════════════ */
    .streamlit-expanderHeader {
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        border-radius: 12px !important;
    }
    details[data-testid="stExpander"] {
        border: 1px solid rgba(128,128,128,0.12) !important;
        border-radius: 14px !important;
        overflow: hidden;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       COMPARISON CARDS — Glow borders
       ═══════════════════════════════════════════════════════════════════════ */
    .compare-card {
        border-radius: 16px;
        padding: 1.6rem;
        text-align: center;
        transition: all 0.3s ease;
        backdrop-filter: blur(8px);
    }
    .compare-card:hover {
        transform: translateY(-3px);
    }
    .compare-with {
        background: rgba(34,197,94,0.06);
        border: 2px solid rgba(34,197,94,0.3);
        box-shadow: 0 4px 20px rgba(34,197,94,0.08);
    }
    .compare-with:hover {
        box-shadow: 0 8px 30px rgba(34,197,94,0.15);
    }
    .compare-without {
        background: rgba(239,68,68,0.06);
        border: 2px solid rgba(239,68,68,0.3);
        box-shadow: 0 4px 20px rgba(239,68,68,0.08);
    }
    .compare-without:hover {
        box-shadow: 0 8px 30px rgba(239,68,68,0.15);
    }
    .compare-label-with {
        color: #4ade80;
        font-weight: 800;
        font-size: 0.82rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .compare-label-without {
        color: #f87171;
        font-weight: 800;
        font-size: 0.82rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .compare-score-with {
        color: #22c55e;
        font-size: 3rem;
        font-weight: 900;
        text-shadow: 0 0 30px rgba(34,197,94,0.2);
    }
    .compare-score-without {
        color: #ef4444;
        font-size: 3rem;
        font-weight: 900;
        text-shadow: 0 0 30px rgba(239,68,68,0.2);
    }
    .compare-feedback {
        opacity: 0.75;
        font-size: 0.82rem;
        margin-top: 0.85rem;
        text-align: left;
        line-height: 1.6;
        color: inherit;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       BADGES — Pill style with subtle glow
       ═══════════════════════════════════════════════════════════════════════ */
    .match-badge {
        display: inline-block;
        padding: 0.35rem 0.9rem;
        border-radius: 999px;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }
    .badge-strong {
        background: rgba(34,197,94,0.12);
        color: #22c55e;
        border: 1px solid rgba(34,197,94,0.25);
        box-shadow: 0 0 12px rgba(34,197,94,0.1);
    }
    .badge-partial {
        background: rgba(234,179,8,0.12);
        color: #eab308;
        border: 1px solid rgba(234,179,8,0.25);
        box-shadow: 0 0 12px rgba(234,179,8,0.1);
    }
    .badge-fallback {
        background: rgba(156,163,175,0.12);
        color: inherit;
        opacity: 0.65;
        border: 1px solid rgba(156,163,175,0.25);
    }

    /* ═══════════════════════════════════════════════════════════════════════
       MODEL TAG — Monospace pill
       ═══════════════════════════════════════════════════════════════════════ */
    .model-tag {
        display: inline-block;
        background: rgba(14,165,233,0.08);
        border: 1px solid rgba(14,165,233,0.2);
        padding: 0.25rem 0.7rem;
        border-radius: 8px;
        font-size: 0.74rem;
        font-family: 'Courier New', monospace;
        color: #38bdf8;
        font-weight: 600;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       DIVIDER — Gradient fade line
       ═══════════════════════════════════════════════════════════════════════ */
    .section-divider {
        height: 1px;
        background: linear-gradient(to right, transparent, rgba(14,165,233,0.15), transparent);
        margin: 1.8rem 0;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       CHECKBOX — Custom accent
       ═══════════════════════════════════════════════════════════════════════ */
    .stCheckbox label span {
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       SIDEBAR — Subtle styling
       ═══════════════════════════════════════════════════════════════════════ */
    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(128,128,128,0.1) !important;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       SPINNER — Override default color
       ═══════════════════════════════════════════════════════════════════════ */
    .stSpinner > div > div {
        border-top-color: #0ea5e9 !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       SECTION HEADINGS — Tighter tracking
       ═══════════════════════════════════════════════════════════════════════ */
    h3 {
        letter-spacing: -0.02em !important;
        font-weight: 700 !important;
    }
    h4 {
        letter-spacing: -0.01em !important;
        font-weight: 700 !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       ALERTS (st.success, st.warning, st.info) — Rounded
       ═══════════════════════════════════════════════════════════════════════ */
    .stAlert {
        border-radius: 12px !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       CAPTION TEXT — Slightly larger
       ═══════════════════════════════════════════════════════════════════════ */
    .stCaption, small {
        font-size: 0.82rem !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       CODE BLOCKS (sample questions) — Styled
       ═══════════════════════════════════════════════════════════════════════ */
    code {
        border-radius: 8px !important;
        font-size: 0.82rem !important;
        padding: 0.5rem 0.8rem !important;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       HOW-TO-USE CARDS — Premium icon cards
       ═══════════════════════════════════════════════════════════════════════ */
    .howto-card {
        border: 1px solid rgba(128,128,128,0.12);
        border-radius: 16px;
        padding: 1.6rem 1.2rem;
        text-align: center;
        background: rgba(128,128,128,0.03);
        backdrop-filter: blur(8px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        height: 100%;
    }
    .howto-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(14,165,233,0.12);
        border-color: rgba(14,165,233,0.3);
    }
    .howto-icon {
        width: 52px;
        height: 52px;
        border-radius: 14px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        margin-bottom: 0.8rem;
    }
    .howto-icon-1 {
        background: linear-gradient(135deg, rgba(14,165,233,0.15), rgba(6,182,212,0.15));
        box-shadow: 0 4px 12px rgba(14,165,233,0.1);
    }
    .howto-icon-2 {
        background: linear-gradient(135deg, rgba(34,197,94,0.15), rgba(16,185,129,0.15));
        box-shadow: 0 4px 12px rgba(34,197,94,0.1);
    }
    .howto-icon-3 {
        background: linear-gradient(135deg, rgba(245,158,11,0.15), rgba(234,179,8,0.15));
        box-shadow: 0 4px 12px rgba(245,158,11,0.1);
    }
    .howto-title {
        font-weight: 700;
        font-size: 0.95rem;
        margin-bottom: 0.4rem;
        color: inherit;
    }
    .howto-desc {
        font-size: 0.82rem;
        opacity: 0.65;
        line-height: 1.5;
        color: inherit;
    }

    /* ═══════════════════════════════════════════════════════════════════════
       SAMPLE QUESTION CARDS — Subject-colored
       ═══════════════════════════════════════════════════════════════════════ */
    .sample-card {
        border: 1px solid rgba(128,128,128,0.1);
        border-radius: 12px;
        padding: 0.85rem 1.1rem;
        margin-bottom: 0.5rem;
        transition: all 0.2s ease;
        background: rgba(128,128,128,0.02);
        display: flex;
        align-items: center;
        gap: 0.75rem;
        cursor: default;
    }
    .sample-card:hover {
        background: rgba(14,165,233,0.04);
        transform: translateX(4px);
        border-color: rgba(14,165,233,0.2);
    }
    .sample-icon {
        font-size: 1.2rem;
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .sample-icon-physics { background: rgba(99,102,241,0.12); }
    .sample-icon-math { background: rgba(234,179,8,0.12); }
    .sample-icon-english { background: rgba(34,197,94,0.12); }
    .sample-icon-chemistry { background: rgba(239,68,68,0.12); }
    .sample-icon-biology { background: rgba(16,185,129,0.12); }
    .sample-subject {
        font-weight: 700;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        opacity: 0.6;
    }
    .sample-question {
        font-size: 0.88rem;
        color: inherit;
        font-weight: 500;
    }

</style>
""", unsafe_allow_html=True)


# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🎯 Rubric-Grounded AI Answer Evaluation System</h1>
    <p style="opacity: 0.8; font-size: 0.9rem; margin-top: 0.6rem; font-style: italic;">
        " Because every answer deserves fair, consistent, and transparent grading. "
    </p>
</div>
""", unsafe_allow_html=True)


# ── Sidebar: Available Rubrics ───────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📚 Available Rubrics")
    st.caption("These rubrics are automatically matched to your question")
    for r in RUBRICS:
        icon = {
            "physics": "🔬", "mathematics": "📐", "english": "📝",
            "chemistry": "🧪", "biology": "🧬", "social_science": "📜",
            "general": "🔄"
        }.get(r["subject"], "📋")
        st.markdown(f"**{icon} {r['id']}** — {r['subject']} / {r['question_type']}")
    st.markdown("---")
    st.caption("RubricAI · Built for Evalvia AI Internship")


# ── Input Form ───────────────────────────────────────────────────────────────
st.markdown("### 📝 Enter Evaluation Details")

question = st.text_area(
    "Question",
    placeholder="e.g., Define Newton's Second Law of Motion.",
    height=100,
    help="The exam question to evaluate the answer against",
)

answer = st.text_area(
    "Student's Answer",
    placeholder="Enter the student's written answer here...",
    height=180,
    help="The student's response to be evaluated",
)

# Word count
if answer.strip():
    word_count = len(answer.strip().split())
    st.caption(f"📊 Word count: **{word_count}** words")

# Model selection toggle
deep_reasoning_mode = st.toggle(
    "🧠 Enable Deep Reasoning Mode",
    value=False,
    help="Switches from the ultra-fast Llama 3.3 70B to the powerful but slower DeepSeek V4 Pro model for highly complex evaluations."
)

# Compare mode toggle
compare_mode = st.checkbox(
    "⚖️ Enable comparison mode (with rubric vs without rubric)",
    help="Runs two evaluations — one using the matched rubric and one without any rubric. "
         "This demonstrates why rubric-grounded evaluation produces more consistent results.",
)

# Evaluate button
evaluate_btn = st.button(
    "🔍 Evaluate Answer",
    type="primary",
    use_container_width=True,
    disabled=not (question.strip() and answer.strip()),
)


# ── Evaluation Logic ─────────────────────────────────────────────────────────
if evaluate_btn and question.strip() and answer.strip():

    # Show rubric preview first
    rubric, match_score = retrieve_rubric(question)

    # ── Rubric Display ───────────────────────────────────────────────────
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("### 📖 Retrieved Rubric")

    # Match quality badge
    if match_score >= 3:
        badge_class, badge_text = "badge-strong", f"✅ Strong match (score: {match_score})"
    elif match_score >= 1:
        badge_class, badge_text = "badge-partial", f"⚠️ Partial match (score: {match_score})"
    else:
        badge_class, badge_text = "badge-fallback", "🔄 Using fallback rubric"

    col_info, col_badge = st.columns([3, 2])
    with col_info:
        st.markdown(
            f"**Subject:** {rubric['subject'].title()} · "
            f"**Type:** {rubric['question_type'].replace('_', ' ').title()} · "
            f"**ID:** `{rubric['id']}`"
        )
    with col_badge:
        st.markdown(
            f'<span class="match-badge {badge_class}">{badge_text}</span>',
            unsafe_allow_html=True,
        )

    # Show criteria table
    for c in rubric["criteria"]:
        col_name, col_marks = st.columns([4, 1])
        with col_name:
            st.markdown(f"&nbsp;&nbsp;• {c['name']}")
        with col_marks:
            st.markdown(f"**{c['marks']}** {'mark' if c['marks'] == 1 else 'marks'}")
    st.caption(f"**Total: {rubric['max_marks']} marks**")

    # ── Run Evaluation ───────────────────────────────────────────────────
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    with st.spinner("🧠 AI is evaluating the answer... Please wait."):
        try:
            result = evaluate(question, answer, use_deep_reasoning=deep_reasoning_mode)
        except Exception as e:
            st.error(f"❌ Evaluation failed: {str(e)}")
            st.info("💡 **Tip:** Free-tier models can be busy. Wait a minute and try again.")
            st.stop()

    # ── Score Display ────────────────────────────────────────────────────
    st.markdown("### 📊 Evaluation Result")

    marks = result["marks_awarded"]
    max_m = result["max_marks"]
    pct = round((marks / max_m) * 100) if max_m > 0 else 0

    # Color based on score
    if pct >= 80:
        score_color, score_emoji = "#16a34a", "🟢"
    elif pct >= 50:
        score_color, score_emoji = "#ca8a04", "🟡"
    else:
        score_color, score_emoji = "#dc2626", "🔴"

    # Score + model info
    col_score, col_meta = st.columns([1, 2])

    with col_score:
        st.markdown(f"""
        <div class="score-container">
            <div class="score-big" style="color: {score_color};">{marks}</div>
            <div class="score-max">/ {max_m}</div>
            <div class="score-pct" style="color: {score_color};">{score_emoji} {pct}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col_meta:
        # Progress bar
        st.progress(pct / 100)

        # Model used — clean display name
        model_name = result.get("model_used", "unknown")
        short_model = model_name.split("/")[-1].replace(":free", "") if "/" in model_name else model_name
        # Truncate very long model names for cleaner display
        if len(short_model) > 22:
            short_model = short_model[:20] + "…"
        st.markdown(f'**Model:** <span class="model-tag">{short_model}</span>', unsafe_allow_html=True)

        # Quick stats — styled inline
        st.markdown(f'**Rubric:** <span class="model-tag">{result["rubric_used"]}</span>', unsafe_allow_html=True)
        st.markdown(f"**Match score:** {result['match_score']}")

    # ── Feedback & Justification ─────────────────────────────────────────
    st.markdown(f"""
    <div class="feedback-box">
        <strong>💬 Feedback</strong><br/>
        {result.get('feedback', 'No feedback provided.')}
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📋 Detailed Justification", expanded=False):
        st.markdown(result.get("justification", "No justification provided."))

    # ── Criterion Breakdown ──────────────────────────────────────────────
    st.markdown("#### 📐 Criterion Breakdown")

    for c in result.get("criterion_breakdown", []):
        c_marks = c["marks_awarded"]
        c_max = c["max_marks"]
        c_pct = (c_marks / c_max * 100) if c_max > 0 else 0

        # Status icon
        if c_pct == 100:
            icon = "✅"
        elif c_pct > 0:
            icon = "⚠️"
        else:
            icon = "❌"

        # Color for marks
        if c_pct >= 80:
            m_color = "#16a34a"
        elif c_pct >= 50:
            m_color = "#ca8a04"
        else:
            m_color = "#dc2626"

        # Pick card border class based on score
        if c_pct == 100:
            card_class = "criterion-card-full"
        elif c_pct > 0:
            card_class = "criterion-card-partial"
        else:
            card_class = "criterion-card-zero"

        st.markdown(f"""
        <div class="criterion-card {card_class}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span class="criterion-name">{icon} {c['criterion']}</span>
                <span style="color: {m_color}; font-weight: 700; font-size: 1.05rem;">
                    {c_marks}/{c_max}
                </span>
            </div>
            <div class="criterion-reason">
                {c.get('reason', '')}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Comparison Mode ──────────────────────────────────────────────────
    if compare_mode:
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("### ⚖️ Rubric vs No Rubric Comparison")
        st.caption("Demonstrates why rubric-grounded evaluation produces more consistent and fair results")

        with st.spinner("🔄 Running evaluation without rubric for comparison..."):
            try:
                result_no_rubric = evaluate_without_rubric(question, answer, use_deep_reasoning=deep_reasoning_mode)
            except Exception as e:
                st.warning(f"Comparison evaluation failed: {e}")
                result_no_rubric = None

        if result_no_rubric:
            with_marks = result["marks_awarded"]
            without_marks = result_no_rubric.get("marks_awarded", 0)
            diff = with_marks - without_marks

            col_with, col_without = st.columns(2)

            with col_with:
                st.markdown(f"""
                <div class="compare-card compare-with">
                    <div class="compare-label-with">✅ WITH RUBRIC</div>
                    <div class="compare-score-with">
                        {with_marks}<span style="font-size: 1rem; color: #9ca3af;"> / {max_m}</span>
                    </div>
                    <div class="compare-feedback">
                        {result.get('feedback', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with col_without:
                st.markdown(f"""
                <div class="compare-card compare-without">
                    <div class="compare-label-without">❌ WITHOUT RUBRIC</div>
                    <div class="compare-score-without">
                        {without_marks}<span style="font-size: 1rem; color: #9ca3af;"> / 5</span>
                    </div>
                    <div class="compare-feedback">
                        {result_no_rubric.get('feedback', '')}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Difference insight
            if diff > 0:
                st.success(
                    f"📈 Rubric awarded **{diff} more mark{'s' if diff > 1 else ''}** — "
                    f"rubric-grounded evaluation rewards structured, complete answers."
                )
            elif diff < 0:
                st.warning(
                    f"📉 Without rubric awarded **{abs(diff)} more mark{'s' if abs(diff) > 1 else ''}** — "
                    f"the evaluator was more lenient without constraints."
                )
            else:
                st.info("📊 Both evaluations gave the same score — the rubric validated the AI's judgment.")


# ── Empty state ──────────────────────────────────────────────────────────────
elif not evaluate_btn:
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("#### 💡 How to use")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="howto-card">
            <div class="howto-icon howto-icon-1">📝</div>
            <div class="howto-title">Enter Question</div>
            <div class="howto-desc">Any subject — Physics, Math, English, Chemistry, Biology</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="howto-card">
            <div class="howto-icon howto-icon-2">✍️</div>
            <div class="howto-title">Paste Answer</div>
            <div class="howto-desc">Enter the student's written response to be evaluated</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="howto-card">
            <div class="howto-icon howto-icon-3">📊</div>
            <div class="howto-title">Get Results</div>
            <div class="howto-desc">AI grades with CBSE rubrics & per-criterion breakdown</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # Sample questions for quick testing
    st.markdown("#### 🧪 Try These Examples")

    samples = [
        ("🔬", "Physics",    "physics",    "Define Newton's Second Law of Motion."),
        ("📐", "Math",       "math",       "Solve: x² − 5x + 6 = 0"),
        ("📝", "English",    "english",    "Write an essay on climate change."),
        ("🧪", "Chemistry",  "chemistry",  "Balance the equation: H₂ + O₂ → H₂O"),
        ("🧬", "Biology",    "biology",    "Explain the process of photosynthesis."),
    ]
    for icon, subj, cls, sample_q in samples:
        st.markdown(f"""
        <div class="sample-card">
            <div class="sample-icon sample-icon-{cls}">{icon}</div>
            <div>
                <div class="sample-subject">{subj}</div>
                <div class="sample-question">{sample_q}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
