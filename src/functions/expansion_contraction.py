"""
Expansion & Contraction Simulation for SaaS Financial Analysis

This module simulates realistic expansion (upsells/upgrades) and contraction 
(downgrades/seat reductions) for existing customer accounts based on segment 
characteristics.

Expansion and contraction only apply to accounts with opening_arr > 0 
(existing customers at period start).
"""

import numpy as np


# Segment-based expansion/contraction probabilities and rates
EXPANSION_RATES = {
    'Enterprise': {'probability': 0.40, 'mean_rate': 0.15, 'std_rate': 0.08},  # 40% chance, ~15% growth
    'Corporate':  {'probability': 0.30, 'mean_rate': 0.10, 'std_rate': 0.06},  # 30% chance, ~10% growth
    'SMB':        {'probability': 0.20, 'mean_rate': 0.05, 'std_rate': 0.04}   # 20% chance, ~5% growth
}

CONTRACTION_RATES = {
    'Enterprise': {'probability': 0.10, 'mean_rate': 0.04, 'std_rate': 0.03},  # 10% chance, ~4% reduction
    'Corporate':  {'probability': 0.15, 'mean_rate': 0.06, 'std_rate': 0.04},  # 15% chance, ~6% reduction
    'SMB':        {'probability': 0.25, 'mean_rate': 0.10, 'std_rate': 0.06}   # 25% chance, ~10% reduction
}


def simulate_expansion(row, expansion_rates=None, seed=None):
    """
    Generate expansion ARR for existing customers (opening_arr > 0).
    
    Returns segment-based probabilistic expansion (upsells/upgrades).
    """
    if row['opening_arr'] <= 0:
        return 0
    
    rates = expansion_rates or EXPANSION_RATES
    segment = row.get('segment', 'SMB')
    
    if segment not in rates:
        segment = 'SMB'  # Default fallback
    
    params = rates[segment]
    
    # Probabilistic expansion: some accounts expand, others don't
    if np.random.random() < params['probability']:
        # Generate expansion rate with some randomness
        rate = np.random.normal(params['mean_rate'], params['std_rate'])
        rate = np.clip(rate, 0.01, 0.30)  # Cap between 1% and 30%
        return round(row['opening_arr'] * rate, 2)
    
    return 0


def simulate_contraction(row, contraction_rates=None, seed=None):
    """
    Generate contraction ARR for existing customers (opening_arr > 0).
    
    Returns segment-based probabilistic contraction (downgrades/seat reductions).
    """
    if row['opening_arr'] <= 0:
        return 0
    
    rates = contraction_rates or CONTRACTION_RATES
    segment = row.get('segment', 'SMB')
    
    if segment not in rates:
        segment = 'SMB'  # Default fallback
    
    params = rates[segment]
    
    # Probabilistic contraction: some accounts downgrade, others don't
    if np.random.random() < params['probability']:
        # Generate contraction rate with some randomness
        rate = np.random.normal(params['mean_rate'], params['std_rate'])
        rate = np.clip(rate, 0.01, 0.50)  # Cap between 1% and 50%
        return round(row['opening_arr'] * rate, 2)
    
    return 0
