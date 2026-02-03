from __future__ import annotations
import pandas as pd


def region_segment_net_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build Region x Segment matrix using net ARR contribution normalized by region ARR.
    Returns a pivot DataFrame with values = net_pct_region as in the notebook.
    """
    cols_needed = ["region", "segment", "annual_contract_value"]
    for c in ["net_arr_change"]:
        if c in df.columns:
            cols_needed.append(c)
    agg = (
        df[cols_needed]
        .groupby(["region", "segment"], dropna=False)
        .agg(arr_region=("annual_contract_value", "sum"),
             net=("net_arr_change", "sum") if "net_arr_change" in df.columns else ("annual_contract_value", "sum"))
        .reset_index()
    )
    agg["net_pct_region"] = agg["net"] / agg["arr_region"].replace(0, pd.NA)
    pivot = agg.pivot(index="region", columns="segment", values="net_pct_region")
    return pivot
