"""Tests for research_rubric.evals framework."""

from pathlib import Path

from research_rubric.evals import (
    EvalCase,
    EvalSuite,
    load_eval_dataset,
    run_eval,
)


DATASET_PATH = Path("tests/fixtures/evals_dataset.json")


def test_load_eval_dataset_returns_list():
    cases = load_eval_dataset(DATASET_PATH)
    assert isinstance(cases, list)
    assert len(cases) > 0


def test_load_eval_dataset_case_structure():
    cases = load_eval_dataset(DATASET_PATH)
    case = cases[0]
    assert isinstance(case, EvalCase)
    assert case.id
    assert case.text
    assert case.expected_level in {"high", "medium", "low"}
    assert isinstance(case.expected_ranges, dict)


def test_run_eval_returns_suite():
    cases = load_eval_dataset(DATASET_PATH)
    suite = run_eval(cases)
    assert isinstance(suite, EvalSuite)


def test_run_eval_result_count_matches_cases():
    cases = load_eval_dataset(DATASET_PATH)
    suite = run_eval(cases)
    assert len(suite.results) == len(cases)


def test_eval_suite_level_accuracy_in_range():
    cases = load_eval_dataset(DATASET_PATH)
    suite = run_eval(cases)
    assert 0.0 <= suite.level_accuracy <= 1.0


def test_eval_suite_mean_dimension_accuracy_in_range():
    cases = load_eval_dataset(DATASET_PATH)
    suite = run_eval(cases)
    assert 0.0 <= suite.mean_dimension_accuracy <= 1.0


def test_eval_suite_meets_minimum_accuracy():
    """Rubric must achieve at least 60% dimension accuracy on labeled cases."""
    cases = load_eval_dataset(DATASET_PATH)
    suite = run_eval(cases)
    assert suite.mean_dimension_accuracy >= 0.60, (
        f"Dimension accuracy {suite.mean_dimension_accuracy:.0%} below 60% threshold"
    )


def test_eval_suite_to_dict_structure():
    cases = load_eval_dataset(DATASET_PATH)
    suite = run_eval(cases)
    d = suite.to_dict()
    assert "total_cases" in d
    assert "level_accuracy" in d
    assert "mean_dimension_accuracy" in d
    assert "results" in d


def test_eval_result_has_dimension_accuracy():
    cases = load_eval_dataset(DATASET_PATH)
    suite = run_eval(cases)
    for r in suite.results:
        assert 0.0 <= r.dimension_accuracy <= 1.0


def test_run_eval_empty_cases():
    suite = run_eval([])
    assert suite.level_accuracy == 0.0
    assert suite.mean_dimension_accuracy == 0.0
    assert len(suite.results) == 0
