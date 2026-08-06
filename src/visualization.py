# Reusable plots will be in this file. For example, a function to plot the top 10 countries based on priority score.

# Reusable visualization functions for the project.

import matplotlib.pyplot as plt


def plot_average_access(df, years):
    """
    Plot the average electricity access across Sub-Saharan Africa
    from 2014 to 2023.
    """

    mean_electricity = df[years].mean()

    plt.figure(figsize=(10, 5))

    plt.plot(
        mean_electricity.index,
        mean_electricity.values,
        marker="o"
    )

    plt.title("Average Electricity Access in Sub-Saharan Africa (2014–2023)")
    plt.xlabel("Year")
    plt.ylabel("Access to Electricity (%)")

    plt.xticks(rotation=45)
    plt.grid(True)

    plt.tight_layout()
    plt.show()


def plot_improvement_scatter(df):
    """
    Plot starting electricity access against improvement.
    """

    plt.figure(figsize=(8, 6))

    plt.scatter(
        df["2014"],
        df["Improvement"]
    )

    plt.xlabel("Electricity Access in 2014 (%)")
    plt.ylabel("Improvement (2014–2023)")
    plt.title("Starting Electricity Access vs Improvement")

    plt.grid(True)

    plt.tight_layout()
    plt.show()


def plot_priority_ranking(
    df,
    score_column="Priority_Score",
    top_n=10
):
    """
    Plot the top countries ranked by a priority score.
    """

    priority = (
        df[["Country Name", score_column]]
        .sort_values(score_column, ascending=False)
        .head(top_n)
    )

    plt.figure(figsize=(10, 6))

    bars = plt.barh(
        priority["Country Name"],
        priority[score_column]
    )

    plt.gca().invert_yaxis()

    for bar in bars:
        width = bar.get_width()

        plt.text(
            width + 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{width:.2f}",
            va="center"
        )

    plt.title(f"Top {top_n} Priority Countries")
    plt.xlabel("Priority Score")
    plt.ylabel("Country")

    plt.xlim(0, 1)

    plt.tight_layout()
    plt.show()




def plot_investment_opportunities(
    df,
    score_column="Investment_Opportunity_Score",
    top_n=10,
):
    """
    Plot the top countries ranked by investment opportunity score.

    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe containing country names and the investment score.
    score_column : str, default="Investment_Opportunity_Score"
        Column used to rank countries.
    top_n : int, default=10
        Number of countries to display.
    """

    investment_opportunities = (
        df[["Country Name", score_column]]
        .dropna(subset=[score_column])
        .sort_values(score_column, ascending=False)
        .head(top_n)
    )

    plt.figure(figsize=(10, 6))

    bars = plt.barh(
        investment_opportunities["Country Name"],
        investment_opportunities[score_column],
    )

    plt.gca().invert_yaxis()

    for bar in bars:
        width = bar.get_width()

        plt.text(
            width + 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{width:.2f}",
            va="center",
        )

    plt.title(f"Top {top_n} Investment Opportunity Countries")
    plt.xlabel("Investment Opportunity Score")
    plt.ylabel("Country")

    plt.xlim(0, 1)
    plt.tight_layout()
    plt.show()





def plot_priority_vs_investment(
    df,
    rank_change_column="Rank_Change",
    annotate_top_n=5,
):
    """
    Compare the Version 1 Priority Score with the
    Version 2 Investment Opportunity Score and label
    the countries with the largest absolute rank changes.
    """

    plot_df = df.dropna(
        subset=[
            "Priority_Score",
            "Investment_Opportunity_Score",
        ]
    ).copy()

    plt.figure(figsize=(9, 7))

    plt.scatter(
        plot_df["Priority_Score"],
        plot_df["Investment_Opportunity_Score"],
    )

    if rank_change_column in plot_df.columns:
        movers = (
            plot_df.assign(
                Absolute_Rank_Change=plot_df[
                    rank_change_column
                ].abs()
            )
            .sort_values(
                "Absolute_Rank_Change",
                ascending=False,
            )
            .head(annotate_top_n)
        )

        for _, row in movers.iterrows():
            plt.annotate(
                row["Country Name"],
                (
                    row["Priority_Score"],
                    row["Investment_Opportunity_Score"],
                ),
                xytext=(5, 5),
                textcoords="offset points",
                fontsize=9,
            )

    plt.xlabel("Version 1 Priority Score")
    plt.ylabel("Version 2 Investment Opportunity Score")
    plt.title("Version 1 vs Version 2 Scores")

    plt.grid(True)
    plt.tight_layout()
    plt.show()