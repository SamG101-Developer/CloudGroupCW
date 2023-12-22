import unittest
import requests
import json

from vpq.tests.MetaTest import MetaTest
from vpq.helper.exceptions import DatabaseDoesNotContainUsernameError, UsersNotFriendsError


class TestPlayerFaveQuizDel(unittest.TestCase, MetaTest):
    PUBLIC_URL = None
    LOCAL_URL = "http://localhost:7071/api/playerFriendDel?code={}".format(MetaTest.key)
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
    
    def testValidDelFaveQuiz(self):
        # Add 2 users that are friends
        player_copy = self.DEFAULT_PLAYER_JSON.copy()
        player_copy['friends'].append("bsab1g21_2")
        player_friend = player_copy.copy()
        player_friend['username'] = "bsab1g21_2"
        player_friend['friends'].append("bsab1g21")
        requests.post(self.TEST_URL_ADD, data=json.dumps(player_copy))
        requests.put(self.TEST_URL_INFO_SET, data=json.dumps(player_copy))
        requests.post(self.TEST_URL_ADD, data=json.dumps(player_friend))
        requests.put(self.TEST_URL_INFO_SET, data=json.dumps(player_friend))

        # Send request for player to delete friend
        request_json = {"username": player_copy["username"], "friendUsername": player_friend['username']}
        response = requests.put(self.TEST_URL, data=json.dumps(request_json))

        self.assertEqual(response.json(), {'result': True, "msg": "Success"})

    def testPlayerDoesNotExist(self):
        # Friend exists but player does not
        # Delete the default player from the database to ensure it is not there before testing
        requests.delete(self.TEST_URL_DEL, data=json.dumps(self.DEFAULT_PLAYER_JSON))

        # Add the friend player to the database
        player_friend = self.DEFAULT_PLAYER_JSON.copy()
        player_friend['username'] += "_2"
        requests.post(self.TEST_URL_ADD, data=json.dumps(player_friend))
        requests.put(self.TEST_URL_INFO_SET, data=json.dumps(player_friend))

        # Send request to delete friend
        request_json = {"username": self.DEFAULT_PLAYER_JSON["username"], "friendUsername": player_friend['username']}
        response = requests.put(self.TEST_URL, data=json.dumps(request_json))

        self.assertEqual(response.json(), {'result': False, "msg": DatabaseDoesNotContainUsernameError.getMessage()})

    def testUsersAreNotFriends(self):
        # Add 2 users that are friends
        player_copy = self.DEFAULT_PLAYER_JSON.copy()
        player_friend = player_copy.copy()
        player_friend['username'] = "bsab1g21_2"
        requests.post(self.TEST_URL_ADD, data=json.dumps(player_copy))
        requests.post(self.TEST_URL_ADD, data=json.dumps(player_friend))

        # Send request for player to delete friend
        request_json = {"username": player_copy["username"], "friendUsername": player_friend['username']}
        response = requests.put(self.TEST_URL, data=json.dumps(request_json))

        self.assertEqual(response.json(), {'result': False, "msg": UsersNotFriendsError.getMessage()})
