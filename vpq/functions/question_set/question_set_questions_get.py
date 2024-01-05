import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

import json, logging, os

try:
    from helper.exceptions import CosmosHttpResponseErrorMessage
except ModuleNotFoundError:
    from vpq.helper.exceptions import CosmosHttpResponseErrorMessage

function = func.Blueprint()


@function.route(route="questionSetQuestionsGet", auth_level=func.AuthLevel.FUNCTION, methods=["GET"])
def questionSetQuestionsGet(req: func.HttpRequest) -> func.HttpResponse:
    try:
        cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
        database = cosmos.get_database_client(os.environ['DatabaseName'])
        questionSetContainer = database.get_container_client(os.environ['Container_QuestionSets'])
        questionsContainer = database.get_container_client(os.environ['Container_Questions'])

        # Get the request
        reqJson = req.get_json()
        logging.info('Python HTTP trigger function processed a request to get question set questions. JSON: {}'.format(reqJson))

        # Get all questions IDs
        query = f"SELECT p.questions FROM p WHERE p.id = '{reqJson['question_set_id']}'"
        info = list(questionSetContainer.query_items(query=query, enable_cross_partition_query=True))[0]

        # Get all questions from the IDs
        rounds_of_questions = []
        for round_of_questions in info["questions"]:
            # Use the ARRAY_CONTAINS to get all the questions from this round
            query = f"SELECT p.question, p.answers, p.correct_answer, p.question_type FROM p WHERE ARRAY_CONTAINS({round_of_questions}, p.id)"
            questions = list(questionsContainer.query_items(query=query, enable_cross_partition_query=True))
            rounds_of_questions.append(questions)

        # Return the response
        logging.info("Question set questions retrieved Successfully")
        return func.HttpResponse(body=json.dumps({'result': True, "msg": "Success", "questions": rounds_of_questions}), mimetype="application/json")

    except CosmosHttpResponseError as e:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message + " " + str(e) + "!")
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json", status_code=500)

    except Exception as e:
        message = str(e)
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json", status_code=500)
