"""
KPI computation module for SaaS financial analysis.

Provides functions to compute CFO-grade metrics (GRR, NRR, churn) from ARR flows.
All KPIs are opening-based: metrics use opening_arr as the denominator for consistency.
"""

import pandas as pd
import numpy as np


def compute_cfo_kpis(df: pd.DataFrame, format_output: bool = False) -> pd.DataFrame:
    """
    Compute CFO-grade retention and growth KPIs from ARR flow columns.
    
    Input columns: opening, churned, new, reactivated, expansion, contraction
    Output columns: opening, churned, new, reactivated, expansion, contraction, 
                    accounts, net, gross_churn, GRR, NRR, net_growth_pct
    
    GRR = 1 - (churned / opening)
    NRR = (opening - churned + expansion - contraction) / opening
    Net Growth % = net_arr / opening
    """
    result = df.copy()
    
    # Ensure all required columns exist with 0 defaults
    required = ['opening', 'churned', 'new', 'reactivated', 'expansion', 'contraction']
    for col in required:
        if col not in result.columns:
            result[col] = 0.0
    
    # Add 'accounts' column if missing
    if 'accounts' not in result.columns:
        result['accounts'] = 1.0
    
    # Compute net flows
    result['net'] = (
        result['new'] + 
        result['reactivated'] + 
        result['expansion'] - 
        result['contraction'] - 
        result['churned']
    )
    
    # Safe division (avoid divide-by-zero)
    opening_safe = np.where(result['opening'] > 0, result['opening'], 1.0)
    result['gross_churn'] = result['churned'] / opening_safe
    result['GRR'] = 1.0 - result['gross_churn']
    result['NRR'] = (
        (result['opening'] - result['churned'] + result['expansion'] - result['contraction']) 
        / opening_safe
    )
    # Net Growth % = (new + reactivated + expansion - contraction - churned) / opening
    result['net_growth_pct'] = result['net'] / opening_safe
    
    if format_output:
        # Format for display
        display_cols = {
            'opening': lambda x: f"${x:,.0f}",
            'new': lambda x: f"${x:,.0f}",
            'reactivated': lambda x: f"${x:,.0f}",
            'expansion': lambda x: f"${x:,.0f}",
            'contraction': lambda x: f"${x:,.0f}",
            'churned': lambda x: f"${x:,.0f}",
            'accounts': lambda x: f"{x:,.0f}",
            'net': lambda x: f"${x:,.0f}",
            'gross_churn': lambda x: f"{x*100:.1f}%",
            'GRR': lambda x: f"{x*100:.1f}%",
            'NRR': lambda x: f"{x*100:.1f}%",
            'net_growth_pct': lambda x: f"{x*100:.2f}%",
        }
        for col, fmt_fn in display_cols.items():
            if col in result.columns:
                result[col] = result[col].apply(fmt_fn)
    
    return result


def compute_retention_metrics(df: pd.DataFrame, selected_group: str = 'segment',
                              segment_order=None, format_output: bool = False) -> pd.DataFrame:
    """
    Group ARR flows by segment or region, compute KPIs at group level.
    
    Parameters:
        df: Full account-level DataFrame with ARR columns
        selected_group: 'segment' or 'region' (key for groupby)
        segment_order: List of segment names in desired order (for Categorical sorting)
        format_output: If True, format numbers as display strings
    
    Returns:
        DataFrame with one row per group, KPI columns
    """
    if selected_group not in df.columns:
        raise ValueError(f"Column '{selected_group}' not found in DataFrame")
    
    # Group by selected key and aggregate
    agg_dict = {
        'opening_arr': 'sum',
        'churned_arr': 'sum',
        'new_arr': 'sum',
        'reactivated_arr': 'sum',
        'expansion_arr': 'sum',
        'contraction_arr': 'sum',
        'account_id': 'nunique',
    }
    
    grouped = df.groupby(selected_group).agg(agg_dict).reset_index()
    grouped = grouped.rename(columns={
        'opening_arr': 'opening',
        'churned_arr': 'churned',
        'new_arr': 'new',
        'reactivated_arr': 'reactivated',
        'expansion_arr': 'expansion',
        'contraction_arr': 'contraction',
        'account_id': 'accounts',
    })
    
    # Apply segment ordering if specified
    if selected_group == 'segment' and segment_order:
        grouped[selected_group] = pd.Categorical(
            grouped[selected_group], 
            categories=segment_order, 
            ordered=True
        )
        grouped = grouped.sort_values(selected_group).reset_index(drop=True)
    
    # Compute KPIs using compute_cfo_kpis
    kpi_result = compute_cfo_kpis(grouped, format_output=False)
    
    # Add logo-level churn (# of churned accounts / total accounts)
    total_accounts = kpi_result['accounts'].sum() if 'accounts' in kpi_result.columns else 1.0
    kpi_result['logos_churn'] = 0.0
    
    # Recompute at data level to get logo churn
    grouped_with_churn = df.groupby(selected_group).agg({
        'opening_arr': 'sum',
        'churned_arr': 'sum',
        'new_arr': 'sum',
        'reactivated_arr': 'sum',
        'expansion_arr': 'sum',
        'contraction_arr': 'sum',
        'account_id': 'nunique',
    }).reset_index()
    
    # Count churned accounts per group
    churned_accounts = df[df['net_arr_change'] < 0].groupby(selected_group)['account_id'].nunique()
    grouped_with_churn['logos_churn'] = grouped_with_churn[selected_group].map(
        lambda x: (churned_accounts.get(x, 0) / grouped_with_churn.loc[grouped_with_churn[selected_group]==x, 'account_id'].iloc[0]) if grouped_with_churn.loc[grouped_with_churn[selected_group]==x, 'account_id'].iloc[0] > 0 else 0.0
    )
    
    # Rename revenue churn for display
    result = kpi_result.copy()
    result.columns = [col.replace('gross_churn', 'rev_churn_ratio_on_stock') for col in result.columns]
    
    if format_output:
        # Format display columns
        display_cols = {
            'opening': lambda x: f"${x:,.0f}",
            'churned': lambda x: f"${x:,.0f}",
            'new': lambda x: f"${x:,.0f}",
            'reactivated': lambda x: f"${x:,.0f}",
            'expansion': lambda x: f"${x:,.0f}",
            'contraction': lambda x: f"${x:,.0f}",
            'accounts': lambda x: f"{x:,.0f}",
            'net': lambda x: f"${x:,.0f}",
            'rev_churn_ratio_on_stock': lambda x: f"{x*100:.1f}%",
            'GRR': lambda x: f"{x*100:.1f}%",
            'NRR': lambda x: f"{x*100:.1f}%",
            'net_growth_pct': lambda x: f"{x*100:.2f}%",
            'logos_churn': lambda x: f"{x*100:.1f}%",
        }
        for col, fmt_fn in display_cols.items():
            if col in result.columns:
                result[col] = result[col].apply(fmt_fn)
    
    return result
