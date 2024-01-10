import json
import logging
import os

import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

try:
    from helper.exceptions import CosmosHttpResponseErrorMessage
    from helper.room import Room, RoomDoesNotExist

except ModuleNotFoundError:
    from vpq.helper.exceptions import CosmosHttpResponseErrorMessage
    from vpq.helper.room import Room, RoomDoesNotExist

function = func.Blueprint()

@function.route(route="roomSessionDel", auth_level=func.AuthLevel.FUNCTION, methods=["DELETE"])
def roomSessionDel(req: func.HttpRequest) -> func.HttpResponse:
    try:
        logging.info("DELETE REQUEST SENT WITH {}".format(req.get_json()))
        cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
        database = cosmos.get_database_client(os.environ['DatabaseName'])
        roomContainer = database.get_container_client(os.environ['Container_Rooms'])

        reqJson = req.get_json()

        username = reqJson["username"]
        logging.info(f"Python HTTP trigger function processed a request to delete a room: Admin Username: {username}.")

        # Query to find the room by admin username (room_admin)
        query = "SELECT * FROM r where r.room_admin='{}'".format(username)
        rooms = list(roomContainer.query_items(query=query, enable_cross_partition_query=True))
        if len(rooms) == 0:
            raise RoomDoesNotExist

        # Get the players currently in the room
        players = rooms[0]['players_in_room']

        # Retrieve room ID and delete the room
        roomID = rooms[0]['id']
        roomContainer.delete_item(item=roomID, partition_key=roomID)
        logging.info(f"Room with admin username {username} deleted successfully.")
        return func.HttpResponse(body=json.dumps({'result': True, 'msg': f'Room with admin username {username} deleted successfully', "players": players}), mimetype="application/json")

    except RoomDoesNotExist:
        message = RoomDoesNotExist.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, 'msg': message}), mimetype="application/json")

    except CosmosHttpResponseError:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except Exception as e:
        message = str(e)
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")
