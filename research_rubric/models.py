"""Data models for research-rubric."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class QualityLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


_THRESHOLDS = {
    QualityLevel.HIGH: 70.0,
    QualityLevel.MEDIUM: 40.0,
    QualityLevel.LOW: 0.0,
}


def score_to_level(score: float) -> QualityLevel:
    """Map a 0-100 score to a QualityLevel."""
    if score >= _THRESHOLDS[QualityLevel.HIGH]:
        return QualityLevel.HIGH
    if score >= _THRESHOLDS[QualityLevel.MEDIUM]:
        return QualityLevel.MEDIUM
    return QualityLevel.LOW


@dataclass
class DimensionScore:
    """Score for a single rubric dimension."""

    name: str
    label: str
    score: float  # 0-100
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    llm_rationale: Optional[str] = None

    @property
    def level(self) -> QualityLevel:
        return score_to_level(self.score)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "label": self.label,
            "score": round(self.score, 1),
            "level": self.level.value,
            "issues": self.issues,
            "suggestions": self.suggestions,
            "llm_rationale": self.llm_rationale,
        }


@dataclass
class RubricReport:
    """Full rubric evaluation report for a research document."""

    source: str
    word_count: int
    dimensions: list[DimensionScore] = field(default_factory=list)
    llm_summary: Optional[str] = None

    @property
    def overall_score(self) -> float:
        if not self.dimensions:
            return 0.0
        return sum(d.score for d in self.dimensions) / len(self.dimensions)

    @property
    def overall_level(self) -> QualityLevel:
        return score_to_level(self.overall_score)

    @property
    def dimension_map(self) -> dict[str, DimensionScore]:
        return {d.name: d for d in self.dimensions}

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "word_count": self.word_count,
            "overall_score": round(self.overall_score, 1),
            "overall_level": self.overall_level.value,
            "dimensions": [d.to_dict() for d in self.dimensions],
            "llm_summary": self.llm_summary,
        }
