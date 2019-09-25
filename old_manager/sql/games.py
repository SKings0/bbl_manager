import re
from datetime import datetime

from sql import sql
from util import utils


COLUMNS = [
        ("MatchDay", "INT"),
        ("Date", "TEXT"),
        ("Time", "TEXT"),
        ("Home", "TEXT"),
        ("Away", "TEXT")
    ]
TABLE = "games"
HOST = "https://www.easycredit-bbl.de"
REQUEST = HOST + "/ajax.php?contelPageId=15408"
FILENAME = "&filename=daten/html/schedules/{}/y{}_m_c1-schedule.html"

TBD_INDEX = 0
UPCOMING_KEY = "upcoming"
FINISHED_KEY = "finished"
GAMEDAY_TRIM = ". Spieltag"


def get_soup(season="2018"):
    filename = FILENAME.format(season, season)
    url = REQUEST + filename

    return utils.get_soup(url, is_json=True)


def populate(reset=False):
    if reset:
        sql.reset_table(TABLE, COLUMNS)

    soup = get_soup()

    # Each table contains games played in single date
    tables = soup.find_all("table")

    index = 1
    total = len(tables)
    for table in tables:
        date = extract_date(table.parent.find("time").text)

        utils.log_progress(index, total, date)
        index += 1

        insert_info_from_table(table, date)


def insert_info_from_table(table, date):
    upcoming = UPCOMING_KEY in table["class"]
    body = table.find("tbody")
    games = body.find_all("tr")

    index = 1
    total = len(games)
    for game in games:
        values = get_game_info(game, date, upcoming=upcoming)
        sql.insert(TABLE, values)

        utils.log_progress(index, total, values[0], indent=True)
        index += 1


def get_game_info(game, date, upcoming):
    infos = game.find_all("td")

    time, gameday = [x.text for x in infos[0].find_all("p")]
    gameday = gameday.replace(GAMEDAY_TRIM, "")

    home, away = [x.text for x in infos[1].find_all("p")]

    return (gameday.strip(), date.strip(), time.strip(), 
            home.strip(), away.strip())



def extract_date(string):
    regex = "[0-9]+\.[0-9]+\.[0-9]+"
    date = re.search(regex, string)

    if date is None:
        return string
    else:
        date = date.group(0)

    return reformat_date(date)


def reformat_date(date):
    from_format = "%d.%m.%Y"
    to_format = utils.TO_DATE_FORMAT

    date_object = datetime.strptime(date, from_format)

    return datetime.strftime(date_object, to_format)


if __name__ == "__main__":
    populate(True)
