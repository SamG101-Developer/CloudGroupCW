import unittest
import requests
import json

from vpq.tests.MetaTest import MetaTest
from vpq.helper.exceptions import DatabaseDoesNotContainUsernameError


class TestPlayerInfoGet(unittest.TestCase, MetaTest):
    PUBLIC_URL = None
    LOCAL_URL = "http://localhost:7071/api/playerInfoGet?code={}".format(MetaTest.key)
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

    def testValidInfoGet(self):
        # Add a user and update their information so that they have 10 currency, 5 premium currency and 20 score
        player_copy = self.DEFAULT_PLAYER_JSON.copy()
        player_copy['currency'] = 10
        player_copy['overall_score'] = 20
        player_copy['premium_currency'] = 5
        requests.post(self.TEST_URL_ADD, data=json.dumps(player_copy))
        requests.put(self.TEST_URL_INFO_SET, data=json.dumps(player_copy))

        # Send request for player information
        request_json = {"username": player_copy["username"]}
        response = requests.get(self.TEST_URL, data=json.dumps(request_json))

        self.assertTrue(response.json()["result"])
        self.assertEqual(response.json()["body"]["currency"], 10)
        self.assertEqual(response.json()["body"]["premium_currency"], 5)
        self.assertEqual(response.json()["body"]["overall_score"], 20)

    def testPlayerDoesNotExist(self):
        # Delete the default player from the database to ensure it is not there before testing
        requests.delete(self.TEST_URL_DEL, data=json.dumps(self.DEFAULT_PLAYER_JSON))

        # Send request to get info
        request_json = {"username": self.DEFAULT_PLAYER_JSON["username"]}
        response = requests.get(self.TEST_URL, data=json.dumps(request_json))

        self.assertEqual(response.json(), {'result': False, "msg": DatabaseDoesNotContainUsernameError.getMessage()})
