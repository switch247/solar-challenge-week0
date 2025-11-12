import pandas as pd
import pytest

from app.utils import DataValidator, DataMerger, DataCleaner, SummaryService, StatTests


def make_sample_irradiance():
    data = {
        "Timestamp": ["2020-01-15", "2020-01-16", "2020-02-15"],
        "GHI": [0.0, 500.0, 600.0],
        "DNI": [0.0, 300.0, 350.0],
        "DHI": [0.0, 200.0, 250.0],
    }
    return pd.DataFrame(data)


def test_validate_columns():
    df = make_sample_irradiance()
    ok, missing = DataValidator.validate_columns(df, ["GHI", "DNI", "DHI"]) 
    assert ok is True
    assert missing == []


def test_data_merger_and_month():
    a = make_sample_irradiance()
    b = make_sample_irradiance()
    combined = DataMerger.combine([a, b], ["Benin", "Togo"]) 
    assert "Country" in combined.columns
    assert "Month" in combined.columns
    assert set(combined["Country"]) == {"Benin", "Togo"}


def test_daylight_filter():
    df = make_sample_irradiance()
    filtered = DataCleaner.daylight_only(df, ghi_col="GHI")
    assert (filtered["GHI"] > 0).all()


def test_summary_and_stats():
    # create simple dataset where Country A has low values and Country B high
    df = pd.DataFrame({
        "Country": ["A"] * 3 + ["B"] * 3,
        "GHI": [1.0, 1.1, 0.9, 10.0, 9.8, 10.2],
    })
    stats = SummaryService.by_country(df, ["GHI"]) 
    assert "A" in stats.index
    assert "B" in stats.index

    res = StatTests.run(df, "GHI")
    # Expect ANOVA to detect a difference between groups
    assert res.get("anova_p") is not None
    assert res.get("kruskal_p") is not None
    assert isinstance(res.get("anova_p"), float)
