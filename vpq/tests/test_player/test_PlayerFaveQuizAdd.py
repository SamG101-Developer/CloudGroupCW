import unittest
import requests
import json

from vpq.tests.MetaTest import MetaTest
from vpq.helper.exceptions import DatabaseDoesNotContainUsernameError, DatabaseDoesNotContainQuestionSetIDError


class TestPlayerFaveQuizAdd(unittest.TestCase, MetaTest):
    PUBLIC_URL = None
    LOCAL_URL = "http://localhost:7071/api/playerFaveQuizAdd?code={}".format(MetaTest.key)
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

    def testValidAddFaveQuiz(self):
        # Currently just have a question set as a placeholder
        # TODO: Make a question set and get its id. This will be the set used to test

        # Add a user that has no favourite quizzes
        requests.post(self.TEST_URL_ADD, data=json.dumps(self.DEFAULT_PLAYER_JSON))
        requests.put(self.TEST_URL_INFO_SET, data=json.dumps(self.DEFAULT_PLAYER_JSON))

        # Get the id of a favourite quiz
        query = "SELECT p.id FROM p"
        questionSetId = list(self.questionSetContainer.query_items(query=query, enable_cross_partition_query=True))[0]

        # Send request to add favourite quiz
        request_json = {"username": self.DEFAULT_PLAYER_JSON["username"], "quizId": questionSetId['id']}
        response = requests.put(self.TEST_URL, data=json.dumps(request_json))

        self.assertEqual(response.json(), {'result': True, "msg": "Success"})

    def testPlayerDoesNotExist(self):
        # Delete the default player from the database to ensure it is not there before testing
        requests.delete(self.TEST_URL_DEL, data=json.dumps(self.DEFAULT_PLAYER_JSON))

        # Get the id of a favourite quiz
        query = "SELECT p.id FROM p"
        questionSetId = list(self.questionSetContainer.query_items(query=query, enable_cross_partition_query=True))[0]

        # Send request to add favourite quiz
        request_json = {"username": self.DEFAULT_PLAYER_JSON["username"], "quizId": questionSetId['id']}
        response = requests.put(self.TEST_URL, data=json.dumps(request_json))

        self.assertEqual(response.json(), {'result': False, "msg": DatabaseDoesNotContainUsernameError.getMessage()})

    def testInvalidQuestionSetID(self):
        # Add a user that has no favourite quizzes
        requests.post(self.TEST_URL_ADD, data=json.dumps(self.DEFAULT_PLAYER_JSON))
        requests.put(self.TEST_URL_INFO_SET, data=json.dumps(self.DEFAULT_PLAYER_JSON))

        # Send request to add favourite quiz
        request_json = {"username": self.DEFAULT_PLAYER_JSON["username"], "quizId": "myFakeId"}
        response = requests.put(self.TEST_URL, data=json.dumps(request_json))

        self.assertEqual(response.json(), {'result': False, "msg": DatabaseDoesNotContainQuestionSetIDError.getMessage()})
