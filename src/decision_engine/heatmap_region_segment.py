import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_region_segment_heatmap(region_segment_data: pd.DataFrame, title: str):
    """
    Plot a heatmap of normalized net ARR delta by region and segment.
    """
    pvt = region_segment_data.pivot(index='region', columns='segment', values='delta_net_pct_region').fillna(0.0)
    fig, ax = plt.subplots(figsize=(9,3.6))
    sns.heatmap(pvt, annot=True, fmt='.1%', cmap='YlGnBu', cbar=True, ax=ax)
    ax.set_title(title)
    ax.set_xlabel('Segment'); ax.set_ylabel('Region')
    plt.tight_layout(); plt.show()

