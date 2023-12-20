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
    LOCAL_URL = "http://localhost:7071/api/playerQuestionGroupsGet?code={}".format(key)
    TEST_URL = LOCAL_URL
    PUBLIC_URL_ADD = None
    LOCAL_URL_ADD = "http://localhost:7071/api/playerAdd?code={}".format(key)
    TEST_URL_ADD = LOCAL_URL_ADD
    PUBLIC_URL_DEL = None
    LOCAL_URL_DEL = "http://localhost:7071/api/playerDel?code={}".format(key)
    TEST_URL_DEL = LOCAL_URL_DEL
    cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
    database = cosmos.get_database_client(os.environ['DatabaseName'])
    playerContainer = database.get_container_client(os.environ['Container_Players'])
    questionContainer = database.get_container_client(os.environ['Container_Questions'])
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

    def testUserAndQuestionsExist(self):
        # Add a user
        requests.post(self.TEST_URL_ADD, data=json.dumps(self.defaultPlayerJson))

        # Send request for player questions
        response = requests.get(self.TEST_URL, data=json.dumps(self.defaultPlayerJson))

        self.assertEqual(response.json(), {'result': True, "body": [{'id': 'replace_with_new_document_id'}]})

    def testUserNoQuestions(self):
        # Add a user
        player_copy = self.defaultPlayerJson.copy()
        player_copy['username'] += "_3"
        requests.post(self.TEST_URL_ADD, data=json.dumps(player_copy))

        # Send request for player questions
        response = requests.get(self.TEST_URL, data=json.dumps(player_copy))

        self.assertEqual(response.json(), {'result': True, "body": []})

