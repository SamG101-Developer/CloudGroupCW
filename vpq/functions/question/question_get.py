import json
import os
import logging

import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

from vpq.helper.exceptions import DatabaseDoesNotContainQuestionError, CosmosHttpResponseErrorMessage

function = func.Blueprint()
cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
database = cosmos.get_database_client(os.environ['DatabaseName'])
questionContainer = database.get_container_client(os.environ['Container_Questions'])


@function.route(route="questionGet", auth_level=func.AuthLevel.ANONYMOUS)
def questionGet(req: func.HttpRequest) -> func.HttpResponse:
    try:
        reqJson = req.get_json()
        logging.info(f"Python HTTP trigger function processed a request to get a question's info: JSON: {reqJson}.")

        query = "SELECT p.author, p.question_text, p.all_options, p.correct_option FROM p where p.id='{}'".format(reqJson['id'])
        users = list(questionContainer.query_items(query=query, enable_cross_partition_query=True))
        if len(users) == 0:
            raise DatabaseDoesNotContainQuestionError

        # Send the question data to the client
        logging.info("Question data retrieved")
        return func.HttpResponse(body=json.dumps({'result': True, "body": users[0]}), mimetype="application/json")

    except DatabaseDoesNotContainQuestionError:
        message = DatabaseDoesNotContainQuestionError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except CosmosHttpResponseError:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")
