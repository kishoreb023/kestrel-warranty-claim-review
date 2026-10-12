
import pandas as pd
import numpy as np
from pathlib import Path

from sklearn.model_selection import GroupShuffleSplit
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score

# Locate files despite their long filenames
files = list(Path(".").glob("*.csv"))
train_file = next(f for f in files if f.name.endswith("train.csv"))


df = pd.read_csv(train_file)

# Load partner and product reference data
partners_file = next(
    f for f in files if f.name.endswith("partners.csv")
)
products_file = next(
    f for f in files if f.name.endswith("products.csv")
)

partners = pd.read_csv(partners_file)
products = pd.read_csv(products_file)

# Remove duplicate reference keys before joining
partners = partners.drop_duplicates("partner_id")
products = products.drop_duplicates("sku")

# Join reference data to claims
df = df.merge(
    partners, on="partner_id", how="left",
    validate="many_to_one"
)
df = df.merge(
    products, on="sku", how="left",
    validate="many_to_one"
)

# Partner tenure when the claim was submitted
df["submitted_at"] = pd.to_datetime(
    df["submitted_at"], errors="coerce"
)
partners["onboarded_date"] = pd.to_datetime(
    partners["onboarded_date"], errors="coerce"
)

# Use onboarding date joined from the partner table
df["onboarded_date"] = pd.to_datetime(
    df["onboarded_date"], errors="coerce"
)
df["partner_tenure_days"] = (
    df["submitted_at"] - df["onboarded_date"]
).dt.days

# Product price relative to the claim amount
df["claim_to_list_price_ratio"] = (
    df["claim_amount_inr"]
    / df["list_price_inr"].replace(0, np.nan)
)


# Exclude rows with unknown outcomes
df = df[df["is_fraud"].notna()].copy()
df["is_fraud"] = df["is_fraud"].astype(int)

# Basic feature engineering
df["submitted_at"] = pd.to_datetime(
    df["submitted_at"], errors="coerce"
)
df["submitted_month"] = df["submitted_at"].dt.month
df["submitted_dayofweek"] = df["submitted_at"].dt.dayofweek

# Do not use identifiers, raw dates, or inspector notes in this baseline.
# Inspector notes may reveal the investigation outcome and cause leakage.
numeric_features = [
    "days_since_purchase",
    "claim_amount_inr",
    "customer_prior_claims",
    "submitted_month",
    "submitted_dayofweek",
    "partner_tenure_days",
    "list_price_inr",
    "warranty_months",
    "claim_to_list_price_ratio",
]

categorical_features = [
    "sku",
    "photo_attached",
    "partner_inspected",
    "source",
    "city",
    "partner_type",
    "family",
]

text_feature = "claim_description"

features = numeric_features + categorical_features + [text_feature]
X = df[features].copy()
y = df["is_fraud"]
groups = df["claim_id"]

# Keep each claim ID in only one split
splitter = GroupShuffleSplit(
    n_splits=1, test_size=0.25, random_state=42
)
train_idx, val_idx = next(splitter.split(X, y, groups=groups))

X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]

numeric_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="median")),
    ("scaler", StandardScaler()),
])

categorical_pipeline = Pipeline([
    ("imputer", SimpleImputer(strategy="most_frequent")),
    ("encoder", OneHotEncoder(handle_unknown="ignore")),
])

preprocessor = ColumnTransformer([
    ("numeric", numeric_pipeline, numeric_features),
    ("categorical", categorical_pipeline, categorical_features),
    ("description", TfidfVectorizer(
        max_features=3000, ngram_range=(1, 2)
    ), text_feature),
])

model = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", LogisticRegression(
        class_weight="balanced", max_iter=1000, random_state=42
    )),
])

model.fit(X_train, y_train)

val_scores = model.predict_proba(X_val)[:, 1]

print("Training rows:", len(X_train))
print("Validation rows:", len(X_val))
print("Fraud labels in validation:", int(y_val.sum()))
print("Average precision:", round(
    average_precision_score(y_val, val_scores), 4
))
print("ROC-AUC:", round(
    roc_auc_score(y_val, val_scores), 4
))

# Evaluate the top 40 validation claims
validation_results = pd.DataFrame({
    "claim_id": df.iloc[val_idx]["claim_id"].values,
    "actual": y_val.values,
    "score": val_scores,
})

top_40 = validation_results.nlargest(40, "score")

print("\n=== TOP-40 REVIEW ANALYSIS ===")
print("Fraud-labelled claims in top 40:",
      int(top_40["actual"].sum()))
print("Total fraud-labelled claims in validation:",
      int(validation_results["actual"].sum()))
print("Precision at 40:",
      round(top_40["actual"].mean(), 4))
print("Recall at 40:",
      round(
          top_40["actual"].sum()
          / max(validation_results["actual"].sum(), 1),
          4
      ))

