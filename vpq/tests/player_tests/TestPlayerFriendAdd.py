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


class TestPlayerFaveQuizAdd(unittest.TestCase):
    key = os.environ["FunctionAppKey"]
    PUBLIC_URL = None
    LOCAL_URL = "http://localhost:7071/api/playerFriendAdd?code={}".format(key)
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

    def testValidAddFriend(self):
        # Add 2 users that have no friends
        requests.post(self.TEST_URL_ADD, data=json.dumps(self.defaultPlayerJson))
        requests.put(self.TEST_URL_INFO_SET, data=json.dumps(self.defaultPlayerJson))
        player_friend = self.defaultPlayerJson.copy()
        player_friend['username'] += "_2"
        requests.post(self.TEST_URL_ADD, data=json.dumps(player_friend))
        requests.put(self.TEST_URL_INFO_SET, data=json.dumps(player_friend))

        # Send request to add friend
        request_json = {"username": self.defaultPlayerJson["username"], "friendUsername": player_friend['username']}
        response = requests.put(self.TEST_URL, data=json.dumps(request_json))

        self.assertEqual(response.json(), {'result': True, "msg": "Success"})

    def testPlayerDoesNotExist(self):
        # Friend exists but player does not
        # Delete the default player from the database to ensure it is not there before testing
        requests.delete(self.TEST_URL_DEL, data=json.dumps(self.defaultPlayerJson))

        # Add the friend player to the database
        player_friend = self.defaultPlayerJson.copy()
        player_friend['username'] += "_2"
        requests.post(self.TEST_URL_ADD, data=json.dumps(player_friend))
        requests.put(self.TEST_URL_INFO_SET, data=json.dumps(player_friend))

        # Send request to add friend
        request_json = {"username": self.defaultPlayerJson["username"], "friendUsername": player_friend['username']}
        response = requests.put(self.TEST_URL, data=json.dumps(request_json))

        self.assertEqual(response.json(), {'result': False, "msg": 'Database DOES NOT contain username.'})

        # Player exists but Friend does not
        # Delete the friend player from the database to ensure it is not there before testing
        requests.delete(self.TEST_URL_DEL, data=json.dumps(player_friend))

        # Add the default player to the database
        requests.post(self.TEST_URL_ADD, data=json.dumps(self.defaultPlayerJson))
        requests.put(self.TEST_URL_INFO_SET, data=json.dumps(self.defaultPlayerJson))

        # Send request to add friend
        request_json = {"username": self.defaultPlayerJson["username"], "friendUsername": player_friend['username']}
        response = requests.put(self.TEST_URL, data=json.dumps(request_json))

        self.assertEqual(response.json(), {'result': False, "msg": 'Database DOES NOT contain username.'})

    def testUsersAlreadyFriends(self):
        # Add 2 users that have no friends
        requests.post(self.TEST_URL_ADD, data=json.dumps(self.defaultPlayerJson))
        requests.put(self.TEST_URL_INFO_SET, data=json.dumps(self.defaultPlayerJson))
        player_friend = self.defaultPlayerJson.copy()
        player_friend['username'] += "_2"
        requests.post(self.TEST_URL_ADD, data=json.dumps(player_friend))
        requests.put(self.TEST_URL_INFO_SET, data=json.dumps(player_friend))

        # Make default player add friend player
        request_json = {"username": self.defaultPlayerJson["username"], "friendUsername": player_friend['username']}
        requests.put(self.TEST_URL, data=json.dumps(request_json))

        # Make default player add friend player again, now it should not work
        request_json = {"username": self.defaultPlayerJson["username"], "friendUsername": player_friend['username']}
        response = requests.put(self.TEST_URL, data=json.dumps(request_json))

        self.assertEqual(response.json(), {'result': False, "msg": 'The users are already friends.'})
