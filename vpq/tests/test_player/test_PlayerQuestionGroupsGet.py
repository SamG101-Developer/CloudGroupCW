import unittest
import requests
import json

from vpq.tests.MetaTest import MetaTest


class TestPlayerInfoGet(unittest.TestCase, MetaTest):
    PUBLIC_URL = None
    LOCAL_URL = "http://localhost:7071/api/playerQuestionGroupsGet?code={}".format(MetaTest.key)
    TEST_URL = LOCAL_URL
    
    PUBLIC_URL_ADD = None
    LOCAL_URL_ADD = "http://localhost:7071/api/playerAdd?code={}".format(MetaTest.key)
    TEST_URL_ADD = LOCAL_URL_ADD
    
    PUBLIC_URL_DEL = None
    LOCAL_URL_DEL = "http://localhost:7071/api/playerDel?code={}".format(MetaTest.key)
    TEST_URL_DEL = LOCAL_URL_DEL

    def testUserAndQuestionsExist(self):
        # Add a user
        requests.post(self.TEST_URL_ADD, data=json.dumps(self.DEFAULT_PLAYER_JSON))

        # Send request for player questions
        response = requests.get(self.TEST_URL, data=json.dumps(self.DEFAULT_PLAYER_JSON))

        self.assertEqual(response.json(), {'result': True, "body": [{'id': 'replace_with_new_document_id'}]})

    def testUserNoQuestions(self):
        # Add a user
        player_copy = self.DEFAULT_PLAYER_JSON.copy()
        player_copy['username'] += "_3"
        requests.post(self.TEST_URL_ADD, data=json.dumps(player_copy))

        # Send request for player questions
        response = requests.get(self.TEST_URL, data=json.dumps(player_copy))

        self.assertEqual(response.json(), {'result': True, "body": []})
