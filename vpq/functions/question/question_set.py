import json
import os
import logging

import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

try:
    from helper.exceptions import DatabaseDoesNotContainQuestionError, CosmosHttpResponseErrorMessage
except ModuleNotFoundError:
    from vpq.helper.exceptions import DatabaseDoesNotContainQuestionError, CosmosHttpResponseErrorMessage

function = func.Blueprint()

@function.route(route="questionSet", auth_level=func.AuthLevel.FUNCTION, methods=["PUT"])
def questionSet(req: func.HttpRequest) -> func.HttpResponse:
    try:
        cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
        database = cosmos.get_database_client(os.environ['DatabaseName'])
        questionContainer = database.get_container_client(os.environ['Container_Questions'])

        reqJson = req.get_json()
        logging.info(f"Python HTTP trigger function processed a request to update a question: JSON: {reqJson}.")

        # Check the question is in the database (ID)
        query = "SELECT * FROM q where q.id='{}'".format(reqJson['id'])
        questions = list(questionContainer.query_items(query=query, enable_cross_partition_query=True))
        if len(questions) == 0:
            raise DatabaseDoesNotContainQuestionError

        # For all fields passed, set the data
        for dataName in reqJson:
            if dataName in questions[0].keys():
                questions[0][dataName] = reqJson[dataName]

        # Replace the question's data
        questionContainer.replace_item(questions[0]['id'], body=questions[0])

        logging.info("Question data set Successfully")
        return func.HttpResponse(body=json.dumps({'result': True, "body": questions[0]}), mimetype="application/json")

    except DatabaseDoesNotContainQuestionError:
        message = DatabaseDoesNotContainQuestionError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except CosmosHttpResponseError:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")
