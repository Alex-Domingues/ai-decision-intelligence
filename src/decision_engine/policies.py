"""Effort policies & constraints for the decision engine.

Keep these simple and explicit so they can be audited easily.
"""

POLICIES = {
    "baseline": {"uplift_cap": 1.0, "decay": 0.15, "payback_months_max": 18},
    "enterprise_retention": {"uplift_cap": 1.2, "decay": 0.10, "payback_months_max": 18},
}
