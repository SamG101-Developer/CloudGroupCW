import json

import azure.functions as func
import logging
import os
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from vpq.helper.player import DatabaseDoesNotContainUsernameError

function = func.Blueprint()

cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
database = cosmos.get_database_client(os.environ['DatabaseName'])
playerContainer = database.get_container_client(os.environ['Players'])


@function.route(route="playerDel", auth_level=func.AuthLevel.ANONYMOUS)
def playerDel(req: func.HttpRequest) -> func.HttpResponse:
    try:
        reqJson = req.get_json()
        logging.info('Python HTTP trigger function processed a request to delete a player. JSON: {}'.format(reqJson))

        # Check the database does contain the username
        query = "SELECT p.id, p.username FROM p where p.username='{}'".format(reqJson['username'])
        users = playerContainer.query_items(query=query, enable_cross_partition_query=True)
        if len(list(users)) == 0:
            raise DatabaseDoesNotContainUsernameError

        # Delete the player from the database
        playerContainer.delete_item(item=users[0]['id'], partition_key=users[0]['id'])

        logging.info("User Deleted Successfully")
        return func.HttpResponse(body=json.dumps({'result': True, "msg": "Success"}), mimetype="application/json")

    except DatabaseDoesNotContainUsernameError:
        logging.error("Database does not contain username.")
        return func.HttpResponse(body=json.dumps({'result': False, "msg": "Database does not contain username."}),
                                 mimetype="application/json")

    except CosmosHttpResponseError:
        logging.error("Did not complete the request due to an issue connecting to the database."
                      " Please try again later.")
        return func.HttpResponse(body=json.dumps({'result': False, "msg": "Database already contains username"}),
                                 mimetype="application/json")
