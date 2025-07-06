import logging
from typing import Any

from selenium import webdriver

from .models import App, Comment, User
from .scraper import extract_all_comment_elements, extract_app_details, extract_comment_details
from .utils import parse_installs, parse_jalali_date, parse_size


def save_app_details(app_data: dict[str, Any]) -> App:
    """
    Saves or updates an App instance in the database using the provided app data.

    Args:
        app_data (dict): Dictionary containing app details with keys:
            - "name" (str): Name of the app.
            - "description" (str): Description of the app.
            - "installs" (str): Number of installs as a string to be parsed.
            - "size" (str): App size as a string to be parsed.
            - "updated_at" (str): Last update date in Jalali format string.
            - "image_urls" (list): List of image URLs for the app.

    Returns:
        App: The created or updated App model instance.
    """

    app_instance, _ = App.objects.update_or_create(
        name=app_data["name"],
        defaults={
            "description": app_data["description"],
            "installs": parse_installs(app_data["installs"]),
            "size": parse_size(app_data["size"]),
            "updated_at": parse_jalali_date(app_data["updated_at"]),
            "image_urls": app_data["image_urls"],
        }
    )
    return app_instance


def save_comment_details(app_instance: App, comment_data: dict[str, Any]) -> None:
    """
    Saves or updates a Comment instance related to the given App and User.

    Args:
        app_instance (App): The App model instance the comment belongs to.
        comment_data (dict): Dictionary containing comment details with keys:
            - "id" (str): Unique user identifier.
            - "username" (Optional[str]): Username of the commenter.
            - "text" (str): Comment text.
            - "rating" (Optional[int]): Rating value (0-5).
            - "date" (str): Comment date in Jalali format string.

    Returns:
        None
    """
    user_instance = None
    if comment_data["username"]:
        user_instance, _ = User.objects.get_or_create(
            user_id=comment_data["id"],
            defaults={"display_name": comment_data["username"]}
        )

    Comment.objects.update_or_create(
        app=app_instance,
        user=user_instance,
        text=comment_data["text"],
        defaults={
            "rating": comment_data["rating"],
            "comment_date": parse_jalali_date(comment_data["date"]),
        }
    )


def save_app_and_comments(wd: webdriver.Firefox, app_url: str) -> None:
    """
    Extracts app details and comments from the given app URL, then saves them to the database.

    Args:
        wd (webdriver.Firefox): An active Selenium WebDriver instance.
        app_url (str): The URL of the app page to scrape and save data from.

    Returns:
        None

    Side Effects:
        Saves or updates App, User, and Comment instances in the database.
        Logs info and error messages regarding the scraping and saving process.
    """
    try:
        # extract and save app
        app_data = extract_app_details(app_url)
        app_instance = save_app_details(app_data)
        logging.info(f"Saved app: {app_instance.name}")

        # extract comment elements
        comment_elements = extract_all_comment_elements(wd, app_url)

        # loop through and save each comment
        for el in comment_elements:
            comment_data = extract_comment_details(el)
            if comment_data:
                save_comment_details(app_instance, comment_data)
        logging.info(f"Saved {len(comment_elements)} comments for app: {app_instance.name}")

    except Exception as e:
        logging.error(f"Failed to save app and comments for {app_url}: {e}")
