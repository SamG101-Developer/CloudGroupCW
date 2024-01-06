import unittest
import json
import requests

from vpq.tests.MetaTest import MetaTest
from vpq.helper.room import UserInRoomAlready,UserDoesNotExist,RoomDoesNotExist

class TestRoomSetAdultOnly(unittest.TestCase, MetaTest):

    PUBLIC_URL_ROOM_ADD = None
    LOCAL_URL_ROOM_ADD = "http://localhost:7071/api/roomSessionAdd?code={}".format(MetaTest.key)
    TEST_URL_PLAYER_ADD = "http://localhost:7071/api/playerAdd?code={}".format(MetaTest.key)
    TEST_URL_ROOM_DELETE = "http://localhost:7071/api/roomSessionDel?code={}".format(MetaTest.key)
    TEST_URL_PLAYER_DELETE = "http://localhost:7071/api/playerDelete?code={}".format(MetaTest.key)
    TEST_URL_ROOM_SET_ADULT_ONLY = "http://localhost:7071/api/roomAdultOnlySet?code={}".format(MetaTest.key)
    TEST_URL_ROOM_ADD = LOCAL_URL_ROOM_ADD
    def setUp(self):
        # Add the player to the database
        requests.post(self.TEST_URL_PLAYER_ADD, data=json.dumps(self.DEFAULT_PLAYER_JSON))
        requests.post(self.TEST_URL_PLAYER_ADD, data=json.dumps(self.DEFAULT_PLAYER_JSON_2))

        # Create room
        username = self.DEFAULT_PLAYER_JSON['username']
        requests.post(self.TEST_URL_ROOM_ADD, data=json.dumps({"username": username}))

    def tearDown(self):
        try:
            requests.delete(self.TEST_URL_ROOM_DELETE, data=json.dumps({"username":self.DEFAULT_PLAYER_JSON['username']}))
            requests.delete(self.TEST_URL_PLAYER_DELETE, data=json.dumps({"username":self.DEFAULT_PLAYER_JSON['username']}))
        except Exception as e:
            print(f"An error occurred during tearDown: {e}")

    def testValidSetAdultOnly(self):

        # Add player to room
        response = requests.post(self.TEST_URL_ROOM_SET_ADULT_ONLY, data=json.dumps({"adminUsername": self.DEFAULT_PLAYER_JSON['username'],"valueToSet": True}))

        # Check adult only flag is True
        roomQuery = "SELECT * FROM r where r.room_admin='{}'".format(self.DEFAULT_PLAYER_JSON['username'])
        adultOnlyValue = list(self.roomContainer.query_items(query=roomQuery, enable_cross_partition_query=True))[0]['adult_only']
        self.assertTrue(adultOnlyValue)

        # Check correct http response given
        self.assertEqual({'result': True, "msg": "Successfully changed adult only flag to: True"}, response.json())
