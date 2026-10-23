"""Evaluate the language layer on a labeled set.

Run:  python -m app.evaluation.language_eval

CAUTION: this set was written together with the lexicons, so scores are optimistic.
Add independent cases (real user transcripts, speakers of each language) before
trusting the numbers.
"""

import json
from pathlib import Path
from typing import Any

from app.language.analyzer import analyze_text

DEFAULT_PATH = Path(__file__).resolve().parents[2] / "data" / "eval" / "language_cases.json"
FIELDS = ("primary_language", "script", "style", "response_language")


def evaluate(path: Path = DEFAULT_PATH) -> dict[str, Any]:
    cases = json.loads(path.read_text(encoding="utf-8"))
    correct = dict.fromkeys(FIELDS, 0)
    all_correct = 0
    failures: list[dict[str, Any]] = []

    for case in cases:
        analysis = analyze_text(case["text"], selected_language=case.get("selected_language"))
        actual = {
            "primary_language": analysis.primary_language,
            "script": analysis.script.value,
            "style": analysis.style,
            "response_language": analysis.response_language,
        }
        wrong = {f: (case[f], actual[f]) for f in FIELDS if case[f] != actual[f]}
        for field in FIELDS:
            correct[field] += field not in wrong
        if wrong:
            failures.append({"text": case["text"], "expected_vs_actual": wrong})
        else:
            all_correct += 1

    total = len(cases)
    return {
        "total": total,
        "accuracy": {f: round(correct[f] / total, 3) for f in FIELDS},
        "all_fields_accuracy": round(all_correct / total, 3),
        "failures": failures,
    }


if __name__ == "__main__":
    print(json.dumps(evaluate(), ensure_ascii=False, indent=2))