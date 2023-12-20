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


class TestPlayerAdd(unittest.TestCase):
    key = os.environ["FunctionAppKey"]
    PUBLIC_URL = None
    LOCAL_URL = "http://localhost:7071/api/playerAdd?code={}".format(key)
    TEST_URL = LOCAL_URL
    cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
    database = cosmos.get_database_client(os.environ['DatabaseName'])
    playerContainer = database.get_container_client(os.environ['Container_Players'])
    defaultPlayerJson = {
        'username': "bsab1g21",
        'password': "myTestPassword2",
        'firstName': "Ben",
        'lastName': "Burbridge",
        'dob': "06/02/2003",
        'freeCurrency': 0,
        'premiumCurrency': 0,
        'totalScore': 0,
        'friends': [],
        'favQuizzes': []
    }

    def testValidPlayerAdd(self):
        # If the default player already exists, delete it
        query = "SELECT * FROM p where p.username='{}'".format(self.defaultPlayerJson['username'])
        users = list(self.playerContainer.query_items(query=query, enable_cross_partition_query=True))
        if len(users) != 0:
            self.playerContainer.delete_item(item=users[0]['id'], partition_key=users[0]['id'])

        # Add the player to the database
        response = requests.post(self.TEST_URL, data=json.dumps(self.defaultPlayerJson))

        # Check the player was successfully added
        usernameExists = len(
            list(self.playerContainer.query_items(query=query, enable_cross_partition_query=True))) == 1
        self.assertEqual(usernameExists, True)
        self.assertEqual(response.json(), {'result': True, "msg": "Success"})

    def testPlayerAlreadyExists(self):
        # Add the default player to the database to ensure it is there before testing
        requests.post(self.TEST_URL, data=json.dumps(self.defaultPlayerJson))

        # Add the player to the database
        response = requests.post(self.TEST_URL, data=json.dumps(self.defaultPlayerJson))

        # Check the correct message was received from the client
        self.assertEqual(response.json(), {'result': False, "msg": "Database already contains username."})

    def testUsernameLength(self):
        player_copy = self.defaultPlayerJson.copy()

        # Test for username being too short
        player_copy['username'] = ""

        # Add the player to the database
        response = requests.post(self.TEST_URL, data=json.dumps(player_copy))

        # Check the correct message was received from the client, username must be at least 1 character
        self.assertEqual(response.json(), {'result': False, "msg": "Username length invalid."})

        # Test for username being too long
        player_copy['username'] = "abcdefghijklm"
        response = requests.post(self.TEST_URL, data=json.dumps(player_copy))

        # Check the correct message was received from the client, username must be at most 12 characters
        self.assertEqual(response.json(), {'result': False, "msg": "Username length invalid."})

    def testPasswordLength(self):
        player_copy = self.defaultPlayerJson.copy()

        # Test for password being too short
        player_copy['password'] = "1"

        # Add the player to the database
        response = requests.post(self.TEST_URL, data=json.dumps(player_copy))

        # Check the correct message was received from the client, password must be at least 2 characters
        self.assertEqual(response.json(), {'result': False, "msg": "Password length invalid."})

        # Test for password being too long
        player_copy['password'] = "abcdefghijklmnopqrstu"
        response = requests.post(self.TEST_URL, data=json.dumps(player_copy))

        # Check the correct message was received from the client, password must be at most 20 characters
        self.assertEqual(response.json(), {'result': False, "msg": "Password length invalid."})
