from fastapi.responses import FileResponse
from pathlib import Path


import joblib
import pandas as pd
import numpy as np

from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Kestrel Warranty Claim Review",
    description="Risk scoring to support human claim investigation."
)

BASE_DIR = Path(__file__).resolve().parent

model = joblib.load(BASE_DIR / "fraud_model.joblib")
partners = pd.read_csv(
    next(BASE_DIR.glob("*partners.csv"))
)
products = pd.read_csv(
    next(BASE_DIR.glob("*products.csv"))
)

partners = partners.drop_duplicates("partner_id")
products = products.drop_duplicates("sku")


class Claim(BaseModel):
    claim_id: str
    submitted_at: str
    partner_id: str
    sku: str
    days_since_purchase: int = Field(ge=0)
    claim_amount_inr: float = Field(gt=0)
    photo_attached: str
    partner_inspected: str
    claim_description: str
    customer_prior_claims: int = Field(ge=0)
    source: str


def prepare_claim(data: dict) -> pd.DataFrame:
    df = pd.DataFrame([data])

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


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")


@app.post("/score")
def score_claim(claim: Claim):
    try:
        data = claim.model_dump()
        df = prepare_claim(data)

        # Use the same model feature columns as training
        features = [
            "days_since_purchase",
            "claim_amount_inr",
            "customer_prior_claims",
            "submitted_month",
            "submitted_dayofweek",
            "partner_tenure_days",
            "list_price_inr",
            "warranty_months",
            "claim_to_list_price_ratio",
            "sku",
            "photo_attached",
            "partner_inspected",
            "source",
            "city",
            "partner_type",
            "family",
            "claim_description",
        ]

        score = float(model.predict_proba(df[features])[0, 1])

        reasons = []
        if claim.claim_amount_inr >= 2000:
            reasons.append(
                "Claim is at or above ₹2,000 and requires inspection under the stated policy."
            )
        if claim.customer_prior_claims > 0:
            reasons.append(
                "Customer has previous claims; review their history in context."
            )
        if claim.days_since_purchase < 30:
            reasons.append(
                "Claim was submitted within 30 days of purchase; verify dates and evidence."
            )
        if claim.partner_inspected.lower() not in ("yes", "true", "1"):
            reasons.append(
                "Partner inspection is not recorded as completed; verify the inspection status."
            )
        if not reasons:
            reasons.append(
                "No simple rule-based indicators were triggered; review supporting evidence."
            )

        return {
            "claim_id": claim.claim_id,
            "risk_score": round(score, 6),
            "reasons": reasons,
            "decision": "Human review required; score is not proof of fraud."
        }

    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Could not score claim: {str(exc)}"
        )
