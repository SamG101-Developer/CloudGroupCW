import json
import unittest
import requests

from vpq.tests.MetaTest import MetaTest
from vpq.helper.room import UserInRoomAlready,UserDoesNotExist,RoomDoesNotExist

class TestRoomAdd(unittest.TestCase, MetaTest):
    PUBLIC_URL_ROOM_ADD = None
    LOCAL_URL_ROOM_ADD = "http://localhost:7071/api/roomSessionAdd?code={}".format(MetaTest.key)
    TEST_URL_ROOM_ADD = LOCAL_URL_ROOM_ADD
    TEST_URL_PLAYER_ADD = "http://localhost:7071/api/playerAdd?code={}".format(MetaTest.key)
    TEST_URL_ROOM_DELETE = "http://localhost:7071/api/roomSessionDel?code={}".format(MetaTest.key)
    TEST_URL_ROOM_PLAYER_ADD = "http://localhost:7071/api/roomPlayerAdd?code={}".format(MetaTest.key)

    def setUp(self):
        # If the default player already exists, delete it
        query = "SELECT * FROM p where p.username='{}'".format(self.DEFAULT_PLAYER_JSON['username'])
        users = list(self.playerContainer.query_items(query=query, enable_cross_partition_query=True))
        if len(users) != 0:
            self.playerContainer.delete_item(item=users[0]['id'], partition_key=users[0]['id'])

        # Add the player to the database
        requests.post(self.TEST_URL_PLAYER_ADD, data=json.dumps(self.DEFAULT_PLAYER_JSON))

    def tearDown(self):
        try:
            requests.delete(self.TEST_URL_ROOM_DELETE, data=json.dumps({"username":self.DEFAULT_PLAYER_JSON['username']}))
        except Exception as e:
            print(f"An error occurred during tearDown: {e}")

    def testValidRoomAdd(self):

        # Create room
        username = self.DEFAULT_PLAYER_JSON['username']
        response = requests.post(self.TEST_URL_ROOM_ADD, data=json.dumps({"username":username}))

        # Check room has been created
        query = "SELECT * FROM p where p.room_admin='{}'".format(self.DEFAULT_PLAYER_JSON['username'])
        roomExists = len( list(self.roomContainer.query_items(query=query, enable_cross_partition_query=True)))
        self.assertEqual(True, (roomExists==1))

        # Check correct output message received
        roomIDQuery = "SELECT * FROM r where r.room_admin='{}'".format(username)
        roomID = list(self.roomContainer.query_items(query=roomIDQuery, enable_cross_partition_query=True))[0]['id']
        responseOutput = {'result': True, "msg": "Room created with id:{}".format(roomID)}
        self.assertEqual(responseOutput, response.json())



    def testUsernameAlreadyAdmin(self):
        # Try to create a room
        username = self.DEFAULT_PLAYER_JSON['username']
        requests.post(self.TEST_URL_ROOM_ADD, data=json.dumps({"username": username}))
        response = requests.post(self.TEST_URL_ROOM_ADD, data=json.dumps({"username": username}))


        self.assertEqual({'result': False, "msg":"User is already in another room."}, response.json())

    def testUsernameNotInDatabase(self):

        # If the default player already exists, delete it
        query = "SELECT * FROM p where p.username='{}'".format(self.DEFAULT_PLAYER_JSON['username'])
        users = list(self.playerContainer.query_items(query=query, enable_cross_partition_query=True))
        if len(users) != 0:
            self.playerContainer.delete_item(item=users[0]['id'], partition_key=users[0]['id'])

        # Create room
        username = self.DEFAULT_PLAYER_JSON['username']
        response = requests.post(self.TEST_URL_ROOM_ADD, data=json.dumps({"username": username}))

        # Check room has not been created
        query = "SELECT * FROM p where p.room_admin='{}'".format(self.DEFAULT_PLAYER_JSON['username'])
        roomExists = len(list(self.roomContainer.query_items(query=query, enable_cross_partition_query=True)))
        self.assertEqual(True, (roomExists == 0))

        # Check correct output message received
        responseOutput = {'result': False,'msg':UserDoesNotExist.getMessage()}
        self.assertEqual(responseOutput, response.json())






