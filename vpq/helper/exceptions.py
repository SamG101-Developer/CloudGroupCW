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
        return "The quiz is not a favourite."


class IncorrectUsernameOrPasswordError(ValueError):
    @staticmethod
    def getMessage():
        return "Username and password DO NOT match."
