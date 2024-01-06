import unittest
import json
import requests

from vpq.helper.exceptions import DatabaseDoesNotContainUsernameError
from vpq.tests.MetaTest import MetaTest
from vpq.helper.room import UserInRoomAlready,UserDoesNotExist,RoomDoesNotExist

class TestRoomPlayerAdd(unittest.TestCase, MetaTest):


    PUBLIC_URL_ROOM_ADD = None
    LOCAL_URL_ROOM_ADD = "http://localhost:7071/api/roomSessionAdd?code={}".format(MetaTest.key)
    TEST_URL_ROOM_ADD = LOCAL_URL_ROOM_ADD
    TEST_URL_PLAYER_ADD = "http://localhost:7071/api/playerAdd?code={}".format(MetaTest.key)
    TEST_URL_ROOM_DELETE = "http://localhost:7071/api/roomSessionDel?code={}".format(MetaTest.key)
    TEST_URL_ROOM_PLAYER_ADD = "http://localhost:7071/api/roomPlayerAdd?code={}".format(MetaTest.key)
    Test_URL_PLAYER_DELETE = "http://localhost:7071/api/playerDelete?code={}".format(MetaTest.key)

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
            requests.delete(self.Test_URL_PLAYER_DELETE, data=json.dumps({"username":self.DEFAULT_PLAYER_JSON['username']}))
        except Exception as e:
            print(f"An error occurred during tearDown: {e}")

    def testValidPlayerAdd(self):

        # Add player to room
        response = requests.post(self.TEST_URL_ROOM_PLAYER_ADD, data=json.dumps({"adminUsername": self.DEFAULT_PLAYER_JSON['username'], "usernameToAdd": self.DEFAULT_PLAYER_JSON_2['username']}))

        # Check player is in list of players.
        roomQuery = "SELECT * FROM r where r.room_admin='{}'".format(self.DEFAULT_PLAYER_JSON['username'])
        playersInRoom = list(self.roomContainer.query_items(query=roomQuery, enable_cross_partition_query=True))[0]['players_in_room']
        self.assertIn("player1",playersInRoom)

        # Check correct http response given
        self.assertEqual({'result': True, "msg": "Successfully added player to room."}, response.json())

    def testAdminPlayerNotInDatabase(self):

        # Add player to room
        response = requests.post(self.TEST_URL_ROOM_PLAYER_ADD, data=json.dumps({"adminUsername": "", "usernameToAdd": "player1"}))

        # Check correct http response given
        self.assertEqual({'result': False, "msg": DatabaseDoesNotContainUsernameError.getMessage()}, response.json())

    def testPlayerToAddNotInDatabase(self):

        # Add player to room
        response = requests.post(self.TEST_URL_ROOM_PLAYER_ADD, data=json.dumps({"adminUsername": self.DEFAULT_PLAYER_JSON['username'], "usernameToAdd": ""}))

        # Check correct http response given
        self.assertEqual({'result': False, "msg": DatabaseDoesNotContainUsernameError.getMessage()}, response.json())

    def testAdminPlayerAlreadyInRoom(self):

        # Add player to room
        response = requests.post(self.TEST_URL_ROOM_PLAYER_ADD, data=json.dumps({"adminUsername": self.DEFAULT_PLAYER_JSON['username'], "usernameToAdd": self.DEFAULT_PLAYER_JSON['username']}))

        # Check player is in list of players.
        roomQuery = "SELECT * FROM r where r.room_admin='{}'".format(self.DEFAULT_PLAYER_JSON['username'])
        playersInRoom = list(self.roomContainer.query_items(query=roomQuery, enable_cross_partition_query=True))[0]['players_in_room']
        self.assertEqual([],playersInRoom)

        # Check correct http response given
        self.assertEqual({'result': False, "msg": "User is already in another room."}, response.json())

    def testPlayerToAddAlreadyInRoom(self):

        # Add player to room
        requests.post(self.TEST_URL_ROOM_PLAYER_ADD, data=json.dumps({"adminUsername": self.DEFAULT_PLAYER_JSON['username'], "usernameToAdd": "player1"}))
        response = requests.post(self.TEST_URL_ROOM_PLAYER_ADD, data=json.dumps({"adminUsername": self.DEFAULT_PLAYER_JSON['username'], "usernameToAdd": "player1"}))

        # Check player is in list of players.
        roomQuery = "SELECT * FROM r where r.room_admin='{}'".format(self.DEFAULT_PLAYER_JSON['username'])
        playersInRoom = list(self.roomContainer.query_items(query=roomQuery, enable_cross_partition_query=True))[0]['players_in_room']
        self.assertEqual(['player1'],playersInRoom)

        # Check correct http response given
        self.assertEqual({'result': False, "msg": "User is already in another room."}, response.json())

