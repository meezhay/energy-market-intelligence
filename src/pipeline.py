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

        # Merge country metadata
    electricity_df = merge_metadata(
        electricity_df,
        metadata
    )

    # Filter to Sub-Saharan Africa
    ssa_df = filter_ssa(electricity_df)

        # Feature engineering
    ssa_df = calculate_access_improvement(ssa_df)

    ssa_df = calculate_relative_improvement(ssa_df)

    ssa_df = calculate_access_score(ssa_df)

    ssa_df = calculate_improvement_score(ssa_df)

        # Load population data
    population_df = load_worldbank_data(
        PROJECT_ROOT
        / "data/raw/population/API_SP.POP.TOTL_DS2_en_csv_v2_33112.csv"
    )

    # Merge country metadata
    population_df = merge_metadata(
        population_df,
        metadata
    )

    # Rename the population column
    population_df = population_df.rename(
        columns={"2023": "Population_2023"}
    )

    # Filter to Sub-Saharan Africa
    population_ssa = filter_ssa(population_df)

    # Keep only the columns needed for the merge
    population_subset = population_ssa[
        [
            "Country Code",
            "Population_2023",
        ]
    ].copy()

    # Merge population into the electricity dataset
    ssa_df = merge_indicator(
        ssa_df,
        population_subset
    )

    # Calculate population-related features
    ssa_df = calculate_people_without_electricity(ssa_df)

    ssa_df = calculate_population_score(ssa_df)

    # Calculate the priority score with population
    ssa_df = calculate_priority_score_with_population(
        ssa_df,
        access_weight=1/3,
        improvement_weight=1/3,
        population_weight=1/3,
    )


    return ssa_df

