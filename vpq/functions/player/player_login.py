import json

import azure.functions as func
import logging
import os
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from vpq.helper.player import Player, UsernameLengthError, PasswordLengthError, DatabaseContainsUsernameError

function = func.Blueprint()

cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
database = cosmos.get_database_client(os.environ['DatabaseName'])
playerContainer = database.get_container_client(os.environ['Players'])


@function.route(route="playerLogin", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def playerLogin(req: func.HttpRequest) -> func.HttpResponse:
    pass
