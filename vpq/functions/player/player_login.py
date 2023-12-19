import json

import azure.functions as func
import logging
import os
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

from vpq.helper.exceptions import IncorrectUsernameOrPasswordError

function = func.Blueprint()

cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
database = cosmos.get_database_client(os.environ['DatabaseName'])
playerContainer = database.get_container_client(os.environ['Container_Players'])


@function.route(route="playerLogin", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def playerLogin(req: func.HttpRequest) -> func.HttpResponse:
    try:
        reqJson = req.get_json()
        logging.info('Python HTTP trigger function processed a request to login. JSON: {}'.format(reqJson))

        # Check the database contains an entry where the username and password match
        query = "SELECT * FROM p where p.username='{0}' AND p.password='{1}'".format(reqJson['username'],
                                                                                     reqJson['password'])
        usernamePasswordMatch = len(
            list(playerContainer.query_items(query=query, enable_cross_partition_query=True))) > 0
        if not usernamePasswordMatch:
            raise IncorrectUsernameOrPasswordError

        logging.info("User Login Successful")
        return func.HttpResponse(body=json.dumps({'result': True, "msg": "Success"}), mimetype="application/json")

    except IncorrectUsernameOrPasswordError:
        message = IncorrectUsernameOrPasswordError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except CosmosHttpResponseError:
        logging.error("Did not complete the request due to an issue connecting to the database."
                      " Please try again later.")
        return func.HttpResponse(body=json.dumps({'result': False, "msg": "Did not complete the request due to an "
                                                                          "issue connecting to the database. Please "
                                                                          "try again later."}),
                                 mimetype="application/json")
