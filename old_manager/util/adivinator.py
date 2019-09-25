import sqlite3
import itertools

from . import utils
from sql import sql

team_candidates = set()
black_list = set()


def extendPossibleTeams(date, points, count, delta=0):
    control = lambda x : below_limit(points, x)

    players = getPossiblePlayers(date)

    candidates = list(itertools.product(players, repeat=1))
    candidates = list(filter(control, candidates))
    for i in range(2, count + 1):
        candidates = product(candidates, players)

        if i == count:
            control = lambda x : equals_limit(points, x)
            candidates = list(filter(control, candidates))
        else:
            candidates = list(filter(control, candidates))

    if len(candidates) == 0:
        print("No matches")
        return

    for candidate in set(candidates):
        print(candidate)

    print(len(set(candidates)))


def product(candidates, players):
    new_candidates = list()
    for candidate in [list(x) for x in candidates]:
        for player in players:
            c = candidate.copy()
            c.append(player)
            new_candidates.append(tuple(sorted(c)))

    return list(set(new_candidates))
    

def below_limit(limit, players):
    points = sum([p[1] for p in players])

    return points <= limit


def equals_limit(limit, players):
    return sum([p[1] for p in players]) == limit


def getPossiblePlayers(date):
    query = "SELECT PlayerId, FantasyPoints FROM stats " \
            "WHERE date = '{}'".format(date)

    conn = sqlite3.connect(sql.DATABASE)
    c = conn.cursor()

    c.execute(query)

    players = c.fetchall()
    players = [p for p in players if p[0] not in black_list]

    return players


def projectPriceChanges():
    query = "SELECT p.LastName, p.FirstName, p.Team, " \
            "AVG(s.FantasyPoints) AS Avg " \
            "FROM players AS p JOIN stats AS s ON p.PlayerId = s.PlayerId " \
            "GROUP BY s.PlayerId " \
            "ORDER BY LOWER(p.LastName)"

    conn = sqlite3.connect(sql.DATABASE)
    c = conn.cursor()

    c.execute(query)

    stats = c.fetchall()

    for stat in stats:
        print(stat)


if __name__ == "__main__":
    # date = "2018-10-13"
    # points = 17
    # count = 2

    # extendPossibleTeams(date, points, count, delta=0)
    projectPriceChanges()
