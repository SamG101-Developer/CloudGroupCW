import azure.functions as func
import logging
import json
import os

import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

try:
    from helper.exceptions import CosmosHttpResponseErrorMessage, DatabaseDoesNotContainUsernameError
    from helper.room import Room, UserDoesNotExist, UserInRoomAlready, RoomDoesNotExist

except ModuleNotFoundError:
    from vpq.helper.exceptions import CosmosHttpResponseErrorMessage, DatabaseDoesNotContainUsernameError
    from vpq.helper.room import Room, UserDoesNotExist, UserInRoomAlready, RoomDoesNotExist

function = func.Blueprint()


@function.route(route="roomAdminSet", auth_level=func.AuthLevel.ANONYMOUS, methods=['POST'])
def roomAdminSet(req: func.HttpRequest) -> func.HttpResponse:
    try:
        cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
        database = cosmos.get_database_client(os.environ['DatabaseName'])
        playerContainer = database.get_container_client(os.environ['Container_Players'])
        questionContainer = database.get_container_client(os.environ['Container_Questions'])
        roomContainer = database.get_container_client(os.environ['Container_Rooms'])

        reqJson = req.get_json()
        adminUsername = reqJson['adminUsername']
        newAdminValue = reqJson['valueToSet']

        # Check Admin and new admin exist
        adminUsernameQuery = "SELECT * FROM r where r.username='{}'".format(adminUsername)
        adminUsernameCheck = len(
            list(playerContainer.query_items(query=adminUsernameQuery, enable_cross_partition_query=True))) == 0

        newAdminUsernameQuery = "SELECT * FROM r where r.username='{}'".format(newAdminValue)
        newAdminUsernameCheck = len(
            list(playerContainer.query_items(query=newAdminUsernameQuery, enable_cross_partition_query=True))) == 0

        if adminUsernameCheck or newAdminUsernameCheck:
            raise DatabaseDoesNotContainUsernameError

        # Get room data from admin username
        query = "SELECT * FROM r where r.room_admin='{}'".format(adminUsername)
        rooms = list(roomContainer.query_items(query=query, enable_cross_partition_query=True))

        # Check if room exists
        if len(rooms) == 0:
            raise RoomDoesNotExist

        # Constants
        roomId = rooms[0]['id']

        # add player to list and change list in database
        item_to_modify = roomContainer.read_item(item=roomId, partition_key=roomId)
        item_to_modify['room_admin'] = newAdminValue
        roomContainer.replace_item(item=item_to_modify, body=item_to_modify)

        return func.HttpResponse(
            body=json.dumps({'result': True, "msg": "Successfully changed admin player to: {}".format(newAdminValue)}),
            mimetype="application/json")

    except CosmosHttpResponseError:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except DatabaseDoesNotContainUsernameError:
        message = DatabaseDoesNotContainUsernameError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except RoomDoesNotExist:
        message = RoomDoesNotExist.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

