import asyncio
import os

import asynctest
import socketio
import uvicorn

# Set the port as environment variable as it is pulled when starting the uvicorn server.
# This has to be done before the import.
os.environ['PORT'] = '8080'
from api.main import composed_app, SOCKETIO_PATH


# The test setup is taken from https://github.com/miguelgrinberg/python-socketio/issues/332#issuecomment-523886747
class TestSocket(asynctest.TestCase):

    def setUp(self):
        """Test setup; is called before every unit test"""
        self.test_loop = asyncio.new_event_loop()
        self.test_loop.run_until_complete(self.run_server())
        self.socket_client1 = socketio.AsyncClient()
        self.socket_client2 = socketio.AsyncClient()

    def tearDown(self) -> None:
        self.test_loop.stop()
        self.test_loop.close()

    @staticmethod
    def init_server():
        config = uvicorn.Config(composed_app)
        server = uvicorn.Server(config=config)
        config.setup_event_loop()
        return server

    async def run_server(self):
        server = self.init_server()
        server_task = server.serve()
        asyncio.create_task(server_task)

    async def test_connect(self):
        """Test if connecting to SocketIO server works"""
        await self.socket_client1.connect('http://localhost:8080', transports='websocket', socketio_path=SOCKETIO_PATH)
        self.assertTrue(self.socket_client1.connected())
        # self.socket_client1.call
        await self.socket_client1.disconnect()
        # self.assertTrue(self.socket_client2.is_connected())
        # self.assertNotEqual(client.sid, client2.sid)
        # received = client.get_received()
        # self.assertEqual(len(received), 3)
        # self.assertEqual(received[0]['args'], 'connected')
        # self.assertEqual(received[1]['args'], '{}')
        # self.assertEqual(received[2]['args'], '{}')
        # client.disconnect()
        # self.assertFalse(client.is_connected())
        # self.assertTrue(client2.is_connected())
        # client2.disconnect()
        # self.assertFalse(client2.is_connected())
