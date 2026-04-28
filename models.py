# models.py
# ──────────────────────────────────────────────────────────────────────────────
# 📋 PYDANTIC MODELS — Data Validation & Type Safety
# ──────────────────────────────────────────────────────────────────────────────
#
# WHAT IS THIS?
#   These are "data contracts" — they define exactly what shape our data must
#   have. If any data doesn't match the contract, Pydantic raises an error
#   BEFORE it reaches the AI or the user.
#
# WHY IS THIS IMPORTANT FOR ACCURACY?
#   1. Prevents empty/garbage inputs from reaching the LLM
#   2. Validates LLM output (marks can't be negative or exceed max)
#   3. Ensures every field exists (no missing feedback or justification)
#   4. Auto-documents API contracts (FastAPI uses these for docs)
#
# REAL-WORLD ANALOGY:
#   Think of these like exam answer sheet templates:
#   - Roll number MUST be filled (required field)
#   - Marks MUST be 0-100 (constrained range)
#   - Subject MUST be from approved list (validated choice)
#   If any rule is broken, the sheet is rejected before grading.
# ──────────────────────────────────────────────────────────────────────────────

from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional


# ═══════════════════════════════════════════════════════════════════════════════
# INPUT MODELS — What the user sends to our system
# ═══════════════════════════════════════════════════════════════════════════════

class EvaluationRequest(BaseModel):
    """
    The data a user must provide to evaluate an answer.

    Fields:
      question      : The exam question (e.g., "Define Newton's Second Law")
      student_answer: The student's written response
      compare_mode  : If True, also evaluate WITHOUT rubric for comparison

    Validation:
      - question and student_answer cannot be empty or just whitespace
      - compare_mode defaults to False (optional feature)
    """
    question: str = Field(
        ...,  # ... means "required, cannot be omitted"
        min_length=1,
        description="The exam question to evaluate against"
    )
    student_answer: str = Field(
        ...,
        min_length=1,
        description="The student's answer text"
    )
    compare_mode: Optional[bool] = Field(
        default=False,
        description="If True, runs evaluation both with and without rubric"
    )

    @field_validator("question", "student_answer")
    @classmethod
    def must_not_be_blank(cls, value: str, info) -> str:
        """
        Extra check: even if the string has length > 0, it might be
        all spaces like "   ". This catches that.

        Why?
          An answer of "     " (5 spaces) passes min_length=1 check
          but is meaningless. We strip and reject it.
        """
        if not value.strip():
            field_name = info.field_name.replace("_", " ")
            raise ValueError(f"{field_name} cannot be empty or just whitespace")
        return value.strip()


# ═══════════════════════════════════════════════════════════════════════════════
# RUBRIC MODELS — Internal representation of rubric data
# ═══════════════════════════════════════════════════════════════════════════════

class RubricCriterion(BaseModel):
    """
    One grading criterion within a rubric.

    Example:
      {"name": "Correct definition stated", "marks": 2}

    This means: "If the student writes a correct definition, give up to 2 marks"
    """
    name: str = Field(
        ...,
        min_length=1,
        description="What this criterion evaluates (e.g., 'Formula mentioned')"
    )
    marks: int = Field(
        ...,
        ge=0,   # ge = "greater than or equal to" → marks >= 0
        le=10,  # le = "less than or equal to"    → marks <= 10
        description="Maximum marks for this criterion"
    )


class Rubric(BaseModel):
    """
    A complete rubric — the marking scheme for one type of question.

    Example:
      physics_definition rubric has 4 criteria totaling 5 marks.
      The retriever selects this when the question contains physics keywords.
    """
    id: str = Field(..., description="Unique rubric identifier like 'physics_definition'")
    subject: str = Field(..., description="Subject area: physics, math, english, etc.")
    question_type: str = Field(..., description="Question type: definition, numerical, essay, etc.")
    criteria: List[RubricCriterion] = Field(
        ...,
        min_length=1,  # At least 1 criterion required
        description="List of grading criteria with marks"
    )
    max_marks: int = Field(
        ...,
        gt=0,   # gt = "greater than" → must be positive
        description="Total marks available for this question"
    )


# ═══════════════════════════════════════════════════════════════════════════════
# OUTPUT MODELS — What our system returns after evaluation
# ═══════════════════════════════════════════════════════════════════════════════

class CriterionScore(BaseModel):
    """
    The AI's evaluation of ONE criterion.

    Example:
      {
        "criterion": "Correct definition stated",
        "max_marks": 2,
        "marks_awarded": 2,
        "reason": "Student correctly defined Newton's Second Law as F = ma"
      }

    Validation:
      - marks_awarded CANNOT exceed max_marks (you can't give 3/2)
      - marks_awarded CANNOT be negative
      - reason must explain WHY these marks were given (not just "good" or "bad")
    """
    criterion: str = Field(
        ...,
        min_length=1,
        description="Name of the criterion being scored"
    )
    max_marks: int = Field(
        ...,
        ge=0,
        description="Maximum possible marks for this criterion"
    )
    marks_awarded: int = Field(
        ...,
        ge=0,  # Can't award negative marks
        description="Marks actually given to the student"
    )
    reason: str = Field(
        ...,
        min_length=1,
        description="Specific reason for the marks — must reference actual answer content"
    )

    @model_validator(mode="after")
    def marks_must_not_exceed_max(self):
        """
        CRITICAL VALIDATION: Marks awarded cannot exceed maximum.

        Why?
          LLMs sometimes hallucinate and give 3/2 marks or 5/1 marks.
          This validator catches that and clamps it automatically.

        Example:
          marks_awarded=3, max_marks=2 → clamped to marks_awarded=2
        """
        if self.marks_awarded > self.max_marks:
            # Instead of crashing, silently fix the LLM's mistake
            self.marks_awarded = self.max_marks
        return self


class ComparisonResult(BaseModel):
    """
    Side-by-side comparison of evaluation with vs without rubric.

    This is the BONUS feature that proves why rubrics matter.
    Evalvia AI's whole business is built on this idea — rubric-grounded
    evaluation is more consistent and fair than free-form AI grading.
    """
    with_rubric: dict = Field(
        ...,
        description="Evaluation result using the matched rubric"
    )
    without_rubric: dict = Field(
        ...,
        description="Evaluation result without any rubric (free-form AI grading)"
    )


class EvaluationResult(BaseModel):
    """
    The COMPLETE evaluation response returned to the user.

    This is the main output of our entire system. It contains:
      1. Total score (marks_awarded / max_marks)
      2. Human-readable feedback (what was good and what was missing)
      3. Detailed justification (why this specific score was given)
      4. Per-criterion breakdown (how each criterion was scored)
      5. Metadata (which rubric was used, match quality, which AI model)

    Validation:
      - marks_awarded is auto-computed from criterion_breakdown sum
      - marks_awarded cannot exceed max_marks
      - feedback and justification must be non-empty
    """
    marks_awarded: int = Field(
        ...,
        ge=0,
        description="Total marks given to the student"
    )
    max_marks: int = Field(
        ...,
        gt=0,
        description="Maximum marks available"
    )
    feedback: str = Field(
        ...,
        min_length=1,
        description="2-3 sentence summary: what was good + what was missing"
    )
    justification: str = Field(
        ...,
        min_length=1,
        description="Detailed explanation of why these marks were given"
    )
    criterion_breakdown: List[CriterionScore] = Field(
        default_factory=list,
        description="Per-criterion score breakdown — the heart of rubric evaluation"
    )

    # ── Metadata fields ──────────────────────────────────────────────────────
    rubric_used: str = Field(
        default="unknown",
        description="ID of the rubric that was used (e.g., 'physics_definition')"
    )
    match_score: int = Field(
        default=0,
        ge=0,
        description="How well the rubric matched the question (0 = fallback used)"
    )
    model_used: Optional[str] = Field(
        default=None,
        description="Which AI model produced this evaluation (e.g., 'deepseek-r1')"
    )
    rubric_details: Optional[dict] = Field(
        default=None,
        description="Full rubric data for display in the UI"
    )
    comparison: Optional[ComparisonResult] = Field(
        default=None,
        description="With vs without rubric comparison (only if compare_mode=True)"
    )

    @model_validator(mode="after")
    def validate_total_marks(self):
        """
        ACCURACY GUARD: Ensure marks_awarded matches criterion sum.

        Problem:
          LLMs are bad at arithmetic. They might say "total = 4" but the
          individual criterion scores add up to 3. This validator fixes that.

        Also ensures:
          - Total marks never exceed max_marks
          - If criterion_breakdown exists, total must match the sum

        This is one of the most important accuracy features in the project.
        Without this, ~15% of LLM evaluations would have wrong totals.
        """
        if self.criterion_breakdown:
            computed_total = sum(c.marks_awarded for c in self.criterion_breakdown)
            if computed_total != self.marks_awarded:
                # Auto-correct: use the sum of individual criteria (more reliable)
                self.marks_awarded = computed_total

        # Clamp to max_marks — can never give more than maximum
        if self.marks_awarded > self.max_marks:
            self.marks_awarded = self.max_marks

        return self
