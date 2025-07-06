import logging
from .scraper import get_app_links, create_webdriver
from .savers import save_app_and_comments

logging.basicConfig(level=logging.INFO)

LIST_URL = "https://cafebazaar.ir/lists/ml-mental-health-exercises"
BASE_URL = "https://cafebazaar.ir"

def run_scraper() -> None:
    """
    Runs the scraper to fetch app links from the listing page,
    then processes each app URL to save app details and comments.

    Logs progress info for each processed app.
    """
    logging.info("Fetching app links...")
    app_links = get_app_links(LIST_URL, BASE_URL)

    wd = create_webdriver()

    try:
        for app_url in app_links:
            logging.info(f"Processing app: {app_url}")
            save_app_and_comments(wd, app_url)
    finally:
        wd.quit()
        logging.info("WebDriver quit, scraper finished.")


if __name__ == "__main__":
    run_scraper()
