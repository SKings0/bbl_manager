from sql import sql


class Player:
    def __init__(self, player_id):
        query = "SELECT * FROM players WHERE PlayerId = {}".format(player_id)
        # Return value is a tuple within a list
        values = sql.fetchall(query)[0]

        self._player_id = player_id
        self._last_name = values[1]
        self._first_name = values[2]
        self._team = values[3]
        self._position = values[4]
        self._nationality = values[5]

        query = "SELECT Price FROM prices WHERE PlayerId = {} ORDER BY " \
                "Iteration ASC".format(player_id)
        prices = sql.fetchall(query)
        self._price_history = [p[0] for p in prices]

        query = "SELECT * FROM stats WHERE PlayerId = {} " \
                "ORDER BY Date ASC".format(player_id)
        stats = sql.fetchall(query)

        self._stats = list()
        for stat in stats:
            s = Stat(player_id, stat)
            self._stats.append(s)

    def __eq__(self, other):
        return self._player_id == other.player_id

    def __neq__(self, other):
        return not self.__eq__(other)

    @property
    def player_id(self):
        return self._player_id

    @property
    def nationality(self):
        return self._nationality

    @property
    def position(self):
        return self._position

    @property
    def team(self):
        return self._team

    @property
    def current_price(self):
        return self._price_history[-1]

    @property
    def original_price(self):
        return self._price_history[0]

    @property
    def name(self):
        return self._last_name + ", " + self._first_name

    def is_german(self):
        return self._nationality == "GER"
    

class Stat:
    def __init__(self, player_id, values):
        self._player_id = player_id
        self._date = values[1]
        self._minutes = values[2]
        self._points = values[3]
        self._two_points_made = values[4]
        self._two_points_attempted = values[5]
        self._three_points_made = values[6]
        self._three_points_attempted = values[7]
        self._free_throws_made = values[8]
        self._free_throws_attempted = values[9]
        self._defensive_rebounds = values[10]
        self._offensive_rebounds = values[11]
        self._assists = values[12]
        self._steals = values[13]
        self._turnovers = values[14]
        self._blocks = values[15]
        self._fouls = values[16]

    @property
    def rebounds(self):
        return self._defensive_rebounds + self._offensive_rebounds

    @property
    def points_delta(self):
        made = self._two_points_made + self._three_points_made
        attempted = self._two_points_attempted + self._three_points_attempted

        return attempted - made

    @property
    def free_throws_delta(self):
        return self._free_throws_attempted - self._free_throws_made

    def positive_fantasy_points(self):
        return (self._points + self.rebounds + self._assists * 1.5 + 
                self._steals * 2.0 + self._blocks * 2.0)

    def negative_fantasy_points(self):
        return (self._turnovers * 2.0 + self.points_delta * 0.5 +
                self.free_throws_delta * 0.5 + self._fouls * 0.5)

    def fantasy_points(self):
        return (self._positive_fantasy_points()
                - self._negative_fantasy_points())
