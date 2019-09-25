import json
import requests

from bs4 import BeautifulSoup
from datetime import datetime

STATS_TABLE = "stats"
INDENT = "    "
COOKIES_FILE = "file/cookies.json"
FROM_DATE_FORMAT = "%d.%m.%y"
TO_DATE_FORMAT = "%Y-%m-%d"
ALIASES = "file/aliases.json"


def log_progress(index, total, data, indent=False):
    width = len(str(total))
    formatter = "[%{}d/%{}d] %s".format(width, width)

    if indent:
        formatter = INDENT + formatter

    print(formatter % (index, total, data))


def get_soup(url, is_json=False, session=None):
    try:
        if session is None:
            response = requests.get(url)
        else:
            response = session.get(url)
    except Exception:
        print("Couldn't reach {}".format(url))
        return None

    if is_json:
        # Responses may packed in json format
        data = json.loads(response.text)["html"]
    else:
        data = response.text

    return BeautifulSoup(data, "html.parser")


def get_id_from_url(url):
    """Extract the id from the easycredit player url."""
    pass


def get_last_update():
    with open(COOKIES_FILE, "r") as f:
        json_data = json.loads(f.read())

    return string_to_datetime(json_data["last_update"])


def string_to_datetime(date):
    return datetime.strptime(date, FROM_DATE_FORMAT)


def find_alias(name):
    with open(ALIASES) as f:
        json_data = json.loads(f.read())

    try:
        return json_data[name]
    except KeyError:
        return None
