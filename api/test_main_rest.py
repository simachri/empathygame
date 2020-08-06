import os
import unittest

from starlette.testclient import TestClient

# Set the port as environment variable as it is pulled when starting the uvicorn server.
os.environ['PORT'] = '8080'

SCENARIO_ID = 1


class TestREST(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        self._bin = []
        super().__init__(*args, **kwargs)

    def setUp(self):
        """Test setup; is called before every unit test"""
        # Launch the server.
        from api.main import composed_app
        self.client = TestClient(composed_app)

    def test_get_scenario(self):
        """Test GET /scenario/{id}"""
        res = self.client.get(f'/scenario/{SCENARIO_ID}')
        self.assertEqual(200, res.status_code, 'Status code 200 expected.')
        data = res.json()
        self.assertIsNotNone(data.get('id'), 'Missing attribute in result data.')
        self.assertIsNotNone(data.get('titel'), 'Missing attribute in result data.')
        self.assertIsNotNone(data.get('descr'), 'Missing attribute in result data.')
        self.assertIsNotNone(data.get('background_info'), 'Missing attribute in result data.')
        self.assertIsNotNone(data.get('decision_options'), 'Missing attribute in result data.')
        self.assertIsNotNone(data.get('personas'), 'Missing attribute in result data.')
        self.assertIsNotNone(data['decision_options'][0].get('id'), 'Missing attribute in result data.')
        self.assertIsNotNone(data['decision_options'][0].get('titel'), 'Missing attribute in result data.')
        self.assertIsNotNone(data['decision_options'][0].get('descr'), 'Missing attribute in result data.')
        self.assertIsNotNone(data['personas'][0].get('id'), 'Missing attribute in result data.')
        self.assertIsNotNone(data['personas'][0].get('name'), 'Missing attribute in result data.')
        self.assertIsNotNone(data['personas'][0].get('descr'), 'Missing attribute in result data.')
        self.assertIsNotNone(data['personas'][0].get('mandatory'), 'Missing attribute in result data.')
