import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

import json, logging, os


try:
    from helper.exceptions import CosmosHttpResponseErrorMessage
except ModuleNotFoundError:
    from vpq.helper.exceptions import DatabaseContainsUsernameError, CosmosHttpResponseErrorMessage

function = func.Blueprint()


@function.route(route="roomAllGet", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
def roomAllGet(req: func.HttpRequest) -> func.HttpResponse:
    try:
        cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
        database = cosmos.get_database_client(os.environ['DatabaseName'])
        roomContainer = database.get_container_client(os.environ['Container_Rooms'])

        # Get the request
        reqJson = req.get_json()
        logging.info('Python HTTP trigger function processed a request to get all rooms. JSON: {}'.format(reqJson))

        # Get all rooms
        query = "SELECT p.room_admin, p.adult_only FROM p"
        rooms = list(roomContainer.query_items(query=query, enable_cross_partition_query=True))
        formattedRooms = []
        for room in rooms:
            formattedRooms.append({"adminUsername": room['room_admin'], "adultOnly": room['adult_only']})

        # Return the response
        logging.info("Rooms Retrieved Successfully")
        return func.HttpResponse(body=json.dumps({'result': True, "msg": "Success", "rooms": formattedRooms}), mimetype="application/json")

    except CosmosHttpResponseError as e:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message + " " + str(e))
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except Exception as e:
        message = str(e)
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")
