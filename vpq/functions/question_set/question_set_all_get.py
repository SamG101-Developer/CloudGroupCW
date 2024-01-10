import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

import json, logging, os


try:
    from helper.exceptions import CosmosHttpResponseErrorMessage
except ModuleNotFoundError:
    from vpq.helper.exceptions import DatabaseContainsUsernameError, CosmosHttpResponseErrorMessage

function = func.Blueprint()


@function.route(route="questionSetAllGet", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
def questionSetAllGet(req: func.HttpRequest) -> func.HttpResponse:
    try:
        cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
        database = cosmos.get_database_client(os.environ['DatabaseName'])
        questionSetContainer = database.get_container_client(os.environ['Container_QuestionSets'])

        # Get the request
        logging.info('Python HTTP trigger function processed a request to get all Question Set IDs.')

        # Get all question sets
        query = "SELECT p.id FROM p"
        questionSets = list(questionSetContainer.query_items(query=query, enable_cross_partition_query=True))
        formattedQuestionSets = []
        for questionSet in questionSets:
            formattedQuestionSets.append({"id": questionSet['id']})

        # Return the response
        logging.info("Rooms Retrieved Successfully")
        return func.HttpResponse(body=json.dumps({'result': True, "msg": "Success", "questionSetIDs": formattedQuestionSets}), mimetype="application/json")

    except CosmosHttpResponseError as e:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message + " " + str(e))
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except Exception as e:
        message = str(e)
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")
