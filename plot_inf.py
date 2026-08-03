# plot_inf.py
# Inferential Statistical Analysis of IMDb Movie Data

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import scipy.stats as stats
import seaborn as sns


# ============================================================
# Global configuration
# ============================================================

SIGNIFICANCE_LEVEL = 0.05
REFERENCE_RATING = 7.0
YEAR_SPLIT = 2000
MIN_MOVIES_PER_DIRECTOR = 2
NUMBER_OF_DIRECTORS = 5

sns.set_theme(style="whitegrid")


# ============================================================
# File paths
# ============================================================

# Directory where the current Python script is located
PROJECT_DIRECTORY = Path(__file__).resolve().parent

# Portable dataset path
DATASET_PATH = (
    PROJECT_DIRECTORY
    / "dataset"
    / "imdb_movies.csv"
)

# Directory for plots and statistical results
RESULTS_DIRECTORY = (
    PROJECT_DIRECTORY
    / "results"
    / "inferential_statistics"
)

RESULTS_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# Helper functions
# ============================================================

def interpret_p_value(p_value):
    """
    Interpret a p-value using the configured significance level.
    """

    if pd.isna(p_value):
        return "Test could not be performed"

    if p_value < SIGNIFICANCE_LEVEL:
        return "Statistically significant"

    return "Not statistically significant"


def save_plot(file_name):
    """
    Save the current Matplotlib figure and close it.
    """

    output_path = RESULTS_DIRECTORY / file_name

    plt.tight_layout()

    plt.savefig(
        output_path,
        dpi=300,
        bbox_inches="tight",
    )

    plt.close()

    print(f"Plot saved: {output_path}")


def load_and_clean_dataset():
    """
    Load and clean the IMDb movie dataset.
    """

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"CSV file was not found:\n{DATASET_PATH}\n"
            "Run scraper.py before running this script."
        )

    dataframe = pd.read_csv(
        DATASET_PATH,
        sep=";",
        encoding="utf-8-sig",
    )

    required_columns = {
        "Title",
        "Rating",
        "Year",
        "Director",
    }

    missing_columns = (
        required_columns
        - set(dataframe.columns)
    )

    if missing_columns:
        raise ValueError(
            "The dataset is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    # Remove extra spaces from column names
    dataframe.columns = (
        dataframe.columns
        .str.strip()
    )

    # Convert movie ratings into numeric values
    dataframe["Rating"] = pd.to_numeric(
        dataframe["Rating"]
        .astype(str)
        .str.strip()
        .str.replace(",", ".", regex=False),
        errors="coerce",
    )

    # Extract a four-digit year and convert it into nullable integers
    extracted_years = (
        dataframe["Year"]
        .astype(str)
        .str.extract(r"((?:18|19|20)\d{2})")[0]
    )

    dataframe["Year"] = pd.to_numeric(
        extracted_years,
        errors="coerce",
    ).astype("Int64")

    # Clean director names
    dataframe["Director"] = (
        dataframe["Director"]
        .astype("string")
        .str.strip()
    )

    dataframe["Director"] = dataframe["Director"].replace(
        {
            "": pd.NA,
            "N/A": pd.NA,
            "nan": pd.NA,
            "None": pd.NA,
        }
    )

    # Remove rows without valid ratings
    dataframe = dataframe.dropna(
        subset=["Rating"]
    ).reset_index(drop=True)

    return dataframe


# ============================================================
# Statistical tests
# ============================================================

def run_one_sample_t_test(dataframe):
    """
    Test whether the average movie rating differs from 7.0.
    """

    ratings = dataframe["Rating"].dropna()

    if len(ratings) < 2:
        print(
            "\nOne-sample t-test skipped: "
            "not enough rating observations."
        )
        return None

    t_statistic, p_value = stats.ttest_1samp(
        ratings,
        popmean=REFERENCE_RATING,
    )

    sample_mean = ratings.mean()

    print("\n1. One-sample t-test")
    print(
        f"Hypothesized mean: {REFERENCE_RATING:.2f}"
    )
    print(
        f"Sample mean: {sample_mean:.3f}"
    )
    print(
        f"Sample size: {len(ratings)}"
    )
    print(
        f"T-statistic: {t_statistic:.3f}"
    )
    print(
        f"P-value: {p_value:.6f}"
    )
    print(
        f"Interpretation: {interpret_p_value(p_value)}"
    )

    # Create the rating distribution plot
    plt.figure(figsize=(9, 6))

    sns.histplot(
        ratings,
        bins=20,
        kde=True,
    )

    plt.axvline(
        REFERENCE_RATING,
        linestyle="--",
        label=f"Hypothesized mean = {REFERENCE_RATING:.1f}",
    )

    plt.axvline(
        sample_mean,
        linestyle="--",
        label=f"Sample mean = {sample_mean:.2f}",
    )

    plt.title(
        "One-Sample T-Test: Movie Ratings Compared with 7.0"
    )
    plt.xlabel("IMDb Rating")
    plt.ylabel("Number of Movies")
    plt.legend()

    save_plot(
        "one_sample_t_test.png"
    )

    return {
        "Test": "One-sample t-test",
        "Comparison": "Mean rating vs 7.0",
        "Statistic": t_statistic,
        "P-value": p_value,
        "Sample size": len(ratings),
        "Group 1 mean": sample_mean,
        "Group 2 mean": REFERENCE_RATING,
        "Interpretation": interpret_p_value(p_value),
    }


def run_two_sample_t_test(dataframe):
    """
    Compare movie ratings before and after the year 2000.
    """

    valid_data = dataframe.dropna(
        subset=["Year", "Rating"]
    ).copy()

    before_2000 = valid_data.loc[
        valid_data["Year"] < YEAR_SPLIT,
        "Rating",
    ]

    from_2000 = valid_data.loc[
        valid_data["Year"] >= YEAR_SPLIT,
        "Rating",
    ]

    if len(before_2000) < 2 or len(from_2000) < 2:
        print(
            "\nTwo-sample t-test skipped: "
            "not enough movies with valid years."
        )
        return None

    # Welch's t-test does not assume equal variances
    t_statistic, p_value = stats.ttest_ind(
        before_2000,
        from_2000,
        equal_var=False,
    )

    before_mean = before_2000.mean()
    from_mean = from_2000.mean()

    print("\n2. Welch's two-sample t-test")
    print(
        f"Movies before {YEAR_SPLIT}: {len(before_2000)}"
    )
    print(
        f"Mean rating before {YEAR_SPLIT}: "
        f"{before_mean:.3f}"
    )
    print(
        f"Movies from {YEAR_SPLIT}: {len(from_2000)}"
    )
    print(
        f"Mean rating from {YEAR_SPLIT}: "
        f"{from_mean:.3f}"
    )
    print(
        f"T-statistic: {t_statistic:.3f}"
    )
    print(
        f"P-value: {p_value:.6f}"
    )
    print(
        f"Interpretation: {interpret_p_value(p_value)}"
    )

    plot_data = pd.DataFrame(
        {
            "Rating": pd.concat(
                [
                    before_2000,
                    from_2000,
                ],
                ignore_index=True,
            ),
            "Period": (
                [f"Before {YEAR_SPLIT}"] * len(before_2000)
                + [f"{YEAR_SPLIT} and later"] * len(from_2000)
            ),
        }
    )

    plt.figure(figsize=(9, 6))

    sns.boxplot(
        data=plot_data,
        x="Period",
        y="Rating",
        hue="Period",
        legend=False,
    )

    plt.title(
        f"Movie Ratings Before and After {YEAR_SPLIT}"
    )
    plt.xlabel("Release Period")
    plt.ylabel("IMDb Rating")

    save_plot(
        "two_sample_t_test.png"
    )

    return {
        "Test": "Welch's two-sample t-test",
        "Comparison": (
            f"Ratings before {YEAR_SPLIT} "
            f"vs {YEAR_SPLIT} and later"
        ),
        "Statistic": t_statistic,
        "P-value": p_value,
        "Sample size": len(before_2000) + len(from_2000),
        "Group 1 mean": before_mean,
        "Group 2 mean": from_mean,
        "Interpretation": interpret_p_value(p_value),
    }


def run_director_anova(dataframe):
    """
    Compare ratings among the five directors with the largest
    number of movies, requiring at least two movies per director.
    """

    valid_data = dataframe.dropna(
        subset=["Director", "Rating"]
    ).copy()

    director_counts = (
        valid_data["Director"]
        .value_counts()
    )

    eligible_directors = (
        director_counts[
            director_counts >= MIN_MOVIES_PER_DIRECTOR
        ]
        .head(NUMBER_OF_DIRECTORS)
        .index
        .tolist()
    )

    if len(eligible_directors) < 2:
        print(
            "\nANOVA skipped: at least two directors "
            f"with {MIN_MOVIES_PER_DIRECTOR} or more movies "
            "are required."
        )
        return None

    director_data = valid_data[
        valid_data["Director"].isin(
            eligible_directors
        )
    ].copy()

    rating_groups = [
        director_data.loc[
            director_data["Director"] == director,
            "Rating",
        ]
        for director in eligible_directors
    ]

    f_statistic, p_value = stats.f_oneway(
        *rating_groups
    )

    print("\n3. One-way ANOVA")
    print(
        "Directors included: "
        + ", ".join(eligible_directors)
    )

    for director in eligible_directors:
        director_ratings = director_data.loc[
            director_data["Director"] == director,
            "Rating",
        ]

        print(
            f"{director}: "
            f"n={len(director_ratings)}, "
            f"mean={director_ratings.mean():.3f}"
        )

    print(
        f"F-statistic: {f_statistic:.3f}"
    )
    print(
        f"P-value: {p_value:.6f}"
    )
    print(
        f"Interpretation: {interpret_p_value(p_value)}"
    )

    plt.figure(figsize=(11, 7))

    sns.boxplot(
        data=director_data,
        x="Director",
        y="Rating",
        hue="Director",
        order=eligible_directors,
        legend=False,
    )

    plt.title(
        "One-Way ANOVA: Movie Ratings by Director"
    )
    plt.xlabel("Director")
    plt.ylabel("IMDb Rating")
    plt.xticks(
        rotation=35,
        ha="right",
    )

    save_plot(
        "director_anova.png"
    )

    return {
        "Test": "One-way ANOVA",
        "Comparison": (
            "Ratings among directors: "
            + ", ".join(eligible_directors)
        ),
        "Statistic": f_statistic,
        "P-value": p_value,
        "Sample size": len(director_data),
        "Group 1 mean": pd.NA,
        "Group 2 mean": pd.NA,
        "Interpretation": interpret_p_value(p_value),
    }


def run_pearson_correlation(dataframe):
    """
    Test the linear relationship between release year and rating.
    """

    correlation_data = dataframe.dropna(
        subset=["Year", "Rating"]
    ).copy()

    if len(correlation_data) < 3:
        print(
            "\nPearson correlation skipped: "
            "not enough movies with valid years."
        )
        return None

    if (
        correlation_data["Year"].nunique() < 2
        or correlation_data["Rating"].nunique() < 2
    ):
        print(
            "\nPearson correlation skipped: "
            "one of the variables has no variation."
        )
        return None

    correlation, p_value = stats.pearsonr(
        correlation_data["Year"].astype(float),
        correlation_data["Rating"],
    )

    print("\n4. Pearson correlation")
    print(
        f"Valid observations: {len(correlation_data)}"
    )
    print(
        f"Correlation coefficient: {correlation:.3f}"
    )
    print(
        f"P-value: {p_value:.6f}"
    )
    print(
        f"Interpretation: {interpret_p_value(p_value)}"
    )

    plt.figure(figsize=(10, 6))

    sns.regplot(
        data=correlation_data,
        x="Year",
        y="Rating",
        scatter_kws={
            "alpha": 0.5,
        },
    )

    plt.title(
        "Relationship Between Release Year and IMDb Rating"
    )
    plt.xlabel("Release Year")
    plt.ylabel("IMDb Rating")

    save_plot(
        "year_rating_correlation.png"
    )

    return {
        "Test": "Pearson correlation",
        "Comparison": "Release year vs rating",
        "Statistic": correlation,
        "P-value": p_value,
        "Sample size": len(correlation_data),
        "Group 1 mean": pd.NA,
        "Group 2 mean": pd.NA,
        "Interpretation": interpret_p_value(p_value),
    }


# ============================================================
# Main program
# ============================================================

def main():
    """
    Run all inferential statistical tests.
    """

    print("=" * 65)
    print("INFERENTIAL STATISTICAL ANALYSIS OF IMDb MOVIES")
    print("=" * 65)

    print(f"\nDataset path:\n{DATASET_PATH}")
    print(f"\nResults directory:\n{RESULTS_DIRECTORY}")

    dataframe = load_and_clean_dataset()

    print("\nDataset loaded successfully.")
    print(f"Total rows with valid ratings: {len(dataframe)}")
    print(
        "Rows with valid years: "
        f"{dataframe['Year'].notna().sum()}"
    )
    print(
        "Rows with valid directors: "
        f"{dataframe['Director'].notna().sum()}"
    )

    print("\nFirst five rows:")
    print(
        dataframe.head().to_string(
            index=False
        )
    )

    results = []

    test_results = [
        run_one_sample_t_test(dataframe),
        run_two_sample_t_test(dataframe),
        run_director_anova(dataframe),
        run_pearson_correlation(dataframe),
    ]

    for result in test_results:
        if result is not None:
            results.append(result)

    if results:
        results_dataframe = pd.DataFrame(results)

        results_path = (
            RESULTS_DIRECTORY
            / "inferential_statistics_results.csv"
        )

        results_dataframe.to_csv(
            results_path,
            index=False,
            encoding="utf-8-sig",
            sep=";",
        )

        print(
            f"\nStatistical results saved to:\n{results_path}"
        )

    print("\nAnalysis completed successfully.")


if __name__ == "__main__":
    main()