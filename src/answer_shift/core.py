"""Pair snapshots and score semantic changes for human review."""

from __future__ import annotations

import json
from typing import Protocol


MAX_CASES = 100


class BatchScorer(Protocol):
    def score_many(self, pairs: list[tuple[str, str]]) -> list[dict[str, float]]: ...


def read_jsonl(text: str) -> dict[str, str]:
    rows: dict[str, str] = {}
    for line_number, raw in enumerate(text.splitlines(), 1):
        if not raw.strip():
            continue
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON on line {line_number}: {exc.msg}") from exc
        if not isinstance(obj, dict) or not isinstance(obj.get("case_id"), str) or not isinstance(obj.get("answer"), str):
            raise ValueError(f"line {line_number} needs string case_id and answer")
        case_id = obj["case_id"].strip()
        answer = obj["answer"].strip()
        if not case_id or not answer or case_id in rows:
            raise ValueError(f"line {line_number} has empty answer/id or duplicate case_id")
        if len(answer) > 1500:
            raise ValueError(f"line {line_number} answer exceeds 1500 characters; split into atomic cases")
        rows[case_id] = answer
    if not rows:
        raise ValueError("snapshot is empty")
    if len(rows) > MAX_CASES:
        raise ValueError(f"MVP limit is {MAX_CASES} cases per snapshot")
    return rows


def compare(baseline: dict[str, str], candidate: dict[str, str], scorer: BatchScorer, threshold: float = 0.70) -> dict:
    if not 0.0 < threshold < 1.0:
        raise ValueError("threshold must be between 0 and 1")
    common = sorted(baseline.keys() & candidate.keys())
    pairs = []
    for key in common:
        pairs.extend([(baseline[key], candidate[key]), (candidate[key], baseline[key])])
    scores = scorer.score_many(pairs)
    if len(scores) != len(pairs):
        raise ValueError("model returned an unexpected number of scores")
    changes = []
    for i, key in enumerate(common):
        forward, backward = scores[2 * i : 2 * i + 2]
        contradiction = max(forward["contradiction"], backward["contradiction"])
        if baseline[key] == candidate[key]:
            verdict = "exact_match"
        elif contradiction >= threshold:
            verdict = "possible_meaning_change"
        elif min(forward["entailment"], backward["entailment"]) >= threshold:
            verdict = "likely_same_meaning"
        else:
            verdict = "needs_review"
        changes.append({
            "case_id": key,
            "baseline": baseline[key],
            "candidate": candidate[key],
            "verdict": verdict,
            "contradiction_signal": round(contradiction, 4),
            "bidirectional_entailment_signal": round(min(forward["entailment"], backward["entailment"]), 4),
        })
    return {
        "model": "cross-encoder/nli-MiniLM2-L6-H768",
        "compared": len(common),
        "removed_case_ids": sorted(baseline.keys() - candidate.keys()),
        "added_case_ids": sorted(candidate.keys() - baseline.keys()),
        "changes": changes,
        "disclaimer": "A semantic change may be an improvement, not a regression. Review the original task and ground truth.",
    }
