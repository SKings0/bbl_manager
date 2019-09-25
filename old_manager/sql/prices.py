from sql import basketball, sql
from util import utils


COLUMNS = [
        ("PlayerId", "INT"),
        ("Iteration", "INT"),
        ("Price", "REAL")
    ]
TABLE = "prices"
GAMES_FOR_PRICE_UPDATE = 4


def populate(reset=False):
    if reset:
        sql.reset_table(TABLE, COLUMNS)

    to_update = get_outdated_players()
    prices = dict(basketball.get_current_prices())

    index = 1
    total = len(to_update)
    for player_id, iteration in to_update:
        try:
            price = prices[player_id]
        except KeyError:
            error = "ID '{}' not found in bbl app list".format(player_id)
            utils.log_progress(index, total, data=error)
            index += 1
            continue

        sql.insert(TABLE, (player_id, iteration, price))

        utils.log_progress(index, total, data=player_id)
        index += 1


def get_current_iterations():
    query = "SELECT PlayerId, COUNT(PlayerId) AS Games " \
            "FROM stats GROUP BY PlayerId"
    games = sql.fetchall(query)

    iterations = [(x, y // GAMES_FOR_PRICE_UPDATE) for (x, y) in games]

    return iterations 


# TODO Drop latest iteration to be insert read value from website
# since it can happen that it is already 4th game but price isn't updated
def get_outdated_players():
    # Get the latest iteration currently in the table for each player
    query = "SELECT PlayerId, MAX(Iteration) AS Last FROM prices " \
            "GROUP BY PlayerId ORDER BY PlayerId ASC"
    db_iterations = dict(sql.fetchall(query))
    current_iterations = get_current_iterations()

    # For each player in the given list check if the iteration is higher than
    # the others currently in the prices table
    to_update = list()
    for player_id, iteration in current_iterations:
        try:
            latest = db_iterations[player_id]
        except KeyError:
            # If KeyError then the player is not in the database
            # so set a dummy value to ensure he is added
            latest = -1

        if latest < iteration:
            # If so then a new iteration will be inserted into the table
            to_update.append((player_id, iteration))

    return to_update


if __name__ == "__main__":
    reset = False
    populate(reset)
