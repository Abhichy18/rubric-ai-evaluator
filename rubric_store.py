# rubric_store.py
# ──────────────────────────────────────────────────────────────────────────────
# 📚 RUBRIC STORE — The Brain of Our Evaluation System
# ──────────────────────────────────────────────────────────────────────────────
#
# WHAT IS THIS?
#   A collection of marking schemes (rubrics) for different types of questions.
#   Each rubric tells the AI exactly HOW to grade an answer — what to look for,
#   how many marks each part is worth, and examples of good/poor answers.
#
# HOW IT WORKS:
#   1. Student asks a question like "Define Newton's Second Law"
#   2. Our retriever (retriever.py) searches these rubrics using keywords
#   3. It picks the best-matching rubric (e.g., physics_definition)
#   4. The AI evaluator uses THAT rubric to grade the student's answer
#
# WHY NOT JUST LET AI GRADE FREELY?
#   Without a rubric, AI gives inconsistent marks — sometimes 3/5, sometimes 5/5
#   for the same answer. Rubrics make grading FAIR and CONSISTENT, just like
#   how CBSE provides marking schemes to teachers.
# ──────────────────────────────────────────────────────────────────────────────

RUBRICS = [

    # ═══════════════════════════════════════════════════════════════════════════
    # PHYSICS RUBRICS
    # ═══════════════════════════════════════════════════════════════════════════

    {
        "id": "physics_definition",
        "subject": "physics",
        "question_type": "definition",
        "keywords": [
            "define", "definition", "meaning", "state", "explain",
            "newton", "force", "law", "motion", "second", "first", "third",
            "acceleration", "velocity", "momentum", "energy", "power",
            "pressure", "ohm", "current", "resistance", "electric", "inertia",
            "displacement", "scalar", "vector", "work", "potential",
            "gravitational", "friction", "density", "mass"
        ],
        "criteria": [
            {"name": "Correct definition stated",         "marks": 2},
            {"name": "SI unit mentioned (if applicable)", "marks": 1},
            {"name": "Formula / mathematical expression", "marks": 1},
            {"name": "Example or real-world application", "marks": 1},
        ],
        "max_marks": 5,
        "examples": {
            "good": "Newton's Second Law states that the net force acting on an object equals the product of its mass and acceleration (F = ma). The SI unit of force is Newton (N). For example, pushing a heavier cart requires more force than a lighter one.",
            "poor": "Force equals mass times acceleration."
        }
    },

    {
        "id": "physics_derivation",
        "subject": "physics",
        "question_type": "derivation",
        "keywords": [
            "derive", "derivation", "prove", "proof", "show that",
            "lens formula", "mirror formula", "derive expression",
            "kirchhoff", "gauss", "coulomb", "snell", "refraction",
            "ohm's law", "establish", "starting from", "step by step"
        ],
        "criteria": [
            {"name": "Correct starting point / assumptions stated", "marks": 1},
            {"name": "Each mathematical step is correct",           "marks": 2},
            {"name": "Final formula correctly obtained",            "marks": 1},
            {"name": "Diagram (if applicable)",                     "marks": 1},
        ],
        "max_marks": 5,
        "examples": {
            "good": "Starting from Snell's law (n1 sin i = n2 sin r), applying it to a thin lens with two refracting surfaces, using the lens-maker's equation step by step, we arrive at 1/f = 1/v - 1/u.",
            "poor": "The lens formula is 1/f = 1/v - 1/u."
        }
    },

    {
        "id": "physics_numerical",
        "subject": "physics",
        "question_type": "numerical",
        "keywords": [
            "calculate", "find", "compute", "determine", "how much", "what is the value",
            "numerical", "given", "kg", "m/s", "joule", "watt", "newton",
            "resistance", "current", "voltage", "wavelength", "frequency",
            "if", "when", "a body", "an object", "mass of", "speed of"
        ],
        "criteria": [
            {"name": "Correct formula identified and written", "marks": 1},
            {"name": "Values correctly substituted",           "marks": 1},
            {"name": "Calculation steps shown",                "marks": 1},
            {"name": "Correct final answer",                   "marks": 1},
            {"name": "Correct unit in final answer",           "marks": 1},
        ],
        "max_marks": 5,
        "examples": {
            "good": "Given: V = 12V, R = 4Ω. Using Ohm's Law: I = V/R = 12/4 = 3A. The current flowing through the circuit is 3 Amperes.",
            "poor": "I = 3A"
        }
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # MATHEMATICS RUBRICS
    # ═══════════════════════════════════════════════════════════════════════════

    {
        "id": "math_proof",
        "subject": "mathematics",
        "question_type": "proof",
        "keywords": [
            "prove", "proof", "show", "verify", "LHS", "RHS",
            "theorem", "identity", "trigonometric", "algebraic",
            "show that", "establish that", "demonstrate",
            "sin", "cos", "tan", "sec", "cosec", "cot",
            "sin2", "cos2", "lhs", "rhs", "hence proved"
        ],
        "criteria": [
            {"name": "Correct approach / method chosen", "marks": 1},
            {"name": "Each step logically follows",      "marks": 2},
            {"name": "Correct conclusion stated",        "marks": 1},
            {"name": "No logical gaps or missing steps", "marks": 1},
        ],
        "max_marks": 5,
        "examples": {
            "good": "To prove sin²θ + cos²θ = 1: Starting with the Pythagorean theorem in a right triangle (a² + b² = c²), dividing both sides by c², we get (a/c)² + (b/c)² = 1, which gives sin²θ + cos²θ = 1. Hence proved.",
            "poor": "sin²θ + cos²θ = 1 is a standard identity."
        }
    },

    {
        "id": "math_problem_solving",
        "subject": "mathematics",
        "question_type": "problem_solving",
        "keywords": [
            "solve", "find", "evaluate", "integrate", "differentiate",
            "limit", "matrix", "determinant", "equation",
            "quadratic", "linear", "probability", "permutation", "combination",
            "x =", "y =", "roots", "value of", "simplify"
        ],
        "criteria": [
            {"name": "Correct method/approach selected", "marks": 1},
            {"name": "All intermediate steps shown",     "marks": 2},
            {"name": "Correct final answer",             "marks": 1},
            {"name": "Simplified to lowest form / units","marks": 1},
        ],
        "max_marks": 5,
        "examples": {
            "good": "To solve x² - 5x + 6 = 0: Using factorization, (x - 2)(x - 3) = 0, so x = 2 or x = 3. The roots are x = 2 and x = 3.",
            "poor": "x = 2, 3"
        }
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # ENGLISH RUBRICS
    # ═══════════════════════════════════════════════════════════════════════════

    {
        "id": "english_comprehension",
        "subject": "english",
        "question_type": "comprehension",
        "keywords": [
            "passage", "read", "answer the following", "what does", "why did",
            "explain", "how does", "describe", "author", "meaning", "word",
            "according to", "in the passage", "the writer", "paragraph"
        ],
        "criteria": [
            {"name": "Directly answers the question asked",  "marks": 2},
            {"name": "Uses evidence from the passage",       "marks": 1},
            {"name": "Clarity and coherence of explanation", "marks": 1},
            {"name": "Correct grammar and spelling",         "marks": 1},
        ],
        "max_marks": 5,
    },

    {
        "id": "english_essay",
        "subject": "english",
        "question_type": "essay",
        "keywords": [
            "write an essay", "discuss", "write about", "paragraph",
            "describe in detail", "your opinion", "advantages", "disadvantages",
            "write a", "composition", "article on", "speech on"
        ],
        "criteria": [
            {"name": "Clear introduction with thesis statement",  "marks": 1},
            {"name": "Body paragraphs with relevant key points", "marks": 2},
            {"name": "Coherent conclusion",                      "marks": 1},
            {"name": "Language quality, grammar, vocabulary",    "marks": 1},
        ],
        "max_marks": 5,
        "examples": {
            "good": "Climate change is one of the most pressing issues of our time. [Introduction with thesis] Rising temperatures have led to melting ice caps, extreme weather events, and loss of biodiversity. [Body with key points] In conclusion, immediate collective action is needed to mitigate these effects. [Conclusion]",
            "poor": "Climate change is bad. We should stop pollution."
        }
    },

    {
        "id": "english_grammar",
        "subject": "english",
        "question_type": "grammar",
        "keywords": [
            "fill in", "correct the", "rewrite", "change the voice",
            "active", "passive", "tense", "narration", "direct", "indirect",
            "transformation", "conjunction", "preposition", "article",
            "reported speech", "question tag"
        ],
        "criteria": [
            {"name": "Grammatically correct transformation", "marks": 2},
            {"name": "Meaning preserved",                   "marks": 2},
            {"name": "Correct punctuation",                 "marks": 1},
        ],
        "max_marks": 5,
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # CHEMISTRY RUBRICS
    # ═══════════════════════════════════════════════════════════════════════════

    {
        "id": "chemistry_reaction",
        "subject": "chemistry",
        "question_type": "chemical_reaction",
        "keywords": [
            "reaction", "equation", "balance", "chemical", "acid", "base",
            "oxidation", "reduction", "redox", "precipitate", "electrolysis",
            "write the equation", "complete the reaction", "products"
        ],
        "criteria": [
            {"name": "Correct chemical equation written",     "marks": 2},
            {"name": "Equation is balanced",                  "marks": 1},
            {"name": "State symbols included (s, l, g, aq)", "marks": 1},
            {"name": "Type of reaction correctly identified", "marks": 1},
        ],
        "max_marks": 5,
        "examples": {
            "good": "2H₂(g) + O₂(g) → 2H₂O(l). This is a combination/synthesis reaction. The equation is balanced with 4 hydrogen atoms and 2 oxygen atoms on each side.",
            "poor": "H2 + O2 = H2O"
        }
    },

    {
        "id": "chemistry_concept",
        "subject": "chemistry",
        "question_type": "concept",
        "keywords": [
            "explain", "define", "what is", "why", "how does",
            "bond", "bonding", "ionic", "covalent", "periodic", "element",
            "mole", "molarity", "concentration", "pH", "catalyst",
            "hybridization", "isomer", "polymer", "enthalpy"
        ],
        "criteria": [
            {"name": "Correct concept / definition stated",    "marks": 2},
            {"name": "Scientific reasoning / mechanism given", "marks": 2},
            {"name": "Example or diagram (if applicable)",     "marks": 1},
        ],
        "max_marks": 5,
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # BIOLOGY RUBRICS
    # ═══════════════════════════════════════════════════════════════════════════

    {
        "id": "biology_process",
        "subject": "biology",
        "question_type": "process",
        "keywords": [
            "explain the process", "describe", "how does", "photosynthesis",
            "respiration", "digestion", "reproduction", "mitosis", "meiosis",
            "transpiration", "osmosis", "diffusion", "DNA", "protein synthesis",
            "enzyme", "hormone", "neuron", "reflex"
        ],
        "criteria": [
            {"name": "Process correctly named and initiated",  "marks": 1},
            {"name": "All major steps described in order",     "marks": 2},
            {"name": "Diagram/flowchart (if applicable)",      "marks": 1},
            {"name": "Final outcome or product stated",        "marks": 1},
        ],
        "max_marks": 5,
        "examples": {
            "good": "Photosynthesis is the process by which green plants convert carbon dioxide and water into glucose and oxygen using sunlight. It occurs in the chloroplasts. The equation is: 6CO₂ + 6H₂O → C₆H₁₂O₆ + 6O₂. The light reaction occurs in the thylakoid membrane, and the Calvin cycle occurs in the stroma.",
            "poor": "Plants make food from sunlight."
        }
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # SOCIAL SCIENCE / HISTORY RUBRICS
    # ═══════════════════════════════════════════════════════════════════════════

    {
        "id": "social_short_answer",
        "subject": "social_science",
        "question_type": "short_answer",
        "keywords": [
            "what was", "who was", "when did", "where did", "why did",
            "war", "revolution", "independence", "parliament", "democracy",
            "constitution", "rights", "amendment", "movement", "treaty",
            "civilization", "culture", "economy", "trade", "colonialism"
        ],
        "criteria": [
            {"name": "Correct factual answer provided",   "marks": 2},
            {"name": "Historical/social context given",   "marks": 1},
            {"name": "Cause and effect explained",        "marks": 1},
            {"name": "Relevant example or event cited",   "marks": 1},
        ],
        "max_marks": 5,
    },

    # ═══════════════════════════════════════════════════════════════════════════
    # FALLBACK RUBRIC — Used when no specific rubric matches
    # ═══════════════════════════════════════════════════════════════════════════
    #
    # WHY IS THIS MANDATORY?
    #   The JD specifically says: "You must include a generic fallback rubric"
    #   If someone asks "What is the capital of France?" — no subject rubric
    #   matches, so we use this generic one instead of crashing.
    #
    # ═══════════════════════════════════════════════════════════════════════════

    {
        "id": "fallback_generic",
        "subject": "general",
        "question_type": "generic",
        "keywords": [],  # Empty — matches anything when nothing else matches
        "criteria": [
            {"name": "Relevance — answer directly addresses the question", "marks": 2},
            {"name": "Coverage — all key points mentioned",               "marks": 1},
            {"name": "Clarity — explanation is easy to understand",       "marks": 1},
            {"name": "Language — grammatically correct, well-structured", "marks": 1},
        ],
        "max_marks": 5,
    },
]
