import os
import time
import unittest
from multiprocessing import Process
from typing import List

import socketio
# Set the port as environment variable as it is pulled when starting the uvicorn server.
# This has to be done before the import.
import uvicorn
from socketio import Client

from events import NEW_GAME, GAME_JOINED, JOIN_GAME
from models import SioNewGame, Game, Player, Scenario

os.environ['PORT'] = '8080'
from api.main import SOCKETIO_PATH

server_proc: Process


# Starting and stopping the uvicorn server in a separate process.
# This coding is taken from https://stackoverflow.com/a/61626742.
def launch_uvicorn():
    """
    Start the uvicorn server.
    """
    uvicorn.run("main:composed_app", host="0.0.0.0", port=8080)
    # config = uvicorn.Config("main:composed_app", host='0.0.0.0', port=8080)
    # config.setup_event_loop()
    # server = uvicorn.Server(config=config)
    # server.run()


def start_server():
    """
    Start the uvicorn server in a new process.
    """
    # create process instance and set the target to run function.
    # use daemon mode to stop the process whenever the program stopped.
    global server_proc
    server_proc = Process(target=launch_uvicorn, args=(), daemon=True)
    server_proc.start()
    # Wait until the server has started. I know this is dirty.
    time.sleep(2)


def stop_server():
    """
    Stop the uvicorn server process.
    """
    # check if the process is not None
    global server_proc
    if server_proc:
        # join (stop) the process with a timeout setten to 0.25 seconds.
        # using timeout (the optional arg) is too important in order to
        # enforce the server to stop.
        server_proc.join(0.25)


class TestSocket(unittest.TestCase):

    def __init__(self, method: str = ...) -> None:
        super().__init__(method)
        self.new_game_model: SioNewGame = SioNewGame(user_name='Player Unittest', game_scenario='42')

    @classmethod
    def setUpClass(cls) -> None:
        """Class set up. Called once before any test is executed."""
        start_server()

    @classmethod
    def tearDownClass(cls) -> None:
        """Class tear down. Called once after all tests have been executed."""
        stop_server()

    def setUp(self) -> None:
        """Test setup; is called before every unit test"""
        # Create socketio clients and connect to the server.
        self.client1 = socketio.Client()
        self.client1.connect('http://localhost:8080', transports='websocket', socketio_path=SOCKETIO_PATH)
        self.client2 = socketio.Client()
        self.client2.connect('http://localhost:8080', transports='websocket', socketio_path=SOCKETIO_PATH)
        # Wait a second until the connection has been established.
        time.sleep(1)

    def tearDown(self) -> None:
        """Test setup; is called before every unit test"""
        self.client1.disconnect()
        self.new_game_model.game = None

    def test_on_game_joined_assigned_roles_sent(self):
        """Test that if the client receives the event that he/she has successfully joined a game, the payload
           of that event contains the assigned roles for each players.
           Tests issue #3."""
        game: Game = self.create_game()
        self.join_game(self.client2, 'Player2', game.id, game.pwd)

    def create_game(self) -> Game:
        """Create a new game for scenario 42.
        :return: Game
        """

        # Set the handler when the server responds after the game has been created.
        def on_new_game(data):
            # Store the game ID and game password.
            self.new_game_model.game = Game(scenario=Scenario(id=self.new_game_model.game_scenario),
                                            host=Player(sid=self.client1.sid,
                                                        user_id=data['user_id'],
                                                        user_name=data['user_name'],
                                                        ),
                                            id=data['game_id'],
                                            pwd=data['game_pwd'])

        self.client1.on(NEW_GAME, on_new_game)
        # Emit the event for creating a new game.
        self.client1.emit(NEW_GAME, self.new_game_model.dict())
        # Wait until on_new_game has been called.
        while not self.new_game_model.game:
            time.sleep(1)

        return self.new_game_model.game

    @staticmethod
    def join_game(client: Client, user_name, game_id, game_pwd) -> List[Player]:
        """Join an existing game.
        :param client: SocketIO client
        :param user_name: Name of the user to join the game
        :param game_id: Game ID
        :param game_pwd: Game password
        :return: SioJoinGame.Game.players
        """
        players: List[Player] = []

        # Set the handler when the server responds after the player has joined the game.
        def on_game_joined(data):
            nonlocal players
            players = data['players']

        client.on(GAME_JOINED, on_game_joined)
        client.emit(JOIN_GAME, {'user_name': user_name, 'game_id': game_id, 'game_pwd': game_pwd})
        # Wait until on_new_joined has been called.
        while not players:
            time.sleep(1)
        return players
