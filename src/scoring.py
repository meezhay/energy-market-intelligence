# Everything involving calculations will be in this file. For example, calculating the priority score based on access, improvement, and population weights.


from src.utils import min_max_scale

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
