import json
import os
import logging

import azure.functions as func
from azure.cosmos import CosmosClient
from azure.cosmos.exceptions import CosmosHttpResponseError

try:
    from helper.exceptions import CosmosHttpResponseErrorMessage, DatabaseDoesNotContainUsernameError, \
        DatabaseDoesNotContainQuestionError
    from helper.question_set import QuestionSet, QuestionSetQuestionsFormatError
    from functions.question.question_add import questionAdd
except ModuleNotFoundError:
    from vpq.helper.exceptions import CosmosHttpResponseErrorMessage, DatabaseDoesNotContainUsernameError, \
        DatabaseDoesNotContainQuestionError
    from vpq.helper.question_set import QuestionSet, QuestionSetQuestionsFormatError
    from vpq.functions.question.question_add import questionAdd

function = func.Blueprint()


@function.route(route="questionSetAdd", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def questionSetAdd(req: func.HttpRequest) -> func.HttpResponse:
    try:
        cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
        database = cosmos.get_database_client(os.environ['DatabaseName'])
        questionSetContainer = database.get_container_client(os.environ['Container_Questions'])
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
                query = ("SELECT * FROM c WHERE c.question='{0} AND c.question_type='{1}' AND c.answers='{2}"
                         " AND c.correct_answer='{3}").format(question['question'], question['question_type'],
                                                              question['answers'], question['correct_answer'])
                dbQuestion = list(
                    questionSetContainer.query_items(query=query, enable_cross_partition_query=True))
                if len(dbQuestion) == 0:
                    questionAdd(question)
                    newQuestions.append([question, None])
                    questionSetToAdd[roundCount].append(question[0]['question'])
                else:
                    questionSetToAdd[roundCount].append(question[0]['id'])
            roundCount += 1

        # Set the IDs of all the newly added questions
        # for i in range(len(newQuestions)):
        #     question = newQuestions[i]
        #     query = ("SELECT * FROM c WHERE c.question='{0} AND c.question_type='{1}' AND c.answers='{2}"
        #              " AND c.correct_answer='{3}").format(question['question'], question['question_type'],
        #                                                   question['answers'], question['correct_answer'])
        #     dbQuestion = list(
        #         questionSetContainer.query_items(query=query, enable_cross_partition_query=True))
        #     newQuestions[i][1] = dbQuestion[0]['id']

        # Replace the questions with their IDs
        for quizRound in questionSetToAdd:
            for question in quizRound:
                for questionIDPair in newQuestions:
                    if questionIDPair[0] == question['question']:
                        question = questionIDPair[1]

        # old
        # Check each question exists
        # for question in reqJson['questions']:
        #     question_query = "SELECT q.id FROM q where q.id='{}'".format(question['id'])
        #     questions = list(questionSetContainer.query_items(query=question_query, enable_cross_partition_query=True))
        #     if len(questions) == 0:
        #         raise DatabaseDoesNotContainQuestionError

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
