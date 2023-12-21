import json

import azure.functions as func
import logging
import os
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

from vpq.helper.exceptions import CosmosHttpResponseErrorMessage

function = func.Blueprint()

cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
database = cosmos.get_database_client(os.environ['DatabaseName'])
questionContainer = database.get_container_client(os.environ['Container_Questions'])


@function.route(route="playerQuestionGroupsGet", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def playerQuestionGroupsGet(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    try:
        reqJson = req.get_json()
        logging.info('Python HTTP trigger function processed a request to retrieve player info. JSON: {}'.format(reqJson))

        # Check the database does contain the username
        query = "SELECT p.id FROM p where p.author='{}'".format(reqJson['username'])
        questions = list(questionContainer.query_items(query=query, enable_cross_partition_query=True))

        # Send the questionIds to the client
        logging.info("User data retrieved")
        return func.HttpResponse(body=json.dumps({'result': True, "body": questions}), mimetype="application/json")

    except CosmosHttpResponseError:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")
