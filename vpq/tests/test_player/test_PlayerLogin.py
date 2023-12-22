import json
import unittest
import requests

from vpq.tests.MetaTest import MetaTest
from vpq.helper.exceptions import IncorrectUsernameOrPasswordError


class TestPlayerAdd(unittest.TestCase, MetaTest):
    PUBLIC_URL = None
    LOCAL_URL = "http://localhost:7071/api/playerLogin?code={}".format(MetaTest.key)
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

    def testValidPlayerLogin(self):
        # Add a user and set it to default settings
        requests.post(self.TEST_URL_ADD, data=json.dumps(self.DEFAULT_PLAYER_JSON))
        requests.put(self.TEST_URL_INFO_SET, data=json.dumps(self.DEFAULT_PLAYER_JSON))

        # Try and log in with the correct username and password
        response = requests.get(self.TEST_URL, data=json.dumps({
            "username": self.DEFAULT_PLAYER_JSON['username'],
            "password": self.DEFAULT_PLAYER_JSON["password"]}))

        self.assertEqual(response.json(), {'result': True, "msg": "Success"})

    def testPlayerLoginIncorrectUsername(self):
        # Add a user and set it to default settings
        requests.post(self.TEST_URL_ADD, data=json.dumps(self.DEFAULT_PLAYER_JSON))
        requests.put(self.TEST_URL_INFO_SET, data=json.dumps(self.DEFAULT_PLAYER_JSON))

        # Delete any users that are called "bsab1g21_2"
        invalidUsername = self.DEFAULT_PLAYER_JSON["username"] + "_2"
        requests.delete(self.TEST_URL_DEL, data=json.dumps({"username": invalidUsername}))

        # Try and log in with the incorrect username
        response = requests.get(self.TEST_URL, data=json.dumps({
            "username": invalidUsername,
            "password": self.DEFAULT_PLAYER_JSON["password"]}))

        self.assertEqual(response.json(), {'result': False, "msg": IncorrectUsernameOrPasswordError.getMessage()})

    def testPlayerLoginIncorrectPassword(self):
        # Add a user and set it to default settings
        requests.post(self.TEST_URL_ADD, data=json.dumps(self.DEFAULT_PLAYER_JSON))
        requests.put(self.TEST_URL_INFO_SET, data=json.dumps(self.DEFAULT_PLAYER_JSON))

        # Try and log in with the incorrect password
        invalidPassword = self.DEFAULT_PLAYER_JSON["password"] + "_2"
        response = requests.get(self.TEST_URL, data=json.dumps({
            "username": self.DEFAULT_PLAYER_JSON["username"],
            "password": invalidPassword}))

        self.assertEqual(response.json(), {'result': False, "msg": IncorrectUsernameOrPasswordError.getMessage()})