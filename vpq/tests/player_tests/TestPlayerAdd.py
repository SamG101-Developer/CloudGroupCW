import unittest
import requests
import json
from azure.cosmos import CosmosClient


class TestPlayerAdd(unittest.TestCase):
    # extend os.environ from local.settings.json
    import os
    local_settings_json = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'local.settings.json')
    if os.path.exists(local_settings_json):
        import json
        with open(local_settings_json) as f:
            settings = json.load(f)
        os.environ.update(settings['Values'])


    key = os.environ["FunctionAppKey"]
    PUBLIC_URL = None
    LOCAL_URL = "http://localhost:7071/api/playerAdd?code={}".format(key)
    TEST_URL = LOCAL_URL
    cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
    database = cosmos.get_database_client(os.environ['DatabaseName'])
    playerContainer = database.get_container_client(os.environ['Container_Players'])
    defaultPlayerJson = {
            'playerId': 0,
            'username': "bsab1g21",
            'password': "myTestPassword",
            'firstName': "Ben",
            'lastName': "Burbridge",
            'dob': "06/02/2003",
            'freeCurrency': 0,
            'premiumCurrency': 0,
            'totalScore': 0,
            'friends': [],
            'favQuizzes': []
          }

    def testValidPlayerAdd(self):
        # If the default player already exists, delete it
        query = "SELECT * FROM p where p.username='{}'".format(self.defaultPlayerJson['username'])
        usernameExists = len(
            list(self.playerContainer.query_items(query=query, enable_cross_partition_query=True))) != 0
        if usernameExists:
            self.playerContainer.delete_item(item=self.defaultPlayerJson['id'], partition_key=self.defaultPlayerJson['id'])

        # Add the player to the database
        response = requests.post(self.TEST_URL, data=json.dumps(self.defaultPlayerJson))

        # Check the player was successfully added
        usernameExists = len(
            list(self.playerContainer.query_items(query=query, enable_cross_partition_query=True))) == 1
        self.assertEqual(usernameExists, True)
        self.assertEqual(response.json(), {'result': True, "msg": "Success"})

