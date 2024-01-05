import json
import logging
import os

import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

try:
    from helper.exceptions import CosmosHttpResponseErrorMessage, RoomDoesNotExist
except ModuleNotFoundError:
    from vpq.helper.exceptions import CosmosHttpResponseErrorMessage, RoomDoesNotExist

function = func.Blueprint()

@function.route(route="roomSessionDel", auth_level=func.AuthLevel.ANONYMOUS, methods=["DELETE"])
def roomSessionDel(req: func.HttpRequest) -> func.HttpResponse:
    try:
        cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
        database = cosmos.get_database_client(os.environ['DatabaseName'])
        roomContainer = database.get_container_client(os.environ['Container_Rooms'])

        reqJson = req.get_json()
        adminUsername = reqJson["adminUsername"]
        logging.info(f"Python HTTP trigger function processed a request to delete a room: Admin Username: {adminUsername}.")

        # Query to find the room by admin username
        query = "SELECT r.id FROM r WHERE r.room_admin='{}'".format(adminUsername)
        rooms = list(roomContainer.query_items(query=query, enable_cross_partition_query=True))
        if len(rooms) == 0:
            raise RoomDoesNotExist

        # Retrieve room ID and delete the room
        roomID = rooms[0]['id']
        roomContainer.delete_item(item=roomID, partition_key=roomID)
        logging.info(f"Room with ID {roomID} deleted successfully.")
        return func.HttpResponse(body=json.dumps({'result': True, 'msg': f'Room with ID {roomID} deleted successfully'}), mimetype="application/json")

    except RoomDoesNotExist:
        message = RoomDoesNotExist.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, 'msg': message}), mimetype="application/json")

    except CosmosHttpResponseError:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")
