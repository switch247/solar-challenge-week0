import pandas as pd

from app.utils import generate_sample_df


def test_generate_sample_df_basic():
    df = generate_sample_df("UnitTestLand", n_days=1, freq="H", seed=123)
    # basic shape checks
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0

    expected_cols = {
        "Timestamp",
        "GHI",
        "DNI",
        "DHI",
        "ModA",
        "ModB",
        "Tamb",
        "RH",
        "WS",
        "WSgust",
        "WSstdev",
        "WD",
        "WDstdev",
        "BP",
        "Cleaning",
        "Precipitation",
        "TModA",
        "TModB",
        "Comments",
    }
    assert expected_cols.issubset(set(df.columns))

