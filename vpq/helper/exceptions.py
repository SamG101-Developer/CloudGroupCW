class DatabaseContainsUsernameError(ValueError):
    @staticmethod
    def getMessage():
        return "Database already contains username."


class DatabaseDoesNotContainUsernameError(ValueError):
    @staticmethod
    def getMessage():
        return "Database DOES NOT contain username."


class IncorrectUsernameOrPasswordError(ValueError):
    @staticmethod
    def getMessage():
        return "Username and password DO NOT match."
