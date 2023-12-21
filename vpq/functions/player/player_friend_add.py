import json

import azure.functions as func
import logging
import os
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

from vpq.helper.exceptions import DatabaseDoesNotContainUsernameError, UsersAlreadyFriendsError, CosmosHttpResponseErrorMessage

function = func.Blueprint()

cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
database = cosmos.get_database_client(os.environ['DatabaseName'])
playerContainer = database.get_container_client(os.environ['Container_Players'])


@function.route(route="playerFriendAdd", auth_level=func.AuthLevel.ANONYMOUS, methods=["PUT"])
def playerAddFriend(req: func.HttpRequest) -> func.HttpResponse:
    try:
        reqJson = req.get_json()
        logging.info('Python HTTP trigger function processed a request to add a friend. JSON: {}'.format(reqJson))

        # Check the both usernames exists
        query = "SELECT * FROM p where p.username='{0}' OR p.username='{1}'".format(reqJson['username'],
                                                                                  reqJson['friendUsername'])
        usernameExists = len(list(playerContainer.query_items(query=query, enable_cross_partition_query=True))) == 2
        if not usernameExists:
            raise DatabaseDoesNotContainUsernameError

        # Check the users are not already friends
        query = "SELECT * FROM p where p.username='{}'".format(reqJson['username'])
        playerInfo = list(playerContainer.query_items(query=query, enable_cross_partition_query=True))[0]
        if reqJson['friendUsername'] in playerInfo['friends']:
            raise UsersAlreadyFriendsError

        # Add the friend
        playerInfo['friends'].append(reqJson['friendUsername'])
        playerContainer.replace_item(playerInfo['id'], body=playerInfo)

        logging.info("Friend added successfully")
        return func.HttpResponse(body=json.dumps({'result': True, "msg": "Success"}), mimetype="application/json")

    except DatabaseDoesNotContainUsernameError:
        message = DatabaseDoesNotContainUsernameError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except UsersAlreadyFriendsError:
        message = UsersAlreadyFriendsError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except CosmosHttpResponseError:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")
