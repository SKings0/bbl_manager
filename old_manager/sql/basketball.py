import json
import requests
import sqlite3
import sys
from bs4 import BeautifulSoup

from util import utils
from sql import sql


HOST = "https://basketball.de"
LOGIN_URL = HOST + "/app/auth/logon"
DIVISION_URL = "https://basketball.de/app/buli_beko/division/2144-Sebas-Co"
APP_URL = HOST + "/app/buli_beko"
PLAYER_LIST_URL = "/top_spieler?search=&page=1&letter=&sort={}&sortType={}" \
        "&country={}&limit={}"
# USERNAME = "sebastianreyes94@hotmail.com"
USERNAME = "SKings0"
PASSWORD = "QE3sI6cj"
ALIASES = "file/aliases.json"

COLUMNS = [
        ("PlayerId", "INT"),
        ("FirstName", "TEXT"),
        ("LastName", "TEXT"),
        ("Position", "TEXT")
    ]
TABLE = "bblapp"


def player_query(sort_by="salary", sort_order="DESC", country="ALL",
        limit="1000"):
    '''
    Return the url for a specific query with the given parameters. The url
    points to ONLY an html table containing player information.

        sort_by = ["lastName", "team", "country_id", "position", "salary",
                "FP", "avgFP", "lastFP"]
        sort_order = ["ASC", "DESC"]
        country = ["ALL", "DE", "US", "WORLD"]
    '''
    query = PLAYER_LIST_URL.format(sort_by, sort_order, country, limit)
    return APP_URL + query


def login_request(session):
    payload = {
            "username": USERNAME,
            "password": PASSWORD
        }
    session.post(LOGIN_URL, data=payload)
    

def get_bbl_players_soup():
    with requests.Session() as s:
        login_request(s)

        query = player_query()
        soup = utils.get_soup(query, session=s)

    return soup


def get_bbl_app_informations():
    soup = get_bbl_players_soup()

    name_index = 0
    position_index = 3
    price_index = 4

    table = soup.find("tbody")
    players = table.find_all("tr")

    infos = list()
    for player in players:
        row = player.find_all("td")

        name = row[name_index].text.strip()
        position = row[position_index].text.strip()
        price = row[price_index].text.strip()

        infos.append((name, position, price))

    infos = extend_player_ids(infos)

    return infos 


def populate(reset=False):
    if reset:
        sql.reset_table(TABLE, COLUMNS)

    players = get_bbl_app_informations()
    total = len(players)
    index = 1

    for player in players:
        player_id = player[0]
        last_name, first_name = player[1].split(", ")
        position = player[2]

        sql_values = (player_id, first_name, last_name, position)
        sql.insert(TABLE, sql_values)

        name = last_name.upper() + " " + first_name
        if player_id == "NULL":
            length = 60 - len(name)
            name += "-" * length + "NOT FOUND"
        utils.log_progress(index, total, name)
        index += 1


def extend_player_ids(infos):
    # Simulate name format from basketball.de table
    ids = sql.get_values("players", ["PlayerId, LastName, FirstName"])
    ids = dict([(ln + ", " + fn, x) for (x, ln, fn) in ids])

    ids_tuple = list()
    for info in infos:
        name = info[0]
        try: 
            player_id = ids[name]
        except KeyError:
            # Safeguard for misspellings
            alias = utils.find_alias(name)

            if alias is None:
                player_id = "NULL"
            else:
                player_id = ids[alias]
        finally:
            ids_tuple.append((player_id, *info))

    return ids_tuple


if __name__ == "__main__":
    populate(True)
