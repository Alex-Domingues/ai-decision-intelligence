"""
Policy application module for SaaS decision engine.

Applies intervention policies (churn reduction, new logo uplift, reactivation) to KPI DataFrames.
Policies are lever-based with capped uplifts per region-segment cell.
"""

import pandas as pd
import numpy as np


def apply_lever_to_row(result: pd.DataFrame, idx, lever: str, value: float, 
                       effort_coeffs: dict, caps: dict) -> float:
    """
    Apply a single lever (churn_bps, new_pct, react_pct) to one row.
    Returns the effort units incurred.
    """
    effort = 0.0
    opening_safe = max(result.loc[idx, 'opening'], 1.0)
    
    if lever == 'churn_bps':
        # Reduce churned by value (in bps, e.g., 50 bps = 0.005 or 0.5%)
        churn_reduction = result.loc[idx, 'churned'] * min(value, 1.0)
        result.loc[idx, 'churned'] -= churn_reduction
        effort = abs(churn_reduction / opening_safe) * effort_coeffs.get('a_churn', 1.0)
    
    elif lever == 'new_pct':
        # Increase new by X% (capped)
        cap = caps.get('max_new_uplift', 0.20)
        new_uplift = result.loc[idx, 'new'] * min(value, cap)
        result.loc[idx, 'new'] += new_uplift
        effort = abs(new_uplift / opening_safe) * effort_coeffs.get('a_new', 0.6)
    
    elif lever == 'react_pct':
        # Increase reactivated by X% (capped)
        cap = caps.get('max_react_uplift', 0.30)
        react_uplift = result.loc[idx, 'reactivated'] * min(value, cap)
        result.loc[idx, 'reactivated'] += react_uplift
        effort = abs(react_uplift / opening_safe) * effort_coeffs.get('a_react', 0.4)
    
    return effort


def apply_policy(kpi_df: pd.DataFrame, policy: dict, 
                 effort_coeffs=None, caps=None) -> tuple:
    """
    Apply a policy dict to KPI DataFrame at multiple levels (cell, segment, region).
    
    Policy structure supports 3 levels:
        {
            'cell': {(region, segment): {lever: value}},      # Apply to specific cells
            'segment': {segment: {lever: value}},             # Apply to all rows with segment
            'region': {region: {lever: value}}                # Apply to all rows with region
        }
    
    Valid levers:
        'churn_bps': Reduce churned by X basis points (e.g., 50 bps = 0.005)
        'new_pct': Increase new by X% (e.g., 0.02 = +2%)
        'react_pct': Increase reactivated by X% (e.g., 0.05 = +5%)
    
    Returns:
        (kpi_modified, total_effort_units)
    """
    if effort_coeffs is None:
        effort_coeffs = {
            'a_churn': 1.0,
            'a_new': 0.6,
            'a_react': 0.4,
            'a_exp': 0.7,
            'a_cont': 0.8,
        }
    if caps is None:
        caps = {
            'max_new_uplift': 0.20,
            'max_react_uplift': 0.30,
        }
    
    result = kpi_df.copy()
    total_effort = 0.0
    
    # Apply region-level policies first
    if 'region' in policy:
        region_policies = policy['region']
        for region, levers in region_policies.items():
            mask = result['region'] == region
            for idx in result[mask].index:
                for lever, value in levers.items():
                    effort = apply_lever_to_row(result, idx, lever, value, effort_coeffs, caps)
                    total_effort += effort
    
    # Apply segment-level policies
    if 'segment' in policy:
        segment_policies = policy['segment']
        for segment, levers in segment_policies.items():
            mask = result['segment'] == segment
            for idx in result[mask].index:
                for lever, value in levers.items():
                    effort = apply_lever_to_row(result, idx, lever, value, effort_coeffs, caps)
                    total_effort += effort
    
    # Apply cell-level policies (most granular)
    if 'cell' in policy:
        cell_policies = policy['cell']
        for (region, segment), levers in cell_policies.items():
            mask = (result['region'] == region) & (result['segment'] == segment)
            if not mask.any():
                continue
            idx = result[mask].index[0]
            for lever, value in levers.items():
                effort = apply_lever_to_row(result, idx, lever, value, effort_coeffs, caps)
                total_effort += effort
    
    return result, total_effort
