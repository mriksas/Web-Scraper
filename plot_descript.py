import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Loading dataset
file_path = r"C:\Users\Vadym\Desktop\webscraping\dataset\imdb_movies.csv"

# Checking if file exists
if not os.path.exists(file_path):
    print("CSV file not found. Make sure the web scraping script has run successfully.")
else:
    # Load data
    df = pd.read_csv(file_path, sep=";", encoding="utf-8-sig")

    # Convert "Rating" to float (remove spaces)
    df["Rating"] = df["Rating"].astype(str).str.strip().astype(float)

    # Convert "Year" to integer (remove spaces)
    df["Year"] = df["Year"].astype(str).str.strip().astype(int)

    # Descriptive Statistics
    print("\n🔹 Descriptive Statistics:")
    print(df.describe())

    # Handling thr missing values
    print("\n🔹 Missing Values:")
    print(df.isnull().sum())

    # Filling missing values in rating with median
    df["Rating"].fillna(df["Rating"].median(), inplace=True)


    # Box plot of patings**
    plt.figure(figsize=(8, 5))
    sns.boxplot(y=df["Rating"], color="blue")
    plt.title("Box plot of IMDb ratings")
    plt.ylabel("Rating")
    plt.grid()
    plt.show()

    # Bar chart of movie counts per year**
    plt.figure(figsize=(10, 5))
    sns.countplot(x=df["Year"], palette="viridis", order=df["Year"].value_counts().index)
    plt.xticks(rotation=90)
    plt.title("Number of movies by year")
    plt.xlabel("Year")
    plt.ylabel("Count")
    plt.grid()
    plt.show()

    # 🔵 **Scatter plot: rating vs year**
    plt.figure(figsize=(10, 5))
    sns.scatterplot(x=df["Year"], y=df["Rating"], alpha=0.7)
    plt.title("Scatter Plot: Rating vs Year")
    plt.xlabel("Year")
    plt.ylabel("Rating")
    plt.grid()
    plt.show()
