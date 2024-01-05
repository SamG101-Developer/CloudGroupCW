import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

import json, logging, os


try:
    from helper.player import Player, UsernameLengthError, PasswordLengthError
    from helper.exceptions import DatabaseContainsUsernameError, CosmosHttpResponseErrorMessage
except ModuleNotFoundError:
    from vpq.helper.player import Player, UsernameLengthError, PasswordLengthError
    from vpq.helper.exceptions import DatabaseContainsUsernameError, CosmosHttpResponseErrorMessage

function = func.Blueprint("playerGetAll")

@function.function_name("playerGetAll")
@function.route(route="playerGetAll", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
def playerGetAll(req: func.HttpRequest) -> func.HttpResponse:
    try:
        cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
        database = cosmos.get_database_client(os.environ['DatabaseName'])
        playerContainer = database.get_container_client(os.environ['Container_Players'])

        # Get the request
        logging.info('Python HTTP trigger function processed a request to get all players.')

        # Query all players
        query = "SELECT * FROM p"
        players = list(playerContainer.query_items(query=query, enable_cross_partition_query=True))

        # Return the response
        logging.info("Got all players.")
        return func.HttpResponse(body=json.dumps({'result': True, "body": players}), mimetype="application/json")

    except CosmosHttpResponseError:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")
