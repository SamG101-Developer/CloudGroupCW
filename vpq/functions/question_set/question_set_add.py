import json
import os
import logging
import time

import azure.functions as func
import requests
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError
import requests

try:
    from helper.exceptions import CosmosHttpResponseErrorMessage, DatabaseDoesNotContainUsernameError, \
        DatabaseDoesNotContainQuestionError
    from helper.question_set import QuestionSet, QuestionSetQuestionsFormatError
    from functions.question.question_add import questionAdd
    key = os.environ["FunctionAppKey"]
    URL = "https://vpq.azurewebsites.net/api/questionAdd?code={}".format(key)
except ModuleNotFoundError:
    from vpq.helper.exceptions import CosmosHttpResponseErrorMessage, DatabaseDoesNotContainUsernameError, \
        DatabaseDoesNotContainQuestionError
    from vpq.helper.question_set import QuestionSet, QuestionSetQuestionsFormatError
    from vpq.functions.question.question_add import questionAdd
    key = os.environ["FunctionAppKey"]
    URL = "http://localhost:7071/api/questionAdd?code={}".format(key)

function = func.Blueprint()


@function.route(route="questionSetAdd", auth_level=func.AuthLevel.FUNCTION, methods=["POST"])
def questionSetAdd(req: func.HttpRequest) -> func.HttpResponse:
    try:
        cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
        database = cosmos.get_database_client(os.environ['DatabaseName'])
        questionSetContainer = database.get_container_client(os.environ['Container_QuestionSets'])
        questionContainer = database.get_container_client(os.environ['Container_Questions'])
        playerContainer = database.get_container_client(os.environ['Container_Players'])

        reqJson = req.get_json()
        logging.info(f"Python HTTP trigger function processed a request to add a question set: JSON: {reqJson}.")


        # Check the question set is valid
        questionSet = QuestionSet(reqJson)
        questionSet.isQuestionsValid()

        # Check the author exists
        author_query = "SELECT p.username FROM p where p.username='{}'".format(reqJson['author'])
        authors = list(playerContainer.query_items(query=author_query, enable_cross_partition_query=True))
        if len(authors) == 0:
            raise DatabaseDoesNotContainUsernameError

        # new
        newQuestions = []
        questionSetList = reqJson["questions"]
        questionSetToAdd = []
        roundCount = 0
        for quizRound in questionSetList:
            questionSetToAdd.append([])
            for question in quizRound:
                logging.error(question)
                query = ("SELECT * FROM c WHERE c.question='{0}' AND c.question_type='{1}' AND c.answers={2}"
                         " AND c.correct_answer='{3}'").format(question['question'], question['question_type'],
                                                               question['answers'], question['correct_answer'])

                dbQuestion = list(questionContainer.query_items(query=query, enable_cross_partition_query=True))
                if len(dbQuestion) == 0:
                    logging.error("Requesting a new question to be added")
                    response = requests.post(URL, data=json.dumps(question))
                    logging.error("Response:"+str(response.json()))

                    newQuestions.append([question, None])
                    logging.error("New Questions:"+str(newQuestions))
                    questionSetToAdd[roundCount].append(question['question'])
                    logging.error("Q to add:" + str(questionSetToAdd))
                else:
                    questionSetToAdd[roundCount].append(dbQuestion[0]['id'])
            roundCount += 1

        # Set the IDs of all the newly added questions
        for i in range(len(newQuestions)):
            logging.error(f"Inspecting new question {i} ({newQuestions[i]})")
            question = newQuestions[i][0]
            logging.error("STAGE 1")
            dbQuestion = []
            logging.error("STAGE 2")

            while len(dbQuestion) == 0:
                logging.error("Waiting for question to be added to DB...")
                query = ("SELECT * FROM c WHERE c.question='{0}' AND c.question_type='{1}' AND c.answers={2}"
                         " AND c.correct_answer='{3}'").format(
                    question['question'], question['question_type'],
                    question['answers'], question['correct_answer'])
                logging.error("Query made")
                dbQuestion = list(questionContainer.query_items(query=query, enable_cross_partition_query=True))
                logging.error(f"Query response received {dbQuestion}")
                time.sleep(2)
                logging.error("PAUSE DONE")

            logging.error("Question added to DB")

            newQuestions[i][1] = dbQuestion[0]['id']

        logging.error(newQuestions)
        # Replace the questions with their IDs
        logging.error(questionSetToAdd)
        # for quizRound in questionSetToAdd:
        #     for question in quizRound:
        #         for questionIDPair in newQuestions:
        #             if questionIDPair[0]['question'] == question:
        #                 question = questionIDPair[1]
        for quizRoundIndex, quizRound in enumerate(questionSetToAdd):
            for questionIndex, question in enumerate(quizRound):
                for questionIDPair in newQuestions:
                    if questionIDPair[0]['question'] == question:
                        # Update the question in quizRound directly using indices
                        questionSetToAdd[quizRoundIndex][questionIndex] = questionIDPair[1]

        logging.error(questionSetToAdd)

        # old
        # Check each question exists
        # for question in reqJson['questions']:
        #     question_query = "SELECT q.id FROM q where q.id='{}'".format(question['id'])
        #     questions = list(questionSetContainer.query_items(query=question_query, enable_cross_partition_query=True))
        #     if len(questions) == 0:
        #         raise DatabaseDoesNotContainQuestionError

        reqJson['questions'] = questionSetToAdd
        # Add the question to the database
        questionSetContainer.create_item(body=reqJson, enable_automatic_id_generation=True)
        logging.info("Question Set Added Successfully")
        return func.HttpResponse(body=json.dumps({'result': True, "msg": "Success"}), mimetype="application/json")

    except DatabaseDoesNotContainUsernameError:
        message = DatabaseDoesNotContainUsernameError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except DatabaseDoesNotContainQuestionError:
        message = DatabaseDoesNotContainQuestionError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except QuestionSetQuestionsFormatError:
        message = QuestionSetQuestionsFormatError.getMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")

    except CosmosHttpResponseError:
        message = CosmosHttpResponseErrorMessage()
        logging.error(message)
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}), mimetype="application/json")
