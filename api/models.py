import random
from typing import Dict, Any, List

from pydantic import BaseModel


class Persona(BaseModel):
    id: int
    name: str
    descr: str


class Player(BaseModel):
    """The socket IO connction ID."""
    sid: str
    user_id: str = None
    user_name: str
    role: Persona = None

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
            self.user_id = str(random.randint(100000, 999999))
        else:
            self.user_id = user_id


class PersonaComposition(BaseModel):
    """A composition of personas defining which personas are mandatory and which ones are optional."""
    mandatory: List[Persona] = []
    """List of mandatory personas"""
    optional: List[Persona] = []
    """List of optional personas"""

    def all(self) -> List[Persona]:
        """Returns the union of all mandatory and optional personas."""
        return self.mandatory + self.optional

    def dict(self, *, include=None,
             exclude=None, by_alias=False,
             skip_defaults: bool = None, exclude_unset: bool = False, exclude_defaults: bool = False,
             exclude_none: bool = False) -> list:
        original = super().dict(include=include, exclude=exclude, by_alias=by_alias, skip_defaults=skip_defaults,
                                exclude_unset=exclude_unset, exclude_defaults=exclude_defaults,
                                exclude_none=exclude_none)
        result = []
        for _ in original['mandatory']:
            _['mandatory'] = True
            result.append(_)
        for _ in original['optional']:
            _['mandatory'] = False
            result.append(_)
        return result


class DecisionOption(BaseModel):
    """Decision options of a scenario."""
    id: str
    titel: str = ''
    descr: str = ''


class Scenario(BaseModel):
    """A scenario that can be played as a game."""
    id: str
    titel: str = ''
    descr: str = ''
    background_info: str = ''
    decision_options: List[DecisionOption] = []
    personas: PersonaComposition = PersonaComposition(
            mandatory=[Persona(id=1, name='Martin, child with Asperger syndrome',
                               descr='Martin is 10 years old with level 2 AS.'),
                       Persona(id=2, name='Martin\'s parents',
                               descr='- The family has modest income, only the father is employed\n' +
                                     '- Financial problems are associated with Martin\'s medical and ' +
                                     'therapy expensed.'),
                       Persona(id=3, name='Helen - teacher',
                               descr='- She is perceived as patient, persistent and grateful.\n' +
                                     '- She is a good communicator, creative and inventing method to ' +
                                     'help a child master the skills required by the curriculum ' +
                                     'plan.')])


class MarkdownScenarioLoader:
    """Loads the data for a scenario from local markdown files."""

    @staticmethod
    def load(scenario_id: str) -> Scenario:
        pass


class Game(BaseModel):
    """A game"""
    scenario: Scenario
    host: Player
    id: str
    pwd: str
    players: Dict[str, Player] = {}
    """The players of the game. The map has format User ID -> Player object instance."""
    roles_assigned: bool = False

    def join(self, player: Player, pwd: str) -> bool:
        """Returns True if the join was successful, otherwise false."""
        if pwd != self.pwd:
            return False
        if player.user_id not in self.players:
            self.players[player.user_id] = player
        return True

    def assign_roles(self) -> Dict[str, Player]:
        """Randomly assign the roles of the scenario to the players.

        If the scenario contains less roles than players, some roles are assigned multiple times."""
        for key in self.players:
            self.players.get(key, {}).role = random.choice(self.scenario.personas.all())
        self.roles_assigned = True
        return self.players

    def is_player(self, sid: str) -> (bool, Player):
        """Checks if the player for the provided SocketIO connection ID has already joined the game.
        :param sid: SocketIO connection ID of the player.
        :return: True if the player for the given SocketIO connection ID has joined the game, false otherwise.
        If 'True': Also returns the player object instance, otherwise None.
        """
        for p in self.players.values():
            if p.sid == sid:
                return True, p
        return False, None


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

    @staticmethod
    def generate_id() -> int:
        """Generates a random 5 digit game ID."""
        return random.randint(10000, 99999)

    @staticmethod
    def generate_pwd() -> int:
        """Generates a random 5 digit game password."""
        return random.randint(10000, 99999)

    # Disable the inspection. We want the instance method for unit testing.
    # noinspection PyMethodMayBeStatic
    def create(self, scenario: Scenario, host: Player) -> Game:
        """Create a new game instance with a random game ID and a random game password."""
        return Game(scenario=scenario, host=host, id=GameFactory.generate_id(), pwd=GameFactory.generate_pwd(),
                    players={host.user_id: host})


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
    players: Dict[str, Player] = {}

    def emit(self) -> Dict:
        ret = {'players': []}
        for key in self.players:
            ret['players'].append({'user_id': self.players[key].user_id,
                                   'user_name': self.players[key].user_name,
                                   'role_id': self.players[key].role.id,
                                   'role_name': self.players[key].role.name,
                                   'role_descr': self.players[key].role.descr})
        return ret


class SioJoinGame(BaseModel):
    game_id: str
    game_pwd: str
    user_id: str = None
    user_name: str = None
    game: Game = None

    def emit(self) -> Dict:
        """Create the dictionary for the emitting event."""
        ret = {'players': [],
               'game_id': self.game.id,
               'game_pwd': self.game.pwd,
               'user_id': self.user_id,
               'user_name': self.user_name}
        for key in self.game.players:
            player: Player = self.game.players[key]
            data = {'user_id': player.user_id, 'user_name': player.user_name}
            if self.game.roles_assigned:
                data['role_id'] = player.role.id
                data['role_name'] = player.role.name
                data['role_descr'] = player.role.descr
            ret['players'].append(data)
        return ret


class SioPlayersChanged(BaseModel):
    game: Game

    def emit(self) -> Dict:
        """Create the dictionary for the emitting event."""
        ret = {'players': []}
        for key in self.game.players:
            ret['players'].append(
                    {'user_id': self.game.players[key].user_id, 'user_name': self.game.players[key].user_name})
        return ret
