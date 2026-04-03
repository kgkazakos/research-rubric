"""Rule-based dimension scorers for qualitative research quality evaluation.

Eight dimensions covering the core pillars of rigorous qualitative research:
saturation, bias awareness, evidence linkage, triangulation, reflexivity,
transferability, credibility, and rigor of analysis.
"""

from __future__ import annotations

import re

from .models import DimensionScore


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _count(text: str, patterns: list[str]) -> int:
    """Count how many patterns appear in lowercased text."""
    lower = text.lower()
    return sum(1 for p in patterns if p in lower)


def _any(text: str, patterns: list[str]) -> bool:
    lower = text.lower()
    return any(p in lower for p in patterns)


def _quote_count(text: str) -> int:
    """Count plausible participant-quote signals in text."""
    count = 0
    # Double-quoted passages >= 15 chars
    count += len(re.findall(r'"[^"]{15,}"', text))
    # Single-quoted passages >= 15 chars (apostrophes excluded by requiring space)
    count += len(re.findall(r"(?<!\w)'[^']{15,}'(?!\w)", text))
    # Attributed quote phrases
    attributed = [
        "participant said", "participant noted", "participant described",
        "one participant", "as p", "p1:", "p2:", "p3:", "p4:", "p5:",
        "interviewee", "respondent said", "user said", "they said",
        "she said", "he said", "they noted",
    ]
    lower = text.lower()
    count += sum(lower.count(p) for p in attributed)
    return count


# ---------------------------------------------------------------------------
# Dimension 1 — Thematic Saturation
# ---------------------------------------------------------------------------

_SAT_POS = [
    "saturation", "data saturation", "thematic saturation",
    "theoretical saturation", "no new themes", "no new codes",
    "informational redundancy", "reached saturation", "saturation point",
    "sufficient sample", "adequate sample", "sample size rationale",
    "stopping criteria", "data sufficiency",
]


def score_saturation(text: str) -> DimensionScore:
    """Evaluate evidence of thematic saturation and sample-size rationale."""
    hits = _count(text, _SAT_POS)
    score = min(hits * 16.0, 85.0)

    if "saturation" in text.lower():
        score = max(score, 52.0)

    issues: list[str] = []
    suggestions: list[str] = []

    if hits == 0:
        issues.append("No saturation discussion or sample-size rationale found.")
        suggestions.append(
            "Explicitly state when and why data collection ceased (e.g., thematic saturation)."
        )
        suggestions.append(
            "Reference the stopping criteria used — theoretical, thematic, or informational."
        )
    elif hits < 2:
        suggestions.append(
            "Strengthen saturation evidence with explicit stopping criteria and participant count."
        )

    return DimensionScore(
        name="saturation",
        label="Thematic Saturation",
        score=min(score, 100.0),
        issues=issues,
        suggestions=suggestions,
    )


# ---------------------------------------------------------------------------
# Dimension 2 — Bias Awareness
# ---------------------------------------------------------------------------

_BIAS_POS = [
    "bias", "reflexivity", "positionality", "bracketing",
    "researcher role", "insider perspective", "outsider perspective",
    "acknowledge", "subjectivity", "researcher influence",
    "standpoint", "researcher background", "potential bias",
    "confirmation bias", "researcher assumptions", "self-reflec",
]


def score_bias_awareness(text: str) -> DimensionScore:
    """Evaluate acknowledgment of researcher bias and positionality."""
    hits = _count(text, _BIAS_POS)
    score = min(hits * 13.0, 90.0)

    if _any(text, ["reflexivity", "positionality"]):
        score = max(score, 55.0)

    issues: list[str] = []
    suggestions: list[str] = []

    if hits == 0:
        issues.append("No acknowledgment of researcher bias or positionality.")
        suggestions.append(
            "Add a reflexivity statement describing your background and potential influence."
        )
        suggestions.append(
            "Acknowledge potential sources of bias in data collection and interpretation."
        )
    elif "limitation" not in text.lower():
        suggestions.append(
            "Include a dedicated limitations section to address potential biases."
        )

    return DimensionScore(
        name="bias_awareness",
        label="Bias Awareness",
        score=min(score, 100.0),
        issues=issues,
        suggestions=suggestions,
    )


# ---------------------------------------------------------------------------
# Dimension 3 — Evidence Linkage
# ---------------------------------------------------------------------------

_CLAIM_SIGNALS = [
    "users", "participants", "respondents", "interviewees",
    "findings show", "findings suggest", "data indicate",
    "results show", "analysis reveals", "theme", "pattern",
    "majority", "most participants", "several participants",
]

_EVIDENCE_PHRASES = [
    "for example", "for instance", "as illustrated", "as one participant",
    "evidence suggests", "as shown", "this is illustrated",
]


def score_evidence_linkage(text: str) -> DimensionScore:
    """Evaluate the ratio of supported claims to evidence and participant quotes."""
    quote_count = _quote_count(text)
    claim_count = _count(text, _CLAIM_SIGNALS)
    evidence_hits = _count(text, _EVIDENCE_PHRASES)

    if claim_count > 0:
        ratio = quote_count / claim_count
        score = min(ratio * 70.0, 80.0)
        if quote_count >= 3:
            score = max(score, 50.0)
    elif quote_count > 0:
        score = 55.0
    else:
        score = 10.0

    score += min(evidence_hits * 5.0, 20.0)

    issues: list[str] = []
    suggestions: list[str] = []

    if quote_count == 0:
        issues.append("No participant quotes or direct evidence found.")
        suggestions.append(
            "Include verbatim participant quotes to support each major finding."
        )
    elif quote_count < 3:
        suggestions.append(
            "Increase the number of supporting quotes — aim for at least one per major theme."
        )

    if claim_count > 0 and quote_count < claim_count * 0.3:
        issues.append("Claims substantially outnumber supporting evidence.")
        suggestions.append(
            "Ensure each major finding is grounded in at least one direct quote or data point."
        )

    return DimensionScore(
        name="evidence_linkage",
        label="Evidence Linkage",
        score=min(score, 100.0),
        issues=issues,
        suggestions=suggestions,
    )


# ---------------------------------------------------------------------------
# Dimension 4 — Triangulation
# ---------------------------------------------------------------------------

_TRI_POS = [
    "triangulat", "multiple methods", "mixed method",
    "survey", "observation", "field notes", "document analysis",
    "secondary data", "audit", "peer debrief", "peer review",
    "member check", "second coder", "intercoder", "independent coder",
    "multiple sources", "convergent", "cross-referenc",
    "two researchers", "independent analysis",
]


def score_triangulation(text: str) -> DimensionScore:
    """Evaluate use of multiple data sources or validation methods."""
    hits = _count(text, _TRI_POS)
    score = min(hits * 14.0, 90.0)

    if "triangulat" in text.lower():
        score = max(score, 60.0)

    issues: list[str] = []
    suggestions: list[str] = []

    if hits == 0:
        issues.append("No triangulation or multiple data-source evidence found.")
        suggestions.append(
            "Describe how multiple data sources or methods were used to validate findings."
        )
        suggestions.append(
            "Consider adding member checking or independent coding to strengthen credibility."
        )
    elif hits < 2:
        suggestions.append(
            "Expand on how different data sources converge or diverge."
        )

    return DimensionScore(
        name="triangulation",
        label="Triangulation",
        score=min(score, 100.0),
        issues=issues,
        suggestions=suggestions,
    )


# ---------------------------------------------------------------------------
# Dimension 5 — Reflexivity
# ---------------------------------------------------------------------------

_REF_POS = [
    "reflexiv", "positionality", "researcher background",
    "my role", "my perspective", "insider perspective",
    "prior knowledge", "preconceptions", "researcher influence",
    "standpoint", "self-reflec", "researcher position",
    "researcher's role", "researcher identity",
]


def score_reflexivity(text: str) -> DimensionScore:
    """Evaluate researcher self-reflection and positionality disclosure."""
    hits = _count(text, _REF_POS)
    score = min(hits * 18.0, 90.0)

    if "reflexiv" in text.lower():
        score = max(score, 55.0)

    issues: list[str] = []
    suggestions: list[str] = []

    if hits == 0:
        issues.append("Researcher reflexivity is not addressed.")
        suggestions.append(
            "Add a reflexivity statement describing your background and how it shaped the study."
        )
        suggestions.append(
            "Describe steps taken to bracket prior assumptions during data collection and analysis."
        )
    elif hits < 2:
        suggestions.append(
            "Deepen the reflexivity discussion — a single mention is rarely sufficient."
        )

    return DimensionScore(
        name="reflexivity",
        label="Reflexivity",
        score=min(score, 100.0),
        issues=issues,
        suggestions=suggestions,
    )


# ---------------------------------------------------------------------------
# Dimension 6 — Transferability
# ---------------------------------------------------------------------------

_TRANS_POS = [
    "transferab", "generaliz", "limitation", "context",
    "scope", "boundary", "thick description", "rich description",
    "context-specific", "not generaliz", "future research",
    "replication", "study context", "setting", "demographic",
    "sample characteristics", "population", "applicability",
]


def score_transferability(text: str) -> DimensionScore:
    """Evaluate context description and transferability of findings."""
    hits = _count(text, _TRANS_POS)
    score = min(hits * 10.0, 85.0)

    if "limitation" in text.lower():
        score = max(score, 45.0)

    issues: list[str] = []
    suggestions: list[str] = []

    if hits == 0:
        issues.append("No discussion of study context, scope, or transferability.")
        suggestions.append(
            "Describe context in enough detail for readers to assess applicability."
        )
        suggestions.append(
            "Explicitly address conditions under which findings may or may not apply."
        )
    elif "limitation" not in text.lower():
        suggestions.append(
            "Add an explicit limitations section to strengthen transferability claims."
        )

    return DimensionScore(
        name="transferability",
        label="Transferability",
        score=min(score, 100.0),
        issues=issues,
        suggestions=suggestions,
    )


# ---------------------------------------------------------------------------
# Dimension 7 — Credibility
# ---------------------------------------------------------------------------

_CRED_POS = [
    "member check", "member checking", "participant validation",
    "respondent validation", "peer debrief", "audit trail",
    "prolonged engagement", "negative case", "deviant case",
    "disconfirm", "credibility", "trustworthiness",
    "communicative validation", "check with participants",
]


def score_credibility(text: str) -> DimensionScore:
    """Evaluate credibility-establishing procedures (member checks, audit trail, etc.)."""
    hits = _count(text, _CRED_POS)
    score = min(hits * 16.0, 90.0)

    if "member check" in text.lower():
        score = max(score, 55.0)
    if "audit trail" in text.lower():
        score = max(score, 50.0)
    if "negative case" in text.lower():
        score = max(score, 45.0)

    issues: list[str] = []
    suggestions: list[str] = []

    if hits == 0:
        issues.append(
            "No credibility procedures found (member checking, audit trail, negative case)."
        )
        suggestions.append(
            "Describe member-checking or respondent-validation procedures used."
        )
        suggestions.append(
            "Maintain and reference an audit trail of key analytical decisions."
        )
    elif hits < 2:
        suggestions.append(
            "Strengthen credibility with additional procedures (e.g., negative case analysis)."
        )

    return DimensionScore(
        name="credibility",
        label="Credibility",
        score=min(score, 100.0),
        issues=issues,
        suggestions=suggestions,
    )


# ---------------------------------------------------------------------------
# Dimension 8 — Rigor of Analysis
# ---------------------------------------------------------------------------

_RIGOR_POS = [
    "thematic analysis", "grounded theory", "constant comparison",
    "open coding", "axial coding", "selective coding",
    "framework analysis", "interpretative phenomenological",
    "ipa", "discourse analysis", "content analysis",
    "systematic", "coding scheme", "codebook",
    "analytical process", "iterative", "inductive",
    "deductive", "abductive", "nvivo", "atlas.ti",
    "two researchers", "independent coding", "inter-rater",
    "coding procedure", "analytical framework",
]

_STRONG_METHODS = [
    "thematic analysis", "grounded theory", "framework analysis",
    "interpretative phenomenological", "ipa", "discourse analysis",
]


def score_rigor_of_analysis(text: str) -> DimensionScore:
    """Evaluate explicitness and systematicity of the analytical approach."""
    hits = _count(text, _RIGOR_POS)
    score = min(hits * 12.0, 90.0)

    if _any(text, _STRONG_METHODS):
        score = max(score, 55.0)

    issues: list[str] = []
    suggestions: list[str] = []

    if hits == 0:
        issues.append("Analytical method is not named or described.")
        suggestions.append(
            "Name the analytical approach (e.g., thematic analysis, grounded theory) "
            "and describe the full coding process."
        )
        suggestions.append(
            "Include details on how codes were developed, refined, and validated."
        )
    elif hits < 3:
        suggestions.append(
            "Provide more detail — how were themes identified, contested, and finalised?"
        )

    return DimensionScore(
        name="rigor_of_analysis",
        label="Rigor of Analysis",
        score=min(score, 100.0),
        issues=issues,
        suggestions=suggestions,
    )
