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