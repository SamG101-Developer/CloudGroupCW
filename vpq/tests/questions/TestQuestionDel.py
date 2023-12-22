import json
import unittest

import requests

from vpq.tests.MetaTest import MetaTest
from vpq.helper.exceptions import DatabaseDoesNotContainQuestionError


class TestQuestionDel(unittest.TestCase, MetaTest):
    PUBLIC_URL = None
    LOCAL_URL = f"http://localhost:7071/api/questionDel?code={MetaTest.key}"
    TEST_URL = LOCAL_URL

    def testQuestionDelete(self):
        # Add the question to the database
        requests.post(self.TEST_URL, data=json.dumps(self.DEFAULT_QUESTION_JSON))

        # Try deleting the question
        response = requests.delete(self.TEST_URL, data=json.dumps(self.DEFAULT_QUESTION_JSON))

        # Check the question was successfully deleted
        query = "SELECT * FROM p where p.id='{}'".format(self.DEFAULT_QUESTION_JSON['id'])
        questionExists = len(list(self.questionContainer.query_items(query=query, enable_cross_partition_query=True))) == 1

        self.assertEqual(questionExists, False)
        self.assertEqual(response.json(), {'result': True, "msg": "Success"})

    def testQuestionDoesNotExist(self):
        # Delete the default question from the database to ensure it is not there before testing
        requests.delete(self.TEST_URL, data=json.dumps(self.DEFAULT_QUESTION_JSON))

        # Delete the question from the database
        response = requests.delete(self.TEST_URL, data=json.dumps(self.DEFAULT_QUESTION_JSON))

        # Check the correct message was received from the client
        self.assertEqual(response.json(), {'result': False, "msg": DatabaseDoesNotContainQuestionError.getMessage()})
