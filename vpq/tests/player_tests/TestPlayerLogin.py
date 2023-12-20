import unittest
import requests

from azure.cosmos import CosmosClient
# extend os.environ from local.settings.json
import os

local_settings_json = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'local.settings.json')
if os.path.exists(local_settings_json):
    import json

    with open(local_settings_json) as f:
        settings = json.load(f)
    os.environ.update(settings['Values'])


class TestPlayerAdd(unittest.TestCase):
    key = os.environ["FunctionAppKey"]
    PUBLIC_URL = None
    LOCAL_URL = "http://localhost:7071/api/playerLogin?code={}".format(key)
    TEST_URL = LOCAL_URL
    PUBLIC_URL_ADD = None
    LOCAL_URL_ADD = "http://localhost:7071/api/playerAdd?code={}".format(key)
    TEST_URL_ADD = LOCAL_URL_ADD
    PUBLIC_URL_INFO_SET = None
    LOCAL_URL_INFO_SET = "http://localhost:7071/api/playerInfoSet?code={}".format(key)
    TEST_URL_INFO_SET = LOCAL_URL_INFO_SET
    PUBLIC_URL_DEL = None
    LOCAL_URL_DEL = "http://localhost:7071/api/playerDel?code={}".format(key)
    TEST_URL_DEL = LOCAL_URL_DEL
    cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
    database = cosmos.get_database_client(os.environ['DatabaseName'])
    playerContainer = database.get_container_client(os.environ['Container_Players'])
    defaultPlayerJson = {
        'username': "bsab1g21",
        'password': "myTestPassword",
        'firstname': "Ben",
        'lastname': "Burbridge",
        'dob': "06/02/2003",
        'currency': 0,
        'premium_currency': 0,
        'overall_score': 0,
        'friends': [],
        'fave_quizzes': []
    }

    def testValidPlayerLogin(self):
        # Add a user and set it to default settings
        requests.post(self.TEST_URL_ADD, data=json.dumps(self.defaultPlayerJson))
        requests.put(self.TEST_URL_INFO_SET, data=json.dumps(self.defaultPlayerJson))

        # Try and log in with the correct username and password
        response = requests.get(self.TEST_URL, data=json.dumps({"username": self.defaultPlayerJson['username'],
                                                                "password": self.defaultPlayerJson["password"]}))

        self.assertEqual(response.json(), {'result': True, "msg": "Success"})

    def testPlayerLoginIncorrectUsername(self):
        # Add a user and set it to default settings
        requests.post(self.TEST_URL_ADD, data=json.dumps(self.defaultPlayerJson))
        requests.put(self.TEST_URL_INFO_SET, data=json.dumps(self.defaultPlayerJson))

        # Delete any users that are called "bsab1g21_2"
        invalidUsername = self.defaultPlayerJson["username"] + "_2"
        requests.delete(self.TEST_URL_DEL, data=json.dumps({"username": invalidUsername}))

        # Try and log in with the incorrect username
        response = requests.get(self.TEST_URL, data=json.dumps({"username": invalidUsername,
                                                                "password": self.defaultPlayerJson["password"]}))

        self.assertEqual(response.json(), {'result': False, "msg": 'Username and password DO NOT match.'})

    def testPlayerLoginIncorrectPassword(self):
        # Add a user and set it to default settings
        requests.post(self.TEST_URL_ADD, data=json.dumps(self.defaultPlayerJson))
        requests.put(self.TEST_URL_INFO_SET, data=json.dumps(self.defaultPlayerJson))

        # Try and log in with the incorrect password
        invalidPassword = self.defaultPlayerJson["password"] + "_2"
        response = requests.get(self.TEST_URL, data=json.dumps({"username": self.defaultPlayerJson["username"],
                                                                "password": invalidPassword}))

        self.assertEqual(response.json(), {'result': False, "msg": 'Username and password DO NOT match.'})