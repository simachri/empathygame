import logging
import os

import socketio
import uvicorn
from fastapi import FastAPI

from events import CONN_SUCCESS, \
    NEW_GAME, \
    JOIN_GAME, \
    JOIN_GAME_ERROR, \
    GAME_JOINED, \
    PLAYERS_CHANGED, \
    ASSIGN_ROLES, \
    ROLES_ASSIGNED
from models import Scenario, \
    Player, \
    SioNewGame, \
    GameFactory, \
    SioJoinGame, \
    GameController, \
    Game, \
    SioPlayersChanged, \
    SioSession, SioRoleAssignment

rest_api = FastAPI()
# Socket.IO will be mounted as a sub application to the FastAPI main app.
# See the info here: https://github.com/tiangolo/fastapi/issues/129
sio = socketio.AsyncServer(async_mode='asgi')
# Note: It is mandatory to perform all calls to the websocket API with a trailing slash /.
# Otherwise, an error is returned, see ASGIApp.__call__.
# We use a constant that we can reference for our unit tests.
SOCKETIO_PATH = '/ws'
composed_app = socketio.ASGIApp(sio, other_asgi_app=rest_api, socketio_path=SOCKETIO_PATH)

# Set up logger.
log = logging.getLogger('api')
# TODO: For productive use, adjust the level.
log.setLevel(logging.DEBUG)

# GameController manages the running games.
game_controller = GameController()


@rest_api.get("/hello")
async def root():
    return {"message": "Hello World"}


# noinspection PyUnusedLocal
@sio.on('connect')
async def connect(sid, environ):
    """Handle a socket connection request.

    A background task for handling incoming requests will be started at the very first invocation.

    A new user session will be created.
    """
    log.debug(f"New connection request with SID {sid}.")
    log.debug(f"Creating new session.")
    await sio.save_session(sid, SioSession())
    log.debug(f"Emitting event {CONN_SUCCESS} to {sid}.")
    await sio.emit(CONN_SUCCESS, room=sid)


@sio.on(NEW_GAME)
async def new_game(sid, data: SioNewGame):
    """Handle the incoming request for creating a new game.

    A new game instance is created for the provided scenario.
    The game ID and the join password is returned as payload with event 'NEW_GAME'.

    A user_name will be provided, user_id will be initial and generated within this method.
    """
    sio_data = SioNewGame.parse_obj(data)
    log.debug(f"Incoming request for creating a new game from {sio_data.user_name} ({sid})"
              f"for scenario {sio_data.game_scenario}.")
    # Create a new game instance.
    player = Player(sid, sio_data.user_name, sio_data.user_id)
    game = GameFactory().create(Scenario(id=sio_data.game_scenario), player)
    game_controller.add(game)
    # Update the user session with the new game.
    sess: SioSession = await sio.get_session(sid)
    sess.game = game
    sess.player = player
    await sio.save_session(sid, sess)
    log.debug(f"New game created with ID {game.id} and password {game.pwd}.")
    # Create a new socket IO room for the game.
    sio.enter_room(sid, game.id)
    # Emit the event that the game has been successfully created.
    sio_data.game = game
    sio_data.user_id = player.user_id
    log.debug(f"Emitting event {NEW_GAME} to {sio_data.user_name} ({sid}).")
    await sio.emit(NEW_GAME, data=sio_data.emit(), room=sid)


@sio.on(JOIN_GAME)
async def join_game(sid, data: SioJoinGame):
    """Handle the incoming request for joining a game.

    If no game for the provided ID exists or the password is wrong, an 'invalid_game_or_pwd' event will be emitted.
    """
    sio_data = SioJoinGame.parse_obj(data)
    log.debug(f"Incoming request from {sio_data.user_name} ({sid}) to join game {sio_data.game_id}.")
    # Find the game for the provided ID and try to join it.
    player = Player(sid, sio_data.user_name, sio_data.user_id)
    game = game_controller.get(sio_data.game_id)
    if game is None:
        await sio.emit(JOIN_GAME_ERROR, room=sid)
        return
    join_succeeded = game.join(player, sio_data.game_pwd)
    if not join_succeeded:
        await sio.emit(JOIN_GAME_ERROR, room=sid)
        return
    # Update the user session.
    sess: SioSession = await sio.get_session(sid)
    sess.game = game
    sess.player = player
    await sio.save_session(sid, sess)
    log.debug(f"{sid} successfully joined game {game.id}.")
    # Join the socket IO room for the game.
    sio.enter_room(sid, game.id)
    # Emit the event that the game has been successfully joined.
    sio_data.game = game
    sio_data.user_name = player.user_name
    sio_data.user_id = player.user_id
    log.debug(f"Emitting event {GAME_JOINED} to {sio_data.user_name} ({sid}).")
    await sio.emit(GAME_JOINED, data=sio_data.emit(), room=sid)
    # Notify all other players of the room.
    await notify_player_joined(player, game)


async def notify_player_joined(player: Player, game: Game):
    """Emit an event 'players_changed" when a player joins a game."""
    log.debug(f"Notifying the players of game {game.id} that a new player has joined by emitting event "
              f"'{PLAYERS_CHANGED}'.")
    # Do not send the event to the player herself/himself.
    await sio.emit(PLAYERS_CHANGED, SioPlayersChanged(game=game).emit(), room=game.id, skip_sid=player.sid)


# noinspection PyUnusedLocal
@sio.on(ASSIGN_ROLES)
async def assign_roles(sid, data):
    """Handle the incoming request for assigning the roles to each player.
    """
    sess: SioSession = await sio.get_session(sid)
    log.debug(f"Incoming request from {sess.player.user_name} ({sid}) to assign the roles to the players "
              f"of game {sess.game.id}.")
    assignments = SioRoleAssignment(players=sess.game.assign_roles())
    log.debug(f"Assigned the following roles to each player:")
    for key in assignments.players:
        log.debug(f"\t{assignments.players.get(key).user_name}: {assignments.players.get(key).role.name}")
    log.debug(f"Notifying the players of game {sess.game.id} about their role assignment by "
              f"emitting event '{ROLES_ASSIGNED}'.")
    # Notify all players about the roles.
    await sio.emit(ROLES_ASSIGNED,  assignments.emit(), room=sess.game.id)


if __name__ == "__main__":
    port = os.environ['PORT']
    # TODO: Remove 'reload' before deploying for production.
    uvicorn.run("main:composed_app", host="0.0.0.0", port=int(port), reload=True)
