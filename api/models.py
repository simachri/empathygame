import random
from typing import Dict, Any, List

from pydantic import BaseModel

class Role(BaseModel):
    id: int
    name: str
    descr: str

class Player(BaseModel):
    """The socket IO connction ID."""
    sid: str
    user_id: str = None
    user_name: str
    role: Role = None

    def __init__(self, sid: str, user_name: str, user_id: str = None, **data: Any):
        """Create a new player.
        :param sid: Socket connection ID of the user
        :param user_name:
        :param user_id: Will be generated if empty.
        """
        super().__init__(sid=sid, user_id=user_id, user_name=user_name, **data)
        self.sid = sid
        self.user_name = user_name
        if self.user_id is None or self.user_id == "":
            self.user_id = random.randint(100000, 999999)
        else:
            self.user_id = user_id





class Scenario(BaseModel):
    """A scenario that can be played as a game."""
    id: str
    roles: List[Role] = [Role(id=1, name='Child with Asperger syndrome', descr='Lorem ipsum'),
                         Role(id=2, name='Parents', descr='Lorem ipsum'),
                         Role(id=3, name='Teacher', descr='Lorem ipsum')]


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

    def assign_roles(self) -> List[Player]:
        """Randomly assign the roles of the scenario to the players.

        If the scenario contains less roles than players, some roles are assigned multiple times."""
        for i in range(len(self.players)):
           self.players[i].role = random.choice(self.scenario.roles)
        return self.players


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

    def emit(self) -> Dict:
        """Create the dictionary for the emitting event."""
        return {'game_id': self.game.id,
                'game_pwd': self.game.pwd,
                'user_id': self.user_id,
                'user_name': self.user_name}


class SioSession(BaseModel):
    """Session date of a socket connection."""
    game: Game = None
    player: Player = None


class SioRoleAssignment(BaseModel):
    players: List[Player] = None

    def emit(self) -> Dict:
        ret = {'players': []}
        for player in self.players:
            ret['players'].append({'user_id': player.user_id,
                                          'user_name': player.user_name,
                                          'role_id': player.role.id,
                                          'role_name': player.role.name,
                                          'role_descr': player.role.descr})
        return ret


class SioJoinGame(BaseModel):
    game_id: str
    game_pwd: str
    user_id: str = None
    user_name: str = None
    game: Game = None

    def emit(self) -> Dict:
        """Create the dictionary for the emitting event."""
        ret = {'players': []}
        for player in self.game.players:
            ret['players'].append({'user_id': player.user_id, 'user_name': player.user_name})
        return ret


class SioPlayersChanged(BaseModel):
    game: Game

    def emit(self) -> Dict:
        """Create the dictionary for the emitting event."""
        ret = {'players': []}
        for player in self.game.players:
            ret['players'].append({'user_id': player.user_id, 'user_name': player.user_name})
        return ret
