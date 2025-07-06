import logging
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from typing import Dict, List, Optional, Union


def get_app_links(list_url: str, base_url: str, headers: Optional[dict] = None) -> List[str]:
    """
    Fetches app links from a CafeBazaar list page.

    Args:
        list_url (str): URL of the CafeBazaar list page containing app entries.
        base_url (str): Base URL used to construct full app URLs.
        headers (dict, optional): Optional HTTP headers for the request.

    Returns:
        List[str]: A list of full URLs to individual app detail pages.
    """
    response = requests.get(list_url, headers=headers)
    if response.status_code != 200:
        logging.warning(f"Failed to fetch page. Status code: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')

    app_tags = soup.select('a.SimpleAppItem--single')
    app_links = []

    for tag in app_tags:
        href = tag.get("href")
        if href and href.startswith("/app/"):
            full_link = base_url + href
            app_links.append(full_link)

    return app_links


def extract_app_details(app_url: str) -> Dict[str, str | list]:
    """
    Extracts details of an app from its page.

    Args:
        app_url (str): The full URL of the app page.

    Returns:
        dict: A dictionary containing:
            - name (str): App name.
            - description (str): App description.
            - installs (str): Number of installs.
            - size (str): App size.
            - updated_at (str): Last updated date.
            - image_urls (list): List of screenshot/image URLs.
    """
    headers = {
        "Accept-Language": "fa",
    }

    response = requests.get(app_url, headers=headers)

    if response.status_code != 200:
        logging.warning(f"error in loading page: {response.status_code}")

    soup = BeautifulSoup(response.text, 'html.parser')

    # extract app name
    app_name = soup.find("h1", class_="AppName fs-20")
    if not app_name:
        logging.warning("could not find app name")
        app_name = "untitled"

    # extract app description
    app_description = soup.find("div", class_="AppDescription__content fs-14")
    if not app_description:
        logging.warning("could not find app description")
        app_description = "untitled"

    info_cubes = soup.find_all("td", class_= "InfoCube__content fs-14")

    # extract app installs
    app_installs = info_cubes[0]
    if not app_installs:
        logging.warning("could not find app installs")
        app_installs = "-"

    # extract app size
    app_size = info_cubes[3]

    # extract app update
    app_update_at = info_cubes[4]

    # extract app image urls
    screenshots = []
    for pic in soup.find_all("picture", class_="sg__image"):
        img = pic.find("img")
        if img and img.get("data-lazy-src"):
            screenshots.append(img["data-lazy-src"])
        else:
            source = pic.find("source")
            if source and source.get("data-lazy-srcset"):
                srcset = source["data-lazy-srcset"]
                first_src = srcset.split(",")[0].split()[0]
                screenshots.append(first_src)
    return {
        "name": app_name.text,
        "description": app_description.text,
        "installs": app_installs.text,
        "size": app_size.text,
        "updated_at": app_update_at.text,
        "image_urls": screenshots,
    }

def create_webdriver() -> webdriver.Firefox:
    """
    Creates and returns a headless Firefox WebDriver with recommended options.

    Returns:
        webdriver.Firefox: A configured Firefox WebDriver instance.
    """

    selenium_url = "http://selenium:4444/wd/hub"
    wd_options = Options()
    wd_options.add_argument("--headless")
    wd_options.add_argument('--disable-dev-shm-usage')
    wd_options.add_argument('--no-sandbox')

    wd = webdriver.Remote(command_executor=selenium_url, options=wd_options)

    return wd


def extract_all_comment_elements(wd: webdriver.Firefox, app_url: str) -> List[WebElement]:
    """
    Loads all comment elements for a given app page using Selenium.

    Continuously clicks the "Load more" button to fetch all visible comments, then
    returns the list of WebElement objects representing individual comments.

    Args:
        wd (webdriver.Firefox): An active Selenium WebDriver instance.
        app_url (str): The full URL of the app detail page.

    Returns:
        List[WebElement]: A list of Selenium WebElement objects, each representing a comment.
    """
    logging.info("Extracting app comments")
    wd.get(app_url)

    wait = WebDriverWait(wd, 10)

    try:
        while True:
            load_more_button = wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "AppCommentsList__loadmore"))
            )
            if load_more_button:
                wd.execute_script("arguments[0].scrollIntoView(true);", load_more_button)
                time.sleep(0.5)
                load_more_button.click()
                time.sleep(1)
            else:
                break
    except:
        logging.info("No more 'Load more' buttons or timeout occurred.")

    comment_elements = wd.find_elements(By.CLASS_NAME, "AppCommentsList__item")
    logging.info(f"Found {len(comment_elements)} comments")
    return comment_elements


def extract_comment_details(el: WebElement) -> Dict[str, Optional[Union[str, int]]]:
    """
    Extract details from a Selenium WebElement representing a comment.

    Args:
        el (WebElement): The Selenium WebElement for a single comment.

    Returns:
        Dict[str, Optional[object]]: A dictionary containing:
            - 'id' (Optional[str]): The comment element's id attribute, or None if not found.
            - 'username' (Optional[str]): Username text, or None if not found.
            - 'text' (Optional[str]): Comment body text, or None if not found.
            - 'rating' (Optional[int]): Rating as an integer 0-5, or None if not found or invalid.
            - 'date' (Optional[str]): Comment date text, or None if not found or malformed.
    """
    try:
        external_id = el.get_attribute("id")
    except NoSuchElementException:
        logging.warning(f"could not find 'id' attribute for comment: {el}")
        external_id = None

    try:
        username = el.find_element(By.CLASS_NAME, "AppComment__username").text.strip()
    except NoSuchElementException:
        logging.warning(f"Username not found for comment id: {external_id}")
        username = None

    try:
        body = el.find_element(By.CLASS_NAME, "AppComment__body").text.strip()
    except NoSuchElementException:
        logging.warning(f"Comment body not found for comment id: {external_id}")
        body = None

    try:
        rating_el = el.find_element(By.CLASS_NAME, "rating__fill")
        style = rating_el.get_attribute("style")
        percent = int(style.replace("width:", "").replace("%;", "").replace("%", "").strip()) if style else 0
        rating = round(percent / 20)
    except (NoSuchElementException, ValueError):
        logging.warning(f"Rating not found for comment id: {external_id}")
        rating = None

    try:
        meta_el = el.find_element(By.CLASS_NAME, "AppComment__meta")
        child_divs = meta_el.find_elements(By.XPATH, "./div")
        date = child_divs[1].text.strip() if len(child_divs) > 1 else ""
    except (NoSuchElementException, IndexError):
        logging.warning(f"Date not found or malformed for comment id: {external_id}")
        date = None

    return {
        "id": external_id,
        "username": username,
        "text": body,
        "rating": rating,
        "date": date
    }
