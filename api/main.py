import logging
import os

import socketio
import uvicorn
from fastapi import FastAPI

from controller import Game, Scenario, Player
from events import CONN_SUCCESS, NEW_GAME

rest_api = FastAPI()
# Socket.IO will be mounted as a sub application to the FastAPI main app.
# See the info here: https://github.com/tiangolo/fastapi/issues/129
sio = socketio.AsyncServer(async_mode='asgi')
# Note: It is mandatory to perform all calls to the websocket API with a trailing slash /.
# Otherwise, an error is returned, see ASGIApp.__call__.
# We use a constant that we can reference for our unit tests.
SOCKETIO_PATH = '/ws'
composed_app = socketio.ASGIApp(sio, other_asgi_app=rest_api, socketio_path=SOCKETIO_PATH)

logging.basicConfig(
        # TODO: Set to a less severe level for a productive system.
        level=logging.DEBUG,
        format="%(asctime)s,%(msecs)d %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
        )


@rest_api.get("/hello")
async def root():
    return {"message": "Hello World"}


# See the example coding from https://github.com/miguelgrinberg/python-socketio/blob/master/examples/server/asgi/app.py
background_task_started = False


async def background_task():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        await sio.sleep(10)
        count += 1
        await sio.emit('server_response', {'data': 'Server generated event'})


# noinspection PyUnusedLocal
@sio.on('connect')
async def connect(sid, environ):
    """Handle a socket connection request.

    A background task for handling incoming requests will be started at the very first invocation.

    A new user session will be created.
    """
    logging.debug(f"New connection request with SID {sid}.")
    global background_task_started
    if not background_task_started:
        logging.debug(f"Background task not yet started. Launching...")
        sio.start_background_task(background_task)
        background_task_started = True
        logging.debug(f"Background task started.")
    logging.debug(f"Creating new session.")
    await sio.save_session(sid, {})
    logging.debug(f"Emitting event {CONN_SUCCESS} to {sid}.")
    await sio.emit(CONN_SUCCESS, room=sid)


games = []
GAME_SCENARIO = 'game_scenario'


@sio.on('new_game')
async def connect(sid, data):
    """Handle the incoming request for creating a new game.

    A new game instance is created for the provided scenario.
    The game ID and the join password is returned as payload with event 'NEW_GAME'.
    """
    logging.debug(f"Incoming request for creating a new game from {sid} for scenario {data[GAME_SCENARIO]}.")
    game = Game(Scenario(data[GAME_SCENARIO]), Player(sid))
    games.append(game)
    sess = await sio.get_session(sid)
    sess['game_id'] = game.id
    logging.debug(f"New game created with ID {game.id} and password {game.pwd}.")
    await sio.save_session(sid, sess)
    logging.debug(f"Emitting event {NEW_GAME} to {sid}.")
    await sio.emit(NEW_GAME, data={'game_id': game.id, 'game_pwd': game.pwd})


if __name__ == "__main__":
    port = os.environ['PORT']
    # TODO: Remove 'reload' before deploying for production.
    uvicorn.run(composed_app, host="0.0.0.0", port=int(port))
