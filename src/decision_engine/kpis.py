"""SaaS KPI helpers (B2B).

Guiding principles: deterministic, explainable, testable.
"""

def eur_per_au(delta_net_eur: float, effort_au: float) -> float:
    """Return EUR impact per effort AU (guarded)."""
    au = max(float(effort_au), 1e-6)
    return float(delta_net_eur) / au
