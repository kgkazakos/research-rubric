"""Optional LLM enrichment for research-rubric.

DSPy-inspired structured prompting — one API call, structured JSON output,
per-dimension rationale plus an executive summary.

Usage:
    report = evaluate(text)
    report = enrich_with_llm(text, report, backend="anthropic")
"""

from __future__ import annotations

import json
import warnings
from typing import Optional

from .models import RubricReport

_SYSTEM = (
    "You are an expert in qualitative research methodology. "
    "Evaluate research documents for rigour and quality. "
    "Respond ONLY with a valid JSON object — no markdown, no preamble."
)

_DIMENSIONS = [
    "saturation", "bias_awareness", "evidence_linkage", "triangulation",
    "reflexivity", "transferability", "credibility", "rigor_of_analysis",
]


def enrich_with_llm(
    text: str,
    report: RubricReport,
    backend: str,
    model: Optional[str] = None,
) -> RubricReport:
    """
    Enrich a pre-computed RubricReport with LLM-generated rationale.

    Parameters
    ----------
    text : str
        Original research document text.
    report : RubricReport
        Rule-based report from ``evaluate()``.
    backend : str
        One of ``'openai'``, ``'anthropic'``, ``'gemini'``.
    model : str, optional
        Override the default model for the chosen backend.

    Returns
    -------
    RubricReport
        The same report with ``llm_summary`` and per-dimension
        ``llm_rationale`` fields populated.
    """
    dim_lines = "\n".join(
        f"  {d.label}: {d.score:.0f}/100 ({d.level.value})"
        + (f" — {d.issues[0]}" if d.issues else "")
        for d in report.dimensions
    )
    excerpt = " ".join(text.split()[:2000])

    prompt = f"""You are reviewing a qualitative research document.

Rule-based quality scores:
{dim_lines}
Overall: {report.overall_score:.0f}/100 ({report.overall_level.value})

Research text excerpt (first 2 000 words):
{excerpt}

Return ONLY this JSON structure:
{{
  "overall_summary": "<2-3 sentence executive assessment>",
  "dimension_rationales": {{
    "saturation": "<one sentence>",
    "bias_awareness": "<one sentence>",
    "evidence_linkage": "<one sentence>",
    "triangulation": "<one sentence>",
    "reflexivity": "<one sentence>",
    "transferability": "<one sentence>",
    "credibility": "<one sentence>",
    "rigor_of_analysis": "<one sentence>"
  }},
  "top_recommendation": "<single most impactful improvement>"
}}"""

    result = _dispatch(prompt, backend, model)
    if result is None:
        return report

    report.llm_summary = result.get("overall_summary")
    rationales = result.get("dimension_rationales", {})
    for dim in report.dimensions:
        if dim.name in rationales:
            dim.llm_rationale = rationales[dim.name]

    return report


# ---------------------------------------------------------------------------
# Backend dispatch
# ---------------------------------------------------------------------------


def _dispatch(prompt: str, backend: str, model: Optional[str]) -> Optional[dict]:
    try:
        if backend == "openai":
            return _openai(prompt, model or "gpt-4o-mini")
        if backend == "anthropic":
            return _anthropic(prompt, model or "claude-haiku-4-5-20251001")
        if backend == "gemini":
            return _gemini(prompt, model or "gemini-3.1-pro-preview")
        warnings.warn(f"Unknown LLM backend: {backend!r}")
    except Exception as exc:  # pragma: no cover
        warnings.warn(f"LLM enrichment failed ({backend}): {exc}")
    return None


def _parse(raw: str) -> Optional[dict]:
    raw = raw.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as exc:  # pragma: no cover
        warnings.warn(f"LLM returned invalid JSON: {exc}")
        return None


def _openai(prompt: str, model: str) -> Optional[dict]:
    from openai import OpenAI  # type: ignore

    client = OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return _parse(response.choices[0].message.content or "")


def _anthropic(prompt: str, model: str) -> Optional[dict]:
    import anthropic  # type: ignore

    client = anthropic.Anthropic()
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system=_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    return _parse(response.content[0].text)


def _gemini(prompt: str, model: str) -> Optional[dict]:
    import google.generativeai as genai  # type: ignore

    client = genai.GenerativeModel(
        model_name=model,
        system_instruction=_SYSTEM,
    )
    response = client.generate_content(
        prompt,
        generation_config={"temperature": 0.2},
    )
    return _parse(response.text)
