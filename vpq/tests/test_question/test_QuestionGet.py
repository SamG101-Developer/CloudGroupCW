import json
import unittest

import requests

from vpq.helper.exceptions import DatabaseDoesNotContainQuestionError
from vpq.tests.MetaTest import MetaTest


class TestQuestionGet(unittest.TestCase, MetaTest):
    PUBLIC_URL = None
    LOCAL_URL = f"http://localhost:7071/api/questionGet?code={MetaTest.key}"
    TEST_URL = LOCAL_URL

    PUBLIC_URL_ADD = None
    LOCAL_URL_ADD = f"http://localhost:7071/api/questionAdd?code={MetaTest.key}"
    TEST_URL_ADD = LOCAL_URL_ADD

    PUBLIC_URL_SET = None
    LOCAL_URL_SET = f"http://localhost:7071/api/questionSet?code={MetaTest.key}"
    TEST_URL_SET = LOCAL_URL_SET

    PUBLIC_URL_DEL = None
    LOCAL_URL_DEL = f"http://localhost:7071/api/questionDel?code={MetaTest.key}"
    TEST_URL_DEL = LOCAL_URL_DEL

    def testValidGet(self):
        # Add a question and update the question answer
        question_copy = self.DEFAULT_QUESTION_JSON.copy()
        question_copy['question'] = "What is the capital of Britain?"
        question_copy['correct_answer'] = 2
        question_copy['id'] = "2"

        requests.post(self.TEST_URL_ADD, data=json.dumps(question_copy))

        # Send request to get the question
        request_json = {"id": question_copy["id"]}
        response = requests.get(self.TEST_URL, data=json.dumps(request_json))

        self.assertEqual(response.json(), {'result': True, "body": {
            'id': '2',
            'author': 'bsab1g21',
            'correct_answer': 1,
            'answers': ["Paris", "London", "Madrid", "Berlin"],
            'question': "What is the capital of France?"
        }})

    def testQuestionDoesNotExist(self):
        # Delete the default question from the database to ensure it is not there before testing
        requests.delete(self.TEST_URL_DEL, data=json.dumps(self.DEFAULT_QUESTION_JSON))

        # Get the question from the database
        response = requests.get(self.TEST_URL, data=json.dumps(self.DEFAULT_QUESTION_JSON))

        # Check the correct message was received from the client
        self.assertEqual(response.json(), {'result': False, "msg": DatabaseDoesNotContainQuestionError.getMessage()})
