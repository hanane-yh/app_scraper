import logging
import re
from datetime import date, datetime
from typing import Optional
import jdatetime

PERSIAN_MONTHS = {
    "فروردین": 1,
    "اردیبهشت": 2,
    "خرداد": 3,
    "تیر": 4,
    "مرداد": 5,
    "شهریور": 6,
    "مهر": 7,
    "آبان": 8,
    "آذر": 9,
    "دی": 10,
    "بهمن": 11,
    "اسفند": 12,
}

def convert_persian_digits_to_english(persian_str: str) -> str:
    """
    Convert Persian digits in a string to English digits.

    Args:
        persian_str (str): String potentially containing Persian digits.

    Returns:
        str: String with Persian digits replaced by English digits.
    """
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    english_digits = "0123456789"
    return persian_str.translate(str.maketrans(persian_digits, english_digits))


def contains_persian(text: str) -> bool:
    """
    Check if the given text contains any Persian characters.

    Args:
        text (str): Text to check.

    Returns:
        bool: True if Persian characters found, False otherwise.
    """
    return bool(re.search(r'[\u0600-\u06FF]', text))


def parse_jalali_date(persian_date_str: Optional[str]) -> Optional[date]:
    """
    Parses a Persian (Jalali) or Gregorian date string and returns a corresponding Gregorian `date` object.

    The function supports:
    - Numeric formats: e.g. '۱۴۰۴/۰۴/۰۱', '1404/4/1', or '2025/4/1'
    - Textual formats: e.g. '۱ تیر ۱۴۰۴' (Jalali) or '2025 July 5' (Gregorian)

    Persian digits are automatically converted to English digits.

    Args:
        persian_date_str (Optional[str]): The input date string in Persian or Gregorian format.

    Returns:
        Optional[date]: A Python `date` object in Gregorian calendar, or `None` if parsing fails.
    """

    if not persian_date_str:
        return None

    is_jalali = contains_persian(persian_date_str)
    cleaned = convert_persian_digits_to_english(persian_date_str.strip())

    # ۱۴۰۴/۰۴/۰۱ or 1404/4/1 or 2025/4/1
    if "/" in cleaned and len(cleaned.split("/")) == 3:
        try:
            year, month, day = map(int, cleaned.split("/"))
            if is_jalali:
                jalali_date = jdatetime.date(year, month, day)
                return jalali_date.togregorian()
            else:
                return date(year, month, day)
        except (ValueError, TypeError) as e:
            logging.warning(f"Error parsing slash date '{persian_date_str}': {e}")
            return None

    # ۱ تیر ۱۴۰۴  July 5 2025 or
    parts = cleaned.split()
    if len(parts) == 3:
        day_str, month_str, year_str = parts
        if is_jalali:
            try:
                day = int(day_str)
                month = PERSIAN_MONTHS.get(month_str)
                year = int(year_str)
                if not month:
                    logging.warning(f"Invalid Persian month name: {month_str}")
                    return None
                jalali_date = jdatetime.date(year, month, day)
                return jalali_date.togregorian()
            except (ValueError, TypeError) as e:
                logging.warning(f"Error parsing Jalali text date '{persian_date_str}': {e}")
                return None
        else:
            try:
                return datetime.strptime(cleaned, "%Y %B %d").date()
            except ValueError as e:
                logging.warning(f"Error parsing Gregorian text date '{persian_date_str}': {e}")
                return None
    return None



def parse_installs(installs_str: Optional[str]) -> int:
    """
    Parses an installation count string and returns the numeric value as an integer.

    This function handles:
    - Persian digits (e.g., "۱۰ هزار")
    - English digits with units (e.g., "5k", "1000+")
    - Strips irrelevant symbols and performs appropriate conversion.

    Args:
        installs_str (Optional[str]): A string representing the number of installs.

    Returns:
        int: The parsed number of installs as an integer. Returns 0 if input is None or cannot be parsed.
    """
    if not installs_str:
        return 0

    text = convert_persian_digits_to_english(installs_str)
    text = text.replace('+', '').strip().lower()

    if 'هزار' in text:
        number = text.replace('هزار', '').strip()
        return int(float(number) * 1000)

    elif 'k' in text:
        number = text.replace('k', '').strip()
        return int(float(number) * 1000)

    else:
        number = ''.join(filter(str.isdigit, text))
        return int(number) if number else 0


def parse_size(size_str: Optional[str]) -> int:
    """
    Parses a file size string and returns the size as an integer in megabytes (MB).

    Handles both Persian and English representations of:
    - Numbers (e.g., '۲۱۵' → '215')
    - Units (e.g., 'مگابایت', 'MB')

    Args:
        size_str (Optional[str]): A string representing the file size, possibly with Persian digits or units.

    Returns:
        int: The parsed size in megabytes. Returns 0 if the input is None, empty, or cannot be parsed.
    """
    if not size_str:
        return 0

    text = convert_persian_digits_to_english(size_str)
    text = text.strip().lower()

    if 'مگابایت' in text:
        text = text.replace('مگابایت', '').strip()
    elif 'MB' in text:
        text = text.replace('MB', '').strip()

    try:
        return int(float(text))
    except ValueError:
        return 0
