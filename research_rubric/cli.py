"""Click CLI for research-rubric."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .models import QualityLevel
from .rubric import evaluate

console = Console()

_LEVEL_COLOUR = {
    QualityLevel.HIGH: "green",
    QualityLevel.MEDIUM: "yellow",
    QualityLevel.LOW: "red",
}
_LEVEL_ICON = {
    QualityLevel.HIGH: "●",
    QualityLevel.MEDIUM: "◑",
    QualityLevel.LOW: "○",
}


@click.group()
@click.version_option()
def cli() -> None:
    """research-rubric · CPR Orbital #06

    Evaluate qualitative research quality across eight dimensions:
    saturation, bias awareness, evidence linkage, triangulation,
    reflexivity, transferability, credibility, and rigor of analysis.
    """


@cli.command()
@click.argument("file", type=click.Path(exists=True, dir_okay=False))
@click.option(
    "--llm-backend",
    type=click.Choice(["openai", "anthropic", "gemini"]),
    default=None,
    help="Optional LLM backend for per-dimension narrative enrichment.",
)
@click.option("--json", "as_json", is_flag=True, default=False, help="Output JSON.")
@click.option("--output", type=click.Path(), default=None, help="Save results to file.")
def score(
    file: str,
    llm_backend: Optional[str],
    as_json: bool,
    output: Optional[str],
) -> None:
    """Score a qualitative research document."""
    text = Path(file).read_text(encoding="utf-8")
    if not text.strip():
        console.print("[red]Error: file is empty.[/red]")
        sys.exit(1)

    report = evaluate(text, source=Path(file).name)

    if llm_backend:
        from .llm import enrich_with_llm

        report = enrich_with_llm(text, report, backend=llm_backend)

    if as_json or output:
        payload = json.dumps(report.to_dict(), indent=2)
        if output:
            Path(output).write_text(payload, encoding="utf-8")
        if as_json:
            click.echo(payload)
        return

    # ── Rich terminal output ──────────────────────────────────────────────
    level = report.overall_level
    c = _LEVEL_COLOUR[level]
    icon = _LEVEL_ICON[level]

    console.print()
    console.print(
        Panel(
            f"[bold]{Path(file).name}[/bold]  [dim]{report.word_count:,} words[/dim]\n\n"
            f"Overall quality: [{c}]{icon} {report.overall_score:.0f}/100  "
            f"({level.value.upper()})[/{c}]",
            title="[bold]research-rubric[/bold] · CPR Orbital #06",
            border_style="dim",
        )
    )

    tbl = Table(box=box.SIMPLE, show_header=True, header_style="bold dim")
    tbl.add_column("Dimension", width=24)
    tbl.add_column("Score", justify="right", width=7)
    tbl.add_column("Level", width=9)
    tbl.add_column("Top issue", style="dim")

    for dim in report.dimensions:
        dc = _LEVEL_COLOUR[dim.level]
        di = _LEVEL_ICON[dim.level]
        issue = (dim.issues[0][:58] + "…") if dim.issues else "—"
        tbl.add_row(
            dim.label,
            f"[{dc}]{dim.score:.0f}[/{dc}]",
            f"[{dc}]{di} {dim.level.value}[/{dc}]",
            issue,
        )

    console.print(tbl)

    if report.llm_summary:
        console.print(Panel(report.llm_summary, title="LLM Summary", border_style="dim"))

    for dim in report.dimensions:
        if dim.issues or (dim.suggestions and dim.level != QualityLevel.HIGH):
            console.print(f"\n[bold]{dim.label}[/bold]")
            for iss in dim.issues:
                console.print(f"  [red]✗[/red] {iss}")
            for sug in dim.suggestions:
                console.print(f"  [dim]→[/dim] {sug}")
            if dim.llm_rationale:
                console.print(f"  [blue]◈[/blue] {dim.llm_rationale}")


@cli.command("eval")
@click.argument("eval_file", type=click.Path(exists=True, dir_okay=False))
@click.option("--json", "as_json", is_flag=True, default=False)
@click.option("--output", type=click.Path(), default=None)
def run_eval_cmd(eval_file: str, as_json: bool, output: Optional[str]) -> None:
    """Run the rubric eval suite against a labeled JSON dataset."""
    from .evals import load_eval_dataset, run_eval

    cases = load_eval_dataset(Path(eval_file))
    suite = run_eval(cases)

    if as_json or output:
        payload = json.dumps(suite.to_dict(), indent=2)
        if output:
            Path(output).write_text(payload, encoding="utf-8")
        if as_json:
            click.echo(payload)
        return

    la_c = "green" if suite.level_accuracy >= 0.7 else "yellow"
    da_c = "green" if suite.mean_dimension_accuracy >= 0.6 else "yellow"

    console.print()
    console.print(
        Panel(
            f"[bold]{len(suite.results)} cases[/bold]\n"
            f"Level accuracy:           [{la_c}]{suite.level_accuracy:.0%}[/{la_c}]\n"
            f"Mean dimension accuracy:  [{da_c}]{suite.mean_dimension_accuracy:.0%}[/{da_c}]",
            title="[bold]Eval Results[/bold]",
            border_style="dim",
        )
    )

    tbl = Table(box=box.SIMPLE)
    tbl.add_column("Case", width=22)
    tbl.add_column("Expected", width=10)
    tbl.add_column("Actual", width=10)
    tbl.add_column("✓", width=4)
    tbl.add_column("Dim acc", width=9)

    for r in suite.results:
        mark = "[green]✓[/green]" if r.level_match else "[red]✗[/red]"
        tbl.add_row(
            r.case_id[:22],
            r.expected_level,
            r.actual_level,
            mark,
            f"{r.dimension_accuracy:.0%}",
        )

    console.print(tbl)

    if output:
        console.print(f"\n[dim]Results saved to {output}[/dim]")
