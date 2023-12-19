import json

import azure.functions as func
import logging
import os
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from vpq.helper.exceptions import DatabaseDoesNotContainUsernameError

function = func.Blueprint()

cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
database = cosmos.get_database_client(os.environ['DatabaseName'])
playerContainer = database.get_container_client(os.environ['Container_Players'])

@function.route(route="playerInfoSet", auth_level=func.AuthLevel.ANONYMOUS)
def playerInfoSet(req: func.HttpRequest) -> func.HttpResponse:
    try:
        reqJson = req.get_json()
        logging.info(
            'Python HTTP trigger function processed a request to set player info. JSON: {}'.format(reqJson))

        # Check the database does contain the username
        query = ("SELECT p.username, p.currency, p.premium_currency, p.overall_score, p.friends, p.fave_quizzes"
                 " FROM p where p.username='{}'").format(reqJson['username'])
        users = playerContainer.query_items(query=query, enable_cross_partition_query=True)
        if len(list(users)) == 0:
            raise DatabaseDoesNotContainUsernameError

        # For all fields passed, set the data
        for dataName, dataValue in reqJson:
            if dataName in users[0].keys():
                users[0][dataName] = dataValue

        # Replace the user's data
        playerContainer.replace_item(users[0]['id'], body=users[0])

        logging.info("User data set Successfully")
        return func.HttpResponse(body=json.dumps({'result': True, "body": users[0]}), mimetype="application/json")

    except DatabaseDoesNotContainUsernameError:
        message = DatabaseDoesNotContainUsernameError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except CosmosHttpResponseError:
        logging.error("Did not complete the request due to an issue connecting to the database."
                      " Please try again later.")
        return func.HttpResponse(body=json.dumps({'result': False, "msg": "Did not complete the request due to an "
                                                                          "issue connecting to the database. Please "
                                                                          "try again later."}),
                                 mimetype="application/json")