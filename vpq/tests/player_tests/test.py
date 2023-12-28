import os
import unittest
import requests
import json
from azure.cosmos.exceptions import CosmosHttpResponseError, CosmosResourceExistsError, CosmosResourceNotFoundError
from azure.cosmos import CosmosClient


class TestPlayerLoginFunction(unittest.TestCase):
    key = "yqIylz7jqEUIYHkdB2PFWig4f4EdEbWD-OID8xLVcpI8AzFuW2OuXg=="
    PUBLIC_URL = "https://quiplash-bsab1g21.azurewebsites.net/player/login?code={0}".format(key)
    PUBLIC_URL_REGISTER = "https://quiplash-bsab1g21.azurewebsites.net/player/register?code={0}".format(key)
    TEST_URL = PUBLIC_URL
    MyCosmos = CosmosClient.from_connection_string(
        'AccountEndpoint=https://treehuggers-bsab1g21-2324-db.documents.azure.com:443/;AccountKey=SbOBSRC3HbFbJoyhLfKeJxvLVgyYTyBMpqM4qW1INdRLZADaEYX3GE8Bdd46EYAXzz0IPlS0gCmaACDblpEszg==;')
    QuiplashDBProxy = MyCosmos.get_database_client('quiplash')
    PlayerContainerProxy = QuiplashDBProxy.get_container_client('player')

    def test_valid_login(self):
        for item in list(self.PlayerContainerProxy.read_all_items()):
            self.PlayerContainerProxy.delete_item(item=item, partition_key=item['id'])

        # registering a player
        username = "bsab1g21"
        password = "test_password"
        player = {"username": username, "password": password}
        requests.post(self.PUBLIC_URL_REGISTER, data=json.dumps(player)).json()

        username = "bsab1g21"
        password = "test_password"
        player_login = {"username": username, "password": password}
        response_json = requests.get(self.TEST_URL, data=json.dumps(player_login)).json()
        # test that the response is correct for a valid login
        self.assertEqual(response_json, {"result": True, "msg": "OK"})

    def test_invalid_username(self):
        for item in list(self.PlayerContainerProxy.read_all_items()):
            self.PlayerContainerProxy.delete_item(item=item, partition_key=item['id'])

        # registering a player
        username = "bsab1g21"
        password = "test_password"
        player = {"username": username, "password": password}
        requests.post(self.PUBLIC_URL_REGISTER, data=json.dumps(player)).json()

        username = "bsab1g211"
        password = "test_password"
        player_login = {"username": username, "password": password}
        response_json = requests.get(self.TEST_URL, data=json.dumps(player_login)).json()
        # test that the response is correct for a invalid login
        self.assertEqual(response_json, {"result": False, "msg": "Username or password incorrect"})

    def test_invalid_password(self):
        for item in list(self.PlayerContainerProxy.read_all_items()):
            self.PlayerContainerProxy.delete_item(item=item, partition_key=item['id'])
        # registering a player
        username = "bsab1g21"
        password = "test_password"
        player = {"username": username, "password": password}
        requests.post(self.PUBLIC_URL_REGISTER, data=json.dumps(player)).json()

        username = "bsab1g21"
        password = "test_passwords"
        player_login = {"username": username, "password": password}
        response_json = requests.get(self.TEST_URL, data=json.dumps(player_login)).json()
        # test that the response is correct for a invalid login
        self.assertEqual(response_json, {"result": False, "msg": "Username or password incorrect"})

    def test_invalid_password_username(self):
        for item in list(self.PlayerContainerProxy.read_all_items()):
            self.PlayerContainerProxy.delete_item(item=item, partition_key=item['id'])
        # registering a player
        username = "bsab1g21"
        password = "test_password"
        player = {"username": username, "password": password}
        requests.post(self.PUBLIC_URL_REGISTER, data=json.dumps(player)).json()

        username = "bsab1g211"
        password = "test_passwords"
        player_login = {"username": username, "password": password}
        response_json = requests.get(self.TEST_URL, data=json.dumps(player_login)).json()
        # test that the response is correct for a invalid login
        self.assertEqual(response_json, {"result": False, "msg": "Username or password incorrect"})
