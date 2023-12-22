import unittest
import requests
import json

from vpq.tests.MetaTest import MetaTest
from vpq.helper.exceptions import DatabaseDoesNotContainUsernameError


class TestPlayerDel(unittest.TestCase, MetaTest):
    PUBLIC_URL = None
    LOCAL_URL = "http://localhost:7071/api/playerAdd?code={}".format(MetaTest.key)
    TEST_URL = LOCAL_URL

    def testValidPlayerDel(self):
        # Add the player to the database
        requests.post(self.TEST_URL, data=json.dumps(self.DEFAULT_PLAYER_JSON))

        # Try deleting the player
        response = requests.delete(self.TEST_URL, data=json.dumps(self.DEFAULT_PLAYER_JSON))

        # Check the player was successfully deleted
        query = "SELECT * FROM p where p.username='{}'".format(self.DEFAULT_PLAYER_JSON['username'])
        usernameExists = len(list(self.playerContainer.query_items(query=query, enable_cross_partition_query=True))) == 1

        self.assertEqual(usernameExists, False)
        self.assertEqual(response.json(), {'result': True, "msg": "Success"})

    def testPlayerDoesNotExist(self):
        # Delete the default player from the database to ensure it is not there before testing
        requests.delete(self.TEST_URL, data=json.dumps(self.DEFAULT_PLAYER_JSON))

        # Delete the player from the database
        response = requests.delete(self.TEST_URL, data=json.dumps(self.DEFAULT_PLAYER_JSON))

        # Check the correct message was received from the client
        self.assertEqual(response.json(), {'result': False, "msg": DatabaseDoesNotContainUsernameError.getMessage()})
