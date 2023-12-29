import json
import logging
import os

import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

try:
    from helper.exceptions import CosmosHttpResponseErrorMessage
    from helper.room import Room

except ModuleNotFoundError:
    from vpq.helper.exceptions import CosmosHttpResponseErrorMessage
    from vpq.helper.room import Room

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

        # Check Player Exists


        # Add the room to the database
        roomContainer.create_item(body=dictData, enable_automatic_id_generation=True)
        logging.info("Question Added Successfully")
        return func.HttpResponse(body=json.dumps({'result': True, "msg": "Success"}), mimetype="application/json")

    except CosmosHttpResponseError:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")



