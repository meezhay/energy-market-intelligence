from pathlib import Path

from src.load_data import (
    load_worldbank_data,
    load_metadata,
)

from src.clean_data import (
    merge_metadata,
    filter_ssa,
    merge_indicator,
)

from src.scoring import (
    calculate_access_improvement,
    calculate_relative_improvement,
    calculate_people_without_electricity,
    calculate_access_score,
    calculate_improvement_score,
    calculate_population_score,
    calculate_priority_score_with_population,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def prepare_ssa_dataset():
    """
    Build the Version 1 dataset.

    Returns
    -------
    pandas.DataFrame
        Clean SSA electricity dataset with
        population-adjusted priority score.
    """
    electricity_df = load_worldbank_data(
        PROJECT_ROOT
        / "data/raw/electricity/API_EG.ELC.ACCS.ZS_DS2_en_csv_v2_3606.csv"
    )

    metadata = load_metadata(
        PROJECT_ROOT
        / "data/raw/electricity/Metadata_Country_API_EG.ELC.ACCS.ZS_DS2_en_csv_v2_3606.csv"
    )

    return electricity_df, metadata