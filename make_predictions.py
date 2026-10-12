import joblib
import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

files = list(Path(".").glob("*.csv"))

def find_file(suffix):
    return next(f for f in files if f.name.endswith(suffix))

train = pd.read_csv(find_file("train.csv"))
test = pd.read_csv(find_file("test_unlabelled.csv"))
partners = pd.read_csv(find_file("partners.csv"))
products = pd.read_csv(find_file("products.csv"))

# Exclude uncertain labels from supervised training
train = train[train["is_fraud"].notna()].copy()
train["is_fraud"] = train["is_fraud"].astype(int)

# Join reference data consistently
partners = partners.drop_duplicates("partner_id")
products = products.drop_duplicates("sku")

def add_features(df):
    df = df.merge(
        partners, on="partner_id", how="left",
        validate="many_to_one"
    )
    df = df.merge(
        products, on="sku", how="left",
        validate="many_to_one"
    )

    df["submitted_at"] = pd.to_datetime(
        df["submitted_at"], errors="coerce"
    )
    df["onboarded_date"] = pd.to_datetime(
        df["onboarded_date"], errors="coerce"
    )
    df["submitted_month"] = df["submitted_at"].dt.month
    df["submitted_dayofweek"] = (
        df["submitted_at"].dt.dayofweek
    )
    df["partner_tenure_days"] = (
        df["submitted_at"] - df["onboarded_date"]
    ).dt.days
    df["claim_to_list_price_ratio"] = (
        df["claim_amount_inr"]
        / df["list_price_inr"].replace(0, np.nan)
    )

    return df

train = add_features(train)
test = add_features(test)

numeric = [
    "days_since_purchase", "claim_amount_inr",
    "customer_prior_claims", "submitted_month",
    "submitted_dayofweek", "partner_tenure_days",
    "list_price_inr", "warranty_months",
    "claim_to_list_price_ratio",
]
categorical = [
    "sku", "photo_attached", "partner_inspected",
    "source", "city", "partner_type", "family",
]
text = "claim_description"
features = numeric + categorical + [text]

preprocessor = ColumnTransformer([
    ("numeric", Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ]), numeric),
    ("categorical", Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore")),
    ]), categorical),
    ("description", TfidfVectorizer(
        max_features=3000, ngram_range=(1, 2)
    ), text),
])

model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", LogisticRegression(
        class_weight="balanced", max_iter=1000,
        random_state=42
    )),
])

model.fit(train[features], train["is_fraud"])
joblib.dump(model, "fraud_model.joblib")
print("Saved fraud_model.joblib")
scores = model.predict_proba(test[features])[:, 1]

# Use the exact required submission column order
submission = pd.DataFrame({
    "claim_id": test["claim_id"],
    "score": scores,
})

assert len(submission) == len(test) == 2252
assert submission["claim_id"].is_unique
assert submission["score"].between(0, 1).all()
assert submission["score"].notna().all()

submission.to_csv("predictions.csv", index=False)

print("Created predictions.csv")
print("Rows:", len(submission))
print("Columns:", submission.columns.tolist())
print("\nHighest-ranked claims:")
print(submission.nlargest(10, "score").to_string(index=False))
