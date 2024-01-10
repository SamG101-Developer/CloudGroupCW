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


@function.route(route="questionSetSet", auth_level=func.AuthLevel.FUNCTION, methods=["PUT"])
def questionSetSet(req: func.HttpRequest) -> func.HttpResponse:
    try:
        cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
        database = cosmos.get_database_client(os.environ['DatabaseName'])
        questionSetContainer = database.get_container_client(os.environ['Container_Questions'])

        reqJson = req.get_json()
        logging.info(f"Python HTTP trigger function processed a request to update a question set: JSON: {reqJson}.")

        # Check the question is in the database (ID)
        query = "SELECT q.id FROM q where q.id='{}'".format(reqJson['id'])
        questionSets = list(questionSetContainer.query_items(query=query, enable_cross_partition_query=True))
        if len(questionSets) == 0:
            raise DatabaseDoesNotContainQuestionSetIDError

        # For all fields passed, set the data
        for dataName in reqJson:
            if dataName in questionSets[0].keys():
                questionSets[0][dataName] = reqJson[dataName]

        # Replace the question's data
        questionSetContainer.replace_item(questionSets[0]['id'], body=questionSets[0])

        logging.info("Question set data set Successfully")
        return func.HttpResponse(body=json.dumps({'result': True, "body": questionSets[0]}), mimetype="application/json")

    except DatabaseDoesNotContainQuestionSetIDError:
        message = DatabaseDoesNotContainQuestionSetIDError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except CosmosHttpResponseError:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")
