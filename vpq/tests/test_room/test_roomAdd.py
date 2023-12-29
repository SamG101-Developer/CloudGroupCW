import json
import logging
import unittest

import requests

from vpq.tests.MetaTest import MetaTest
#from vpq.helper.exceptions import
from vpq.helper.room import Room

class TestRoomAdd(unittest.TestCase, MetaTest):
    PUBLIC_URL_PLAYER_ADD = None
    LOCAL_URL_PLAYER_ADD = f"http://localhost:7071/api/roomSessionAdd?code={MetaTest.key}"
    TEST_URL_PLAYER_ADD = LOCAL_URL_PLAYER_ADD

    def testValidQuestionAdd(self):
        # Create Room
        response = requests.post(self.TEST_URL_PLAYER_ADD, data=json.dumps({"username":"ethan"}))
        self.assertTrue(True)

