# AI / Machine Learning Component - Intelligent Customer Intent Detector

> **Assigned Team Member:** AI / ML Developer (Member 3)  
> **Technologies:** Python 3.10+, scikit-learn, pandas, joblib, regex NLP.

---

## 1. Directory Structure

```
ml_model/
├── config.py              # Centralized paths and decision thresholds
├── preprocess.py          # Unicode normalizer, script-ratio language detector & clause splitter
├── privacy.py             # PII detector with Luhn card checksum and protected span exclusion
├── entity_extractor.py    # Context-aware regex rules & product catalog gazetteer
├── intent_detector.py     # TF-IDF FeatureUnion (word + char_wb) + Logistic Regression pipeline
├── analyzer.py            # Primary pipeline orchestrator implementing Analyzer.analyze()
├── train.py               # Model trainer supporting cross-validation & feedback retraining
├── evaluate.py            # Offline test evaluation, classification report & threshold curves
├── data/                  # Datasets & Knowledge assets
│   ├── intents.json       # 10 intent labels, display names, teams & required entities
│   ├── products.txt       # Product catalog names
│   ├── training_data.csv  # Training dataset (English, Kannada script, Romanized Kanglish)
│   └── test_messages.csv  # Held-out benchmark test dataset
├── models/                # Generated model artifacts
│   ├── intent_model.joblib# Serialized scikit-learn pipeline
│   └── model_info.json    # Training metadata and holdout metrics
└── README.md              # This AI/ML component guide
```

---

## 2. Independent Development & Commands

Member 3 can work, iterate on dataset examples, adjust threshold values, and test models completely on their laptop without running the web server!

### Train the Intent Model:
```powershell
python -m ml_model.train
```
*(Optionally include reviewed data from the database with `python -m ml_model.train --include-feedback`).*

### Evaluate Model Accuracy on Held-Out Test Data:
```powershell
python -m ml_model.evaluate
```
Reports overall accuracy, precision, recall, F1-scores, per-language accuracy (`en`, `kn`, `kn-latn`), and coverage vs accuracy across different confidence thresholds.

### Test Predictions in Python Shell:
```python
from ml_model.analyzer import Analyzer

analyzer = Analyzer()
result = analyzer.analyze("My payment failed but Rs. 2,499 was deducted. Please refund it urgently.")
print("Status:", result["status"])
print("Intents:", result["intents"])
print("Entities:", result["entities"])
print("Clarification:", result["clarification_question"])
```

---

## 3. Thresholds & Decision Parameters (`ml_model/config.py`)

| Parameter | Default | Meaning |
|---|---|---|
| `ACCEPT_THRESHOLD` | `0.55` | Confidence required to auto-route without review |
| `REVIEW_THRESHOLD` | `0.35` | Below this, marked `unknown` and queued for human review |
| `MARGIN_THRESHOLD` | `0.15` | Minimum score difference between top 2 intents; smaller gap triggers clarification |
| `CLAUSE_MIN_CONF` | `0.40` | Minimum clause score to be included as a secondary intent |
