import unittest
import requests
import json
from azure.cosmos import CosmosClient
# extend os.environ from local.settings.json
import os

from vpq.helper.player import Player, PasswordLengthError

local_settings_json = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'local.settings.json')
if os.path.exists(local_settings_json):
    import json

    with open(local_settings_json) as f:
        settings = json.load(f)
    os.environ.update(settings['Values'])


class TestPlayerDel(unittest.TestCase):
    key = os.environ["FunctionAppKey"]
    PUBLIC_URL = None
    LOCAL_URL = "http://localhost:7071/api/playerDel?code={}".format(key)
    TEST_URL = LOCAL_URL
    PUBLIC_URL_ADD = None
    LOCAL_URL_ADD = "http://localhost:7071/api/playerAdd?code={}".format(key)
    TEST_URL_ADD = LOCAL_URL_ADD
    cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
    database = cosmos.get_database_client(os.environ['DatabaseName'])
    playerContainer = database.get_container_client(os.environ['Container_Players'])
    defaultPlayerJson = {
        'username': "bsab1g21",
        'password': "myTestPassword2",
        'firstname': "Ben",
        'lastname': "Burbridge",
        'dob': "06/02/2003",
        'currency': 0,
        'premium_currency': 0,
        'overall_score': 0,
        'friends': [],
        'fave_quizzes': []
    }

    def testValidPlayerDel(self):
        # Add the player to the database
        requests.post(self.TEST_URL_ADD, data=json.dumps(self.defaultPlayerJson))

        # Try deleting the player
        response = requests.delete(self.TEST_URL, data=json.dumps(self.defaultPlayerJson))

        # Check the player was successfully deleted
        query = "SELECT * FROM p where p.username='{}'".format(self.defaultPlayerJson['username'])
        usernameExists = len(
            list(self.playerContainer.query_items(query=query, enable_cross_partition_query=True))) == 1
        # self.assertEqual(usernameExists, False)
        print(response)
        self.assertEqual(response.json(), {'result': True, "msg": "Success"})

    def testPlayerDoesNotExist(self):
        # Delete the default player from the database to ensure it is not there before testing
        requests.delete(self.TEST_URL, data=json.dumps(self.defaultPlayerJson))

        # Delete the player from the database
        response = requests.delete(self.TEST_URL, data=json.dumps(self.defaultPlayerJson))

        # Check the correct message was received from the client
        self.assertEqual(response.json(), {'result': False, "msg": "Database DOES NOT contain username."})
