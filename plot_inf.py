import pandas as pd
import scipy.stats as stats
import os
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
file_path = r"C:\Users\Vadym\Desktop\webscraping\dataset\imdb_movies.csv"

if not os.path.exists(file_path):
    print("CSV file not found. Please run the scraper first.")
else:
    df = pd.read_csv(file_path, sep=";", encoding="utf-8-sig")

    # Clean columns
    df["Rating"] = df["Rating"].astype(str).str.strip().astype(float)
    df["Year"] = df["Year"].astype(str).str.strip().astype(int)

    print("\n🔹 Dataset loaded for inferential statistics")
    print(df.head())

    # 1️⃣ One-sample t-test: Is the mean rating different from 7.0?
    t_stat, p_val = stats.ttest_1samp(df["Rating"], 7.0)
    print("\n📊 One-sample t-test (mean rating vs 7.0):")
    print(f"T-statistic = {t_stat:.3f}, p-value = {p_val:.4f}")

    # Plot histogram with test mean line
    plt.figure(figsize=(8, 5))
    sns.histplot(df["Rating"], bins=20, kde=True, color="blue")
    plt.axvline(7.0, color="red", linestyle="--", label="Test mean = 7.0")
    plt.axvline(df["Rating"].mean(), color="green", linestyle="--", label=f"Sample mean = {df['Rating'].mean():.2f}")
    plt.title("One-sample t-test: Ratings vs Mean 7.0")
    plt.xlabel("Rating")
    plt.ylabel("Frequency")
    plt.legend()
    plt.show()

    # 2️⃣ Two-sample t-test: Before vs after 2000
    before_2000 = df[df["Year"] < 2000]["Rating"]
    after_2000 = df[df["Year"] >= 2000]["Rating"]
    t_stat, p_val = stats.ttest_ind(before_2000, after_2000, equal_var=False)
    print("\n📊 Two-sample t-test (before 2000 vs after 2000):")
    print(f"T-statistic = {t_stat:.3f}, p-value = {p_val:.4f}")

    # Plot boxplot comparison
    plt.figure(figsize=(8, 5))
    sns.boxplot(data=[before_2000, after_2000], palette="Set2")
    plt.xticks([0, 1], ["Before 2000", "After 2000"])
    plt.title("Two-sample t-test: Ratings Before vs After 2000")
    plt.ylabel("Rating")
    plt.show()

    # 3️⃣ ANOVA: Directors’ ratings
    top_directors = df["Director"].value_counts().index[:5]  # top 5 directors
    df_top_directors = df[df["Director"].isin(top_directors)]
    f_stat, p_val = stats.f_oneway(*[df_top_directors[df_top_directors["Director"] == d]["Rating"] for d in top_directors])
    print("\n📊 ANOVA test (top 5 directors' ratings):")
    print(f"F-statistic = {f_stat:.3f}, p-value = {p_val:.4f}")

    # Plot boxplot for directors
    plt.figure(figsize=(10, 6))
    sns.boxplot(x="Director", y="Rating", data=df_top_directors, palette="muted")
    plt.title("ANOVA: Ratings by Top 5 Directors")
    plt.xticks(rotation=45)
    plt.ylabel("Rating")
    plt.show()

    # 4️⃣ Correlation test: Year vs Rating
    corr, p_val = stats.pearsonr(df["Year"], df["Rating"])
    print("\n📊 Pearson correlation (Year vs Rating):")
    print(f"Correlation coefficient = {corr:.3f}, p-value = {p_val:.4f}")

    # Scatterplot with regression line
    plt.figure(figsize=(10, 6))
    sns.regplot(x="Year", y="Rating", data=df, scatter_kws={'alpha':0.5}, line_kws={"color":"red"})
    plt.title("Correlation: Year vs Rating")
    plt.xlabel("Year")
    plt.ylabel("Rating")
    plt.show()
