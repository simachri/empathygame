import os
import unittest

from starlette.testclient import TestClient

# Set the port as environment variable as it is pulled when starting the uvicorn server.
os.environ['PORT'] = '8080'


class TestREST(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        self._bin = []
        super().__init__(*args, **kwargs)

    def setUp(self):
        """Test setup; is called before every unit test"""
        # Launch the server.
        from api.main import composed_app
        self.client = TestClient(composed_app)

    def test_hello_world(self):
        """Test if 'Hello World' works."""
        res = self.client.get(f'/hello')
        assert res.status_code == 200, 'Status code 200 is expected.'
        assert res.json()['message'] == 'Hello World'
