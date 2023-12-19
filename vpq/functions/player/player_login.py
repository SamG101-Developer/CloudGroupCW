import json

import azure.functions as func
import logging
import os
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
from vpq.helper.player import Player, UsernameLengthError, PasswordLengthError, DatabaseContainsUsernameError

function = func.Blueprint()

cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
database = cosmos.get_database_client(os.environ['DatabaseName'])
playerContainer = database.get_container_client(os.environ['Players'])


@function.route(route="playerLogin", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def playerLogin(req: func.HttpRequest) -> func.HttpResponse:
    try:
        reqJson = req.get_json()
        logging.info('Python HTTP trigger function processed a request to login. JSON: {}'.format(reqJson))

        # Check the database contains an entry where the username and password match
        query = "SELECT * FROM p where p.username='{0}' AND p.password='{1}'".format(reqJson['username'],
                                                                                     reqJson['password'])
        usernamePasswordMatch = len(list(playerContainer.query_items(query=query, enable_cross_partition_query=True))) > 0
        if not usernamePasswordMatch:
            raise DatabaseContainsUsernameError

        # Add the player to the database
        playerContainer.create_item(body=reqJson, enable_automatic_id_generation=True)

        logging.info("User Added Successfully")
        return func.HttpResponse(body=json.dumps({'result': True, "msg": "Success"}), mimetype="application/json")

    except UsernameLengthError:
        logging.error("Username length invalid.")
        return func.HttpResponse(body=json.dumps({'result': False, "msg": "Username length invalid"}),
                                 mimetype="application/json")

    except PasswordLengthError:
        logging.error("Password length invalid.")
        return func.HttpResponse(body=json.dumps({'result': False, "msg": "Password length invalid"}),
                                 mimetype="application/json")

    except DatabaseContainsUsernameError:
        logging.error("Database already contains username.")
        return func.HttpResponse(body=json.dumps({'result': False, "msg": "Database already contains username"}),
                                 mimetype="application/json")

    except CosmosHttpResponseError:
        logging.error("Did not complete the request due to an issue connecting to the database."
                      " Please try again later.")
        return func.HttpResponse(body=json.dumps({'result': False, "msg": "Database already contains username"}),
                                 mimetype="application/json")
