# Everything involving calculations will be in this file. For example, calculating the priority score based on access, improvement, and population weights.


from src.utils import (
    min_max_scale,
    log_transform,
)

def calculate_access_score(df):
    """
    Normalize electricity access so that countries with lower access
    receive higher scores.
    """
    df = df.copy()

    df["Access_Score"] = min_max_scale(
        df["2023"],
        reverse=True
    )

    return df


def calculate_improvement_score(df):
    """
    Normalize improvement within the SSA region to create a new score column.
    """
    df = df.copy()

    df["Improvement_Score"] = min_max_scale(
        df["Improvement"]
    )

    return df


def calculate_population_score(df):
    """
    Normalize the number of people without electricity within the SSA region to create a new score column.
    """
    df = df.copy()

    df["Population_Score"] = min_max_scale(
        df["People_Without_Electricity"]
    )

    return df


def calculate_priority_score(
    df,
    access_weight,
    improvement_weight,
    output_column="Priority_Score"
):
    """
    Calculate the weighted priority score using
    electricity access and improvement scores.
    """

    if not abs(
        access_weight + improvement_weight - 1
    ) < 1e-9:
        raise ValueError("Weights must sum to 1.")

    df = df.copy()

    df[output_column] = (
        access_weight * df["Access_Score"]
        + improvement_weight * df["Improvement_Score"]
    )

    return df


def calculate_priority_score_with_population(
    df,
    access_weight,
    improvement_weight,
    population_weight,
    output_column="Priority_Score"
):
    """
    Calculate the weighted priority score using
    electricity access, improvement, and population scores.
    """

    if not abs(
        access_weight +
        improvement_weight +
        population_weight - 1
    ) < 1e-9:
        raise ValueError("Weights must sum to 1.")

    df = df.copy()

    df[output_column] = (
        access_weight * df["Access_Score"]
        + improvement_weight * df["Improvement_Score"]
        + population_weight * df["Population_Score"]
    )

    return df




def calculate_access_improvement(df):
    """
    Calculate electricity access improvement between 2014 and 2023.
    """
    df = df.copy()

    df["Improvement"] = df["2023"] - df["2014"]

    return df


def calculate_relative_improvement(df):
    """
    Calculate the relative percentage improvement in electricity access
    between 2014 and 2023.
    """
    df = df.copy()

    df["Relative Improvement (%)"] = (
        (df["2023"] - df["2014"])
        / df["2014"]
    ) * 100

    return df

def calculate_people_without_electricity(df):
    """
    Estimate the number of people without electricity.
    """
    df = df.copy()

    df["People_Without_Electricity"] = (
        df["Population_2023"]
        * (1 - df["2023"] / 100)
    )

    return df



def calculate_gdp_score(df):
    """
    Calculate a normalized GDP score using
    log-transformed GDP per capita.
    """

    df = df.copy()

    df["GDP_Log"] = log_transform(
        df["GDP_Per_Capita_2023"]
    )

    df["GDP_Score"] = min_max_scale(
        df["GDP_Log"]
    )

    return df





def calculate_investment_opportunity_score(
    df,
    access_weight,
    improvement_weight,
    population_weight,
    gdp_weight,
    output_column="Investment_Opportunity_Score",
):
    """
    Calculate a weighted investment opportunity score using
    electricity access, improvement, population, and GDP scores.

    The weights must sum to 1.
    """

    if not abs(
        access_weight
        + improvement_weight
        + population_weight
        + gdp_weight
        - 1
    ) < 1e-9:
        raise ValueError("Weights must sum to 1.")

    df = df.copy()

    df[output_column] = (
        access_weight * df["Access_Score"]
        + improvement_weight * df["Improvement_Score"]
        + population_weight * df["Population_Score"]
        + gdp_weight * df["GDP_Score"]
    )

    return df


def calculate_weighted_score(df, weights, output_column):
    """
    Weighted sum of score columns.

    weights : dict of {column name: weight}; weights must sum to 1.
    Only the listed columns are used.
    """
    if abs(sum(weights.values()) - 1) > 1e-9:
        raise ValueError("Weights must sum to 1.")

    df = df.copy()
    df[output_column] = sum(
        weight * df[column] for column, weight in weights.items()
    )
    return df


def calculate_opportunity_scores(df, weights, max_access=90):
    """
    Score countries within scope (2023 access <= max_access).

    All component scores are rescaled within the in-scope group,
    then combined with the given weights. Components with zero
    weight are skipped, so a missing value can't turn the score into NaN.

    Returns Country Code, Opportunity_Score and Opportunity_Rank
    for the in-scope countries.
    """
    scope_df = df[df["2023"] <= max_access].copy()

    scope_df = calculate_access_score(scope_df)
    scope_df = calculate_population_score(scope_df)
    scope_df = calculate_gdp_score(scope_df)
    scope_df = calculate_improvement_score(scope_df)

    active_weights = {column: w for column, w in weights.items() if w > 0}
    scope_df = calculate_weighted_score(scope_df, active_weights, "Opportunity_Score")

    scope_df["Opportunity_Rank"] = scope_df["Opportunity_Score"].rank(
        ascending=False, method="min"
    )

    return scope_df[["Country Code", "Opportunity_Score", "Opportunity_Rank"]]