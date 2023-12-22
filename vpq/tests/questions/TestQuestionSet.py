import json
import unittest

import requests

from vpq.tests.MetaTest import MetaTest
from vpq.helper.exceptions import DatabaseDoesNotContainQuestionError


class TestQuestionSGet(unittest.TestCase, MetaTest):
    PUBLIC_URL = None
    LOCAL_URL = f"http://localhost:7071/api/questionSet?code={MetaTest.key}"
    TEST_URL = LOCAL_URL

    PUBLIC_URL_ADD = None
    LOCAL_URL_ADD = f"http://localhost:7071/api/questionAdd?code={MetaTest.key}"
    TEST_URL_ADD = LOCAL_URL_ADD

    PUBLIC_URL_DEL = None
    LOCAL_URL_DEL = f"http://localhost:7071/api/questionDel?code={MetaTest.key}"
    TEST_URL_DEL = LOCAL_URL_DEL

    def testValidInfoSet(self):
        # Add a question to make sure it exists
        question_copy = self.DEFAULT_QUESTION_JSON.copy()
        requests.post(self.TEST_URL_ADD, data=json.dumps(question_copy))
        requests.put(self.TEST_URL, data=json.dumps(question_copy))

        question_copy_new = {
            "id": "1",
            "question": "testQuestion",
            "answers": ["testAnswer1", "testAnswer2", "testAnswer3", "testAnswer4"],
            "correctAnswer": 1,
        }

        # Send request to set question information
        response = requests.put(self.TEST_URL, data=json.dumps(question_copy_new))
        query = "SELECT * FROM p where p.id='1'"
        question = list(self.questionContainer.query_items(query=query, enable_cross_partition_query=True))[0]

        test_question = {}
        for dataName in question_copy_new:
            if dataName in question.keys():
                test_question[dataName] = question[dataName]

        self.assertEqual(question_copy_new, test_question)
        self.assertEqual(response.json()["result"], True)

    def testQuestionDoesNotExist(self):
        # Delete the default question from the database to ensure it is not there before testing
        requests.delete(self.TEST_URL_DEL, data=json.dumps(self.DEFAULT_QUESTION_JSON))

        # Send request to get info
        question_copy_new = {
            "id": "1",
            "question": "testQuestion",
            "answers": ["testAnswer1", "testAnswer2", "testAnswer3", "testAnswer4"],
            "correctAnswer": 1,
        }
        response = requests.put(self.TEST_URL, data=json.dumps(question_copy_new))

        self.assertEqual(response.json(), {'result': False, "msg": DatabaseDoesNotContainQuestionError.getMessage()})
