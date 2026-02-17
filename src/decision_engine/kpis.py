import numpy as np
import pandas as pd


def compute_cfo_kpis(segments_df: pd.DataFrame) -> pd.DataFrame:
       
        """
        Compute CFO-style KPIs from region×segment aggregated data.

        expected columns in segments_df:
            opening, churned, new, reactivated, expansion, contraction

        Returns the same rows with added:
            net, gross_churn, GRR, NRR, net_growth_pct
        """

        cfo_kpis = segments_df.copy()
        cfo_kpis["net"] = cfo_kpis["new"] + cfo_kpis["reactivated"] + cfo_kpis["expansion"] - cfo_kpis["churned"] - cfo_kpis["contraction"]
        cfo_kpis["gross_churn"] = np.where(cfo_kpis["opening"] > 0, cfo_kpis["churned"] / cfo_kpis["opening"], 0.0)
        cfo_kpis["GRR"] = 1 - cfo_kpis["gross_churn"]
        cfo_kpis["NRR"] = np.where(
                cfo_kpis["opening"] > 0,
                (cfo_kpis["opening"] - cfo_kpis["churned"] + cfo_kpis["expansion"] - cfo_kpis["contraction"]) / cfo_kpis["opening"],
                0.0,
            )
        
        # Net ARR Growth % = (Net ARR Change / Opening ARR) × 100
        # Direct measure of period-over-period ARR growth
        # Positive = growing, Negative = shrinking
        cfo_kpis["net_growth_pct"] = np.where(
            cfo_kpis["opening"] > 0,
            cfo_kpis["net"] / cfo_kpis["opening"],
            0.0
        )
        return cfo_kpis
