import unittest
import requests
import json

from vpq.tests.MetaTest import MetaTest
from vpq.helper.exceptions import DatabaseContainsUsernameError
from vpq.helper.player import UsernameLengthError, PasswordLengthError


class TestPlayerAdd(unittest.TestCase, MetaTest):
    PUBLIC_URL = None
    LOCAL_URL = "http://localhost:7071/api/playerAdd?code={}".format(MetaTest.key)
    TEST_URL = LOCAL_URL

    def testValidPlayerAdd(self):
        # If the default player already exists, delete it
        query = "SELECT * FROM p where p.username='{}'".format(self.DEFAULT_PLAYER_JSON['username'])
        users = list(self.playerContainer.query_items(query=query, enable_cross_partition_query=True))
        if len(users) != 0:
            self.playerContainer.delete_item(item=users[0]['id'], partition_key=users[0]['id'])

        # Add the player to the database
        response = requests.post(self.TEST_URL, data=json.dumps(self.DEFAULT_PLAYER_JSON))

        # Check the player was successfully added
        usernameExists = len(list(self.playerContainer.query_items(query=query, enable_cross_partition_query=True))) == 1
        self.assertEqual(usernameExists, True)
        self.assertEqual(response.json(), {'result': True, "msg": "Success"})

    def testPlayerAlreadyExists(self):
        # Add the default player to the database to ensure it is there before testing
        requests.post(self.TEST_URL, data=json.dumps(self.DEFAULT_PLAYER_JSON))

        # Add the player to the database
        response = requests.post(self.TEST_URL, data=json.dumps(self.DEFAULT_PLAYER_JSON))

        # Check the correct message was received from the client
        self.assertEqual(response.json(), {'result': False, "msg": DatabaseContainsUsernameError.getMessage()})

    def testUsernameLength(self):
        player_copy = self.DEFAULT_PLAYER_JSON.copy()

        # Test for username being too short
        player_copy['username'] = ""

        # Add the player to the database
        response = requests.post(self.TEST_URL, data=json.dumps(player_copy))

        # Check the correct message was received from the client, username must be at least 1 character
        self.assertEqual(response.json(), {'result': False, "msg": UsernameLengthError.getMessage()})

        # Test for username being too long
        player_copy['username'] = "abcdefghijklm"
        response = requests.post(self.TEST_URL, data=json.dumps(player_copy))

        # Check the correct message was received from the client, username must be at most 12 characters
        self.assertEqual(response.json(), {'result': False, "msg": UsernameLengthError.getMessage()})

    def testPasswordLength(self):
        player_copy = self.DEFAULT_PLAYER_JSON.copy()

        # Test for password being too short
        player_copy['password'] = "1"

        # Add the player to the database
        response = requests.post(self.TEST_URL, data=json.dumps(player_copy))

        # Check the correct message was received from the client, password must be at least 2 characters
        self.assertEqual(response.json(), {'result': False, "msg": PasswordLengthError.getMessage()})

        # Test for password being too long
        player_copy['password'] = "abcdefghijklmnopqrstu"
        response = requests.post(self.TEST_URL, data=json.dumps(player_copy))

        # Check the correct message was received from the client, password must be at most 20 characters
        self.assertEqual(response.json(), {'result': False, "msg": PasswordLengthError.getMessage()})
