# all reading data goes in this file, so that we can easily change the data source in one place if needed

import pandas as pd


def load_worldbank_data(filepath):
    """
    Load a World Bank CSV file.
    """
    return pd.read_csv(filepath, skiprows=4)


def load_metadata(filepath):
    """
    Load World Bank metadata.
    """
    return pd.read_csv(filepath)