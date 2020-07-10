import random
from typing import Dict, Any, List

from pydantic import BaseModel


class Player(BaseModel):
    conn_id: str
    user_id: str = None
    user_name: str

    def __init__(self, conn_id: str, user_name: str, user_id: str = None, **data: Any):
        """Create a new player.
        :param guid: Socket connection ID of the user
        :param user_name:
        :param user_id: Will be generated if empty.
        """
        super().__init__(conn_id=conn_id, user_id=user_id, user_name=user_name, **data)
        self.conn_id = conn_id
        self.user_name = user_name
        if user_id is None:
            self.user_id = random.randint(100000, 999999)
        else:
            self.user_id = user_id


class Scenario(BaseModel):
    """A scenario that can be played as a game."""
    id: str


class Game(BaseModel):
    """A game"""
    scenario: Scenario
    host: Player
    id: str
    pwd: str
    players: List[Player] = []

    def join(self, player: Player, pwd: str) -> bool:
        """Returns True if the join was successful, otherwise false."""
        if pwd != self.pwd:
            return False
        self.players.append(player)
        return True


class GameController:
    """Controls all running games and provides methods for searching and querying games."""
    running_games: Dict[str, Game] = {}

    def add(self, game: Game):
        """Add a game to the controller."""
        self.running_games[game.id] = game

    def get(self, game_id: str) -> Game:
        """Returns None if no game is found for the provided game_id."""
        return self.running_games.get(game_id)


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
        return Game(scenario=scenario, host=host, id=self.generate_id(), pwd=self.generate_pwd(), players=[host])


class SioNewGame(BaseModel):
    game_scenario: str
    user_id: str = None
    user_name: str = None
    game: Game = None

    def __getitem__(self, item):
        """Is required to work with python-socketio."""
        return self.__root__[item]

    def get(self, item):
        """Provide the usual 'get' method of a dictionary."""
        self.dict().get(item)

    def emit(self) -> Dict:
        """Create the dictionary for the emitting event."""
        return {'game_id': self.game.id,
                'game_pwd': self.game.pwd,
                'user_id': self.user_id,
                'user_name': self.user_name}


class SioJoinGame(BaseModel):
    game_id: str
    game_pwd: str
    user_id: str = None
    user_name: str = None
    game: Game = None

    def __getitem__(self, item):
        """Is required to work with python-socketio."""
        return self.__root__[item]

    def get(self, item):
        """Provide the usual 'get' method of a dictionary."""
        self.dict().get(item)

    def emit(self) -> Dict:
        """Create the dictionary for the emitting event."""
        ret = {'players': []}
        for player in self.game.players:
            ret['players'].append({'user_id': player.user_id, 'user_name': player.user_name})
        return ret
