# Memo to Ritu Deshpande
**Subject:** Kestrel warranty claims — pilot risk scoring and next steps  
**Date:** 13 October 2026

## Decision
Proceed with a controlled, human-reviewed pilot of the warranty-claim risk-scoring prototype—not an automatic fraud rejection or payout-blocking system. Use the score to help investigators prioritize claims, and verify each case against evidence and warranty policy.

## Business impact and numbers
Kestrel handles approximately **750 warranty claims per month**. The prototype is intended to direct investigator attention toward claims that may warrant additional checks. At this stage, validated fraud-detection performance, review-time savings, prevented losses, and rupee savings have **not yet been established**. I therefore recommend measuring these during the pilot rather than presenting a speculative savings figure as a result.

The service is designed to run locally without paid inference API calls. On that assumption, direct paid inference cost is **₹0 per prediction** and **750 × ₹0 = ₹0 per month**. This excludes hosting, maintenance, development, and human-review costs; total operating cost may therefore be higher.

## What the evidence does—and does not—say
The prototype returns a claim risk score and human-readable indicators. A displayed score is a prioritization signal, not proof of fraud or a calibrated probability. Before operational use, evaluate on held-out historical claims and report the sample size, fraud prevalence, precision, recall, PR-AUC, confusion matrix, and representative false positives and false negatives. Accuracy alone is insufficient when fraud cases are uncommon.

## Actions for next week
1. **Validate:** Reproduce the evaluation on a held-out set; check for data leakage, missing values, duplicate claims, and policy-rule errors.
2. **Run a supervised pilot:** Have investigators review flagged claims and a sample of unflagged claims. Record confirmed outcomes, reviewer time, false positives, and missed cases.
3. **Decide using evidence:** Select a review threshold only after examining error trade-offs. Estimate rupee impact from measured review time and confirmed prevented losses, then decide whether to continue, revise, or stop the pilot.

## Key limitation
Historical investigation outcomes may be incomplete or biased, and new claim patterns may differ from past data. Human review remains mandatory; no claim should be rejected solely because of this score.

**Recommendation:** Treat this as an investigation-prioritization pilot. Expand only when measured performance, policy alignment, and operational value justify it.
