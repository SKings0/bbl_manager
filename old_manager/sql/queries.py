import pandas
import sqlite3
import csv

from sql import sql


def get_connection():
    return sqlite3.connect(sql.DATABASE)


def all_fantasy_points_by_game():
    sql = "SELECT DISTINCT p.PlayerId, p.LastName, p.FirstName, p.Team, " \
            "s.Date, s.FantasyPoints FROM players AS p JOIN stats AS s " \
            "ON p.PlayerId = s.PlayerId " \
            "WHERE s.Date >= '2018-12-01' " \
            "ORDER BY LOWER(p.LastName) ASC"
            # "ORDER BY s.Date ASC, LOWER(p.LastName) ASC"

    print_query(sql)


def fantasy_points_at_date():
    sql = "SELECT DISTINCT p.PlayerId, p.LastName, p.FirstName, p.Team, " \
            "s.Date, s.FantasyPoints FROM players AS p JOIN stats AS s " \
            "ON p.PlayerId = s.PlayerId " \
            "WHERE s.Date = '2019-09-25' " \
            "ORDER BY s.FantasyPoints DESC"
            # "ORDER BY p.LastName ASC, s.Date ASC"
            # "ORDER BY s.Date ASC, s.FantasyPoints DESC"

    print_query(sql)


def fantasy_points_by_player():
    sql = "SELECT p.LastName, p.FirstName, p.Team, SUM(s.FantasyPoints) AS " \
            "Total, ROUND(AVG(s.FantasyPoints),1) AS Avg FROM players AS p JOIN " \
            "stats AS s ON p.PlayerId = s.PlayerId " \
            "GROUP BY s.PlayerId ORDER BY LOWER(p.LastName) ASC " \

    print_query(sql)
    # write_to_csv(sql)


def fantasy_points_by_team():
    sql = "SELECT p.Team, SUM(s.FantasyPoints) AS Total " \
            "FROM stats AS s JOIN players AS p ON s.PlayerId = p.PlayerId " \
            "GROUP BY p.Team ORDER BY Total DESC"

    print_query(sql)


def all_players():
    sql = "SELECT p.PlayerId, p.LastName, p.FirstName, p.Nationality, " \
            "b.Position FROM players AS p JOIN bblapp AS b ON " \
            "p.PlayerId = b.PlayerId ORDER BY LOWER(p.LastName)"

    print_query(sql)


def all_ids():
    sql = "SELECT PlayerId, LastName, FirstName FROM players " \
            "ORDER BY PlayerId"

    print_query(sql)


def games_played_by_player():
    sql = "SELECT p.PlayerId, p.LastName, p.FirstName, p.Team, " \
            "COUNT(s.PlayerId) AS Games, ROUND(AVG(s.FantasyPoints),2) AS Points " \
            "FROM stats AS s JOIN players AS p ON s.PlayerId = p.PlayerId " \
            "GROUP BY s.PlayerId HAVING Games <= 4 " \
            "ORDER BY Points DESC"

    print_query(sql)


def all_games():
    sql = "SELECT * FROM games"

    print_query(sql)


def all_stats():
    sql = "SELECT * FROM stats"

    print_query(sql)

def prices_by_player():
    sql = "SELECT p.LastName, p.FirstName, p.Team, pr.Price, pr.Iteration " \
            "FROM players AS p JOIN prices AS pr " \
            "ON p.PlayerId = pr.PlayerId " \
            "ORDER BY p.LastName ASC"
            # "ORDER BY pr.Price DESC"
            # "WHERE p.Team = 'GIESSEN 46ers' " \
            # "WHERE pr.Iteration = 1 " \

    print_query(sql)


def test_query():
    sql = "SELECT p.Team, MAX(s.FantasyPoints) AS Max " \
            "FROM stats AS s JOIN players AS p " \
            "ON s.PlayerId = p.PlayerId " \
            "GROUP BY Team ORDER BY Max DESC"

    sql = "SELECT PlayerId, COUNT(PlayerId) AS Games " \
            "FROM stats GROUP BY PlayerId"

    sql = "SELECT p.PlayerId, p.LastName, p.FirstName, pr.Price " \
            "FROM prices AS pr JOIN players AS p " \
            "ON pr.PlayerId = p.PlayerId " \
            "ORDER BY pr.Price DESC"

    sql = "SELECT p.LastName, p.FirstName, p.Team, s.Date, s.FantasyPoints " \
            "FROM stats AS s JOIN players AS p ON s.PlayerId = p.PlayerId " \
            "ORDER BY s.Date, s.FantasyPoints DESC"

    sql = "SELECT p.Team, COUNT(s.Date) AS Players, s.Date " \
            "FROM stats AS s JOIN players AS p ON s.PlayerId = p.PlayerId " \
            "GROUP BY p.Team ORDER BY s.Date"

    sql = "SELECT PlayerId, LastName, Href FROM players " \
            "WHERE LastName = 'Schwethelm'"

    sql = "SELECT p.LastName, p.FirstName, p.Team, s.Date, s.FantasyPoints " \
            "FROM stats AS s JOIN players AS p ON s.PlayerId = p.PlayerId " \
            "WHERE p.Team = 'Brose Bamberg' " \
            "ORDER BY p.LastName, s.Date"

    sql = "SELECT s.Date, p.LastName, p.FirstName, p.Team, s.FantasyPoints " \
            "FROM stats AS s JOIN players AS p ON s.PlayerId = p.PlayerId " \
            "WHERE s.PlayerId NOT IN (" \
            "SELECT PlayerId FROM stats " \
            "WHERE Date = '2018-10-19' OR Date = '2018-10-12' OR " \
            "Date = '2018-10-15')"

    sql = "SELECT s.Date, p.LastName, p.FirstName, p.Team, s.FantasyPoints " \
            "FROM stats AS s JOIN players AS p " \
            "ON p.PlayerId = s.PlayerId " \
            "WHERE s.PlayerId NOT IN (" \
            "SELECT PlayerId FROM stats " \
            "WHERE Date = '2018-10-19' OR Date = '2018-10-15' " \
            "OR Date = '2018-10-12') " \
            "ORDER BY s.Date, s.FantasyPoints DESC"

    # print_query(sql)
    write_to_csv(sql)


def print_query(sql):
    conn = get_connection()
    c = conn.cursor()
    pandas.set_option("display.max_rows", None)    
    pandas.set_option("display.max_colwidth", -1)

    print(pandas.read_sql_query(sql, conn))


def write_to_csv(sql):
    conn = get_connection()
    c = conn.cursor()
    
    data = c.execute(sql)
    with open('output.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    

if __name__ == "__main__":
    # fantasy_points_by_player()
    fantasy_points_at_date()
    # games_played_by_player()
    # prices_by_player()
    # all_ids()
    # all_players()
    # all_fantasy_points_by_game()

    # test_query()

    # all_games()
