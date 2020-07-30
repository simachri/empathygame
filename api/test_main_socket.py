import os
import time
import unittest
from multiprocessing import Process

import socketio
# Set the port as environment variable as it is pulled when starting the uvicorn server.
# This has to be done before the import.
import uvicorn

from events import CONN_SUCCESS

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
    time.sleep(3)


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


def on_conn_success():
    pass


class TestSocket(unittest.TestCase):

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
        # await TestSocket.launch_server_async()
        self.client = socketio.Client()

    def tearDown(self) -> None:
        """Test setup; is called before every unit test"""
        self.client.disconnect()

    def test_connect(self):
        """Test if connecting to SocketIO server works"""
        # Use the 'on' method for handling incoming events later.
        self.client.on(CONN_SUCCESS, on_conn_success)
        self.client.connect('http://localhost:8080', transports='websocket', socketio_path=SOCKETIO_PATH)
        # The connected-assertion is trivial as 'connected' is set to True even if no actual connection has been
        # established.
        self.assertTrue(self.client.connected)
