import json
import logging
import os

import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

try:
    # Import custom exceptions
    from helper.exceptions import CosmosHttpResponseErrorMessage
    from helper.room import RoomDoesNotExist, UserDoesNotExist, UserNotInRoom
except ModuleNotFoundError:
    # Fallback imports for different module structure
    from vpq.helper.exceptions import CosmosHttpResponseErrorMessage
    from vpq.helper.room import RoomDoesNotExist, UserDoesNotExist, UserNotInRoom

function = func.Blueprint()


@function.route(route="roomPlayerDel", auth_level=func.AuthLevel.FUNCTION, methods=["DELETE"])
def roomPlayerDel(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Set up Cosmos DB client
        cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
        database = cosmos.get_database_client(os.environ['DatabaseName'])
        roomContainer = database.get_container_client(os.environ['Container_Rooms'])

        # Parse request JSON for required data
        reqJson = req.get_json()
        adminUsername = reqJson['adminUsername']
        usernameToRemove = reqJson['usernameToRemove']

        # Query to find the room by the admin username
        query = "SELECT * FROM r WHERE r.room_admin = '{}'".format(adminUsername)
        rooms = list(roomContainer.query_items(query=query, enable_cross_partition_query=True))

        # Check if room exists
        if len(rooms) == 0:
            raise RoomDoesNotExist

        room = rooms[0]

        #check to see if admin player is removed
        if adminUsername == usernameToRemove:
            return func.HttpResponse(body=json.dumps({'result': False, "msg": "Cannot remove admin user"}),mimetype="application/json")

        # Check if user to remove is in the room
        if usernameToRemove not in room['players_in_room']:
            raise UserNotInRoom

        # Remove the user from the room's player list
        playersList = room['players_in_room']
        roomId = room['id']
        playersList.remove(usernameToRemove)

        item_to_modify= roomContainer.read_item(item=roomId, partition_key=roomId)
        item_to_modify['players_in_room'] = playersList
        roomContainer.replace_item(item=item_to_modify,body= item_to_modify)

        # Return success response
        return func.HttpResponse(body=json.dumps({'result': True, "msg": "User removed from room."}),mimetype="application/json")

    # Handle specific exceptions and return appropriate responses
    except RoomDoesNotExist:
        message = RoomDoesNotExist.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result':False, 'msg':message}), mimetype="application/json")

    except UserDoesNotExist:
        message = UserDoesNotExist.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result':False, 'msg':message}), mimetype="application/json")

    except UserNotInRoom:
        message = UserNotInRoom.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result':False, 'msg':message}), mimetype="application/json")

    except CosmosHttpResponseError as e:
        message = CosmosHttpResponseErrorMessage(e)
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")
