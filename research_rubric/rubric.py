"""Main rubric evaluation orchestrator."""

from __future__ import annotations

from .dimensions import (
    score_bias_awareness,
    score_credibility,
    score_evidence_linkage,
    score_reflexivity,
    score_rigor_of_analysis,
    score_saturation,
    score_transferability,
    score_triangulation,
)
from .models import RubricReport

_DIMENSION_SCORERS = [
    score_saturation,
    score_bias_awareness,
    score_evidence_linkage,
    score_triangulation,
    score_reflexivity,
    score_transferability,
    score_credibility,
    score_rigor_of_analysis,
]

DIMENSION_COUNT = len(_DIMENSION_SCORERS)


def evaluate(text: str, source: str = "input") -> RubricReport:
    """
    Evaluate a qualitative research document across eight quality dimensions.

    The evaluation is fully rule-based. Pass the result to
    ``research_rubric.llm.enrich_with_llm`` to add LLM-generated rationale.

    Parameters
    ----------
    text : str
        Full text of the research document.
    source : str
        Display label (e.g. filename or URL) shown in the report.

    Returns
    -------
    RubricReport
        Per-dimension scores, issues, suggestions, and an overall score.
    """
    word_count = len(text.split())
    report = RubricReport(source=source, word_count=word_count)

    for scorer in _DIMENSION_SCORERS:
        report.dimensions.append(scorer(text))

    return report
