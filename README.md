# research-rubric

**CPR Orbital #06 · Apr 24, 2026**

Evaluate qualitative research quality across eight evidence-based dimensions. Works fully rule-based with no API keys required. LLM backends (OpenAI, Anthropic, Gemini) are optional narrative enrichment only.

---

## The problem

A qualitative study lands in your inbox. The methodology section is three paragraphs. Does it meet CHI standards? Is it credible enough to drive a product decision? You read it twice and still aren't sure what's weak and what's not.

research-rubric gives you an 8-dimension structured answer in seconds.

---

## Eight quality dimensions

| Dimension | What it checks |
|---|---|
| **Thematic Saturation** | Evidence of saturation and sample-size rationale |
| **Bias Awareness** | Researcher positionality, reflexivity, bracketing |
| **Evidence Linkage** | Claim-to-evidence ratio, participant quotes |
| **Triangulation** | Multiple data sources, member checking, inter-rater |
| **Reflexivity** | Researcher self-reflection and positionality disclosure |
| **Transferability** | Context description, limitations, scope |
| **Credibility** | Audit trail, negative case analysis, member checking |
| **Rigor of Analysis** | Named methodology, coding process, systematic approach |

Each dimension scores 0–100. The overall score is the mean. Levels: **high** (≥70) · **medium** (≥40) · **low** (<40).

---

## Install

```bash
pip install research-rubric
# With scikit-learn (improves nothing here — no ML, pure rule-based):
pip install "research-rubric[nlp]"
# With LLM backends:
pip install "research-rubric[anthropic]"   # or openai, gemini, all
```

---

## CLI usage

### Score a report

```bash
research-rubric score my_report.txt
research-rubric score my_report.txt --json
research-rubric score my_report.txt --output results.json
research-rubric score my_report.txt --llm-backend anthropic
```

**Example output:**

```
╭─ research-rubric · CPR Orbital #06 ─────────────────────────────╮
│ usability_study.txt  1,842 words                                  │
│ Overall quality: ◑ 54/100  (MEDIUM)                               │
╰──────────────────────────────────────────────────────────────────╯

 Dimension              Score  Level     Top issue
 ─────────────────────────────────────────────────────────────────
 Thematic Saturation      85   ● high    —
 Bias Awareness           62   ● high    —
 Evidence Linkage         48   ◑ medium  Claims outnumber evidence
 Triangulation            70   ● high    —
 Reflexivity              20   ○ low     Reflexivity not addressed
 Transferability          55   ◑ medium  —
 Credibility              38   ○ low     No credibility procedures
 Rigor of Analysis        82   ● high    —
```

### JSON output

```bash
research-rubric score report.txt --json
```

```json
{
  "source": "report.txt",
  "word_count": 1842,
  "overall_score": 57.5,
  "overall_level": "medium",
  "dimensions": [
    {
      "name": "saturation",
      "label": "Thematic Saturation",
      "score": 85.0,
      "level": "high",
      "issues": [],
      "suggestions": [],
      "llm_rationale": null
    }
  ],
  "llm_summary": null
}
```

### Run the eval suite

```bash
research-rubric eval evals_dataset.json
research-rubric eval evals_dataset.json --json
```

Eval dataset format (JSON array):

```json
[
  {
    "id": "case-01",
    "description": "High quality study with explicit saturation",
    "expected_level": "high",
    "text": "...",
    "expected_ranges": {
      "saturation": [50, 100],
      "reflexivity": [50, 100]
    }
  }
]
```

---

## Python API

```python
from research_rubric.rubric import evaluate

report = evaluate(text, source="my_report.txt")

print(f"Overall: {report.overall_score:.0f}/100 ({report.overall_level.value})")

for dim in report.dimensions:
    print(f"  {dim.label}: {dim.score:.0f} — {dim.level.value}")
    for issue in dim.issues:
        print(f"    ✗ {issue}")
```

### LLM enrichment (community extension)

`llm.py` ships as reference scaffolding — the dispatch pattern, prompt structure,
and JSON parsing are fully implemented for OpenAI, Anthropic, and Gemini. Activate
by installing the optional extras and passing `--llm-backend`. Not tested in CI;
the rule-based core is the shipped deliverable.

```python
from research_rubric.rubric import evaluate
from research_rubric.llm import enrich_with_llm

report = evaluate(text)
report = enrich_with_llm(text, report, backend="anthropic")  # optional extension

print(report.llm_summary)
for dim in report.dimensions:
    print(f"  {dim.label}: {dim.llm_rationale}")
```

### Eval framework

```python
from research_rubric.evals import EvalCase, run_eval

cases = [
    EvalCase(
        id="hq-01",
        text=high_quality_text,
        expected_level="high",
        expected_ranges={"saturation": (50, 100), "reflexivity": (50, 100)},
    )
]

suite = run_eval(cases)
print(f"Level accuracy: {suite.level_accuracy:.0%}")
print(f"Dimension accuracy: {suite.mean_dimension_accuracy:.0%}")
```

---

## Design principles

- **No API keys required** — full rule-based evaluation with zero external calls
- **LLM as community extension** — `llm.py` ships as open scaffolding with the dispatch pattern and prompt structure implemented; not tested in CI
- **Eval-first** — a labeled dataset and eval runner ship with the tool so you can measure rubric performance on your own corpus
- **CI-ready** — JSON output mode for pipeline integration

---

## Part of the CPR Ecosystem

`research-rubric` is **CPR Orbital #06** in a 40-tool open-source series for AI-native product research.

Related tools:
- [**qual-sniffer**](https://github.com/kgkazakos/qual-sniffer) (#03) — detects methodological weaknesses in discussion guides
- [**uxr-prompt-pack**](https://github.com/kgkazakos/uxr-prompt-pack) (#02) — versioned LLM prompt library for UX research tasks
- [**survey-cleaner**](https://github.com/kgkazakos/survey-cleaner) (#04) — removes speeders and straight-liners from survey exports
- **insight-differ** (#05) — compares two research reports, surfaces contradictions and gaps *(coming Apr 17)*

Part of [Computational Product Research (CPR)](https://github.com/kgkazakos) — a discipline combining rigorous research methods with LLM augmentation.

---

## License

MIT © 2026 Kostas Kazakos
