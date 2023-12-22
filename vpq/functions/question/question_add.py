import json
import logging
import os

import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

from vpq.helper.exceptions import CosmosHttpResponseErrorMessage, DatabaseDoesNotContainUsernameError
from vpq.helper.question import Question, QuestionLengthError

function = func.Blueprint()
cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
database = cosmos.get_database_client(os.environ['DatabaseName'])
playerContainer = database.get_container_client(os.environ['Container_Players'])
questionContainer = database.get_container_client(os.environ['Container_Questions'])


@function.route(route="questionAdd", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def questionAdd(req: func.HttpRequest) -> func.HttpResponse:
    try:
        reqJson = req.get_json()
        logging.info(f"Python HTTP trigger function processed a request to add a question: JSON: {reqJson}.")

        # Check the question is valid
        question = Question(reqJson)
        question.isQuestionValid()

        # Check the author exists
        author_query = "SELECT p.username FROM p where p.username='{}'".format(reqJson['author'])
        authors = list(playerContainer.query_items(query=author_query, enable_cross_partition_query=True))
        if len(authors) == 0:
            raise DatabaseDoesNotContainUsernameError

        # Add the question to the database
        questionContainer.create_item(body=reqJson, enable_automatic_id_generation=True)
        logging.info("Question Added Successfully")
        return func.HttpResponse(body=json.dumps({'result': True, "msg": "Success"}), mimetype="application/json")

    except QuestionLengthError:
        message = QuestionLengthError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except DatabaseDoesNotContainUsernameError:
        message = DatabaseDoesNotContainUsernameError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except CosmosHttpResponseError:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")
