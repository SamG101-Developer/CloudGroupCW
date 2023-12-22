import json
import os

import azure.functions as func
import logging

from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

from vpq.helper.exceptions import CosmosHttpResponseErrorMessage, DatabaseDoesNotContainUsernameError
from vpq.helper.question_set import QuestionSet, QuestionSetQuestionsFormatError

function = func.Blueprint()


cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
database = cosmos.get_database_client(os.environ['DatabaseName'])
questionSetContainer = database.get_container_client(os.environ['Container_Questions'])
playerContainer = database.get_container_client(os.environ['Container_Players'])


@function.route(route="questionSetAdd", auth_level=func.AuthLevel.ANONYMOUS)
def questionSetAdd(req: func.HttpRequest) -> func.HttpResponse:
    try:
        reqJson = req.get_json()
        logging.info(f"Python HTTP trigger function processed a request to add a question set: JSON: {reqJson}.")

        # Check the question set is valid
        questionSet = QuestionSet(reqJson)
        questionSet.isQuestionsValid()

        # Check the author is valid
        author_query = "SELECT p.username FROM p where p.username='{}'".format(reqJson['author'])
        authors = list(playerContainer.query_items(query=author_query, enable_cross_partition_query=True))
        if len(authors) == 0:
            raise DatabaseDoesNotContainUsernameError

        # Add the question to the database
        questionSetContainer.create_item(body=reqJson, enable_automatic_id_generation=True)
        logging.info("Question Set Added Successfully")
        return func.HttpResponse(body=json.dumps({'result': True, "msg": "Success"}), mimetype="application/json")

    except DatabaseDoesNotContainUsernameError:
        message = DatabaseDoesNotContainUsernameError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except QuestionSetQuestionsFormatError:
        message = QuestionSetQuestionsFormatError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except CosmosHttpResponseError:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")
