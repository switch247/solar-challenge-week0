"""Helpers for cross-country irradiance comparisons.

This module mirrors the analysis in the notebooks: loading/validating
country data (GHI/DNI/DHI), combining with a Country label, filtering
daylight rows, computing summary statistics, and running ANOVA/Kruskal
tests per metric. Plotly helpers are provided but optional for tests.
"""

from typing import List, Tuple, Dict, Any, Optional
import pandas as pd
import numpy as np

REQUIRED_IRRADIANCE = ["GHI", "DNI", "DHI"]


class DataValidator:
    """Validate dataset columns and basic format expectations."""

    @staticmethod
    def validate_columns(df: pd.DataFrame, required: List[str]) -> Tuple[bool, List[str]]:
        missing = [c for c in required if c not in df.columns]
        return (len(missing) == 0, missing)


class DataMerger:
    """Combine multiple country dataframes into a single dataframe.

    Common expectations:
    - input dfs have a Timestamp column (or Month)
    - a Country label is attached to each frame
    - Month column (YYYY-MM) is added if possible
    """

    @staticmethod
    def _ensure_month(df: pd.DataFrame, ts_col: str = "Timestamp") -> pd.DataFrame:
        df = df.copy()
        if "Month" not in df.columns:
            if ts_col in df.columns:
                try:
                    df["Month"] = pd.to_datetime(df[ts_col], errors="coerce").dt.to_period("M").astype(str)
                except Exception:
                    df["Month"] = "unknown"
            else:
                df["Month"] = "unknown"
        return df

    @staticmethod
    def add_country(df: pd.DataFrame, country: str) -> pd.DataFrame:
        out = df.copy()
        out["Country"] = country
        return out

    @classmethod
    def combine(cls, frames: List[pd.DataFrame], countries: List[str], timestamp_col: str = "Timestamp") -> pd.DataFrame:
        if len(frames) != len(countries):
            raise ValueError("frames and countries must be same length")
        prepared = []
        for df, c in zip(frames, countries):
            d = cls._ensure_month(df, ts_col=timestamp_col)
            d = cls.add_country(d, c)
            prepared.append(d)
        combined = pd.concat(prepared, ignore_index=True, sort=False)
        # put Country as last column for readability
        cols = [c for c in combined.columns if c != "Country"] + ["Country"]
        return combined[cols]


class DataCleaner:
    """Small utilities to clean/prepare irradiance data."""

    @staticmethod
    def daylight_only(df: pd.DataFrame, ghi_col: str = "GHI") -> pd.DataFrame:
        if ghi_col not in df.columns:
            # nothing to do
            return df.copy()
        return df.loc[df[ghi_col] > 0].copy()


class SummaryService:
    """Compute mean/median/std per Country for irradiance metrics."""

    @staticmethod
    def by_country(df: pd.DataFrame, metrics: List[str]) -> pd.DataFrame:
        metrics = [m for m in metrics if m in df.columns]
        if not metrics:
            return pd.DataFrame()
        stats = df.groupby("Country")[metrics].agg(["mean", "median", "std"]).round(3)
        return stats


class StatTests:
    """Run ANOVA and Kruskal-Wallis tests across countries for a metric.

    Returns a dictionary with statistic and p-values. Designed to be simple
    and testable (uses scipy when available).
    """

    @staticmethod
    def run(df: pd.DataFrame, metric: str) -> Dict[str, Any]:
        groups = [g[metric].dropna().values for _, g in df.groupby("Country")]
        # require at least two groups
        result = {"anova_stat": None, "anova_p": None, "kruskal_stat": None, "kruskal_p": None}
        try:
            from scipy.stats import f_oneway, kruskal

            if len(groups) >= 2 and all(len(g) > 0 for g in groups):
                a = f_oneway(*groups)
                k = kruskal(*groups)
                result.update({"anova_stat": float(a.statistic), "anova_p": float(a.pvalue),
                               "kruskal_stat": float(k.statistic), "kruskal_p": float(k.pvalue)})
        except Exception:
            # scipy not available or test failed: leave None
            pass
        return result


class Visualizer:
    """Plot helpers that return plotly figures (optional dependency).

    These are thin wrappers around plotly.express used by the Streamlit app.
    """

    @staticmethod
    def box_by_country(df: pd.DataFrame, metric: str):
        try:
            import plotly.express as px
        except Exception as e:
            raise ImportError("plotly required for plotting") from e
        return px.box(df, x="Country", y=metric, color="Country", title=f"{metric} Distribution by Country")

    @staticmethod
    def mean_bar_by_country(df: pd.DataFrame, metric: str):
        try:
            import plotly.express as px
        except Exception as e:
            raise ImportError("plotly required for plotting") from e
        agg = df.groupby("Country")[metric].mean().reset_index()
        return px.bar(agg, x="Country", y=metric, color="Country", title=f"Average {metric} by Country")

    @staticmethod
    def histogram_by_country(df: pd.DataFrame, metric: str, nbins: int = 30):
        """Return a histogram overlay (colored) across countries for a metric."""
        try:
            import plotly.express as px
        except Exception as e:
            raise ImportError("plotly required for plotting") from e
        return px.histogram(df, x=metric, color="Country", nbins=nbins, barmode="overlay",
                            title=f"{metric} Histogram by Country", opacity=0.7)

    @staticmethod
    def violin_by_country(df: pd.DataFrame, metric: str):
        """Return violin plots per country for the metric."""
        try:
            import plotly.express as px
        except Exception as e:
            raise ImportError("plotly required for plotting") from e
        return px.violin(df, x="Country", y=metric, color="Country", box=True, points="all",
                         title=f"{metric} Violin Plot by Country")

    @staticmethod
    def timeseries_by_country(df: pd.DataFrame, metric: str, ts_col: str = "Timestamp"):
        """Return a time-series line plot for the metric across countries.

        The function will attempt to coerce the timestamp column to datetime.
        """
        try:
            import plotly.express as px
        except Exception as e:
            raise ImportError("plotly required for plotting") from e
        d = df.copy()
        if ts_col in d.columns:
            try:
                d[ts_col] = pd.to_datetime(d[ts_col], errors="coerce")
            except Exception:
                pass
        return px.line(d, x=ts_col, y=metric, color="Country", title=f"{metric} Time Series by Country")


__all__ = [
    "REQUIRED_IRRADIANCE",
    "DataValidator",
    "DataMerger",
    "DataCleaner",
    "SummaryService",
    "StatTests",
    "Visualizer",
    "generate_sample_df",
]


def generate_sample_df(country_name: str, n_days: int = 30, freq: str = "H", seed: Optional[int] = 42) -> pd.DataFrame:
    """Generate an in-memory sample DataFrame matching the dashboard's expected columns.

    Timestamp format: "yyyy-mm-dd hh:mm" (string)
    Columns include GHI, DNI, DHI, ModA, ModB, Tamb, RH, WS, WSgust, WSstdev,
    WD, WDstdev, BP, Cleaning, Precipitation, TModA, TModB, Comments.
    """
    rng = np.random.default_rng(seed)
    periods = pd.date_range(end=pd.Timestamp.today().normalize(), periods=n_days * 24, freq=freq)

    bias = (sum(ord(c) for c in country_name) % 200) + 400
    # ensure we use numpy arrays for numeric ops (avoid Index methods)
    hour_of_day = (periods.hour + periods.minute / 60).to_numpy().astype(float)
    solar_factor = np.clip(np.sin((hour_of_day - 6) / 12 * np.pi), 0, None)
    noise = rng.normal(0, 30, size=len(periods))
    ghi = np.clip(bias * solar_factor + noise, a_min=0, a_max=None)
    dni = (ghi * rng.uniform(0.35, 0.85, size=len(periods))).round(2)
    dhi = (ghi - dni).clip(min=0).round(2)

    mod_factor_a = rng.normal(0.98, 0.02, size=len(periods))
    mod_factor_b = rng.normal(1.02, 0.03, size=len(periods))
    mod_a = (ghi * mod_factor_a + rng.normal(0, 5, size=len(periods))).round(2)
    mod_b = (ghi * mod_factor_b + rng.normal(0, 5, size=len(periods))).round(2)

    tamb = (rng.normal(28, 4, size=len(periods))).round(2)
    rh = (rng.uniform(30, 95, size=len(periods))).round(1)
    ws = (rng.uniform(0, 8, size=len(periods))).round(2)
    ws_gust = (ws + rng.uniform(0, 5, size=len(periods))).round(2)
    ws_stdev = (rng.uniform(0, 1.5, size=len(periods))).round(2)
    wd = (rng.uniform(0, 360, size=len(periods))).round(1)
    wd_stdev = (rng.uniform(0, 30, size=len(periods))).round(1)
    bp = (rng.normal(1013, 8, size=len(periods))).round(1)

    cleaning = rng.choice([0, 1], size=len(periods), p=[0.995, 0.005]).astype(int)
    precip = (rng.choice([0.0, 0.1, 0.5, 1.5], size=len(periods), p=[0.9, 0.06, 0.03, 0.01])).round(3)
    tmod_a = (tamb + rng.normal(5, 2, size=len(periods))).round(2)
    tmod_b = (tamb + rng.normal(5.5, 2.1, size=len(periods))).round(2)
    comments_choices = ["", "", "", "rain", "maintenance", "cleaning"]
    comments = rng.choice(comments_choices, size=len(periods), p=[0.8, 0.05, 0.05, 0.06, 0.03, 0.01])

    df = pd.DataFrame({
        "Timestamp": periods.strftime("%Y-%m-%d %H:%M"),
        "GHI": ghi.round(2),
        "DNI": dni,
        "DHI": dhi,
        "ModA": mod_a,
        "ModB": mod_b,
        "Tamb": tamb,
        "RH": rh,
        "WS": ws,
        "WSgust": ws_gust,
        "WSstdev": ws_stdev,
        "WD": wd,
        "WDstdev": wd_stdev,
        "BP": bp,
        "Cleaning": cleaning,
        "Precipitation": precip,
        "TModA": tmod_a,
        "TModB": tmod_b,
        "Comments": comments,
    })

    return df
