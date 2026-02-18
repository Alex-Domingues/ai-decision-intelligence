"""
Heatmap visualization for region-segment KPI matrices.

Renders a heatmap showing net ARR contribution (normalized by region) 
for quick identification of strategic priority cells.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def plot_region_segment_heatmap(df: pd.DataFrame, title: str = None) -> None:
    """
    Plot a region × segment heatmap from a DataFrame.
    
    Input DataFrame must contain:
        - 'region': Geographic region (rows)
        - 'segment': Customer segment (columns)
        - 'delta_net_pct_region' or 'net_pct_region': Value to heatmap
    
    Parameters:
        df: DataFrame with region, segment, and value columns
        title: Title for the heatmap
    """
    # Identify the value column (prioritize delta_net_pct_region, then net_pct_region)
    value_col = None
    for candidate in ['delta_net_pct_region', 'net_pct_region', 'net']:
        if candidate in df.columns:
            value_col = candidate
            break
    
    if value_col is None:
        raise ValueError("DataFrame must contain 'delta_net_pct_region', 'net_pct_region', or 'net' column")
    
    # Pivot to region × segment matrix
    pivot_df = df.pivot_table(
        index='region',
        columns='segment',
        values=value_col,
        aggfunc='sum'
    )
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(8, 5))
    
    sns.heatmap(
        pivot_df,
        annot=True,
        fmt='.1%' if 'pct' in value_col.lower() else '.0f',
        cmap='RdYlGn',
        center=0.0 if 'delta' in value_col else None,
        cbar_kws={'label': value_col},
        linewidths=0.5,
        linecolor='gray',
        ax=ax,
    )
    
    if title:
        ax.set_title(title, fontsize=12, fontweight='bold')
    
    ax.set_xlabel('Segment', fontsize=10)
    ax.set_ylabel('Region', fontsize=10)
    
    plt.tight_layout()
    plt.show()
