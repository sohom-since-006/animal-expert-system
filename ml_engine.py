"""
ml_engine.py — Lightweight ML classifier for Hybrid Expert System.

Trains a Random Forest on synthetic data generated from rules.
Provides an independent confidence score that fuses with rule engine.
"""

import os
import json
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

from rule_engine import RULES

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'data', 'ml_model.pkl')
ENCODER_PATH = os.path.join(os.path.dirname(__file__), 'data', 'ml_encoder.pkl')

# Feature order must be consistent
FEATURE_ORDER = [
    "has_backbone",      # 0=none/None, 1=yes, -1=no
    "warm_blooded",      # same
    "has_wings",         # same
    "aquatic",           # same
    "body_covering",     # encoded fur=1, feathers=2, scales=3, moist_skin=4, shell=5, none=6, unknown=0
    "reproduction",      # encoded live_birth=1, eggs_land=2, eggs_water=3, metamorphosis=4, unknown=0
    "diet",              # encoded carnivore=1, herbivore=2, omnivore=3, insectivore=4, any=5, unknown=0
]

COVER_MAP = {"fur":1, "feathers":2, "scales":3, "moist_skin":4, "shell":5, "none":6, None:0}
REPRO_MAP = {"live_birth":1, "eggs_land":2, "eggs_water":3, "metamorphosis":4, None:0}
DIET_MAP = {"carnivore":1, "herbivore":2, "omnivore":3, "insectivore":4, "any":5, None:0}
BOOL_MAP = {1:1, 0:-1, None:0, "":0}


def _encode_sample(facts):
    """Convert facts dict to numeric feature vector."""
    return [
        BOOL_MAP.get(facts.get("has_backbone"), 0),
        BOOL_MAP.get(facts.get("warm_blooded"), 0),
        BOOL_MAP.get(facts.get("has_wings"), 0),
        BOOL_MAP.get(facts.get("aquatic"), 0),
        COVER_MAP.get(facts.get("body_covering"), 0),
        REPRO_MAP.get(facts.get("reproduction"), 0),
        DIET_MAP.get(facts.get("diet"), 0),
    ]


def _generate_training_data():
    """Create synthetic training dataset from expert rules."""
    X, y = [], []
    # From each rule, create positive samples by varying 1-2 features
    np.random.seed(42)
    for rule in RULES:
        base = rule["conditions"].copy()
        target = f"class_{rule['class_id']}"
        if rule["order_id"]:
            target = f"order_{rule['order_id']}"

        # Original rule sample (strong positive)
        X.append(_encode_sample(base))
        y.append(target)

        # Slightly noisy variants (partial matches)
        keys = list(base.keys())
        for _ in range(8):
            variant = base.copy()
            if keys:
                k = np.random.choice(keys)
                if np.random.rand() > 0.5:
                    variant[k] = None  # drop a fact
                else:
                    # slight mutation for categorical
                    if k == "body_covering":
                        variant[k] = np.random.choice(list(COVER_MAP.keys())[:6])
                    elif k == "reproduction":
                        variant[k] = np.random.choice(list(REPRO_MAP.keys())[:4])
                    elif k == "diet":
                        variant[k] = np.random.choice(list(DIET_MAP.keys())[:5])
                    elif k in ["has_backbone","warm_blooded","has_wings","aquatic"]:
                        variant[k] = np.random.choice([0,1])
            X.append(_encode_sample(variant))
            y.append(target)

    # Add random counter-examples with different labels
    for _ in range(len(RULES) * 3):
        random_facts = {
            "has_backbone": np.random.choice([0,1,None], p=[0.3,0.6,0.1]),
            "warm_blooded": np.random.choice([0,1,None], p=[0.3,0.5,0.2]),
            "has_wings": np.random.choice([0,1,None], p=[0.6,0.3,0.1]),
            "aquatic": np.random.choice([0,1,None], p=[0.5,0.3,0.2]),
            "body_covering": np.random.choice(list(COVER_MAP.keys())),
            "reproduction": np.random.choice(list(REPRO_MAP.keys())),
            "diet": np.random.choice(list(DIET_MAP.keys())),
        }
        # Determine closest rule by exact match count
        best = None
        best_score = -1
        for rule in RULES:
            score = sum(1 for k,v in rule["conditions"].items() if random_facts.get(k) == v)
            if score > best_score:
                best_score = score
                best = rule
        if best:
            label = f"order_{best['order_id']}" if best['order_id'] else f"class_{best['class_id']}"
            X.append(_encode_sample(random_facts))
            y.append(label)

    return np.array(X), np.array(y)


def train_and_save():
    print("🧠 Training Hybrid ML model from expert rules...")
    X, y = _generate_training_data()
    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
    )
    model.fit(X, y_enc)

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(model, f)
    with open(ENCODER_PATH, 'wb') as f:
        pickle.dump(le, f)

    print(f"✅ ML model trained on {len(X)} synthetic samples, {len(le.classes_)} classes.")
    print("   Classes:", le.classes_.tolist())
    return model, le


def load_model():
    if os.path.exists(MODEL_PATH) and os.path.exists(ENCODER_PATH):
        with open(MODEL_PATH, 'rb') as f:
            model = pickle.load(f)
        with open(ENCODER_PATH, 'rb') as f:
            le = pickle.load(f)
        return model, le
    return train_and_save()


def predict(facts):
    """
    Returns dict with:
      - label: predicted class/order label
      - confidence: probability (0-100)
      - class_id / order_id: parsed from label
    """
    try:
        model, le = load_model()
    except Exception as e:
        print(f"⚠️ ML engine unavailable: {e}")
        return {"confidence": None, "label": None, "class_id": None, "order_id": None}

    vec = np.array([_encode_sample(facts)])
    proba = model.predict_proba(vec)[0]
    pred_idx = np.argmax(proba)
    confidence = int(round(proba[pred_idx] * 100))
    label = le.inverse_transform([pred_idx])[0]

    class_id = None
    order_id = None
    if label.startswith("class_"):
        class_id = int(label.split("_")[1])
    elif label.startswith("order_"):
        order_id = int(label.split("_")[1])
        # infer class from order -> reverse lookup via rules
        for r in RULES:
            if r["order_id"] == order_id:
                class_id = r["class_id"]
                break

    return {
        "confidence": confidence,
        "label": label,
        "class_id": class_id,
        "order_id": order_id,
    }


if __name__ == '__main__':
    train_and_save()
