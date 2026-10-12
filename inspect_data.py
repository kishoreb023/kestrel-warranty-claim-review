
import pandas as pd
from pathlib import Path

files = list(Path(".").glob("*.csv"))
train_file = next(f for f in files if f.name.endswith("train.csv"))
train = pd.read_csv(train_file)

# Show repeated claim IDs
duplicate_rows = train[
    train["claim_id"].duplicated(keep=False)
].sort_values("claim_id")

print("Rows belonging to duplicate claim IDs:",
      len(duplicate_rows))

print("\nFirst 20 duplicate records:")
print(
    duplicate_rows[
        [
            "claim_id",
            "submitted_at",
            "product_serial",
            "claim_amount_inr",
            "source",
            "is_fraud"
        ]
    ].head(20).to_string(index=False)
)

# Count IDs associated with conflicting labels
label_counts = (
    train.groupby("claim_id")["is_fraud"]
    .nunique()
)

print("\nClaim IDs with conflicting non-missing labels:",
      (label_counts > 1).sum())

# Check whether complete rows are duplicated
print("\nCompletely identical duplicate rows:",
      train.duplicated().sum())
