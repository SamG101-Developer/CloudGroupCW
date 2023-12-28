import json
import logging
import os

import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

try:
    from helper.exceptions import DatabaseDoesNotContainUsernameError, QuestionSetNotFavouriteError, CosmosHttpResponseErrorMessage
except ModuleNotFoundError:
    from vpq.helper.exceptions import DatabaseDoesNotContainUsernameError, QuestionSetNotFavouriteError, CosmosHttpResponseErrorMessage

function = func.Blueprint()


@function.route(route="playerFaveQuizDel", auth_level=func.AuthLevel.ANONYMOUS, methods=["PUT"])
def playerFaveQuizDel(req: func.HttpRequest) -> func.HttpResponse:
    try:
        cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
        database = cosmos.get_database_client(os.environ['DatabaseName'])
        playerContainer = database.get_container_client(os.environ['Container_Players'])

        reqJson = req.get_json()
        logging.info('Python HTTP trigger function processed a request to remove a favourite quiz. JSON: {}'.format(reqJson))

        # Get the player
        query = "SELECT * FROM p where p.username='{}'".format(reqJson['username'])
        playerInfo = list(playerContainer.query_items(query=query, enable_cross_partition_query=True))
        usernameExists = len(playerInfo) == 1
        if not usernameExists:
            raise DatabaseDoesNotContainUsernameError

        # Check the question set is a favourite
        if not reqJson['quizId'] in playerInfo[0]['fave_quizzes']:
            raise QuestionSetNotFavouriteError

        # Remove the question set
        playerInfo[0]['fave_quizzes'].remove(reqJson['quizId'])
        playerContainer.replace_item(playerInfo[0]['id'], body=playerInfo[0])

        logging.info("Question set removed successfully")
        return func.HttpResponse(body=json.dumps({'result': True, "msg": "Success"}), mimetype="application/json")

    except DatabaseDoesNotContainUsernameError:
        message = DatabaseDoesNotContainUsernameError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except QuestionSetNotFavouriteError:
        message = QuestionSetNotFavouriteError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except CosmosHttpResponseError:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")
