class Player:

    def __init__(self, guid: str):
        """Create a new player."""
        self.id = guid

class Scenario:
    """A scenario that can be played as a game."""

    def __init__(self, guid: str):
        """Create a new scenario."""
        self.id = guid


class GameFactory():

    def generate_id(self) -> str:
       """Generates a random 5 digit game ID."""
       pass

    def generate_pwd(self) -> str:
       """Generates a random 5 digit game password."""
       pass

class Game:
    """A game"""

    def __init__(self, scenario: Scenario, host: Player):
        """Create a new game instance.

        A random game ID and a password is generated.
        """
        self.scenario = scenario
        self.host = host
        self.id = '22651'
        self.pwd = '13379'
