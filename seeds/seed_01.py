from typing import Dict, List, Union
import json
import sys
import os


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from config.models import Author, Quote
from custom_logger import logger
import config.connect_db


def loading_data__from_file(filename: str) -> Dict[str, Union[str, List[str]]]:
    """
    Load data from a JSON file.

    Args:
        filename (str): The name of the JSON file.

    Returns:
        dict: The loaded data from the JSON file.
    """
    try:
        with open(filename, "r", encoding="utf-8") as fh:
            data = json.load(fh)
            return data
    except FileNotFoundError as e:
        logger.log(f"File does not exist - {e} !", level=40)
    except Exception as e:
        logger.log(f"Error loading data from file - {e}", level=40)


def push_authors() -> None:
    """
    Upload authors data from "authors.json" to the database.
    """
    try:
        authors = loading_data__from_file("authors.json")
        for el in authors:
            Author(
                fullname=el.get("fullname"),
                born_date=el.get("born_date"),
                born_location=el.get("born_location"),
                description=el.get("description"),
            ).save()
            logger.log("Authors data push successfully.")
    except Exception as e:
        logger.log(f"Error push authors data - {e}", level=40)


def push_quotes() -> None:
    """
    Upload quotes data from 'quotes.json' to the database.
    """
    try:
        quotes = loading_data__from_file("quotes.json")
        for el in quotes:
            author, *_ = Author.objects(fullname=el.get("author"))
            Quote(quote=el.get("quote"), tags=el.get("tags"), author=author).save()
            logger.log("Quotes data push successfully.")
    except Exception as e:
        logger.log(f"Error push quotes data - {e}", level=40)


def main() -> None:
    """
    Main function to execute data push.
    """
    try:
        push_authors()
        push_quotes()
    except Exception as e:
        logger.log(f"Error in main function - {e}", level=40)


if __name__ == "__main__":
    main()
