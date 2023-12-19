import json


class QuestionLengthError(ValueError):
    pass


# Setting constants
QUESTION_MIN_LENGTH = 0
QUESTION_MAX_LENGTH = 250


class Question:

    def __init__(self, questionData):
        """
        Constructor for question object

        :param questionData (dict): Contains all the question data stored in the database.
                          Format:
                          {
                            'questionId': (int),
                            'questionTypeId': (int),
                            'question': (string),
                            'answer': (string),
                            'options': ([string]),
                          }
        """
        self.questionData = questionData

    def questionToJson(self):
        return json.dumps(self.questionData)

    def isUsernameValid(self):
        questionLength = len(self.questionData['question'])
        # A question is not valid if it has less than QUESTION_MIN_LENGTH characters or a more than
        # QUESTION_MAX_LENGTH characters
        if (questionLength > QUESTION_MAX_LENGTH) or (questionLength < QUESTION_MIN_LENGTH):
            raise QuestionLengthError("Username less than", QUESTION_MIN_LENGTH, "characters or more than",
                                      QUESTION_MAX_LENGTH, "characters.")
