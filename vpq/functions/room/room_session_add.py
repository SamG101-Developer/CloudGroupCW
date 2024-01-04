import json
import logging
import os

import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

try:
    from helper.exceptions import CosmosHttpResponseErrorMessage
    from helper.room import Room,UserDoesNotExist,UserInRoomAlready

except ModuleNotFoundError:
    from vpq.helper.exceptions import CosmosHttpResponseErrorMessage
    from vpq.helper.room import Room,UserDoesNotExist,UserInRoomAlready

function = func.Blueprint()


@function.route(route="roomSessionAdd", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def roomSessionAdd(req: func.HttpRequest) -> func.HttpResponse:
    try:
        cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
        database = cosmos.get_database_client(os.environ['DatabaseName'])
        playerContainer = database.get_container_client(os.environ['Container_Players'])
        questionContainer = database.get_container_client(os.environ['Container_Questions'])
        roomContainer = database.get_container_client(os.environ['Container_Rooms'])

        reqJson = req.get_json()
        username = reqJson["username"]
        dictData = {"room_admin":username,
                    "players_in_room":[],
                    "question_set_id":"","adult_only":False,
                    "password":""
                    }
        logging.info(f"Python HTTP trigger function processed a request to add a room: JSON: {dictData}.")

        # Check username exists in players
        query = "SELECT * FROM p where p.username='{}'".format(username)
        usernameExists = len(list(playerContainer.query_items(query=query, enable_cross_partition_query=True)))
        if (usernameExists == 0):
            raise UserDoesNotExist

        # Check username isn't in another room
        query = "SELECT * FROM r where r.room_admin='{}'".format(username)
        query2 = "SELECT * FROM r WHERE ARRAY_CONTAINS(r.players_in_room, @username)"
        query_params = [{"name": "@username", "value": username}]
        usernameInRoom = len(list(roomContainer.query_items(query=query2, parameters=query_params, enable_cross_partition_query=True))) != 0
        usernameIsAdmin = len(list(roomContainer.query_items(query=query, enable_cross_partition_query=True))) != 0
        if (usernameIsAdmin or usernameInRoom):
            raise UserInRoomAlready

        # Add the room to the database
        roomContainer.create_item(body=dictData, enable_automatic_id_generation=True)
        logging.info("Question Added Successfully")
        roomID = list(roomContainer.query_items(query=query,enable_cross_partition_query=True))[0]['id']
        responseOutput = {'result': True, "msg": "Room created with id:{}".format(roomID)}
        return func.HttpResponse(body=json.dumps(responseOutput), mimetype="application/json")

    except UserDoesNotExist:
        message = UserDoesNotExist.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, 'msg': message}), mimetype="application/json")

    except UserInRoomAlready:
        message = UserInRoomAlready.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, 'msg': message}), mimetype="application/json")

    except CosmosHttpResponseError:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")



