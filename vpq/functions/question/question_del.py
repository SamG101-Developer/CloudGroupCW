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


@function.route(route="questionDel", auth_level=func.AuthLevel.ANONYMOUS, methods=["DELETE"])
def questionDel(req: func.HttpRequest) -> func.HttpResponse:
    try:
        cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
        database = cosmos.get_database_client(os.environ['DatabaseName'])
        questionContainer = database.get_container_client(os.environ['Container_Questions'])

        reqJson = req.get_json()
        logging.info(f"Python HTTP trigger function processed a request to delete a question: JSON: {reqJson}.")

        # Check the question is in the database (ID)
        query = "SELECT q.id FROM q where q.id='{}'".format(reqJson['id'])
        questions = list(questionContainer.query_items(query=query, enable_cross_partition_query=True))
        if len(questions) == 0:
            raise DatabaseDoesNotContainQuestionError

        # Delete the question from the database
        questionContainer.delete_item(item=questions[0]['id'], partition_key=questions[0]['id'])

        logging.info("Question Deleted Successfully")
        return func.HttpResponse(body=json.dumps({'result': True, "msg": "Success"}), mimetype="application/json")

    except DatabaseDoesNotContainQuestionError:
        message = DatabaseDoesNotContainQuestionError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except CosmosHttpResponseError:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")
