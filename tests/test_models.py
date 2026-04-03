"""Tests for research_rubric.models."""

from research_rubric.models import (
    DimensionScore,
    QualityLevel,
    RubricReport,
    score_to_level,
)


class TestQualityLevel:
    def test_enum_values(self):
        assert QualityLevel.HIGH == "high"
        assert QualityLevel.MEDIUM == "medium"
        assert QualityLevel.LOW == "low"

    def test_score_to_level_high(self):
        assert score_to_level(85.0) == QualityLevel.HIGH
        assert score_to_level(70.0) == QualityLevel.HIGH

    def test_score_to_level_medium(self):
        assert score_to_level(55.0) == QualityLevel.MEDIUM
        assert score_to_level(40.0) == QualityLevel.MEDIUM

    def test_score_to_level_low(self):
        assert score_to_level(39.0) == QualityLevel.LOW
        assert score_to_level(0.0) == QualityLevel.LOW

    def test_boundary_exactly_70(self):
        assert score_to_level(70.0) == QualityLevel.HIGH

    def test_boundary_exactly_40(self):
        assert score_to_level(40.0) == QualityLevel.MEDIUM

    def test_boundary_just_below_40(self):
        assert score_to_level(39.9) == QualityLevel.LOW


class TestDimensionScore:
    def test_creation(self):
        d = DimensionScore(name="saturation", label="Thematic Saturation", score=75.0)
        assert d.name == "saturation"
        assert d.score == 75.0
        assert d.issues == []
        assert d.suggestions == []
        assert d.llm_rationale is None

    def test_level_property(self):
        d = DimensionScore(name="x", label="X", score=80.0)
        assert d.level == QualityLevel.HIGH

    def test_to_dict_keys(self):
        d = DimensionScore(name="x", label="X", score=55.0, issues=["iss1"])
        result = d.to_dict()
        assert set(result.keys()) == {
            "name", "label", "score", "level", "issues", "suggestions", "llm_rationale"
        }

    def test_to_dict_score_rounded(self):
        d = DimensionScore(name="x", label="X", score=66.6666)
        assert d.to_dict()["score"] == 66.7

    def test_to_dict_level_string(self):
        d = DimensionScore(name="x", label="X", score=80.0)
        assert d.to_dict()["level"] == "high"


class TestRubricReport:
    def _make_report(self, scores: list[float]) -> RubricReport:
        r = RubricReport(source="test", word_count=500)
        for i, s in enumerate(scores):
            r.dimensions.append(DimensionScore(name=f"d{i}", label=f"D{i}", score=s))
        return r

    def test_overall_score_average(self):
        r = self._make_report([80.0, 60.0, 40.0, 20.0])
        assert abs(r.overall_score - 50.0) < 0.01

    def test_overall_score_empty(self):
        r = RubricReport(source="test", word_count=0)
        assert r.overall_score == 0.0

    def test_overall_level(self):
        r = self._make_report([90.0, 80.0, 75.0])
        assert r.overall_level == QualityLevel.HIGH

    def test_dimension_map(self):
        r = self._make_report([70.0, 50.0])
        dm = r.dimension_map
        assert "d0" in dm
        assert "d1" in dm
        assert dm["d0"].score == 70.0

    def test_to_dict_structure(self):
        r = self._make_report([60.0])
        d = r.to_dict()
        assert "overall_score" in d
        assert "overall_level" in d
        assert "dimensions" in d
        assert isinstance(d["dimensions"], list)
        assert d["word_count"] == 500
