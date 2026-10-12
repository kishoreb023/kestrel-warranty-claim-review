# Kestrel Warranty Claim Review

**AI-Assisted Risk Scoring for Human Investigation**

An AI-assisted prototype for prioritizing warranty claims that may require further investigation. The system combines claim details, warranty-policy indicators, and a risk score to help reviewers decide which claims to examine first.

> **Important:** A risk score is not proof of fraud. This prototype supports human review and should not automatically reject warranty claims.

## 1. Problem Statement

Kestrel Home Appliances handles warranty claims across its service-partner network. Reviewing every claim with the same level of attention can consume time and resources.

This project aims to help investigators prioritize potentially suspicious claims using available historical claim data and claim-level information.

## 2. Project Objectives

- Generate a risk score for each claim.
- Produce `predictions.csv` in the format required by the supplied submission template.
- Provide a JSON API for analyzing an individual claim.
- Display understandable risk indicators and a recommended review action.
- Evaluate model performance and document limitations.
- Keep final claim decisions under human control.

## 3. Features

- Claim-level risk analysis.
- Risk score display.
- Human-readable indicators explaining potential concerns.
- Recommended action for human investigation.
- JSON endpoint for individual claim analysis.
- Web interface for submitting claim details.
- Evaluation and error analysis using available labeled data.

**Example indicators may include:**
- Claim amount meets a policy-defined inspection threshold.
- Previous customer claims are recorded.
- Claim was submitted shortly after purchase.
- Partner inspection has not been recorded as completed.

These indicators must be checked against the supplied policy and actual implementation.

## 4. Project Structure

The repository may contain the following files:

```text
kestrel-warranty-claim-review/
├── README.md
├── .gitignore
├── train.csv
├── test_unlabelled.csv
├── sample_submission.csv
├── predictions.csv
├── partners.csv
├── products.csv
├── email-thread.txt
├── ops-policy.pdf
├── requirements.txt
├── app.py
├── model.py
├── train.py
├── evaluate.py
├── templates/
│   └── index.html
└── reports/
    └── evaluation_report.md
```

The exact source-code filenames may differ. Keep only files that actually exist in your repository, and follow the task instructions about which supplied data files may be published.

## 5. Technology Stack

Document the technologies actually used in this project. Possible components include:

- **Python** — data processing and risk-scoring logic.
- **Pandas / NumPy** — data preparation and analysis.
- **Scikit-learn** — model training and evaluation, if used.
- **FastAPI or Flask** — JSON API, depending on the implementation.
- **HTML, CSS and JavaScript** — web interface, if applicable.
- **Git and GitHub** — version control and project submission.

## 6. Installation

### Prerequisites

- Python 3.10 or another version supported by the project's dependencies.
- Git.
- A terminal such as PowerShell, Command Prompt, or a VS Code terminal.

### Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/kestrel-warranty-claim-review.git
cd kestrel-warranty-claim-review
```

Replace `YOUR_USERNAME` with your GitHub username.

### Create a virtual environment

**Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Install dependencies

If `requirements.txt` exists:

```bash
python -m pip install -r requirements.txt
```

If it does not exist yet, create it with the packages required by your actual implementation. Do not add unused dependencies.

## 7. Running the Project

Use the command appropriate for your actual application.

For a FastAPI application:

```bash
uvicorn app:app --reload
```

For a Flask application:

```bash
python app.py
```

Open the local address printed by the application in your terminal. If using FastAPI, the interactive API documentation is commonly available at `/docs`.

**Note:** Replace these example commands with the verified command for your project. A fresh installation should be tested by following these instructions from start to finish.

## 8. API Usage

The service should accept one claim as JSON and return a risk score, readable indicators, and a recommended action.

Example request:

```json
{
  "claim_id": "CLM-001",
  "partner_id": "PARTNER-001",
  "product_sku": "SKU-001",
  "days_since_purchase": 20,
  "claim_amount": 2500,
  "photo_attached": true,
  "partner_inspection_completed": false,
  "previous_customer_claims": 2,
  "claim_source": "CRM",
  "claim_description": "Product stopped working"
}
```

Example response format:

```json
{
  "claim_id": "CLM-001",
  "risk_score": 0.70,
  "indicators": [
    "Claim meets the configured inspection threshold",
    "Previous customer claims are recorded",
    "Partner inspection is not recorded as completed"
  ],
  "recommended_action": "Human review required",
  "disclaimer": "Risk score is not proof of fraud."
}
```

**These are illustrative examples, not guaranteed outputs.** Adjust the field names, endpoint, response structure, and values to match the working application. Do not describe a rule-based score as a trained-model prediction unless a trained model actually generates it.

## 9. Prediction File

The required `predictions.csv` file should contain one prediction for every row in `test_unlabelled.csv`.

Before submission, verify that:

1. The output columns match `sample_submission.csv`.
2. The number of prediction rows matches the number of test rows.
3. Claim identifiers are preserved in the correct order, where required by the template.
4. Scores are numeric and higher scores indicate greater suspected fraud risk.
5. There are no missing or infinite scores.
6. The file is saved in the repository root and is not excluded by `.gitignore`.

## 10. Model Evaluation

Model quality must be measured using labeled data that was not used to train the model.

Record the actual results here after running the evaluation:

| Metric | Measured result |
|---|---|
| Evaluation sample size | To be measured |
| Fraud prevalence | To be measured |
| Precision | To be measured |
| Recall | To be measured |
| F1-score | To be measured |
| PR-AUC | To be measured |
| Confusion matrix | To be recorded |

For an imbalanced fraud dataset, accuracy alone can be misleading. Precision helps estimate how many flagged claims are genuinely suspicious, while recall helps measure how many known fraud cases are identified.

Do not report unmeasured performance, financial savings, or fraud-detection accuracy as established results.

## 11. Business Value

The intended business benefit is to help investigators prioritize claims and focus attention on cases that may need additional checks.

For a planning volume of approximately **750 claims per month**, the potential benefit depends on the proportion flagged, the time saved per review, and the measured accuracy of those flags.

Any estimated savings should state the assumptions used and should be distinguished from verified results.

## 12. Limitations and Safeguards

- A high score does not establish that a claim is fraudulent.
- Missing or inaccurate claim records can affect results.
- Historical labels may contain investigation or reporting biases.
- Model performance may change as claim patterns change.
- Policy thresholds and input validation require testing.
- Human investigators must make the final decision.
- The prototype should not automatically deny claims based only on its score.

## 13. Future Improvements

- Validate performance using a time-based holdout set.
- Improve precision and recall through threshold selection.
- Add monitoring for missing values and changing data patterns.
- Validate explanations against the warranty policy.
- Add audit logs and reviewer feedback.
- Test the service from a clean environment before deployment.

## 14. Disclaimer

This project is an AI-assisted warranty-claim review prototype intended to support investigation prioritization. Its risk scores should not be interpreted as verified fraud probabilities unless calibration has been established. It is not a replacement for policy review, evidence gathering, or human decision-making.

## 15. Submission Checklist

- [ ] Working application and API.
- [ ] `predictions.csv` matches the supplied template.
- [ ] Evaluation results and error analysis are documented.
- [ ] Setup instructions have been tested on a clean environment.
- [ ] One-page business memo is included.
- [ ] Required screen recording is available.
- [ ] No passwords, API keys, personal secrets, or prohibited data are committed.
- [ ] Repository contents and access permissions comply with the task instructions.
