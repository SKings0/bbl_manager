from util.player import Player


class ManagerTeam:
    MAX_PLAYERS = 12
    GERMAN_QUOTA = 6
    MIN_GUARDS = 4
    MIN_CENTERS = 2
    MIN_FORWARDS = 4
    FLEX_PLAYERS = 2
    MAX_PRICE = 6.0
    MIN_PLAYER_PRICE = 0.10

    def __init__(self):
        self._players = []
        pass

    def add_player_by_id(self, player_id):
        if len(self._players) >= self.MAX_PLAYERS:
            return False

        player = Player(player_id)

        if player in self._players:
            return False

        self._players.append(player)
        return True

    def add_player_by_name(self, last_name, first_name):
        pass

    def add_player(self, player):
        pass

    def is_valid(self):
        if not self.worth_validity():
            return False

        if not self.position_validity():
            return False

        if not self.quota_validity():
            return False

        return True

    def german_count(self):
        count = 0
        for player in self._players:
            if player.nationality == "GER":
                count += 1

        return count

    def partial_team_validity(self):
        if not self.worth_validity():
            return False

        return True

    def worth_validity(self):
        worth = self.original_worth()
        worth += self.MIN_PLAYER_PRICE * (self.MAX_PLAYERS
                - len(self._players))

        if worth > self.MAX_PRICE:
            return False
        
        return True

    def quota_validity(self):
        count = 0
        for player in self._players:
            if player.nationality != "GER":
                count += 1

        return count <= (self.MAX_PLAYERS - self.GERMAN_QUOTA)

    def positions_count(self):
        centers = 0
        forwards = 0
        guards = 0
        for player in self._players:
            if player.position == "C":
                centers += 1
            elif player.position == "F":
                forwards += 1
            elif player.position == "G":
                guards += 1

        return (centers, forwards, guards)

    def position_validity(self):
        centers, forwards, guards = self.positions_count()

        center_validity = centers <= (self.MIN_CENTERS + self.FLEX_PLAYERS)
        guard_validity = guards <= (self.MIN_GUARDS + self.FLEX_PLAYERS)
        forward_validity = forwards <= (self.MIN_FORWARDS + self.FLEX_PLAYERS)

        return center_validity and guard_validity and forward_validity

    def original_worth(self):
        worth = 0.0
        for player in self._players:
            worth += player.original_price

        return worth


class InvalidTeamError(Exception):
    def __init__(self, message):
        super().__init__(message)
