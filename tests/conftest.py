from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import pytest


@pytest.fixture(scope="session")
def data():
    root = Path(__file__).resolve().parents[1]
    frame = pd.read_parquet(root / "data/processed/detections.parquet")
    frame["timestamp_utc"] = pd.to_datetime(frame.timestamp_utc, utc=True)
    frame["type"] = frame["type"].astype("Int64")
    return frame


@pytest.fixture(scope="session")
def root():
    return Path(__file__).resolve().parents[1]
