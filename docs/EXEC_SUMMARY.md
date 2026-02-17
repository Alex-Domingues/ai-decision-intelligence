# Executive Summary (Phase 3 - Agentic Executive Challenger)

- Post-hoc agent on top of a deterministic decision engine (no re-simulation).
- Uses engine exports: scenario comparisons (Delta Net EUR, Delta GRR/NRR, AU) and greedy summary.
- Heuristics: churn exposure when both retention deltas are zero; under budget cuts prefer low-AU with non-degrading retention; EUR per AU as an efficiency signal.
- Stress tests: Expansion -30%, Churn +100 bps (Enterprise), Budget -50%.
- Output: robust recommendation with conditions to hold.
