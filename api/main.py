import os

import uvicorn
import socketio
from fastapi import FastAPI

rest_api = FastAPI()
# Socket.IO will be mounted as a sub application to the FastAPI main app.
# See the info here: https://github.com/tiangolo/fastapi/issues/129
sio = socketio.AsyncServer(async_mode='asgi')
# Note: It is mandatory to perform all calls to the websocket API with a trailing slash /.
# Otherwise, an error is returned, see ASGIApp.__call__.
# We use a constant that we can reference for our unit tests.
SOCKETIO_PATH = '/ws'
composed_app = socketio.ASGIApp(sio, other_asgi_app=rest_api, socketio_path=SOCKETIO_PATH)


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
async def test_connect(sid, environ):
    print('connect', sid)
    global background_task_started
    if not background_task_started:
        sio.start_background_task(background_task)
        background_task_started = True
    await sio.emit('my_response', {'data': 'Connected', 'count': 0}, room=sid)


port = os.environ['PORT']
if __name__ == "__main__":
    uvicorn.run(composed_app, host="0.0.0.0", port=int(port))
