import azure.functions as func
import logging
import json
import os

import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

try:
    from helper.exceptions import CosmosHttpResponseErrorMessage, DatabaseDoesNotContainUsernameError
    from helper.room import Room,UserDoesNotExist,UserInRoomAlready,RoomDoesNotExist
    from helper.player import Player, PasswordLengthError

except ModuleNotFoundError:
    from vpq.helper.exceptions import CosmosHttpResponseErrorMessage, DatabaseDoesNotContainUsernameError
    from vpq.helper.room import Room,UserDoesNotExist,UserInRoomAlready,RoomDoesNotExist
    from vpq.helper.player import Player, PasswordLengthError

function = func.Blueprint()


@function.route(route="roomFlagPasswordSet",auth_level=func.AuthLevel.FUNCTION, methods=['POST'])
def roomFlagPasswordSet(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    try:
        #lock the room with a password to the room
        cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
        database = cosmos.get_database_client(os.environ['DatabaseName'])
        playerContainer = database.get_container_client(os.environ['Container_Players'])
        questionContainer = database.get_container_client(os.environ['Container_Questions'])
        roomContainer = database.get_container_client(os.environ['Container_Rooms'])

        reqJson = req.get_json()
        adminUsername = reqJson['adminUsername']
        password = reqJson['valueToSet']

        adminUsernameQuery = "SELECT * FROM r where r.username='{}'".format(adminUsername)
        adminUsernameCheck = len(list(playerContainer.query_items(query=adminUsernameQuery, enable_cross_partition_query=True))) == 0
        if adminUsernameCheck:
            raise DatabaseDoesNotContainUsernameError

        query = "SELECT * FROM r where r.room_admin='{}'".format(adminUsername)
        room = list(roomContainer.query_items(query=query, enable_cross_partition_query=True))

        passwordCheck = Player({'password':password})
        passwordCheck.isPasswordValid()

        if len(room) == 0:
            raise RoomDoesNotExist

        # Constants
        roomId = room[0]['id']

        # add player to list and change list in database
        item_to_modify = roomContainer.read_item(item=roomId, partition_key=roomId)
        item_to_modify['password'] = password
        roomContainer.replace_item(item=item_to_modify, body=item_to_modify)

        return func.HttpResponse(body=json.dumps(
            {'result': True, "msg": "Successfully set password: {}".format(adultOnlyNewValue)}),mimetype="application/json")



    except PasswordLengthError:
        message = PasswordLengthError.getMessage()
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}),mimetype="application/json")

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
