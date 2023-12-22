import json
import unittest

import requests

from vpq.tests.MetaTest import MetaTest


class TestQuestionAdd(unittest.TestCase, MetaTest):
    PUBLIC_URL = None
    LOCAL_URL = f"http://localhost:7071/api/questionAdd?code={MetaTest.key}"
    TEST_URL = LOCAL_URL
    
    def testValidQuestionAdd(self):
        # If the default question already exists, delete it
        query = "SELECT * FROM p where p.id='{}'".format(self.DEFAULT_QUESTION_JSON['id'])
        questions = list(self.questionContainer.query_items(query=query, enable_cross_partition_query=True))
        if len(questions) != 0:
            self.questionContainer.delete_item(item=questions[0]['id'], partition_key=questions[0]['id'])
            
        # Add the question to the database
        response = requests.post(self.TEST_URL, data=json.dumps(self.DEFAULT_QUESTION_JSON))
        
        # Check the question was successfully added
        questionExists = len(list(self.questionContainer.query_items(query=query, enable_cross_partition_query=True))) == 1
        self.assertEqual(questionExists, True)
        self.assertEqual(response.json(), {"result": True, "msg": "Success"})

    def testQuestionTooLong(self):
        # Create a question that is too long
        badQuestion = self.DEFAULT_QUESTION_JSON.copy()
        badQuestion["question"] = "a" * 256
        
        # Attempt to add the question to the database
        response = requests.post(self.TEST_URL, data=json.dumps(badQuestion))
        
        # Check the correct message was received from the client
        self.assertEqual(response.json(), {"result": False, "msg": "Question length invalid."})
        
    def testQuestionTooShort(self):
        # Create a question that is too short
        badQuestion = self.DEFAULT_QUESTION_JSON.copy()
        badQuestion["question"] = ""
        
        # Attempt to add the question to the database
        response = requests.post(self.TEST_URL, data=json.dumps(badQuestion))
        
        # Check the correct message was received from the client
        self.assertEqual(response.json(), {"result": False, "msg": "Question length invalid."})

    def testQuestionInvalidAuthor(self):
        # Create a question with an invalid author
        badQuestion = self.DEFAULT_QUESTION_JSON.copy()
        badQuestion["author"] = ""

        # Attempt to add the question to the database
        response = requests.post(self.TEST_URL, data=json.dumps(badQuestion))

        # Check the correct message was received from the client
        self.assertEqual(response.json(), {"result": False, "msg": "Author length invalid."})
