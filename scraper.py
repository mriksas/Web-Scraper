import re
import time
from pathlib import Path

import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


URLS = [
    "https://www.imdb.com/list/ls003857730/",
    "https://www.imdb.com/list/ls003857730/?page=2",
]

MOVIE_CARD_SELECTOR = (
    "div[data-testid='list-page-mc-list-content'] "
    "li.ipc-metadata-list-summary-item"
)


def extract_first_text(element, selector, default="N/A"):
    """
    Return text from the first matching child element.
    """

    elements = element.find_elements(
        By.CSS_SELECTOR,
        selector,
    )

    if not elements:
        return default

    value = elements[0].text.strip()
    return value if value else default


def extract_title(movie_block):
    """
    Extract the movie title and remove its list position.
    """

    title = extract_first_text(
        movie_block,
        "h3.ipc-title__text, h4.ipc-title__text",
    )

    return re.sub(
        r"^\d+\.\s*",
        "",
        title,
    )


def extract_rating(movie_block):
    """
    Extract the IMDb rating as a numeric value.
    """

    rating_text = extract_first_text(
        movie_block,
        "span.ipc-rating-star--rating",
    )

    if rating_text == "N/A":
        return None

    try:
        return float(
            rating_text.replace(",", ".")
        )
    except ValueError:
        return None


def extract_year(movie_block):
    """
    Extract the movie release year from the metadata section.
    """

    year_elements = movie_block.find_elements(
        By.CSS_SELECTOR,
        "div.dli-title-metadata > ul > li:nth-child(1)",
    )

    if not year_elements:
        return None

    year_text = (
        year_elements[0].get_attribute("textContent")
        or ""
    ).strip()

    match = re.search(
        r"\b(?:18|19|20)\d{2}\b",
        year_text,
    )

    return int(match.group()) if match else None


def extract_director(movie_block):
    """
    Extract the first director listed in the movie card.
    """

    director_links = movie_block.find_elements(
        By.XPATH,
        ".//*[normalize-space()='Director' "
        "or normalize-space()='Directors']"
        "/following-sibling::*[1]"
        "//a[contains(@href, '/name/')]",
    )

    if director_links:
        return director_links[0].text.strip()

    # Alternative XPath for a slightly different IMDb structure
    director_links = movie_block.find_elements(
        By.XPATH,
        ".//*[normalize-space()='Director' "
        "or normalize-space()='Directors']"
        "/parent::*"
        "//a[contains(@href, '/name/')]",
    )

    if director_links:
        return director_links[0].text.strip()

    return "N/A"


def extract_imdb_id(movie_block):
    """
    Extract the IMDb title ID for duplicate detection.
    """

    links = movie_block.find_elements(
        By.CSS_SELECTOR,
        "a.ipc-title-link-wrapper[href*='/title/tt']",
    )

    if not links:
        return None

    href = links[0].get_attribute("href") or ""
    match = re.search(r"/title/(tt\d+)", href)

    return match.group(1) if match else None


def scroll_until_loaded(driver):
    """
    Scroll down until the number of loaded movie cards stops changing.
    """

    previous_count = 0
    stable_rounds = 0

    for _ in range(20):
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);"
        )

        time.sleep(1)

        current_count = len(
            driver.find_elements(
                By.CSS_SELECTOR,
                MOVIE_CARD_SELECTOR,
            )
        )

        if current_count == previous_count:
            stable_rounds += 1
        else:
            stable_rounds = 0

        previous_count = current_count

        if stable_rounds >= 2:
            break


def get_movies_from_page(driver, url):
    """
    Scrape all loaded movie cards from one IMDb list page.
    """

    print(f"Loading page: {url}")
    driver.get(url)

    # Wait until at least one movie card appears
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                MOVIE_CARD_SELECTOR,
            )
        )
    )

    scroll_until_loaded(driver)

    movie_blocks = driver.find_elements(
        By.CSS_SELECTOR,
        MOVIE_CARD_SELECTOR,
    )

    print(f"Movie cards found: {len(movie_blocks)}")

    page_movies = []

    for position, movie_block in enumerate(
        movie_blocks,
        start=1,
    ):
        try:
            movie = {
                "IMDb_ID": extract_imdb_id(movie_block),
                "Title": extract_title(movie_block),
                "Rating": extract_rating(movie_block),
                "Year": extract_year(movie_block),
                "Director": extract_director(movie_block),
            }

            page_movies.append(movie)

        except Exception as error:
            print(
                f"Could not parse movie card "
                f"{position}: {error}"
            )

    return page_movies


def scrape_movies():
    """
    Run the complete IMDb scraping workflow.
    """

    project_directory = Path(__file__).resolve().parent

    dataset_directory = (
        project_directory / "dataset"
    )

    dataset_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    save_path = (
        dataset_directory / "imdb_movies.csv"
    )

    print(f"Dataset will be saved to: {save_path}")

    # Delete the previous output file
    if save_path.exists():
        save_path.unlink()

    options = Options()

    options.add_argument("--start-maximized")
    options.add_argument("--lang=en-US")
    options.add_argument(
        "--disable-notifications"
    )

    driver = webdriver.Chrome(
        service=Service(
            ChromeDriverManager().install()
        ),
        options=options,
    )

    movies = []

    try:
        for url in URLS:
            page_movies = get_movies_from_page(
                driver,
                url,
            )

            movies.extend(page_movies)

    finally:
        driver.quit()

    if not movies:
        raise RuntimeError(
            "No movies were scraped. "
            "The IMDb page structure may have changed."
        )

    dataframe = pd.DataFrame(movies)

    # Remove duplicate movies using their IMDb IDs
    dataframe = dataframe.drop_duplicates(
        subset=["IMDb_ID"],
        keep="first",
    )

    # Keep only the first 300 movies
    dataframe = dataframe.head(300)

    # Remove the technical ID from the exported dataset
    dataframe = dataframe[
        [
            "Title",
            "Rating",
            "Year",
            "Director",
        ]
    ]

    dataframe.to_csv(
        save_path,
        index=False,
        encoding="utf-8-sig",
        sep=";",
    )

    print(f"Movies saved: {len(dataframe)}")
    print(f"File saved: {save_path}")

    print("\nFirst five rows:")
    print(dataframe.head().to_string(index=False))


if __name__ == "__main__":
    scrape_movies()