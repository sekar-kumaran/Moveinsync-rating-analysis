import pandas as pd
from . import config

def load_processed_data() -> pd.DataFrame:
    """Loads the processed clean dataset from disk."""
    if not config.PROCESSED_DATA_PATH.exists():
        raise FileNotFoundError(f"Processed data not found at {config.PROCESSED_DATA_PATH}. Please run the EDA notebook first.")
    return pd.read_csv(config.PROCESSED_DATA_PATH, low_memory=False)

def load_raw_data() -> pd.DataFrame:
    """Loads the raw dataset."""
    if not config.RAW_DATA_PATH.exists():
        raise FileNotFoundError(f"Raw data not found at {config.RAW_DATA_PATH}.")
    return pd.read_csv(config.RAW_DATA_PATH, dtype=str, low_memory=False)
