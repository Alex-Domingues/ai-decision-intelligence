# AI Decision Intelligence — B2B SaaS

**Decision Engine + Agentic Validation Layer for SaaS Revenue Operations**

This repository demonstrates a production-grade Decision Intelligence system for B2B SaaS. It combines deterministic decision logic (KPIs, policies, greedy optimization) with an agentic validation layer that stress-tests recommendations under executive constraints.

---

## Executive Summary

**Business Question**: Where should we invest limited effort to maximize revenue growth and retention?

**Approach**:
1. **Data Foundation** (Notebook 00): Reconstruct finance-grade SaaS metrics from raw data with realistic expansion/contraction simulation
2. **Business Intelligence** (Notebook 01): Compute CFO-aligned KPIs (GRR, NRR, churn) and visualize segment priorities
3. **Decision Engine** (Notebook 02): Run what-if scenarios and greedy optimization under business constraints (caps, decay, payback gates)
4. **Agentic Validation** (Notebook 03): Stress-test recommendations with deterministic checks + LLM-powered robustness assessment

**Outcome**: Executive-ready recommendation with confidence bands, risk caveats, and ROI projections.

---

## Repository Structure

```
ai-decision-intelligence-main/
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .gitignore                         # Git exclusions
│
├── data/
│   ├── raw/                          # RavenStack source data (gitignored)
│   │   ├── ravenstack_accounts.csv
│   │   ├── ravenstack_subscriptions.csv
│   │   └── ravenstack_churn_events.csv
│   └── processed/
│       └── saas_financial_snapshot.csv  # Output of Notebook 00
│
├── src/
│   └── functions/                    # Shared analysis modules
│       ├── expansion_contraction.py  # Simulate expansion/contraction flows
│       ├── kpis.py                   # CFO-grade KPI computation (GRR, NRR)
│       ├── policies.py               # Policy application (churn reduction, growth levers)
│       └── heatmap_region_segment.py # Region × Segment visualization
│
├── notebooks/
│   ├── 00_data_treatment_financial_snapshot.ipynb  # Data reconstruction
│   ├── 01_business_eda_enhanced.ipynb              # KPI analysis & dashboards
│   ├── 02_decision_engine_v2_1_optimized.ipynb     # Scenario modeling & optimization
│   └── 03_agentic_agent.ipynb                      # Validation & stress-testing
│
├── outputs/
│   ├── decision_engine_outputs/
│   │   ├── scenario_compare.csv      # Scenario comparison results
│   │   └── greedy_summary.json       # Optimal plan under budget
│   └── agent_outputs/
│       └── agentic_checks.json       # Validation verdict (golden file)
│
├── docs/
│   └── EXEC_SUMMARY.md               # Executive presentation materials
│
├── screenshots/                       # Visual outputs for documentation
└── decision_scoping.md               # Project scoping notes
```

---

## How to Run

### 1. Setup Environment

```bash
# Clone repository
git clone <repo-url>
cd ai-decision-intelligence-main

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Notebooks in Sequence

**Notebook 00 — Data Treatment** (prerequisite for all others)
- Reconstructs SaaS financial snapshot from raw data
- Simulates expansion/contraction flows (makes GRR ≠ NRR)
- Exports: `data/processed/saas_financial_snapshot.csv`

**Notebook 01 — Business EDA**
- Computes CFO-grade KPIs (GRR, NRR, churn rates)
- Visualizes Region × Segment priorities
- Identifies high-impact areas for strategy

**Notebook 02 — Decision Engine**
- Runs what-if scenarios (Retention-first, Balanced Growth, Protect Whales)
- Executes greedy optimization under budget constraint
- Exports: `outputs/decision_engine_outputs/scenario_compare.csv` and `greedy_summary.json`

**Notebook 03 — Agentic Validation**
- Validates decision engine outputs (budget, payback, retention confidence)
- Stress-tests with LLM-powered robustness assessment
- Exports: `outputs/agent_outputs/agentic_checks.json`

### 3. Optional: CLI Agent Runner

```bash
# Set environment variables
export OPENAI_API_KEY="your-key-here"
export BUDGET_CAP_AU=50.0
export SCENARIO_CSV="outputs/decision_engine_outputs/scenario_compare.csv"
export GREEDY_JSON="outputs/decision_engine_outputs/greedy_summary.json"

# Run CLI agent
python agent/run_agent.py --out outputs/agent_outputs/agentic_checks.json
```

---

## Technical Highlights

### Data Foundation (Notebook 00)
- **Churn reconstruction**: Account-level gross churn with reactivation logic
- **Expansion/Contraction simulation**: Segment-aware probabilistic flows (Enterprise 40% expansion rate, SMB 20%)
- **Finance-grade guardrails**: Caps, reactivation constraints, opening balance validation

### Decision Engine (Notebook 02)
- **Multi-level policies**: Region, Segment, or Cell-specific interventions
- **Greedy optimization**: ROI-driven allocator with:
  - Diminishing returns (decay factor 0.85)
  - Payback gate (≤18 months)
  - Minimum impact threshold ($1k Net ARR)
  - Max iterations safety (500)
- **Metrics tracked**: Delta Net ARR ($), Delta Net Growth (%), Effort (units)

### Agentic Layer (Notebook 03)
- **Deterministic checks**: Budget utilization, payback feasibility, retention confidence
- **LLM stress-testing**: Upside/downside variance, assumption robustness
- **Structured output**: JSON verdict with recommendation + caveats

---

## Key Metrics & KPIs

| Metric | Formula | Business Meaning |
|--------|---------|------------------|
| **GRR** | 1 − (churned / opening) | Revenue retention before expansion |
| **NRR** | (opening − churned + expansion − contraction) / opening | Net revenue growth from existing base |
| **Net Growth %** | net_arr / opening | Total ARR change including new logos |
| **Churn Rate** | churned / opening | Revenue loss rate |
| **ROI** | delta_net_arr / effort_units | $ return per unit of effort |

---

## Validation & Quality

### Sanity Checks
- Schema validation (required columns, data types)
- Bounds validation (GRR ∈ [0,2], NRR ∈ [0,3], effort ≥ 0)
- Missing value detection

### Golden File Regression
- `outputs/agent_outputs/agentic_checks.json` tracks validation state
- Non-regression test: recommendation framing should remain "most robust under board constraints"

### LLM Variance Testing
- Run agent 3× with same inputs
- Verify consistent recommendation direction
- Confidence bands should overlap

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Core Data** | pandas 2.3.3, numpy 2.2.6 |
| **Visualization** | matplotlib, seaborn, streamlit 1.51.0 |
| **Agent Framework** | langchain 1.0.8, langgraph 1.0.3, openai 2.8.1 |
| **Utilities** | python-dateutil, PyYAML, tqdm |

---

## Contributing & Extensions

**Potential improvements**:
1. Add Monte Carlo simulation for expansion/contraction uncertainty
2. Extend policy levers (pricing changes, contract term optimization)
3. Multi-period optimization (quarters vs annual)
4. Real-time dashboards (Streamlit app integration)
5. A/B test framework integration

---

## Contact

For questions or collaboration: alex.domingues@essec.edu
