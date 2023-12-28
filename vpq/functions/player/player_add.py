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

function = func.Blueprint("playerAdd")

@function.function_name("playerAdd")
@function.route(route="playerAdd", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
def playerAdd(req: func.HttpRequest) -> func.HttpResponse:
    try:
        cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
        database = cosmos.get_database_client(os.environ['DatabaseName'])
        playerContainer = database.get_container_client(os.environ['Container_Players'])

        # Get the request
        reqJson = req.get_json()
        logging.info('Python HTTP trigger function processed a request to add a player. JSON: {}'.format(reqJson))

        # Check the username and password are valid
        player = Player(reqJson)
        player.isUsernameValid()
        player.isPasswordValid()

        # Check the database does NOT contain the username
        query = "SELECT * FROM p where p.username='{}'".format(reqJson['username'])
        usernameExists = len(list(playerContainer.query_items(query=query, enable_cross_partition_query=True))) != 0
        if usernameExists:
            raise DatabaseContainsUsernameError

        # Add the player to the database
        playerContainer.create_item(body=reqJson, enable_automatic_id_generation=True)

        # Return the response
        logging.info("User Added Successfully")
        return func.HttpResponse(body=json.dumps({'result': True, "msg": "Success"}), mimetype="application/json")

    except UsernameLengthError:
        message = UsernameLengthError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except PasswordLengthError:
        message = PasswordLengthError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except DatabaseContainsUsernameError:
        message = DatabaseContainsUsernameError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except CosmosHttpResponseError:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")
