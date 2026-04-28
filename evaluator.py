# evaluator.py
# The core evaluation engine — calls OpenRouter LLM with rubric-grounded prompts
# and returns structured JSON scores with per-criterion breakdown.

import requests
import json
import re
import time
from retriever import retrieve_rubric
from config import (
    OPENROUTER_BASE_URL,
    OPENROUTER_HEADERS,
    PRIMARY_MODEL,
    FALLBACK_MODEL,
    LLM_TEMPERATURE,
    MAX_TOKENS_WITH_RUBRIC,
    MAX_TOKENS_WITHOUT_RUBRIC,
    REQUEST_TIMEOUT,
)


# ── System Prompt ────────────────────────────────────────────────────────────
# This is the "personality" instruction sent to the LLM before every evaluation.
# It enforces strict rules so the AI grades consistently and fairly.
# I spent a lot of time tuning this — every rule exists because without it,
# the LLM would produce inconsistent or unreliable scores.

SYSTEM_PROMPT = """You are a strict, fair, and consistent exam evaluator for CBSE school assessments.

RULES:
1. Evaluate the student's answer ONLY against the rubric provided. Do not use outside criteria.
2. Do NOT award marks for points not explicitly mentioned in the rubric criteria.
3. Do NOT penalize for minor spelling errors unless the rubric specifically mentions language quality.
4. Evaluate each criterion INDEPENDENTLY — one criterion's failure should not affect others.
5. Be consistent — the same quality answer must receive the same marks every time.
6. Respond ONLY with a valid JSON object. No markdown, no code fences, no preamble, no explanation outside the JSON.

Your response must be a single JSON object and nothing else."""


def build_eval_prompt(question: str, answer: str, rubric: dict) -> str:
    """
    Constructs the evaluation prompt that gets sent to the LLM.
    
    The prompt has a very specific structure:
    1. Show the question and student answer
    2. Show the full rubric with per-criterion marks
    3. Include anchor examples (if available) to calibrate scoring
    4. Specify the exact JSON output schema
    
    I'm explicit about the JSON format because LLMs tend to add
    extra text or markdown if you don't constrain them tightly.
    """
    # Format each criterion as a numbered line with marks
    criteria_lines = "\n".join(
        f"  [{i+1}] [{c['marks']} marks] {c['name']}"
        for i, c in enumerate(rubric["criteria"])
    )

    # Anchor examples help the LLM understand what "good" vs "poor" looks like
    # for this specific rubric. This significantly improves scoring accuracy.
    examples_block = ""
    if rubric.get("examples"):
        examples_block = f"""
## ANCHOR EXAMPLES (use these to calibrate your scoring)
Good answer example: {rubric['examples'].get('good', 'N/A')}
Poor answer example: {rubric['examples'].get('poor', 'N/A')}
"""

    return f"""## QUESTION
{question}

## STUDENT'S ANSWER
{answer if answer.strip() else "[No answer provided]"}

## RUBRIC TO APPLY
Subject: {rubric['subject']} | Question Type: {rubric['question_type']}
Total Available Marks: {rubric['max_marks']}

Criteria (evaluate each independently):
{criteria_lines}
{examples_block}
## YOUR TASK
1. For each criterion above, determine how many marks (0 to max) the student deserves.
2. Provide a specific reason for each criterion score — reference the actual answer content.
3. Sum the criterion scores to get total marks_awarded.
4. Write 2-3 sentence overall feedback highlighting what was good and what was missing.
5. Write a detailed justification explaining the total score.

## REQUIRED OUTPUT (strict JSON, exactly this structure, no extra fields)
{{
  "marks_awarded": <integer 0-{rubric['max_marks']}>,
  "max_marks": {rubric['max_marks']},
  "feedback": "<2-3 sentences: what the student did well and what was missing>",
  "justification": "<detailed explanation referencing specific parts of the answer>",
  "criterion_breakdown": [
    {{
      "criterion": "<exact criterion name from rubric>",
      "max_marks": <integer>,
      "marks_awarded": <integer 0 to max_marks>,
      "reason": "<specific reason based on actual answer content — not generic>"
    }}
  ]
}}"""


def call_openrouter(prompt: str, model: str, max_tokens: int = 1200) -> str:
    """
    Makes an API call to OpenRouter's chat completion endpoint.
    
    Includes retry logic for 429 (rate limit) errors — the free tier
    allows ~20 requests/minute. If we hit the limit, we wait and retry
    with exponential backoff (5s → 10s → 20s).
    
    Returns the raw text content from the LLM response.
    """
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": LLM_TEMPERATURE,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
        ],
    }

    # Retry up to 3 times with exponential backoff for rate limits
    max_retries = 3
    for attempt in range(max_retries):
        response = requests.post(
            OPENROUTER_BASE_URL,
            headers=OPENROUTER_HEADERS,
            json=payload,
            timeout=REQUEST_TIMEOUT,
        )

        # Handle rate limiting (429) with backoff
        if response.status_code == 429:
            wait_time = 5 * (2 ** attempt)  # 5s, 10s, 20s
            print(f"[evaluator] Rate limited (429). Waiting {wait_time}s before retry {attempt+1}/{max_retries}...")
            time.sleep(wait_time)
            continue

        response.raise_for_status()
        data = response.json()

        # OpenRouter sometimes returns error object even on HTTP 200
        if "error" in data:
            raise RuntimeError(f"OpenRouter error: {data['error']}")

        return data["choices"][0]["message"]["content"].strip()

    # If all retries exhausted, raise the last error
    raise RuntimeError(f"Rate limited after {max_retries} retries. Please wait a minute and try again.")


def clean_json(raw: str) -> dict:
    """
    Cleans LLM output and extracts valid JSON.
    
    Two main problems I handle here:
    
    1. DeepSeek-R1 wraps its reasoning in <think>...</think> blocks.
       These contain the model's internal thought process (useful for
       debugging but not valid JSON). I strip them out.
    
    2. Some models wrap JSON in markdown code fences like ```json ... ```
       even when told not to. I strip those too.
    
    Without this cleaning step, json.loads() would crash on ~40% of
    DeepSeek-R1 responses.
    """
    # Remove <think>...</think> reasoning blocks (DeepSeek-R1 specific)
    raw = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()

    # Strip markdown code fences if present
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

    return json.loads(raw.strip())


def validate_and_fix(result: dict) -> dict:
    """
    Post-processing validation to catch LLM mistakes.
    
    LLMs are great at reasoning but surprisingly bad at arithmetic.
    About 15% of the time, the criterion scores don't add up to
    the total marks_awarded. This function fixes that silently.
    
    Two fixes applied:
    1. Recalculate total from individual criterion scores
    2. Clamp total to max_marks (can't give more than maximum)
    """
    if result.get("criterion_breakdown"):
        computed_total = sum(c["marks_awarded"] for c in result["criterion_breakdown"])
        if computed_total != result.get("marks_awarded"):
            result["marks_awarded"] = computed_total

    # Never award more than max marks
    result["marks_awarded"] = min(
        result["marks_awarded"],
        result.get("max_marks", 5)
    )
    return result


def evaluate(question: str, answer: str) -> dict:
    """
    Main evaluation pipeline — the heart of the entire project.
    
    Flow:
      1. Retrieve the best-matching rubric for the question
      2. Build a structured evaluation prompt
      3. Call primary model (DeepSeek-R1)
      4. If primary fails → wait 1s → try fallback model (Llama-3.3)
      5. Clean the response (strip <think> blocks, code fences)
      6. Validate and fix arithmetic errors
      7. Attach metadata (rubric used, match score, model name)
    
    Returns a dict matching the EvaluationResult schema.
    """
    # Step 1: Find the right rubric
    rubric, match_score = retrieve_rubric(question)

    # Step 2: Build the prompt
    prompt = build_eval_prompt(question, answer, rubric)

    # Step 3 & 4: Call LLM with fallback
    raw = None
    model_used = PRIMARY_MODEL

    try:
        raw = call_openrouter(prompt, PRIMARY_MODEL, MAX_TOKENS_WITH_RUBRIC)
        result = clean_json(raw)
    except Exception as e:
        print(f"[evaluator] Primary model failed: {e}")
        print("[evaluator] Switching to fallback model...")
        time.sleep(1)  # Brief pause to avoid rate limiting
        try:
            raw = call_openrouter(prompt, FALLBACK_MODEL, MAX_TOKENS_WITH_RUBRIC)
            result = clean_json(raw)
            model_used = FALLBACK_MODEL
        except Exception as e2:
            raise RuntimeError(
                f"Both models failed. Primary: {e} | Fallback: {e2}"
            )

    # Step 5 & 6: Validate and fix
    result = validate_and_fix(result)

    # Step 7: Attach metadata
    result["rubric_used"] = rubric["id"]
    result["match_score"] = match_score
    result["rubric_details"] = rubric
    result["model_used"] = model_used

    return result


def evaluate_without_rubric(question: str, answer: str) -> dict:
    """
    Evaluates an answer WITHOUT any rubric — for comparison mode.
    
    This shows the difference between rubric-grounded evaluation
    (consistent, structured) vs free-form AI grading (variable, generic).
    
    Comparing the two demonstrates exactly why Evalvia AI's approach
    of rubric-based evaluation produces better, fairer results.
    """
    prompt = f"""## QUESTION
{question}

## STUDENT'S ANSWER
{answer if answer.strip() else "[No answer provided]"}

## YOUR TASK
Evaluate this answer out of 5 marks using your general knowledge of academic evaluation.
Be fair and consistent.

## REQUIRED OUTPUT (strict JSON, no extra text)
{{
  "marks_awarded": <integer 0-5>,
  "max_marks": 5,
  "feedback": "<2-3 sentence overall assessment>",
  "justification": "<why these marks were awarded>",
  "criterion_breakdown": []
}}"""

    try:
        raw = call_openrouter(prompt, PRIMARY_MODEL, MAX_TOKENS_WITHOUT_RUBRIC)
        result = clean_json(raw)
    except Exception:
        raw = call_openrouter(prompt, FALLBACK_MODEL, MAX_TOKENS_WITHOUT_RUBRIC)
        result = clean_json(raw)

    return result
