"""Local pretrained NLI inference for paired answers."""

MODEL_ID = "cross-encoder/nli-MiniLM2-L6-H768"
LABELS = ("contradiction", "entailment", "neutral")


class LocalNLI:
    def __init__(self) -> None:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
        self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_ID)
        self.model.eval()

    def score_many(self, pairs: list[tuple[str, str]]) -> list[dict[str, float]]:
        import torch

        results: list[dict[str, float]] = []
        for start in range(0, len(pairs), 16):
            batch = pairs[start : start + 16]
            features = self.tokenizer(
                [p[0] for p in batch], [p[1] for p in batch],
                return_tensors="pt", padding=True, truncation=True, max_length=512,
            )
            with torch.inference_mode():
                probabilities = self.model(**features).logits.softmax(dim=-1).tolist()
            results.extend(dict(zip(LABELS, row, strict=True)) for row in probabilities)
        return results
