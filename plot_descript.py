# descriptive_statistics.py
# Descriptive Statistical Analysis of IMDb Movie Data

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


# ============================================================
# Global configuration
# ============================================================

sns.set_theme(style="whitegrid")

# Directory where the current Python script is located
PROJECT_DIRECTORY = Path(__file__).resolve().parent

# Portable path to the scraped dataset
DATASET_PATH = (
    PROJECT_DIRECTORY
    / "dataset"
    / "imdb_movies.csv"
)

# Directory where plots and tables will be saved
RESULTS_DIRECTORY = (
    PROJECT_DIRECTORY
    / "results"
    / "descriptive_statistics"
)

RESULTS_DIRECTORY.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# Helper functions
# ============================================================

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

    # Remove spaces from column names
    dataframe.columns = dataframe.columns.str.strip()

    required_columns = {
        "Title",
        "Rating",
        "Year",
        "Director",
    }

    missing_columns = required_columns - set(dataframe.columns)

    if missing_columns:
        raise ValueError(
            "The dataset is missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    # Convert ratings to numeric values
    dataframe["Rating"] = pd.to_numeric(
        dataframe["Rating"]
        .astype(str)
        .str.strip()
        .str.replace(",", ".", regex=False),
        errors="coerce",
    )

    # Extract a valid four-digit year
    extracted_year = (
        dataframe["Year"]
        .astype(str)
        .str.extract(r"((?:18|19|20)\d{2})")[0]
    )

    dataframe["Year"] = pd.to_numeric(
        extracted_year,
        errors="coerce",
    ).astype("Int64")

    # Clean text columns
    dataframe["Title"] = (
        dataframe["Title"]
        .astype("string")
        .str.strip()
    )

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

    return dataframe


# ============================================================
# Descriptive statistics
# ============================================================

def calculate_descriptive_statistics(dataframe):
    """
    Calculate and save descriptive statistics.
    """

    print("\nDescriptive statistics:")

    descriptive_statistics = dataframe[
        [
            "Rating",
            "Year",
        ]
    ].describe()

    print(descriptive_statistics)

    output_path = (
        RESULTS_DIRECTORY
        / "descriptive_statistics.csv"
    )

    descriptive_statistics.to_csv(
        output_path,
        encoding="utf-8-sig",
        sep=";",
    )

    print(f"\nStatistics saved to: {output_path}")


def report_missing_values(dataframe):
    """
    Print and save the number of missing values in each column.
    """

    missing_values = dataframe.isna().sum()

    print("\nMissing values:")
    print(missing_values)

    output_path = (
        RESULTS_DIRECTORY
        / "missing_values.csv"
    )

    missing_values.rename(
        "Missing Values"
    ).to_csv(
        output_path,
        encoding="utf-8-sig",
        sep=";",
    )

    print(f"\nMissing-value report saved to: {output_path}")


# ============================================================
# Data visualization
# ============================================================

def create_rating_boxplot(dataframe):
    """
    Create a box plot of IMDb ratings.
    """

    ratings = dataframe["Rating"].dropna()

    if ratings.empty:
        print("\nRating box plot skipped: no valid ratings.")
        return

    plt.figure(figsize=(8, 5))

    sns.boxplot(
        y=ratings,
    )

    plt.title("Distribution of IMDb Ratings")
    plt.ylabel("IMDb Rating")
    plt.xlabel("")
    plt.grid(
        axis="y",
        alpha=0.3,
    )

    save_plot(
        "rating_boxplot.png"
    )


def create_movies_per_year_plot(dataframe):
    """
    Create a bar chart showing the number of movies released each year.
    """

    year_data = dataframe["Year"].dropna()

    if year_data.empty:
        print("\nMovies-per-year plot skipped: no valid years.")
        return

    year_counts = (
        year_data
        .astype(int)
        .value_counts()
        .sort_index()
        .reset_index()
    )

    year_counts.columns = [
        "Year",
        "Movie Count",
    ]

    plt.figure(figsize=(16, 7))

    sns.barplot(
        data=year_counts,
        x="Year",
        y="Movie Count",
    )

    plt.title("Number of Movies by Release Year")
    plt.xlabel("Release Year")
    plt.ylabel("Number of Movies")

    # Display only some year labels if there are many years
    axis = plt.gca()

    for index, label in enumerate(axis.get_xticklabels()):
        if index % 5 != 0:
            label.set_visible(False)

    plt.xticks(
        rotation=90,
    )

    plt.grid(
        axis="y",
        alpha=0.3,
    )

    save_plot(
        "movies_per_year.png"
    )


def create_rating_year_scatterplot(dataframe):
    """
    Create a scatter plot showing the relationship between year and rating.
    """

    plot_data = dataframe.dropna(
        subset=[
            "Year",
            "Rating",
        ]
    ).copy()

    if plot_data.empty:
        print(
            "\nRating-versus-year plot skipped: "
            "no rows contain both rating and year."
        )
        return

    plot_data["Year"] = plot_data["Year"].astype(int)

    plt.figure(figsize=(11, 6))

    sns.scatterplot(
        data=plot_data,
        x="Year",
        y="Rating",
        alpha=0.65,
    )

    plt.title("IMDb Rating by Release Year")
    plt.xlabel("Release Year")
    plt.ylabel("IMDb Rating")
    plt.grid(
        alpha=0.3,
    )

    save_plot(
        "rating_vs_year.png"
    )


def create_rating_histogram(dataframe):
    """
    Create a histogram of IMDb ratings.
    """

    ratings = dataframe["Rating"].dropna()

    if ratings.empty:
        print("\nRating histogram skipped: no valid ratings.")
        return

    plt.figure(figsize=(9, 6))

    sns.histplot(
        ratings,
        bins=20,
        kde=True,
    )

    plt.axvline(
        ratings.mean(),
        linestyle="--",
        label=f"Mean = {ratings.mean():.2f}",
    )

    plt.axvline(
        ratings.median(),
        linestyle=":",
        label=f"Median = {ratings.median():.2f}",
    )

    plt.title("Distribution of IMDb Ratings")
    plt.xlabel("IMDb Rating")
    plt.ylabel("Number of Movies")
    plt.legend()

    save_plot(
        "rating_distribution.png"
    )


# ============================================================
# Main program
# ============================================================

def main():
    """
    Run the descriptive statistical analysis.
    """

    print("=" * 65)
    print("DESCRIPTIVE STATISTICAL ANALYSIS OF IMDb MOVIES")
    print("=" * 65)

    print(f"\nDataset path:\n{DATASET_PATH}")
    print(f"\nResults directory:\n{RESULTS_DIRECTORY}")

    dataframe = load_and_clean_dataset()

    print("\nDataset loaded successfully.")
    print(f"Total number of rows: {len(dataframe)}")
    print(
        f"Valid ratings: "
        f"{dataframe['Rating'].notna().sum()}"
    )
    print(
        f"Valid years: "
        f"{dataframe['Year'].notna().sum()}"
    )
    print(
        f"Valid directors: "
        f"{dataframe['Director'].notna().sum()}"
    )

    print("\nFirst five rows:")
    print(
        dataframe.head().to_string(
            index=False
        )
    )

    # Report missing values before filling or removing them
    report_missing_values(dataframe)

    # Fill missing ratings with the dataset median
    rating_median = dataframe["Rating"].median()

    if not pd.isna(rating_median):
        dataframe["Rating"] = dataframe["Rating"].fillna(
            rating_median
        )

    calculate_descriptive_statistics(dataframe)

    print("\nCreating plots...")

    create_rating_boxplot(dataframe)
    create_movies_per_year_plot(dataframe)
    create_rating_year_scatterplot(dataframe)
    create_rating_histogram(dataframe)

    print("\nAnalysis completed successfully.")


if __name__ == "__main__":
    main()