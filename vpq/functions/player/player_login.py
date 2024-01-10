import json
import logging
import os

import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

try:
    from helper.exceptions import IncorrectUsernameOrPasswordError, CosmosHttpResponseErrorMessage
except ModuleNotFoundError:
    from vpq.helper.exceptions import IncorrectUsernameOrPasswordError, CosmosHttpResponseErrorMessage


function = func.Blueprint()


@function.route(route="playerLogin", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
def playerLogin(req: func.HttpRequest) -> func.HttpResponse:
    try:
        cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
        database = cosmos.get_database_client(os.environ['DatabaseName'])
        playerContainer = database.get_container_client(os.environ['Container_Players'])

        reqJson = req.get_json()
        logging.info('Python HTTP trigger function processed a request to login. JSON: {}'.format(reqJson))

        # Check the database contains an entry where the username and password match
        query = "SELECT * FROM p where p.username='{0}' AND p.password='{1}'".format(reqJson['username'],
                                                                                     reqJson['password'])
        usernamePasswordMatch = len(
            list(playerContainer.query_items(query=query, enable_cross_partition_query=True))) > 0
        if not usernamePasswordMatch:
            raise IncorrectUsernameOrPasswordError

        logging.info(f"User Login Successful ({reqJson['username']})")
        return func.HttpResponse(body=json.dumps({'result': True, "msg": "Success"}), mimetype="application/json")

    except IncorrectUsernameOrPasswordError:
        message = IncorrectUsernameOrPasswordError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except CosmosHttpResponseError:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except Exception as e:
        message = str(e)
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")
