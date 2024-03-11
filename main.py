from config.models import Author, Quote
from typing import List, Dict, Union
from custom_logger import logger
import config.connect_db


from redis_lru import RedisLRU
from tabulate import tabulate
import redis


client = redis.StrictRedis(host="localhost", port=6379, password=None)
cache = RedisLRU(client)


@cache
def all_commands() -> str:
    """
    Generate and return a string containing available commands and their explanations.

    Returns:
        str: A string containing available commands and their explanations.
    """
    command_list = ["tag", "tags", "name", "exit"]
    command_explain = [
        "search data in the db by the tag. Use it on format 'tag:life' and then press enter",
        "search data in the db by the tags. Use it on format 'tags:life,live' and then press enter",
        "search data in the db by the name. Use it on format name:Steve Martin' and then press enter",
        "Exit",
    ]
    return "".join(
        "|{:<5} - {:<20}|\n".format(command_list[item], command_explain[item])
        for item in range(len(command_list))
    )


@cache
def get_tag(input: str) -> List[Dict[str, str]]:
    """
    Search quotes in the database by tag.

    Args:
        input (str): The input command in the format 'tag:<tag>' or 'tags:<tag1>,<tag2>'.

    Returns:
        List[Dict[str, str]]: A list of dictionaries containing quotes and their authors.
    """
    command, value = input.split(":", 1)
    tag_list = value.split(",")

    logger.log(f"{command.upper()} command execution!")

    result_list = []
    for item in tag_list:
        result_list.append(Quote.objects(tags__iregex=item.strip()))

    result = [{q.author.fullname: q.quote for q in elem} for elem in result_list]

    logger.log("Operation successful!")
    return result


@cache
def get_name(input: str) -> List[Dict[str, List[str]]]:
    """
    Search quotes in the database by author's name.

    Args:
        input (str): The input command in the format 'name:<author>'.

    Returns:
        List[Dict[str, List[str]]]: A list of dictionaries containing authors and their quotes.
    """
    command, value = input.split(":", 1)
    logger.log(f"{command.upper()} command execution!")

    authors = Author.objects(fullname__iregex=value.strip())
    result = {}
    result_list = []
    for a in authors:
        quotes = Quote.objects(author=a)
        result[a.fullname] = [q.quote for q in quotes]
    result_list.append(result)

    logger.log("Operation successful!")
    return result_list


def main() -> None:
    """
    Main function to execute the quote search application.
    """
    while True:
        try:
            logger.log("To see all list of commands enter 'help'.")
            input_from_user = input("Enter your command:>>> ")

            if input_from_user.lower() == "show":
                logger.log(
                    tabulate(
                        [
                            (i, desc)
                            for i, desc in enumerate(all_commands().split("\n"))
                        ],
                        headers=["Command", "Description"],
                        tablefmt="pretty",
                    )
                )

            elif (
                input_from_user.lower().find("tag:") != -1
                or input_from_user.lower().find("tags:") != -1
            ):
                logger.log(
                    tabulate(
                        get_tag(input_from_user), headers="keys", tablefmt="pretty"
                    )
                )

            elif input_from_user.lower().find("name:") != -1:
                logger.log(
                    tabulate(
                        get_name(input_from_user), headers="keys", tablefmt="pretty"
                    )
                )

            elif input_from_user.lower().find("exit") != -1:
                logger.log("Bye bye!")
                break

            else:
                logger.log(
                    f"Sorry your enter wrong command '{input_from_user}'\nPlease choose available command from the below list!\n"
                )
                logger.log(
                    tabulate(
                        [
                            (i, desc)
                            for i, desc in enumerate(all_commands().split("\n"))
                        ],
                        headers=["Command", "Description"],
                        tablefmt="pretty",
                    )
                )

        except Exception as e:
            logger.log(f"An error occurred: {e}", level=40)


if __name__ == "__main__":
    main()
