
import pandas as pd
from pathlib import Path

files = list(Path(".").glob("*.csv"))

def find_file(suffix):
    return next(f for f in files if f.name.endswith(suffix))

submission = pd.read_csv("predictions.csv")
sample = pd.read_csv(find_file("sample_submission.csv"))
test = pd.read_csv(find_file("test_unlabelled.csv"))

print("Submission shape:", submission.shape)
print("Sample shape:", sample.shape)
print("Test shape:", test.shape)

print("\nCorrect columns:",
      submission.columns.tolist() == ["claim_id", "score"])

print("Correct row count:",
      len(submission) == len(sample) == len(test))

print("No duplicate claim IDs:",
      submission["claim_id"].is_unique)

print("All test claim IDs included:",
      set(test["claim_id"]) == set(submission["claim_id"]))

print("All scores valid:",
      submission["score"].notna().all()
      and submission["score"].between(0, 1).all())

print("\nScore distribution:")
print(submission["score"].describe())
