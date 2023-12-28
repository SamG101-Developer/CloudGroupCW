class DatabaseContainsUsernameError(ValueError):
    @staticmethod
    def getMessage():
        return "Database already contains username."


class DatabaseDoesNotContainUsernameError(ValueError):
    @staticmethod
    def getMessage():
        return "Database DOES NOT contain username."


class UsersAlreadyFriendsError(ValueError):
    @staticmethod
    def getMessage():
        return "The users are already friends."


class UsersNotFriendsError(ValueError):
    @staticmethod
    def getMessage():
        return "The users are not friends."


class QuestionSetNotFavouriteError(ValueError):
    @staticmethod
    def getMessage():
        return "The quiz is not a favourite."


class DatabaseDoesNotContainQuestionSetIDError(ValueError):
    @staticmethod
    def getMessage():
        return "The Database does not contain Question Set ID"


class IncorrectUsernameOrPasswordError(ValueError):
    @staticmethod
    def getMessage():
        return "Username and password DO NOT match."


class DatabaseDoesNotContainQuestionError(ValueError):
    @staticmethod
    def getMessage():
        return "The question does not exist in the database."


def CosmosHttpResponseErrorMessage() -> str:
    return "Did not complete the request due to an issue connecting to the database. Please try again later."
