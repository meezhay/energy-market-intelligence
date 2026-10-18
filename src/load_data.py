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

def load_rise_data(filepath, sheet_name="EA 2023"):
    """
    Load one year of the RISE Electricity Access pillar data.
    Drops the 'Scoring System' row beneath the header.
    """
    df = pd.read_excel(filepath, sheet_name=sheet_name)
    return df[df["Country"] != "Scoring System"].copy()