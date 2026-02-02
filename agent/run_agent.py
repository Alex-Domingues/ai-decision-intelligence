#!/usr/bin/env python3
"""Minimal CLI to produce agentic_checks.json without opening notebooks.

It reads scenario & greedy exports, computes deterministic checks, and writes a
robustness-framed JSON. No LLM is required.
"""

import argparse, json, os
from pathlib import Path
import pandas as pd

BUDGET_CAP_AU = float(os.getenv("BUDGET_CAP_AU", "50.0"))

def euros_per_au(row) -> float:
    au = max(float(row["effort_au"]), 1e-6)
    return float(row["delta_net_eur"]) / au

def rank_by_eur_per_au(df):
    ranked = [(r["option"], euros_per_au(r)) for _, r in df.iterrows()]
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked

def budget_compliant(df, cap):
    return [r["option"] for _, r in df.iterrows() if float(r["effort_au"]) <= cap]

def retention_support(df):
    return [r["option"] for _, r in df.iterrows() if float(r["delta_grr_pp"]) >= 0 and float(r["delta_nrr_pp"]) >= 0]

def churn_shock_risk_flags(df):
    return {r["option"]: (float(r["delta_grr_pp"]) == 0.0 and float(r["delta_nrr_pp"]) == 0.0) for _, r in df.iterrows()}

def budget_cut_priority(df, top_k=2):
    eligible = []
    for _, r in df.iterrows():
        if float(r["delta_grr_pp"]) >= 0 and float(r["delta_nrr_pp"]) >= 0:
            eligible.append((r["option"], float(r["effort_au"])) )
    eligible.sort(key=lambda x: x[1])
    return [opt for opt, _ in eligible[:max(1, top_k)]]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--scenarios", default=os.getenv("SCENARIO_CSV", "data/processed/scenario_compare.csv"))
    p.add_argument("--greedy", default=os.getenv("GREEDY_JSON", "data/processed/greedy_summary.json"))
    p.add_argument("--out", default="outputs/agentic_checks.json")
    args = p.parse_args()

    df = pd.read_csv(args.scenarios)
    name_col = next((c for c in df.columns if c.lower() in ("option","scenario","name")), df.columns[0])
    df = df.rename(columns={name_col: "option"})

    with open(args.greedy, "r") as f:
        greedy = json.load(f)

    det = {
        "eur_per_au_rank": rank_by_eur_per_au(df),
        "budget_compliant": budget_compliant(df, BUDGET_CAP_AU),
        "retention_support": retention_support(df),
        "churn_shock_risk_flags": churn_shock_risk_flags(df),
        "budget_cut_priority": budget_cut_priority(df),
        "greedy_budget_used_au": float(greedy.get("budget_used_au", 0.0)),
        "greedy_delta_net_eur": float(greedy.get("delta_net_eur", 0.0)),
        "greedy_delta_grr_pp": float(greedy.get("delta_grr_pp", 0.0)),
        "constraints_note": f"Budget cap={BUDGET_CAP_AU} AU; engine guardrails applied upstream.",
    }

    shortlist = det["budget_cut_priority"] or [det["eur_per_au_rank"][0][0]]
    rec = shortlist[0]

    out = {
        "executive_takeaway": "Most robust recommendation under board constraints; qualitative stress applied.",
        "summary": {
            "best_eur_per_au": {"option": det["eur_per_au_rank"][0][0], "eur_per_au": det["eur_per_au_rank"][0][1]},
            "retention_support": det["retention_support"],
            "budget_compliant": det["budget_compliant"],
        },
        "stress_tests": [
            {"name": "Expansion -30%", "verdicts": [{"option": o, "status": ("at_risk" if o==det["eur_per_au_rank"][0][0] else "holds"), "why": "Efficiency gains most sensitive to negative expansion."} for o,_ in det["eur_per_au_rank"]]},
            {"name": "Churn +100 bps (Enterprise)", "verdicts": [{"option": o, "status": ("more_exposed" if det["churn_shock_risk_flags"][o] else "holds"), "why": "Zero deltas imply higher exposure under churn shock."} for o,_ in det["eur_per_au_rank"]]},
            {"name": "Budget -50%", "verdicts": [{"option": o, "status": ("priority" if o in det["budget_cut_priority"] else "deprioritize"), "why": "Lowest AU among retention-supporting options."} for o,_ in det["eur_per_au_rank"]]},
        ],
        "robust_recommendation": {"option": rec, "rationale": "Shortlisted under budget cuts and does not worsen retention.", "conditions_to_hold": ["respect AU cap", "no retention degradation", "payback within threshold"]},
        "_deterministic_checks": det,
    }

    Path(os.path.dirname(args.out)).mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2)
    print(f"[OK] wrote {args.out}")

if __name__ == "__main__":
    main()
