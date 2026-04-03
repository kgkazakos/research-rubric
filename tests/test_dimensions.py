"""Tests for research_rubric.dimensions — one per dimension scorer plus helpers."""

from research_rubric.dimensions import (
    _count,
    _quote_count,
    score_bias_awareness,
    score_credibility,
    score_evidence_linkage,
    score_reflexivity,
    score_rigor_of_analysis,
    score_saturation,
    score_transferability,
    score_triangulation,
)


# ---------------------------------------------------------------------------
# Helper tests
# ---------------------------------------------------------------------------


def test_count_finds_patterns():
    assert _count("saturation was reached", ["saturation"]) == 1


def test_count_case_insensitive():
    assert _count("SATURATION reached", ["saturation"]) == 1


def test_count_multiple():
    assert _count("saturation and reflexivity both mentioned", ["saturation", "reflexivity"]) == 2


def test_quote_count_double_quotes():
    text = 'She said "this is a fairly long participant quote here".'
    assert _quote_count(text) >= 1


def test_quote_count_attributed():
    text = "One participant noted the experience was positive."
    assert _quote_count(text) >= 1


def test_quote_count_empty():
    assert _quote_count("no quotes here") == 0


# ---------------------------------------------------------------------------
# Dimension: Saturation
# ---------------------------------------------------------------------------


def test_saturation_high_signal():
    text = (
        "Data saturation was reached after 14 interviews. "
        "Thematic saturation was confirmed when no new themes emerged. "
        "The saturation point was documented in our field notes."
    )
    result = score_saturation(text)
    assert result.score > 50


def test_saturation_low_signal():
    text = "We interviewed some people and found interesting results about the product."
    result = score_saturation(text)
    assert result.score < 30
    assert len(result.issues) > 0


def test_saturation_name():
    result = score_saturation("some text")
    assert result.name == "saturation"


# ---------------------------------------------------------------------------
# Dimension: Bias Awareness
# ---------------------------------------------------------------------------


def test_bias_awareness_high():
    text = (
        "A reflexivity statement was prepared. The researcher's positionality "
        "as a former practitioner was acknowledged. We bracketed our bias and "
        "acknowledged potential researcher influence on interpretations."
    )
    result = score_bias_awareness(text)
    assert result.score > 50


def test_bias_awareness_low():
    text = "We conducted interviews and analyzed the data carefully."
    result = score_bias_awareness(text)
    assert result.score < 30
    assert len(result.issues) > 0


# ---------------------------------------------------------------------------
# Dimension: Evidence Linkage
# ---------------------------------------------------------------------------


def test_evidence_linkage_with_quotes():
    text = (
        'One participant noted: "the interface is confusing and hard to navigate." '
        'Another participant said: "I cannot find the search button at all." '
        'A third interviewee described: "the loading times are extremely slow." '
        "Participants described difficulty finding the transfer function. "
        "Users reported frustration with the onboarding flow."
    )
    result = score_evidence_linkage(text)
    assert result.score > 40


def test_evidence_linkage_no_quotes():
    text = (
        "Participants found the app easy to use. Users liked the interface. "
        "Respondents reported positive experiences overall. "
        "Findings show high satisfaction."
    )
    result = score_evidence_linkage(text)
    assert result.score < 40
    assert len(result.issues) > 0


def test_evidence_linkage_name():
    result = score_evidence_linkage("text")
    assert result.name == "evidence_linkage"


# ---------------------------------------------------------------------------
# Dimension: Triangulation
# ---------------------------------------------------------------------------


def test_triangulation_high():
    text = (
        "Triangulation was achieved through multiple data sources: interviews, "
        "a survey, and observation. Peer debriefing was conducted. "
        "Two researchers independently coded the transcripts."
    )
    result = score_triangulation(text)
    assert result.score > 55


def test_triangulation_low():
    text = "We interviewed participants and coded the transcripts ourselves."
    result = score_triangulation(text)
    assert result.score < 35
    assert len(result.issues) > 0


# ---------------------------------------------------------------------------
# Dimension: Reflexivity
# ---------------------------------------------------------------------------


def test_reflexivity_high():
    text = (
        "Reflexivity was maintained throughout. The researcher's positionality "
        "as a former practitioner was documented in a reflexivity journal. "
        "Self-reflection was conducted after each interview."
    )
    result = score_reflexivity(text)
    assert result.score > 50


def test_reflexivity_low():
    text = "The study followed standard qualitative procedures for data collection."
    result = score_reflexivity(text)
    assert result.score < 25
    assert len(result.issues) > 0


# ---------------------------------------------------------------------------
# Dimension: Transferability
# ---------------------------------------------------------------------------


def test_transferability_high():
    text = (
        "This study has several important limitations. Findings are context-specific "
        "and transferability to other settings should be assessed carefully. "
        "The sample demographic and study context are described in detail to support "
        "reader judgement. Future research should replicate findings in different populations."
    )
    result = score_transferability(text)
    assert result.score > 50


def test_transferability_low():
    text = "We found that users enjoy the product and recommend improvements."
    result = score_transferability(text)
    assert result.score < 30
    assert len(result.issues) > 0


# ---------------------------------------------------------------------------
# Dimension: Credibility
# ---------------------------------------------------------------------------


def test_credibility_high():
    text = (
        "Member checking was conducted with six participants. "
        "An audit trail of analytical decisions was maintained. "
        "Negative case analysis was performed to identify disconfirming evidence. "
        "Peer debriefing was conducted to support trustworthiness."
    )
    result = score_credibility(text)
    assert result.score > 55


def test_credibility_low():
    text = "The data were analyzed and themes were identified by the research team."
    result = score_credibility(text)
    assert result.score < 25
    assert len(result.issues) > 0


# ---------------------------------------------------------------------------
# Dimension: Rigor of Analysis
# ---------------------------------------------------------------------------


def test_rigor_high():
    text = (
        "Thematic analysis was applied following Braun and Clarke (2006). "
        "Open coding was followed by axial coding and selective coding. "
        "A codebook was maintained. Two researchers conducted independent coding "
        "and inter-rater reliability was calculated. The analytical process was iterative."
    )
    result = score_rigor_of_analysis(text)
    assert result.score > 55


def test_rigor_low():
    text = "We looked at the data and identified some key themes."
    result = score_rigor_of_analysis(text)
    assert result.score < 25
    assert len(result.issues) > 0


# ---------------------------------------------------------------------------
# Score cap and floor
# ---------------------------------------------------------------------------


def test_scores_within_bounds():
    """All dimension scores must be in [0, 100]."""
    high_text = open(
        "tests/fixtures/high_quality_report.txt", encoding="utf-8"
    ).read()
    for scorer in [
        score_saturation, score_bias_awareness, score_evidence_linkage,
        score_triangulation, score_reflexivity, score_transferability,
        score_credibility, score_rigor_of_analysis,
    ]:
        result = scorer(high_text)
        assert 0.0 <= result.score <= 100.0, f"{scorer.__name__} out of bounds: {result.score}"
