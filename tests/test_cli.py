"""Tests for research_rubric.cli — Click commands."""

import json

from click.testing import CliRunner

from research_rubric.cli import cli


FIXTURE_HIGH = "tests/fixtures/high_quality_report.txt"
FIXTURE_LOW = "tests/fixtures/low_quality_report.txt"
EVAL_FIXTURE = "tests/fixtures/evals_dataset.json"


def test_cli_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "research-rubric" in result.output.lower()


def test_score_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["score", "--help"])
    assert result.exit_code == 0


def test_score_high_quality_file():
    runner = CliRunner()
    result = runner.invoke(cli, ["score", FIXTURE_HIGH])
    assert result.exit_code == 0


def test_score_json_output():
    runner = CliRunner()
    result = runner.invoke(cli, ["score", "--json", FIXTURE_HIGH])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "overall_score" in data
    assert "dimensions" in data
    assert len(data["dimensions"]) == 8


def test_score_json_overall_score_is_number():
    runner = CliRunner()
    result = runner.invoke(cli, ["score", "--json", FIXTURE_HIGH])
    data = json.loads(result.output)
    assert isinstance(data["overall_score"], (int, float))


def test_score_json_low_scores_lower_than_high():
    runner = CliRunner()
    r_high = runner.invoke(cli, ["score", "--json", FIXTURE_HIGH])
    r_low = runner.invoke(cli, ["score", "--json", FIXTURE_LOW])
    high_score = json.loads(r_high.output)["overall_score"]
    low_score = json.loads(r_low.output)["overall_score"]
    assert high_score > low_score


def test_score_output_file(tmp_path):
    out = tmp_path / "result.json"
    runner = CliRunner()
    result = runner.invoke(cli, ["score", "--output", str(out), FIXTURE_HIGH])
    assert result.exit_code == 0
    assert out.exists()
    data = json.loads(out.read_text())
    assert "overall_score" in data


def test_score_nonexistent_file():
    runner = CliRunner()
    result = runner.invoke(cli, ["score", "nonexistent_file.txt"])
    assert result.exit_code != 0


def test_eval_command_json():
    runner = CliRunner()
    result = runner.invoke(cli, ["eval", "--json", EVAL_FIXTURE])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "total_cases" in data
    assert "level_accuracy" in data


def test_eval_command_output_file(tmp_path):
    out = tmp_path / "eval_results.json"
    runner = CliRunner()
    result = runner.invoke(cli, ["eval", "--output", str(out), EVAL_FIXTURE])
    assert result.exit_code == 0
    assert out.exists()
