"""Eval framework for validating research-rubric scoring.

Runs the rubric against a labeled dataset and reports:
- Level accuracy (high / medium / low classification)
- Per-dimension accuracy (score within expected range)
- Mean dimension accuracy across all cases
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .rubric import evaluate


@dataclass
class EvalCase:
    """A single labeled example for rubric evaluation."""

    id: str
    text: str
    expected_level: str  # "high" | "medium" | "low"
    expected_ranges: dict[str, tuple[float, float]]  # dim -> (min, max)
    description: str = ""


@dataclass
class DimensionResult:
    score: float
    expected_min: float
    expected_max: float
    in_range: bool

    def to_dict(self) -> dict:
        return {
            "score": round(self.score, 1),
            "expected_min": self.expected_min,
            "expected_max": self.expected_max,
            "in_range": self.in_range,
        }


@dataclass
class EvalResult:
    """Eval outcome for a single case."""

    case_id: str
    description: str
    expected_level: str
    actual_level: str
    level_match: bool
    overall_score: float
    dimension_results: dict[str, DimensionResult] = field(default_factory=dict)

    @property
    def dimension_accuracy(self) -> float:
        if not self.dimension_results:
            return 1.0
        return sum(1 for r in self.dimension_results.values() if r.in_range) / len(
            self.dimension_results
        )

    def to_dict(self) -> dict:
        return {
            "case_id": self.case_id,
            "description": self.description,
            "expected_level": self.expected_level,
            "actual_level": self.actual_level,
            "level_match": self.level_match,
            "overall_score": round(self.overall_score, 1),
            "dimension_accuracy": round(self.dimension_accuracy, 3),
            "dimension_results": {k: v.to_dict() for k, v in self.dimension_results.items()},
        }


@dataclass
class EvalSuite:
    """Aggregated results across all eval cases."""

    results: list[EvalResult] = field(default_factory=list)

    @property
    def level_accuracy(self) -> float:
        if not self.results:
            return 0.0
        return sum(1 for r in self.results if r.level_match) / len(self.results)

    @property
    def mean_dimension_accuracy(self) -> float:
        if not self.results:
            return 0.0
        return sum(r.dimension_accuracy for r in self.results) / len(self.results)

    def to_dict(self) -> dict:
        return {
            "total_cases": len(self.results),
            "level_accuracy": round(self.level_accuracy, 3),
            "mean_dimension_accuracy": round(self.mean_dimension_accuracy, 3),
            "results": [r.to_dict() for r in self.results],
        }


def run_eval(cases: list[EvalCase]) -> EvalSuite:
    """Run the rubric against a set of labeled eval cases."""
    suite = EvalSuite()

    for case in cases:
        report = evaluate(case.text, source=case.id)
        dim_map = report.dimension_map

        dimension_results: dict[str, DimensionResult] = {}
        for dim_name, (exp_min, exp_max) in case.expected_ranges.items():
            if dim_name in dim_map:
                actual = dim_map[dim_name].score
                dimension_results[dim_name] = DimensionResult(
                    score=actual,
                    expected_min=exp_min,
                    expected_max=exp_max,
                    in_range=exp_min <= actual <= exp_max,
                )

        suite.results.append(
            EvalResult(
                case_id=case.id,
                description=case.description,
                expected_level=case.expected_level,
                actual_level=report.overall_level.value,
                level_match=report.overall_level.value == case.expected_level,
                overall_score=report.overall_score,
                dimension_results=dimension_results,
            )
        )

    return suite


def load_eval_dataset(path: Path) -> list[EvalCase]:
    """Load eval cases from a JSON file.

    Each item must have: ``id``, ``text``, ``expected_level``,
    ``expected_ranges`` (dict of dim -> [min, max]).
    Optional: ``description``.
    """
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)

    return [
        EvalCase(
            id=item["id"],
            text=item["text"],
            expected_level=item["expected_level"],
            expected_ranges={
                k: (float(v[0]), float(v[1]))
                for k, v in item.get("expected_ranges", {}).items()
            },
            description=item.get("description", ""),
        )
        for item in data
    ]
