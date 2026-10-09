# AnswerShift

AnswerShift compares two saved batches of AI-generated answers by `case_id`. A local natural-language-inference (NLI) model spots possible meaning changes even when wording differs. It is a small review aid for model or prompt upgrades, not a live model runner and not a pass/fail quality guarantee.

## Who and when

For AI application developers who keep a small set of representative input cases. After switching a model, prompt, or serving layer, save old and new answers as JSONL and inspect possible semantic shifts before shipping. The recurring task is upgrade review; the output is an auditable JSON report with matched, added, and removed cases.

Non-goals: calling model APIs, generating ground truth, deciding whether a change is beneficial, comprehensive evaluation, or replacing [Promptfoo](https://github.com/promptfoo/promptfoo) and similar test platforms.

## Run

Requires Python 3.11+. First run downloads the [Apache-2.0 English NLI model](https://huggingface.co/cross-encoder/nli-MiniLM2-L6-H768); inference runs locally afterward. No model API key is needed.

```bash
uv sync --python 3.11
uv run answer-shift --baseline examples/baseline.jsonl --candidate examples/candidate.jsonl --out report.local.json
cat report.local.json
uv run python -m unittest discover -s tests -v
```

Each input line is a JSON object such as `{"case_id":"region","answer":"The service is deployed in EU-West."}`. `case_id` must be unique within a file. AnswerShift compares each shared case in both NLI directions. The example deliberately changes a deployment region, paraphrases a price, and leaves a support statement unchanged. The report marks possible meaning changes, likely same meaning, exact matches, and cases missing from either file.

The model's scores are **review signals**, not calibrated probabilities. A change may be an improvement. Compare with the original prompt, expected behavior and real-world evidence before gating a release. The tool never uploads answer contents, but first-run model download uses Hugging Face.

## Why this wedge

Observed on 2026-10-09: a [2025 Dify report](https://github.com/langgenius/dify/issues/21898) shows a structured-output regression after a version change; an [OpenClaw report from September 2026](https://github.com/openclaw/openclaw/issues/143843) describes user-visible prompt behavior changing between releases; [Ollama's August 2026 report](https://github.com/ollama/ollama/issues/17933) documents a serving-path change that made schema-constrained outputs silently fail. These independent events, spread over time, support recurring upgrade risk, not measured demand for this exact tool. Active [Promptfoo development](https://github.com/promptfoo/promptfoo) and the repeated issue stream indicate attention to AI evaluation; the hypothesis is that a no-provider, two-file snapshot comparison is easier to adopt for a small project and naturally fits CI artifacts. We have not tested that hypothesis with users.

Compared with full evaluation platforms, AnswerShift intentionally does not configure prompts, providers, live runs, dashboards or paid judges. The AI core is local bidirectional NLI over *already saved* answer pairs; a text diff alone would not distinguish paraphrase from a changed claim. No code or prompt text from reference projects is copied.

## Limits

- English-trained model; Chinese, code, JSON payloads, multi-step answers and nuanced numerical claims may be misclassified.
- Up to 100 cases and 1,500 characters per answer in this MVP. Split complex responses into atomic cases to avoid model truncation (512 tokens).
- The old answer is not assumed correct. A `possible_meaning_change` is not automatically a regression.
- The MVP acceptance criterion is a clean-install example run, passing tests, case matching and a reviewable offline report. Real-user validation remains open.

Application code is MIT licensed. Model weights are not vendored; use is governed by the model's Apache-2.0 license.
