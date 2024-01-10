import logging
import json
import os

import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

try:
    from helper.exceptions import CosmosHttpResponseErrorMessage, DatabaseDoesNotContainUsernameError
    from helper.room import Room,UserDoesNotExist,UserInRoomAlready,RoomDoesNotExist

except ModuleNotFoundError:
    from vpq.helper.exceptions import CosmosHttpResponseErrorMessage,DatabaseDoesNotContainUsernameError
    from vpq.helper.room import Room,UserDoesNotExist,UserInRoomAlready,RoomDoesNotExist

function = func.Blueprint()


@function.route(route="roomPlayerAdd", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
def roomPlayerAdd(req: func.HttpRequest) -> func.HttpResponse:
    try:
        cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
        database = cosmos.get_database_client(os.environ['DatabaseName'])
        playerContainer = database.get_container_client(os.environ['Container_Players'])
        questionContainer = database.get_container_client(os.environ['Container_Questions'])
        roomContainer = database.get_container_client(os.environ['Container_Rooms'])

        reqJson = req.get_json()
        adminUsername = reqJson['adminUsername']
        usernameToAdd = reqJson['usernameToAdd']

        # Check both players exist in players database
        adminUsernameQuery = "SELECT * FROM r where r.username='{}'".format(adminUsername)
        usernameToAddQuery = "SELECT * FROM r where r.username='{}'".format(usernameToAdd)
        adminUsernameCheck = len(list(playerContainer.query_items(query=adminUsernameQuery, enable_cross_partition_query=True))) == 0
        usernameToAddCheck = len(list(playerContainer.query_items(query=usernameToAddQuery, enable_cross_partition_query=True))) == 0
        if adminUsernameCheck or usernameToAddCheck:
            raise DatabaseDoesNotContainUsernameError

        # Get room data from admin username
        query = "SELECT * FROM r where r.room_admin='{}'".format(adminUsername)
        room = list(roomContainer.query_items(query=query, enable_cross_partition_query=True))

        # Check if room exists
        if len(room) == 0:
            raise RoomDoesNotExist

        # Constants
        playersList = room[0]['players_in_room']
        roomId = room[0]['id']

        # Check if player is already in another room or this room
        query2 = "SELECT * FROM r WHERE ARRAY_CONTAINS(r.players_in_room, @username)"
        query3 = "SELECT * FROM r where r.room_admin='{}'".format(usernameToAdd)
        query_params = [{"name": "@username", "value": usernameToAdd}]
        usernameInRoom = len(list(roomContainer.query_items(query=query2, parameters=query_params, enable_cross_partition_query=True))) != 0
        usernameIsAdmin = len(list(roomContainer.query_items(query=query3, enable_cross_partition_query=True))) != 0

        if usernameIsAdmin or usernameInRoom:
            raise UserInRoomAlready

        # Add player to list and change list in database
        playersList.append(usernameToAdd)
        item_to_modify = roomContainer.read_item(item=roomId, partition_key=roomId)
        item_to_modify['players_in_room'] = playersList
        roomContainer.replace_item(item=item_to_modify, body=item_to_modify)

        return func.HttpResponse(body=json.dumps({'result': True, "msg": "Successfully added player to room."}), mimetype="application/json")

    except UserInRoomAlready:
        message = UserInRoomAlready.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, 'msg': message}), mimetype="application/json")

    except RoomDoesNotExist:
        message = RoomDoesNotExist.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, 'msg': message}), mimetype="application/json")

    except DatabaseDoesNotContainUsernameError:
        message = DatabaseDoesNotContainUsernameError.getMessage()
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
