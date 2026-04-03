"""Basic usage example for research-rubric."""

from research_rubric.rubric import evaluate

# Paste or load any qualitative research report
text = """
This study employed thematic analysis to examine user trust in AI systems.
We conducted in-depth interviews with 16 participants until thematic saturation
was reached — no new themes emerged after the twelfth interview.

Reflexivity was maintained throughout. The researcher's positionality as a
former product designer was acknowledged as a potential source of bias. A
reflexivity journal was kept to document assumptions.

Triangulation was achieved through member checking with six participants and
independent coding by two researchers. An audit trail of analytical decisions
was maintained.

Limitations: findings are context-specific to UK-based professional users
aged 25-45. Transferability to other demographics should be assessed carefully.

As one participant noted: "I only started trusting it after I could verify
the recommendations myself." Another described: "transparency is everything —
if I can't see why, I don't trust it."
"""

report = evaluate(text, source="example_report.txt")

print(f"Overall: {report.overall_score:.0f}/100 ({report.overall_level.value.upper()})")
print()

for dim in report.dimensions:
    print(f"  {dim.label:<26} {dim.score:5.0f}  ({dim.level.value})")
    for issue in dim.issues:
        print(f"    ✗ {issue}")

print()
print("JSON output:")
import json
print(json.dumps(report.to_dict(), indent=2))
