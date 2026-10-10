import json
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from ml_model import config
from ml_model.intent_detector import IntentDetector


def main():
    labels = list(json.loads(config.INTENTS_PATH.read_text(encoding="utf-8")).keys())
    det = IntentDetector(config.MODEL_PATH, labels)

    if not config.TEST_CSV.exists():
        raise SystemExit(f"Test CSV not found at {config.TEST_CSV}")

    df = pd.read_csv(config.TEST_CSV).dropna(subset=["text", "intent"])
    rows = []
    for text, true_label in zip(df.text, df.intent):
        top = det.predict(text, top_k=1)[0]
        rows.append((true_label, top["label"], top["confidence"]))

    res = pd.DataFrame(rows, columns=["true", "pred", "score"])
    res["language"] = df.language.values if "language" in df.columns else "unknown"

    print(f"Evaluation Mode: {det.mode} | Test Rows: {len(res)}")
    acc = accuracy_score(res.true, res.pred)
    print(f"Overall Accuracy: {acc:.3f}\n")
    print("Classification Report:")
    print(classification_report(res.true, res.pred, zero_division=0))

    if "language" in res.columns:
        print("Per-Language Accuracy:")
        res["correct"] = res.true == res.pred
        print(res.groupby("language")["correct"].agg(["mean", "count"]).to_string())

    print("\nThreshold Coverage Table:")
    for t in (0.30, 0.40, 0.50, 0.55, 0.60, 0.70):
        kept = res[res.score >= t]
        acc_kept = (kept.true == kept.pred).mean() if len(kept) > 0 else float("nan")
        print(
            f"  Threshold >= {t:.2f}: Coverage {len(kept)/len(res):.1%}, "
            f"Accuracy on covered {acc_kept:.1%} ({len(kept)}/{len(res)} messages)"
        )


if __name__ == "__main__":
    main()
