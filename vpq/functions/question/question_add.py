import json

import azure.functions as func
import logging
import os
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

from vpq.helper.exceptions import CosmosHttpResponseErrorMessage
from vpq.helper.question import Question, QuestionLengthError

function = func.Blueprint()

cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
database = cosmos.get_database_client(os.environ['DatabaseName'])
questionContainer = database.get_container_client(os.environ['Container_Questions'])


@function.route(route="questionAdd", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def questionAdd(req: func.HttpRequest) -> func.HttpResponse:
    try:
        reqJson = req.get_json()
        logging.info(f"Python HTTP trigger function processed a request to add a question: JSON: {reqJson}.")

        # Check the question is valid
        question = Question(reqJson)
        question.isQuestionValid()

        # Add the question to the database
        questionContainer.create_item(body=reqJson, enable_automatic_id_generation=True)
        logging.info("Question Added Successfully")
        return func.HttpResponse(body=json.dumps({'result': True, "msg": "Success"}), mimetype="application/json")

    except QuestionLengthError:
        message = QuestionLengthError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except CosmosHttpResponseError:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")
