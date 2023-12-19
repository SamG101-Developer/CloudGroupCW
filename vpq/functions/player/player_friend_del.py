import json

import azure.functions as func
import logging
import os
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

from vpq.helper.exceptions import DatabaseDoesNotContainUsernameError, UsersNotFriendsError

function = func.Blueprint()

cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
database = cosmos.get_database_client(os.environ['DatabaseName'])
playerContainer = database.get_container_client(os.environ['Container_Players'])


@function.route(route="playerFriendDel", auth_level=func.AuthLevel.ANONYMOUS)
def playerFriendDel(req: func.HttpRequest) -> func.HttpResponse:
    try:
        reqJson = req.get_json()
        logging.info('Python HTTP trigger function processed a request to remove a friend. JSON: {}'.format(reqJson))

        # Get the player
        query = "SELECT * FROM p where p.username='{}'".format(reqJson['username'])
        playerInfo = list(playerContainer.query_items(query=query, enable_cross_partition_query=True))[0]
        usernameExists = len(playerInfo) == 1
        if not usernameExists:
            raise DatabaseDoesNotContainUsernameError

        # Check the users are friends
        if not reqJson['friendUsername'] in playerInfo['friends']:
            raise UsersNotFriendsError

        # Remove the friend
        playerInfo['friends'].remove(reqJson['friendUsername'])
        playerContainer.replace_item(playerInfo['id'], body=playerInfo)

        logging.info("Friend removed successfully")
        return func.HttpResponse(body=json.dumps({'result': True, "msg": "Success"}), mimetype="application/json")

    except DatabaseDoesNotContainUsernameError:
        message = DatabaseDoesNotContainUsernameError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except UsersNotFriendsError:
        message = UsersNotFriendsError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except CosmosHttpResponseError:
        logging.error("Did not complete the request due to an issue connecting to the database."
                      " Please try again later.")
        return func.HttpResponse(body=json.dumps({'result': False, "msg": "Did not complete the request due to an "
                                                                          "issue connecting to the database. Please "
                                                                          "try again later."}),
                                 mimetype="application/json")