from __future__ import annotations
import pandas as pd


def compute_global_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute CFO-grade SaaS KPIs at global level (no refactor, straight from notebook logic).

    Returns a one-row DataFrame with:
    - opening_total, arr_total, churned_total, new_total, reactivated_total, exp_total, cont_total, net_total
    - gross_churn, GRR, NRR, quick_ratio, logo_churn
    """
    opening_total = df["opening_arr"].sum()
    arr_total = df["annual_contract_value"].sum()
    churned_total = df["churned_arr"].sum()
    new_total = df["new_arr"].sum()
    reactivated_total = df["reactivated_arr"].sum()
    exp_total = df["expansion_arr"].sum()
    cont_total = df["contraction_arr"].sum()
    net_total = df["net_arr_change"].sum() if "net_arr_change" in df.columns else (
        new_total + reactivated_total + exp_total - cont_total - churned_total
    )

    gross_churn = churned_total / opening_total if opening_total else 0.0
    GRR = 1 - gross_churn
    NRR = (opening_total - churned_total + exp_total - cont_total) / opening_total if opening_total else 0.0
    quick_ratio = (new_total + exp_total) / (churned_total + cont_total) if (churned_total + cont_total) else float("inf")
    logo_churn = (df["churned_arr"] > 0).mean()

    out = pd.DataFrame([{
        "opening_total": opening_total,
        "arr_total": arr_total,
        "churned_total": churned_total,
        "new_total": new_total,
        "reactivated_total": reactivated_total,
        "exp_total": exp_total,
        "cont_total": cont_total,
        "net_total": net_total,
        "gross_churn": gross_churn,
        "GRR": GRR,
        "NRR": NRR,
        "quick_ratio": quick_ratio,
        "logo_churn": logo_churn,
    }])
    return out


def compute_segment_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Segment-level KPIs (aggregation + churn logos + GRR/NRR as in notebook).
    Columns returned (one row per segment):
      segment, opening, arr, churn, new, react, exp, cont, accounts,
      logos_churn, rev_churn_ratio_on_stock, gross_churn_on_opening, GRR, NRR
    """
    seg = (
        df.groupby("segment", dropna=False)
          .agg(
              opening=("opening_arr", "sum"),
              arr=("annual_contract_value", "sum"),
              churn=("churned_arr", "sum"),
              new=("new_arr", "sum"),
              react=("reactivated_arr", "sum"),
              exp=("expansion_arr", "sum"),
              cont=("contraction_arr", "sum"),
              accounts=("account_id", "nunique"),
          )
          .reset_index()
    )
    seg["logos_churn"] = (
        df.assign(_c=(df["churned_arr"] > 0).astype(int))
          .groupby("segment", dropna=False)["_c"]
          .mean()
          .reindex(seg["segment"])
          .to_numpy()
    )
    seg["rev_churn_ratio_on_stock"] = seg["churn"] / seg["arr"]
    seg["gross_churn_on_opening"] = seg["churn"] / seg["opening"]
    seg["GRR"] = 1 - seg["gross_churn_on_opening"]
    seg["NRR"] = (seg["opening"] - seg["churn"] + seg["exp"] - seg["cont"]) / seg["opening"]
    return seg


def compute_region_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Region-level KPIs (same structure as segment-level).
    Columns returned:
      region, opening, arr, churn, new, react, exp, cont, accounts,
      logos_churn, rev_churn_ratio_on_stock, gross_churn_on_opening, GRR, NRR
    """
    reg = (
        df.groupby("region", dropna=False)
          .agg(
              opening=("opening_arr", "sum"),
              arr=("annual_contract_value", "sum"),
              churn=("churned_arr", "sum"),
              new=("new_arr", "sum"),
              react=("reactivated_arr", "sum"),
              exp=("expansion_arr", "sum"),
              cont=("contraction_arr", "sum"),
              accounts=("account_id", "nunique"),
          )
          .reset_index()
    )
    reg["logos_churn"] = (
        df.assign(_c=(df["churned_arr"] > 0).astype(int))
          .groupby("region", dropna=False)["_c"]
          .mean()
          .reindex(reg["region"])
          .to_numpy()
    )
    reg["rev_churn_ratio_on_stock"] = reg["churn"] / reg["arr"]
    reg["gross_churn_on_opening"] = reg["churn"] / reg["opening"]
    reg["GRR"] = 1 - reg["gross_churn_on_opening"]
    reg["NRR"] = (reg["opening"] - reg["churn"] + reg["exp"] - reg["cont"]) / reg["opening"]
    return reg
