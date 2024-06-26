import json, logging, os

import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

try:
    from helper.exceptions import CosmosHttpResponseErrorMessage
except ModuleNotFoundError:
    from vpq.helper.exceptions import CosmosHttpResponseErrorMessage

function = func.Blueprint()


@function.route(route="roomInfoGet", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
def roomInfoGet(req: func.HttpRequest) -> func.HttpResponse:
    try:
        cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
        database = cosmos.get_database_client(os.environ['DatabaseName'])
        roomContainer = database.get_container_client(os.environ['Container_Rooms'])

        # Get the request
        reqJson = req.get_json()
        logging.info('Python HTTP trigger function processed a request to get room info. JSON: {}'.format(reqJson))

        # Get all players
        query = f"SELECT p.players_in_room, p.question_set_id FROM p WHERE p.room_admin = '{reqJson['adminUsername']}'"
        logging.error(query)
        info = list(roomContainer.query_items(query=query, enable_cross_partition_query=True))[0]

        question_set_id = info["question_set_id"]
        players = info["players_in_room"] if info else []

        # Return the response
        logging.info("Room players retrieved Successfully")
        return func.HttpResponse(body=json.dumps({'result': True, "msg": "Success", "players": players, "question_set_id": question_set_id}), mimetype="application/json")

    except CosmosHttpResponseError as e:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message + " " + str(e) + "!")
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json", status_code=500)

    except Exception as e:
        message = str(e)
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json", status_code=500)
