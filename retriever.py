# retriever.py
# ──────────────────────────────────────────────────────────────────────────────
# 🔍 RUBRIC RETRIEVER — Finds the Right Rubric for Any Question
# ──────────────────────────────────────────────────────────────────────────────
#
# WHAT DOES THIS DO?
#   Takes a question like "Define Newton's Second Law" and searches through
#   all 13 rubrics to find the best matching one (physics_definition).
#
# HOW?
#   1. Clean the question text (lowercase, remove punctuation)
#   2. Split into individual words (tokens)
#   3. For each rubric, count how many of its keywords appear in the question
#   4. The rubric with the highest count wins
#   5. If no rubric scores above threshold → use fallback_generic
#
# WHY KEYWORD MATCHING (not AI/embeddings)?
#   - The JD says: "You can use simple keyword matching (no embeddings required)"
#   - It's fast, predictable, and easy to debug
#   - For 13 rubrics, keyword matching works perfectly well
# ──────────────────────────────────────────────────────────────────────────────

import re
from typing import Tuple
from rubric_store import RUBRICS


# Common words that appear in many questions but don't indicate subject.
# Without filtering these, "What is the capital of France" would match
# physics_numerical because "what", "is", "the" appear in its keywords.
STOP_WORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "in", "on", "at", "to", "for", "of", "with", "by", "from", "and",
    "or", "not", "it", "its", "this", "that", "these", "those",
    "do", "does", "did", "has", "have", "had", "can", "will", "shall",
    "may", "would", "could", "should", "about", "into", "also", "your",
    "what", "how", "when", "where", "who", "why",  # question words
}


def normalize(text: str) -> set:
    """
    Clean and tokenize text for matching.

    Steps:
      1. Convert to lowercase    → "Define Newton's" → "define newton's"
      2. Remove punctuation       → "define newtons"
      3. Split into word set      → {"define", "newtons"}
      4. Remove stop words        → {"define", "newtons"} (no change here)

    Returns a SET (not list) because we only care about unique words,
    and set intersection is very fast in Python.

    Example:
      normalize("What is the capital of France?")
      → {"capital", "france"}  (stop words removed)
    """
    cleaned = re.sub(r"[^\w\s]", "", text.lower())
    tokens = set(cleaned.split())
    return tokens - STOP_WORDS


def score_rubric(rubric: dict, question_tokens: set) -> int:
    """
    Score how well a rubric matches the question.

    Method: Count how many rubric keywords appear in the question.
    This is called "set intersection" — finding common elements.

    Example:
      question_tokens = {"define", "newtons", "second", "law"}
      rubric keywords = {"define", "newton", "force", "acceleration", ...}
      intersection    = {"define"}  (1 match — but "newton" ≠ "newtons")

    Note: We also normalize the keywords themselves, so multi-word keywords
    like "what is" get split into {"what", "is"} for better matching.

    Returns: integer count of matching keywords (higher = better match)
    """
    # Normalize all rubric keywords into a single token set
    keyword_tokens = normalize(" ".join(rubric["keywords"]))

    # Count common words between question and rubric keywords
    # The & operator on sets = intersection (common elements)
    return len(question_tokens & keyword_tokens)


def retrieve_rubric(question: str) -> Tuple[dict, int]:
    """
    Main function — finds the best rubric for a given question.

    Args:
      question: The exam question text (e.g., "Define Newton's Second Law")

    Returns:
      Tuple of (best_rubric_dict, match_score)
      - best_rubric: The rubric dictionary with id, criteria, etc.
      - match_score: How many keywords matched (0 = fallback was used)

    Algorithm:
      1. Tokenize the question
      2. Score every rubric (except fallback) against the question
      3. Pick the highest-scoring rubric
      4. If best score < MATCH_THRESHOLD → return fallback instead

    Why skip fallback during scoring?
      Fallback has empty keywords, so it would always score 0.
      We only use it as a safety net when nothing else matches.
    """
    # Step 1: Convert question to a set of lowercase tokens
    question_tokens = normalize(question)

    best_rubric = None
    best_score = 0

    # Step 2: Score each rubric (skip the fallback)
    for rubric in RUBRICS:
        if rubric["id"] == "fallback_generic":
            continue  # Don't score fallback — it's our safety net

        score = score_rubric(rubric, question_tokens)

        if score > best_score:
            best_score = score
            best_rubric = rubric

    # Step 3: Apply threshold — minimum score needed to trust the match
    #
    # MATCH_THRESHOLD = 1 means at least 1 keyword must match.
    # After stop word filtering, this is reliable — only subject-specific
    # words contribute to the score.
    #
    # Example: "What is the capital of France?" 
    #   → after stop word removal: {"capital", "france"}
    #   → no rubric matches → fallback triggers correctly
    #
    MATCH_THRESHOLD = 1

    if best_score < MATCH_THRESHOLD or best_rubric is None:
        # No good match found — use the generic fallback rubric
        fallback = next(r for r in RUBRICS if r["id"] == "fallback_generic")
        return fallback, 0

    return best_rubric, best_score
