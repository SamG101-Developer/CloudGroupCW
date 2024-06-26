import unittest
import requests
import json

from vpq.tests.MetaTest import MetaTest
from vpq.helper.exceptions import DatabaseDoesNotContainUsernameError


class TestPlayerInfoGet(unittest.TestCase, MetaTest):
    PUBLIC_URL = None
    LOCAL_URL = "http://localhost:7071/api/playerInfoSet?code={}".format(MetaTest.key)
    TEST_URL = LOCAL_URL
    
    PUBLIC_URL_ADD = None
    LOCAL_URL_ADD = "http://localhost:7071/api/playerAdd?code={}".format(MetaTest.key)
    TEST_URL_ADD = LOCAL_URL_ADD
    
    PUBLIC_URL_INFO_SET = None
    LOCAL_URL_INFO_SET = "http://localhost:7071/api/playerInfoSet?code={}".format(MetaTest.key)
    TEST_URL_INFO_SET = LOCAL_URL_INFO_SET
    
    PUBLIC_URL_DEL = None
    LOCAL_URL_DEL = "http://localhost:7071/api/playerDel?code={}".format(MetaTest.key)
    TEST_URL_DEL = LOCAL_URL_DEL

    def testValidInfoSet(self):
        # Add a user to make sure they exist
        player_copy = self.DEFAULT_PLAYER_JSON.copy()
        requests.post(self.TEST_URL_ADD, data=json.dumps(player_copy))
        requests.put(self.TEST_URL_INFO_SET, data=json.dumps(player_copy))

        player_copy_new = {
            'username': "bsab1g21",
            'password': "myTestPassword2_new",
            'firstname': "Ben_new",
            'lastname': "Burbridge_new",
            'dob': "06/02/2003_new",
            'currency': 100,
            'premium_currency': 100,
            'overall_score': 100,
            'friends': ["a friend"],
            'fave_quizzes': ["a quiz"]
        }

        # Send request to set player information
        response = requests.put(self.TEST_URL, data=json.dumps(player_copy_new))

        query = "SELECT * FROM p where p.username='bsab1g21'"
        user = list(self.playerContainer.query_items(query=query, enable_cross_partition_query=True))[0]

        test_user = {}
        for dataName in player_copy_new:
            if dataName in user.keys():
                test_user[dataName] = user[dataName]

        self.assertEqual(player_copy_new, test_user)
        self.assertEqual(response.json()['result'], True)

    def testPlayerDoesNotExist(self):
        # Delete the default player from the database to ensure it is not there before testing
        requests.delete(self.TEST_URL_DEL, data=json.dumps(self.DEFAULT_PLAYER_JSON))

        # Send request to get info
        player_copy_new = {
            'username': "bsab1g21",
            'password': "myTestPassword2_new",
            'firstname': "Ben_new",
            'lastname': "Burbridge_new",
            'dob': "06/02/2003_new",
            'currency': 100,
            'premium_currency': 100,
            'overall_score': 100,
            'friends': ["a friend"],
            'fave_quizzes': ["a quiz"]
        }
        response = requests.put(self.TEST_URL, data=json.dumps(player_copy_new))

        self.assertEqual(response.json(), {'result': False, "msg": DatabaseDoesNotContainUsernameError.getMessage()})
