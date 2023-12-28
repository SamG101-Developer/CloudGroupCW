from typing import Any


class QuestionSetQuestionsFormatError(Exception):
    @staticmethod
    def getMessage():
        return "Questions must be a list"


class QuestionSet:
    _question_data: dict[str, Any]

    def __init__(self, question_data: dict[str, Any]) -> None:
        self._question_data = question_data

    def isQuestionsValid(self) -> None:
        if type(self._question_data["questions"]) != list:
            raise QuestionSetQuestionsFormatError("Questions must be a list")

    @property
    def question_data(self):
        return self._question_data
