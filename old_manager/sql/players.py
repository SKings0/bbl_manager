import json
import os
import pandas
import re
import requests
import sqlite3
from bs4 import BeautifulSoup
from collections import defaultdict

from util import utils
from sql import sql


COLUMNS = [
        ("PlayerId", "INT"), 
        ("LastName", "TEXT"),
        ("FirstName", "TEXT"),
        ("Team", "TEXT"),
        ("Position", "TEXT"),
        ("Nationality", "TEXT"),
        ("Href", "TEXT")
    ]
# Key constant for player information
POSITION = "Position:"
NATIONALITY = "Nationalität:"
# sql and requests constants
TABLE = "players"
HOST = "https://www.easycredit-bbl.de"
REQUEST = HOST + "/ajax.php?contelPageId=15781"
FILENAME = "&filename=daten/html/player_stats_saison/y{}_c1_p_n-" \
        "playerstats{}.html"


def get_soup(season="2019", table="prospiel"):
    """Generate soup from the easycredit players table.
    
    :params table: prospiel or gesamt
    """
    filename = FILENAME.format(season, table)
    url = REQUEST + filename

    return utils.get_soup(url, is_json=True)


def populate(reset=False):
    """
    Insert the players read from the easycredit players database into the
    players table. If update is true then a check to avoid duplicates will be
    made.
    """
    if reset:
        sql.reset_table(TABLE, COLUMNS)

    hrefs = get_hrefs(missing_only=not reset)

    index = 1
    total = len(hrefs)
    for href in hrefs:
        values = extract_players_info_from_url(href)
        sql.insert(TABLE, values)

        name = " ".join([values[1].upper(), values[2]])
        utils.log_progress(index, total, data=name)
        index += 1


def get_hrefs(missing_only):
    soup = get_soup(table="gesamt")

    table = soup.find("table", {"class": "footable"})
    body = table.find("tbody")

    # Each row contains a link behind the players name
    links = body.find_all("a")
    players = [link.parent for link in links]

    # Extend partial urls found in <a>-tag and generate list
    hrefs = [HOST + p.a["href"] for p in players]

    if missing_only:
        return extract_missing(hrefs)

    return hrefs


def extract_players_info_from_url(url):
    soup = utils.get_soup(url)

    header = soup.find("div", {"class": "spielerheader"})

    player_id = get_id(url)
    # Name
    name = header.find("h1").text
    last_name = header.find("h1").find("strong").text.strip()
    first_name = name.replace(last_name, "").strip()
    team = header.find("h2").text

    # Information column to dictionary
    # Header has 3 columns, the second one contains the information
    column = header.find_all("div", {"class": "col"})[1]
    keys = [dt.text for dt in column.find_all("dt")]
    values = [dd.text for dd in column.find_all("dd")]
    # Defaultdict won't raise KeyErrors
    infos = defaultdict(lambda: "-", zip(keys, values))

    return (player_id, last_name, first_name, team, infos[POSITION],
            infos[NATIONALITY], url)


def get_id(url):
    url.replace(HOST, "")
    player_string = os.path.basename(url.rstrip("/"))
    player_id = int(re.search("[0-9]+", player_string).group(0))

    return player_id


def extract_missing(hrefs):
    existing_hrefs = sql.get_values(TABLE, ["Href"])

    is_missing = lambda h: (h,) not in existing_hrefs
    missing_hrefs = list(filter(is_missing, hrefs))

    return missing_hrefs


if __name__ == "__main__":
    populate(reset=True)

    print("-----------------------------")
    print("Players table update complete")
