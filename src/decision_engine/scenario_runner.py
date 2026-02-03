from __future__ import annotations
import pandas as pd
import numpy as np


class ScenarioRunner:
    """
    Run a per-cell simulation (region x segment), keeping notebook logic:
    - aggregate numeric KPIs by cell
    - simple normalization (minmax or zscore)
    - return tables to be plotted in notebook (heatmaps, waterfalls)
    """

    def __init__(self, df: pd.DataFrame, region_col: str = "region", segment_col: str = "segment"):
        self.df = df.copy()
        self.region_col = region_col
        self.segment_col = segment_col

    def compute_cells(self, score_cols: list[str]) -> pd.DataFrame:
        """Group by region x segment and sum the requested score columns."""
        agg_map = {c: "sum" for c in score_cols}
        g = (
            self.df.groupby([self.region_col, self.segment_col], dropna=False)
                   .agg(agg_map)
                   .reset_index()
        )
        return g

    def normalize(self, cell_df: pd.DataFrame, cols: list[str], method: str = "minmax") -> pd.DataFrame:
        """Normalize columns like in the notebook (min-max or z-score)."""
        out = cell_df.copy()
        for c in cols:
            x = out[c].astype(float)
            if method == "minmax":
                mi, ma = x.min(), x.max()
                denom = (ma - mi) if (ma - mi) else 1.0
                out[c + "_norm"] = (x - mi) / denom
            elif method == "zscore":
                mu, sd = x.mean(), x.std(ddof=0)
                sd = sd if sd else 1.0
                out[c + "_norm"] = (x - mu) / sd
            else:
                raise ValueError("method must be 'minmax' or 'zscore'")
        return out

    def to_pivot(self, cell_df: pd.DataFrame, value_col: str) -> pd.DataFrame:
        """Return a region x segment pivot for plotting heatmaps externally."""
        return cell_df.pivot(index=self.region_col, columns=self.segment_col, values=value_col)
