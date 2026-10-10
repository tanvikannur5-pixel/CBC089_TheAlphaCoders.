import argparse
import json
from datetime import datetime, timezone
import joblib
import pandas as pd
from sklearn.metrics import classification_report, f1_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from ml_model import config
from ml_model.intent_detector import build_pipeline


def load_data(include_feedback: bool) -> pd.DataFrame:
    df = pd.read_csv(config.TRAIN_CSV).dropna(subset=["text", "intent"])
    labels = set(json.loads(config.INTENTS_PATH.read_text(encoding="utf-8")).keys())
    bad_labels = set(df.intent) - labels
    if bad_labels:
        raise SystemExit(f"Unknown labels in CSV (not in intents.json): {bad_labels}")

    if include_feedback:
        try:
            from database.database import get_feedback_rows
            extra = pd.DataFrame(get_feedback_rows(), columns=["text", "intent"])
            if len(extra) > 0:
                print(f"Adding {len(extra)} reviewed rows from the database.")
                df = pd.concat([df[["text", "intent"]], extra], ignore_index=True)
        except Exception as e:
            print(f"Notice: Could not load feedback rows from database ({e}); proceeding with CSV.")

    return df.drop_duplicates(subset=["text"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-feedback", action="store_true", help="Include human corrections from DB")
    args = parser.parse_args()

    df = load_data(args.include_feedback)
    counts = df.intent.value_counts()
    print("Dataset distribution by intent:")
    print(counts.to_string())
    print(f"\nTotal training examples: {len(df)}")

    min_count = counts.min()
    if min_count < 3:
        raise SystemExit("Need at least 3 examples per intent to train. Add more data first.")

    # Train / test split for metrics
    test_size = 0.2 if min_count >= 5 else 0.1
    stratify = df.intent if min_count >= 2 else None
    X_tr, X_te, y_tr, y_te = train_test_split(
        df.text, df.intent, test_size=test_size, stratify=stratify, random_state=42
    )

    model = build_pipeline().fit(X_tr, y_tr)
    pred = model.predict(X_te)
    print("\nHoldout Validation Report:")
    print(classification_report(y_te, pred, zero_division=0))
    macro_f1 = f1_score(y_te, pred, average="macro", zero_division=0)

    # Cross validation if enough samples
    cv_mean = macro_f1
    if min_count >= 3:
        folds = min(5, int(min_count))
        try:
            cv = cross_val_score(
                build_pipeline(),
                df.text,
                df.intent,
                cv=StratifiedKFold(folds, shuffle=True, random_state=42),
                scoring="f1_macro",
            )
            cv_mean = float(cv.mean())
            print(f"{folds}-fold CV macro-F1: {cv.mean():.3f} (+/- {cv.std():.3f})")
        except Exception as e:
            print(f"CV skipped: {e}")

    # Retrain on full dataset for production artifact
    final_pipeline = build_pipeline().fit(df.text, df.intent)
    config.MODEL_PATH.parent.mkdir(exist_ok=True)
    joblib.dump(final_pipeline, config.MODEL_PATH)

    info = {
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "n_examples": int(len(df)),
        "holdout_macro_f1": round(float(macro_f1), 3),
        "cv_macro_f1": round(float(cv_mean), 3),
        "note": "Trained on hackathon seed dataset.",
    }
    config.MODEL_INFO_PATH.write_text(json.dumps(info, indent=2), encoding="utf-8")
    print(f"\nSuccessfully saved trained model to: {config.MODEL_PATH}")


if __name__ == "__main__":
    main()
