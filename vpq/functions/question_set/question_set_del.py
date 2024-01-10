import json
import os
import logging

import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

try:
    from helper.exceptions import DatabaseDoesNotContainQuestionSetIDError, CosmosHttpResponseErrorMessage
except ModuleNotFoundError:
    from vpq.helper.exceptions import DatabaseDoesNotContainQuestionSetIDError, CosmosHttpResponseErrorMessage

function = func.Blueprint()


@function.route(route="questionSetDel", auth_level=func.AuthLevel.FUNCTION, methods=["DELETE"])
def questionSetDel(req: func.HttpRequest) -> func.HttpResponse:
    try:
        cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
        database = cosmos.get_database_client(os.environ['DatabaseName'])
        questionSetContainer = database.get_container_client(os.environ['Container_Questions'])

        reqJson = req.get_json()
        logging.info(f"Python HTTP trigger function processed a request to delete a question set: JSON: {reqJson}.")

        # Check the question set is in the database (ID)
        query = "SELECT q.id FROM q where q.id='{}'".format(reqJson['id'])
        questionSets = list(questionSetContainer.query_items(query=query, enable_cross_partition_query=True))
        if len(questionSets) == 0:
            raise DatabaseDoesNotContainQuestionSetIDError

        # Delete the question from the database
        questionSetContainer.delete_item(item=questionSets[0]['id'], partition_key=questionSets[0]['id'])

        logging.info("Question Deleted Successfully")
        return func.HttpResponse(body=json.dumps({'result': True, "msg": "Success"}), mimetype="application/json")

    except DatabaseDoesNotContainQuestionSetIDError:
        message = DatabaseDoesNotContainQuestionSetIDError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except CosmosHttpResponseError:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")
