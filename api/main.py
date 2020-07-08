import os

import uvicorn
import socketio
from fastapi import FastAPI

# FastAPI will serve as our main app.
from starlette.websockets import WebSocket

app = FastAPI(debug=True)
# Socket.IO will be mounted as a sub application to the FastAPI main app.
# See the info here: https://github.com/tiangolo/fastapi/issues/129
sio = socketio.AsyncServer(async_mode='asgi')
# socket_app = socketio.ASGIApp(sio)
# app.mount('/new', socket_app)


@app.get("/hello")
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

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

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
    uvicorn.run(app, host="0.0.0.0", port=int(port))
