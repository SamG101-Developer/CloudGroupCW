import unittest
import requests
import json

from vpq.tests.MetaTest import MetaTest
from vpq.helper.exceptions import DatabaseDoesNotContainUsernameError, QuestionSetNotFavouriteError


class TestPlayerFaveQuizDel(unittest.TestCase, MetaTest):
    PUBLIC_URL = None
    LOCAL_URL = "http://localhost:7071/api/playerFaveQuizDel?code={}".format(MetaTest.key)
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
        # Currently just have a question set as a placeholder
        # TODO: Make a question set and get its id. This will be the set used to test
        quizId = "2c70e55f-6338-40dd-86a7-b21c4cd24c01"

        # Add a user that has 1 favourite quiz
        player_copy = self.DEFAULT_PLAYER_JSON.copy()
        player_copy['fave_quizzes'].append(quizId)
        requests.post(self.TEST_URL_ADD, data=json.dumps(player_copy))
        requests.put(self.TEST_URL_INFO_SET, data=json.dumps(player_copy))

        # Send request to delete the favourite quiz
        request_json = {"username": player_copy["username"], "quizId": quizId}
        response = requests.put(self.TEST_URL, data=json.dumps(request_json))

        self.assertEqual(response.json(), {'result': True, "msg": "Success"})

    def testPlayerDoesNotExist(self):
        # Delete the default player from the database to ensure it is not there before testing
        requests.delete(self.TEST_URL_DEL, data=json.dumps(self.DEFAULT_PLAYER_JSON))

        # Real quiz ID TODO: Get this properly
        quizId = "2c70e55f-6338-40dd-86a7-b21c4cd24c01"

        # Send request to delete favourite quiz
        request_json = {"username": self.DEFAULT_PLAYER_JSON["username"], "quizId": quizId}
        response = requests.put(self.TEST_URL, data=json.dumps(request_json))

        self.assertEqual(response.json(), {'result': False, "msg": DatabaseDoesNotContainUsernameError.getMessage()})

    def testInvalidQuestionSetID(self):
        # Add a user that has no favourite quizzes
        requests.post(self.TEST_URL_ADD, data=json.dumps(self.DEFAULT_PLAYER_JSON))
        requests.put(self.TEST_URL_INFO_SET, data=json.dumps(self.DEFAULT_PLAYER_JSON))

        quizId = "2c70e55f-6338-40dd-86a7-b21c4cd24c01"

        # Send request to delete favourite quiz
        request_json = {"username": self.DEFAULT_PLAYER_JSON["username"], "quizId": quizId}
        response = requests.put(self.TEST_URL, data=json.dumps(request_json))

        self.assertEqual(response.json(), {'result': False, "msg": QuestionSetNotFavouriteError.getMessage()})
