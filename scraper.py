import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import re  # For removing numbers before movie titles

def scrape_movies():
    # List of IMDb pages to scrape
    urls = [
        "https://www.imdb.com/list/ls003857730/",
        "https://www.imdb.com/list/ls003857730/?page=2"
    ]

    # Path to save the dataset
    save_path = r"C:\Users\Vadym\Desktop\webscraping\dataset\imdb_movies.csv"

    # Delete old file before starting
    if os.path.exists(save_path):
        os.remove(save_path)

    # Selenium browser options
    options = Options()
    options.add_argument("--start-maximized")  # Maximize window
    options.add_argument("--lang=en-US")  # Set English language

    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # List to store movies
    movies = []

    # Function to scrape data from a single page
    def get_movies_from_page(url):
        driver.get(url)
        print(f"🔄 Loading page: {url}")

        # Wait for movie list to load
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='list-page-mc-list-content']"))
        )

        # Scroll down to load all movies
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for content to load

        # Find all movie blocks
        movie_blocks = driver.find_elements(By.CSS_SELECTOR, "li.ipc-metadata-list-summary-item")

        # List to store movies from this page
        page_movies = []
        for block in movie_blocks:
            # Extract movie title and remove numbers like "1. ", "2. "
            title_elem = block.find_elements(By.CSS_SELECTOR, "h3.ipc-title__text")
            title = title_elem[0].text.strip() if title_elem else "N/A"
            title = re.sub(r"^\d+\.\s*", "", title)  # Remove numbers before title

            # Extract movie rating (force text format by adding a space)
            rating_elem = block.find_elements(By.CSS_SELECTOR, "span.ipc-rating-star--rating")
            rating = rating_elem[0].text.strip() if rating_elem else "N/A"
            rating = rating.replace(",", ".")  # Replace comma with dot for decimal format
            rating = f" {rating}"  # Add a space to prevent Excel date conversion

            # Extract movie year
            year_elem = block.find_elements(By.CSS_SELECTOR, "span.sc-15ac7568-7")
            year = year_elem[0].text.strip() if year_elem else "N/A"

            # Extract movie director (only the first one)
            director_elems = block.find_elements(By.CSS_SELECTOR, "span.sc-9d52d06f-2")
            director = director_elems[0].text.strip() if director_elems else "N/A"

            # Append movie data as a tuple
            page_movies.append((title, rating, year, director))

        return page_movies

    # Loop through both pages and collect data
    for url in urls:
        movies.extend(get_movies_from_page(url))

    # Close the browser
    driver.quit()

    # Keep only the first 300 movies
    movies = movies[:300]

    # Save the dataset in CSV format (UTF-8 encoding for proper display)
    df = pd.DataFrame(movies, columns=["Title", "Rating", "Year", "Director"])
    df.to_csv(save_path, index=False, encoding="utf-8-sig", sep=";")  # Set `;` as separator for Excel

    print(f"✅ File saved: {save_path}")

scrape_movies()
