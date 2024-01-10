import json

import logging
import os

import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

try:
    from helper.exceptions import DatabaseDoesNotContainUsernameError, DatabaseDoesNotContainQuestionSetIDError, \
    CosmosHttpResponseErrorMessage
except ModuleNotFoundError:
    from vpq.helper.exceptions import DatabaseDoesNotContainUsernameError, DatabaseDoesNotContainQuestionSetIDError, \
    CosmosHttpResponseErrorMessage

function = func.Blueprint()


@function.route(route="playerFaveQuizAdd", auth_level=func.AuthLevel.FUNCTION, methods=["PUT"])
def playerFaveQuizAdd(req: func.HttpRequest) -> func.HttpResponse:
    try:
        cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
        database = cosmos.get_database_client(os.environ['DatabaseName'])
        playerContainer = database.get_container_client(os.environ['Container_Players'])
        questionSetContainer = database.get_container_client(os.environ['Container_QuestionSets'])

        reqJson = req.get_json()
        logging.info(
            'Python HTTP trigger function processed a request to remove a favourite quiz. JSON: {}'.format(reqJson))

        # Get the player
        query = "SELECT * FROM p where p.username='{}'".format(reqJson['username'])
        playerInfo = list(playerContainer.query_items(query=query, enable_cross_partition_query=True))
        usernameExists = len(playerInfo) == 1
        if not usernameExists:
            raise DatabaseDoesNotContainUsernameError

        # Check the question set is not already a favourite
        if reqJson['quizId'] in playerInfo[0]['fave_quizzes']:
            return func.HttpResponse(body=json.dumps({'result': True, "msg": "Success"}), mimetype="application/json")

        # Check the question set exists
        query = "SELECT * FROM p where p.id='{}'".format(reqJson['quizId'])
        questionSetExists = len(list(questionSetContainer.query_items(query=query, enable_cross_partition_query=True))) == 1
        if not questionSetExists:
            raise DatabaseDoesNotContainQuestionSetIDError

        # Add the question set
        playerInfo[0]['fave_quizzes'].append(reqJson['quizId'])
        playerContainer.replace_item(playerInfo[0]['id'], body=playerInfo[0])

        logging.info("Question Set added successfully")
        return func.HttpResponse(body=json.dumps({'result': True, "msg": "Success"}), mimetype="application/json")

    except DatabaseDoesNotContainUsernameError:
        message = DatabaseDoesNotContainUsernameError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except DatabaseDoesNotContainQuestionSetIDError:
        message = DatabaseDoesNotContainQuestionSetIDError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except CosmosHttpResponseError:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")
