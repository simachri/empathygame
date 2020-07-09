import random

from pydantic import BaseModel


class Player:

    def __init__(self, guid: str):
        """Create a new player."""
        self.id = guid


class Scenario:
    """A scenario that can be played as a game."""

    def __init__(self, guid: str):
        """Create a new scenario."""
        self.id = guid


class Game:
    """A game"""

    def __init__(self, scenario: Scenario, host: Player, game_id: str, game_pwd: str):
        """Create a new game instance."""
        self.scenario = scenario
        self.host = host
        self.id = game_id
        self.pwd = game_pwd


class GameFactory:
    """Create a new game instance with a random game ID and a random game password."""

    # noinspection PyMethodMayBeStatic
    def generate_id(self) -> str:
        """Generates a random 5 digit game ID."""
        return random.randint(10000, 99999)

    # noinspection PyMethodMayBeStatic
    def generate_pwd(self) -> str:
        """Generates a random 5 digit game password."""
        return random.randint(10000, 99999)

    def create(self, scenario: Scenario, host: Player) -> Game:
        """Create a new game instance with a random game ID and a random game password."""
        return Game(scenario, host, self.generate_pwd(), self.generate_pwd())


class SioNewGame(BaseModel):
    game_scenario: str
    user_id: str = None
    user_name: str = None

    def __getitem__(self, item):
        """Is required to work with python-socketio."""
        return self.__root__[item]
