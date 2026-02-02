"""Greedy prioritization logic (transparent and auditable).

Select items that maximize EUR per AU under a budget cap (illustrative).
"""

from .kpis import eur_per_au

def greedy_select(rows, budget_cap_au: float):
    scored = [{**r, "eur_per_au": eur_per_au(r.get("delta_net_eur", 0.0), r.get("effort_au", 0.0))} for r in rows]
    scored.sort(key=lambda x: x["eur_per_au"], reverse=True)
    out, used = [], 0.0
    for r in scored:
        au = float(r.get("effort_au", 0.0))
        if used + au <= budget_cap_au:
            out.append(r); used += au
    return out
