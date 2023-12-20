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


class TestPlayerInfoGet(unittest.TestCase):
    key = os.environ["FunctionAppKey"]
    PUBLIC_URL = None
    LOCAL_URL = "http://localhost:7071/api/playerInfoGet?code={}".format(key)
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
    questionSetContainer = database.get_container_client(os.environ['Container_QuestionSet'])
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

    def testValidInfoGet(self):
        # Add a user and update their information so that they have 10 currency, 5 premium currency and 20 score
        player_copy = self.defaultPlayerJson.copy()
        player_copy['currency'] = 10
        player_copy['overall_score'] = 20
        player_copy['premium_currency'] = 5
        requests.post(self.TEST_URL_ADD, data=json.dumps(player_copy))
        requests.put(self.TEST_URL_INFO_SET, data=json.dumps(player_copy))

        # Send request for player information
        request_json = {"username": player_copy["username"]}
        response = requests.get(self.TEST_URL, data=json.dumps(request_json))

        self.assertEqual(response.json(), {'result': True, "body": {
            'username': "bsab1g21",
            'currency': 10,
            'premium_currency': 5,
            'overall_score': 20,
            'friends': [],
            'fave_quizzes': []
        }})

    def testPlayerDoesNotExist(self):
        # Delete the default player from the database to ensure it is not there before testing
        requests.delete(self.TEST_URL_DEL, data=json.dumps(self.defaultPlayerJson))

        # Send request to get info
        request_json = {"username": self.defaultPlayerJson["username"]}
        response = requests.get(self.TEST_URL, data=json.dumps(request_json))

        self.assertEqual(response.json(), {'result': False, "msg": 'Database DOES NOT contain username.'})

