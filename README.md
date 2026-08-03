# IMDb Web Scraper and Statistical Analysis

## Overview

This project collects movie data from an IMDb list and performs descriptive and inferential statistical analysis.

The workflow includes:

1. Web scraping with Selenium
2. Data cleaning and CSV export
3. Descriptive statistics and visualisation
4. Inferential statistical testing

The dataset contains the following fields:

| Column | Description |
|---|---|
| `Title` | Movie title |
| `Rating` | IMDb user rating |
| `Year` | Movie release year |
| `Director` | First listed director |

The scraper saves the dataset to:

```text
dataset/imdb_movies.csv
```

---

---

## Requirements

- Python 3.10 or later
- Google Chrome
- Internet connection for scraping IMDb

Install the required libraries:

```bash
python -m pip install pandas selenium webdriver-manager matplotlib seaborn scipy
```

### Main Libraries

| Library | Purpose |
|---|---|
| `selenium` | Browser automation and web scraping |
| `webdriver-manager` | Automatic ChromeDriver installation |
| `pandas` | Data cleaning and analysis |
| `matplotlib` | Plot generation |
| `seaborn` | Statistical visualisation |
| `scipy` | Inferential statistical tests |

---

## How to Run

### 1. Scrape the IMDb Data

```bash
python scraper.py
```

The scraper:

- opens the IMDb list pages;
- waits for movie cards to load;
- extracts titles, ratings, years, and directors;
- removes duplicated records;
- saves up to 300 movies in CSV format.

Output:

```text
dataset/imdb_movies.csv
```

### 2. Run Descriptive Analysis

```bash
python plot_descript.py
```

This script:

- loads and cleans the dataset;
- converts ratings and years to numeric values;
- reports missing values;
- calculates descriptive statistics;
- creates exploratory plots.

### 3. Run Inferential Analysis

```bash
python plot_inf.py
```

This script performs:

- one-sample t-test;
- Welch two-sample t-test;
- one-way ANOVA;
- Pearson correlation test.

The numerical results are saved to:

```text
results/inferential_statistics/inferential_statistics_results.csv
```

---

# Experimental Analysis

## Objective

The purpose of the experiment was to answer the following questions:

1. What is the general distribution of IMDb ratings?
2. Is the average rating different from 7.0?
3. Do ratings differ between movies released before 2000 and movies released in 2000 or later?
4. Is release year associated with IMDb rating?
5. Do ratings differ among frequently represented directors?

---

## Data Collection and Preparation

The data were collected from the IMDb **Top 300 Movies** list using Selenium.

The following preprocessing steps were applied:

- removal of leading and trailing spaces;
- conversion of ratings to numeric values;
- extraction and conversion of four-digit release years;
- replacement of invalid values with missing values;
- duplicate removal;
- exclusion of missing values from analyses that require complete observations.

The source is a curated movie list rather than a random sample of all IMDb titles. Therefore, the results describe this particular list and should not be generalised to the complete IMDb database.

---

# Descriptive Results

## Movies by Release Year

![Number of Movies by Release Year](results/descriptive_statistics/movies_per_year.png)

The dataset contains movies released from approximately the late 1920s to the early 2010s.

Earlier decades contain relatively few observations, while the number of selected movies increases in the 1980s, 1990s, and 2000s. The largest concentrations occur in the early and middle 2000s.

This pattern reflects the composition of the selected IMDb list. It should not be interpreted as a direct measure of worldwide movie production.

---

## Rating Box Plot

![IMDb Rating Box Plot](results/descriptive_statistics/rating_boxplot.png)

The median IMDb rating is approximately **7.7**.

The middle 50% of ratings is concentrated approximately between **7.4 and 8.1**. Several observations fall outside the main range, including low outliers near 5.7 and 6.2 and high outliers above 9.1.

The relatively narrow central range confirms that the selected list mainly contains highly rated movies.

---

## Rating Distribution

![Distribution of IMDb Ratings](results/descriptive_statistics/rating_distribution.png)

The mean rating is approximately **7.71**, while the median is approximately **7.70**.

Because the mean and median are nearly identical, the distribution is not strongly skewed. Most movies have ratings between approximately **7.0 and 8.5**, while very low and very high values occur less frequently.

---

## Rating by Release Year

![IMDb Rating by Release Year](results/descriptive_statistics/rating_vs_year.png)

The scatter plot does not show a strong relationship between release year and rating.

Highly rated and moderately rated movies appear across both older and newer periods. More points are visible in recent decades because the dataset contains more recent movies, not because newer movies necessarily receive better ratings.

Release year alone therefore appears to be a weak predictor of IMDb rating.

---

# Inferential Results

## One-Sample T-Test

The one-sample t-test evaluates whether the mean IMDb rating differs from 7.0.

```text
H0: μ = 7.0
H1: μ ≠ 7.0
```

![One-Sample T-Test](results/inferential_statistics/one_sample_t_test.png)

The observed sample mean is approximately **7.71**, which is clearly higher than the hypothesised value of 7.0.

The generated test output should be used to confirm the exact p-value. The difference is large enough to indicate that the average rating in this curated list is substantially above 7.0.

This conclusion applies only to the selected Top 300 list and not to all movies on IMDb.

---

## Ratings Before and After 2000

Welch's two-sample t-test compares:

- movies released before 2000;
- movies released in 2000 or later.

```text
H0: μbefore = μafter
H1: μbefore ≠ μafter
```

![Movie Ratings Before and After 2000](results/inferential_statistics/two_sample_t_test.png)

The two groups have very similar medians, both close to 7.7, and their interquartile ranges overlap strongly.

The visual difference between the groups is small. This suggests that the release period does not substantially change the typical IMDb rating in this dataset.

The exact conclusion about statistical significance should be based on the p-value saved by the script.

---

## Correlation Between Year and Rating

Pearson correlation evaluates the linear relationship between release year and IMDb rating.

```text
H0: ρ = 0
H1: ρ ≠ 0
```

![Relationship Between Release Year and IMDb Rating](results/inferential_statistics/year_rating_correlation.png)

The regression line has a slight negative slope, but the observations are widely dispersed around it.

This indicates that any relationship between release year and rating is weak. Release year explains very little of the variation in IMDb ratings.

Even if the statistical test identifies a significant relationship, its practical effect is likely to be small.

---

## One-Way ANOVA by Director

The one-way ANOVA compares ratings among five frequently represented directors:

- Martin Scorsese
- Stanley Kubrick
- Clint Eastwood
- Roman Polanski
- Francis Ford Coppola

```text
H0: All director mean ratings are equal
H1: At least one director mean rating is different
```

![Movie Ratings by Director](results/inferential_statistics/director_anova.png)

The distributions differ visually across directors.

Francis Ford Coppola has the highest median among the selected groups, while Roman Polanski shows a wider rating spread and a lower median. Stanley Kubrick and Martin Scorsese have relatively high and compact distributions, while Clint Eastwood is centred slightly lower.

The ANOVA p-value should be used to determine whether the observed differences are statistically significant.

If the ANOVA result is significant, a post-hoc test such as Tukey's HSD would be required to identify which director pairs differ.

---

# Main Findings

- The selected movies have a mean and median rating of approximately **7.7**.
- Most ratings fall between approximately **7.0 and 8.5**.
- The average rating is clearly above the reference value of 7.0.
- Movies released before and after 2000 have similar rating distributions.
- Release year has only a weak relationship with IMDb rating.
- Rating distributions differ visually among the selected directors.
- Recent decades are more strongly represented in the dataset than earlier decades.

---

# Limitations

## Selection Bias

The dataset comes from a curated Top 300 list. Low-rated and ordinary movies are underrepresented.

## Non-Random Sampling

The records were not randomly sampled from the complete IMDb database. Statistical inference should therefore be interpreted cautiously.

## IMDb User Ratings

IMDb scores are based on user votes and may be influenced by popularity, fan communities, recency, and vote count.

## Unequal Director Group Sizes

Some directors are represented by only a small number of movies. Their mean and variance estimates may therefore be unstable.

## Temporal Imbalance

Recent decades contain more observations than earlier decades, which may affect comparisons involving release year.

## No Causal Interpretation

Correlation and group differences do not establish causality. Release year or director identity cannot be treated as a direct cause of an IMDb rating.

---

# Conclusion

This project demonstrates a complete data-analysis workflow:

1. automated web scraping;
2. dataset creation;
3. data cleaning;
4. descriptive visualisation;
5. hypothesis testing;
6. interpretation of statistical results.

The selected IMDb list is strongly concentrated around highly rated movies, with a typical score of approximately 7.7.

The analysis provides little evidence of a practically meaningful relationship between release year and rating. Movies released before and after 2000 also show similar central rating distributions.

Differences are visible among director groups, but they should be interpreted together with the ANOVA p-value and the small group sizes.

Overall, the project demonstrates how web-scraped data can be transformed into a structured dataset and used for reproducible statistical analysis.
