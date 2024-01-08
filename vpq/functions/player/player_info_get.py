import json
import logging
import os

import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

try:
    from helper.exceptions import DatabaseDoesNotContainUsernameError, CosmosHttpResponseErrorMessage
except ModuleNotFoundError:
    from vpq.helper.exceptions import DatabaseDoesNotContainUsernameError, CosmosHttpResponseErrorMessage

function = func.Blueprint()


@function.route(route="playerInfoGet", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def playerInfoGet(req: func.HttpRequest) -> func.HttpResponse:
    try:
        cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
        database = cosmos.get_database_client(os.environ['DatabaseName'])
        playerContainer = database.get_container_client(os.environ['Container_Players'])

        reqJson = req.get_json()
        logging.info('Python HTTP trigger function processed a request to retrieve player info. JSON: {}'.format(reqJson))

        # Check the database does contain the username
        query = ("SELECT p.username, p.currency, p.premium_currency, p.overall_score, p.friends, p.fave_quizzes"
                 " FROM p where p.username='{}'").format(reqJson['username'])
        users = list(playerContainer.query_items(query=query, enable_cross_partition_query=True))
        if len(users) == 0:
            raise DatabaseDoesNotContainUsernameError

        # Send the user data to the client
        logging.info("User data retrieved")
        return func.HttpResponse(body=json.dumps({'result': True, "body": users[0]}), mimetype="application/json")

    except DatabaseDoesNotContainUsernameError:
        message = DatabaseDoesNotContainUsernameError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except CosmosHttpResponseError:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")
