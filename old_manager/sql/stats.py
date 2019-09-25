import json
import os
import pandas
import re
import requests
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime

from util import utils
from sql import sql


COLUMNS = [
        ("PlayerId", "INT", -1),
        ("Date", "TEXT", 1),
        ("Mins", "TEXT", 3),
        ("Points", "INT", 4),
        ("TwoPointsMade", "INT", 5),
        ("TwoPointsAttempted", "INT", 6),
        ("ThreePointsMade", "INT", 8),
        ("ThreePointsAttempted", "INT", 9),
        ("FreeThrowsMade", "INT", 14),
        ("FreeThrowsAttempted", "INT", 15),
        ("DefensiveRebounds", "INT", 17),
        ("OffensiveRebounds", "INT", 18),
        ("Assists", "INT", 20),
        ("Steals", "INT", 21),
        ("Turnovers", "INT", 22),
        ("Blocks", "INT", 23),
        ("PersonalFouls", "INT", 24),
        ("DrawnFouls", "INT", 25),
        ("FantasyPoints", "REAL", -1)
    ]
COLUMN_MAPPING_INDEX = 2
TABLE = "stats"
MAIN_ROUND = "Hauptrunde"


def populate(reset=False):
    if reset:
        sql.reset_table(TABLE, COLUMNS)
    else:
        pass

    columns = ["PlayerId", "LastName", "FirstName", "Href"]
    players = sql.get_values("players", columns)

    total = len(players)
    while players:
        player_id, last_name, first_name, href = players.pop()

        name = last_name.upper() + " " + first_name
        utils.log_progress(total - len(players), total, name)

        if not insert_player_games(player_id, href, reset):
            players.append((player_id, last_name, first_name, href))


def insert_player_games(player_id, href, reset=False):
    soup = utils.get_soup(href)

    if soup is None:
        return False

    tables = soup.find_all("table", {"class": "sub"})
    table_types = soup.find_all("a", {"class": "icon more"})

    # Skip tables that don't belong to the 'Hauptrunde' (e.g. pokal, playoffs)
    # since they aren't considered for fantasy points
    tables = [t for (t, tt) in zip(tables, table_types) if 
            tt.text == MAIN_ROUND]

    if len(tables) > 1:
        # TODO update team
        pass

    games = list()
    for table in tables:
        body = table.find("tbody")
        games.extend(body.find_all("tr"))

    # Extract hard coded columns to read values from game row
    sql_indices = [col[COLUMN_MAPPING_INDEX] for col in COLUMNS 
            if col[COLUMN_MAPPING_INDEX] > 0]
    last_update = utils.get_last_update()

    index = 1
    total = len(games)
    for game in games:
        values = [td.text for td in game.find_all("td")]
        # Filter out for values relevant to the table
        sql_values = [values[i] for i in sql_indices]

        game_date = utils.string_to_datetime(sql_values[0])
        if game_date <= last_update and not reset:
            continue

        # Modify date to one that sort correctly in sql
        sql_values[0] = game_date.strftime(utils.TO_DATE_FORMAT)
        # Insert missing values to tuple
        sql_values.insert(0, player_id)
        fantasy_points = calculate_fantasy_points(sql_values)
        sql_values.append(fantasy_points)

        sql.insert(TABLE, sql_values)

        data = sql_values[1]
        utils.log_progress(index, total, data=data, indent=True)
        index += 1

    return True


def calculate_fantasy_points(stats):
    positive_points = calculate_positive_fantasy_points(stats)
    negative_points = calculate_negative_fantasy_points(stats)

    return positive_points - negative_points


def calculate_positive_fantasy_points(stats):
    points = float(stats[3])
    rebounds = float(stats[10]) + float(stats[11])
    assists = float(stats[12])
    steals = float(stats[13])
    blocks = float(stats[15])

    positive_points = (points + rebounds + assists * 1.5 + steals * 2.0
            + blocks * 2.0)

    return positive_points


def calculate_negative_fantasy_points(stats):
    turnovers = float(stats[14])
    field_goals_attempted = float(stats[5]) + float(stats[7])
    field_goals = float(stats[4]) + float(stats[6])
    free_throws_attempted = float(stats[9])
    free_throws = float(stats[8])
    fouls = float(stats[16])

    negative_points = (turnovers * 2.0 + (field_goals_attempted - field_goals)
            * 0.5 + (free_throws_attempted - free_throws) * 0.5 + fouls * 0.5)

    return negative_points


if __name__ == "__main__":
    populate(reset=True)
    print("---------------------------")
    print("Stats table update complete")
