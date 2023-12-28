import json
import logging
import unittest

import requests

from vpq.tests.MetaTest import MetaTest
from vpq.helper.exceptions import DatabaseDoesNotContainUsernameError
from vpq.helper.question import QuestionLengthError


class TestQuestionAdd(unittest.TestCase, MetaTest):
    PUBLIC_URL = None
    LOCAL_URL = f"http://localhost:7071/api/questionAdd?code={MetaTest.key}"
    TEST_URL = LOCAL_URL

    PUBLIC_URL_DEL = None
    LOCAL_URL_DEL = f"http://localhost:7071/api/questionDel?code={MetaTest.key}"
    TEST_URL_DEL = LOCAL_URL_DEL

    PUBLIC_URL_PLAYER_DEL = None
    LOCAL_URL_PLAYER_DEL = f"http://localhost:7071/api/questionDel?code={MetaTest.key}"
    TEST_URL_PLAYER_DEL = LOCAL_URL_PLAYER_DEL

    PUBLIC_URL_PLAYER_ADD = None
    LOCAL_URL_PLAYER_ADD = f"http://localhost:7071/api/playerAdd?code={MetaTest.key}"
    TEST_URL_PLAYER_ADD = LOCAL_URL_PLAYER_ADD
    
    def testValidQuestionAdd(self):
        # Make sure the user is in the players database
        query = "SELECT * FROM p where p.username='{}'".format(self.DEFAULT_QUESTION_JSON["author"])
        players = list(self.playerContainer.query_items(query=query, enable_cross_partition_query=True))
        if len(players) == 0:
            requests.post(self.TEST_URL_PLAYER_ADD, data=json.dumps(self.DEFAULT_PLAYER_JSON))

        # If the default question already exists, delete it
        query = "SELECT * FROM p where p.id='{}'".format(self.DEFAULT_QUESTION_JSON['id'])
        questions = list(self.questionContainer.query_items(query=query, enable_cross_partition_query=True))
        if len(questions) != 0:
            requests.delete(self.TEST_URL_DEL, data=json.dumps(self.DEFAULT_QUESTION_JSON))

        # Check the question was successfully added
        response = requests.post(self.TEST_URL, data=json.dumps(self.DEFAULT_QUESTION_JSON))
        questionExists = len(list(self.questionContainer.query_items(query=query, enable_cross_partition_query=True))) == 1
        self.assertEqual(response.json(), {"result": True, "msg": "Success"})
        self.assertEqual(questionExists, True)

    def testQuestionTooLong(self):
        # Create a question that is too long
        badQuestion = self.DEFAULT_QUESTION_JSON.copy()
        badQuestion["question"] = "a" * 256
        
        # Attempt to add the question to the database
        response = requests.post(self.TEST_URL, data=json.dumps(badQuestion))
        
        # Check the correct message was received from the client
        self.assertEqual(response.json(), {"result": False, "msg": QuestionLengthError.getMessage()})
        
    def testQuestionTooShort(self):
        # Create a question that is too short
        badQuestion = self.DEFAULT_QUESTION_JSON.copy()
        badQuestion["question"] = ""
        
        # Attempt to add the question to the database
        response = requests.post(self.TEST_URL, data=json.dumps(badQuestion))
        
        # Check the correct message was received from the client
        self.assertEqual(response.json(), {"result": False, "msg": QuestionLengthError.getMessage()})

    def testQuestionInvalidAuthor(self):
        # Create a question with an invalid author
        badQuestion = self.DEFAULT_QUESTION_JSON.copy()
        badQuestion["author"] = ""

        # Attempt to add the question to the database
        response = requests.post(self.TEST_URL, data=json.dumps(badQuestion))

        # Check the correct message was received from the client
        self.assertEqual(response.json(), {"result": False, "msg": DatabaseDoesNotContainUsernameError.getMessage()})
