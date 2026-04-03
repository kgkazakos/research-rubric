"""Tests for research_rubric.rubric — evaluate() orchestration."""

from research_rubric.rubric import DIMENSION_COUNT, evaluate
from research_rubric.models import RubricReport


HIGH_TEXT = open("tests/fixtures/high_quality_report.txt", encoding="utf-8").read()
LOW_TEXT = open("tests/fixtures/low_quality_report.txt", encoding="utf-8").read()


def test_evaluate_returns_rubric_report():
    result = evaluate("some research text", source="test")
    assert isinstance(result, RubricReport)


def test_evaluate_correct_dimension_count():
    result = evaluate("some research text about saturation and bias", source="test")
    assert len(result.dimensions) == DIMENSION_COUNT


def test_evaluate_all_dimension_names_present():
    expected = {
        "saturation", "bias_awareness", "evidence_linkage", "triangulation",
        "reflexivity", "transferability", "credibility", "rigor_of_analysis",
    }
    result = evaluate("some text", source="test")
    assert {d.name for d in result.dimensions} == expected


def test_evaluate_high_quality_report_scores_high():
    result = evaluate(HIGH_TEXT, source="high")
    assert result.overall_score > 50, f"Expected >50, got {result.overall_score:.1f}"


def test_evaluate_low_quality_report_scores_low():
    result = evaluate(LOW_TEXT, source="low")
    assert result.overall_score < 40, f"Expected <40, got {result.overall_score:.1f}"


def test_evaluate_source_preserved():
    result = evaluate("text", source="my_report.txt")
    assert result.source == "my_report.txt"


def test_evaluate_word_count():
    text = "word " * 100
    result = evaluate(text.strip(), source="test")
    assert result.word_count == 100


def test_evaluate_empty_text_does_not_crash():
    result = evaluate("", source="empty")
    assert result.overall_score >= 0


def test_evaluate_llm_summary_none_by_default():
    result = evaluate("some text", source="test")
    assert result.llm_summary is None


def test_overall_score_is_mean_of_dimensions():
    result = evaluate(HIGH_TEXT, source="test")
    expected = sum(d.score for d in result.dimensions) / len(result.dimensions)
    assert abs(result.overall_score - expected) < 0.01
