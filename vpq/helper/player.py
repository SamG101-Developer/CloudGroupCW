import json


class UsernameLengthError(ValueError):
    @staticmethod
    def getMessage():
        return "Username length invalid."


class PasswordLengthError(ValueError):
    @staticmethod
    def getMessage():
        return "Password length invalid."


# Setting constants
USERNAME_MIN_LENGTH = 0
USERNAME_MAX_LENGTH = 12
PASSWORD_MIN_LENGTH = 2
PASSWORD_MAX_LENGTH = 20


class Player:

    def __init__(self, playerData):
        """
        Constructor for player object

        :param playerData (dict): Contains all the player data stored in the database.
                          Format:
                          {
                            'playerId': (int),
                            'username': (string),
                            'password': (string),
                            'firstName': (string),
                            'lastName': (string),
                            'dob': (string),
                            'freeCurrency': (int),
                            'premiumCurrency': (int),
                            'totalScore': (int),
                            'friends': ([string]),
                            'favQuizzes': ([int])
                          }
        """
        self.playerData = playerData

    def playerToJson(self):
        return json.dumps(self.playerData)

    def isUsernameValid(self):
        usernameLength = len(self.playerData['username'])
        # A username is not valid if it has less than USERNAME_MIN_LENGTH characters or a more than
        # USERNAME_MAX_LENGTH characters
        if (usernameLength > USERNAME_MAX_LENGTH) or (usernameLength < USERNAME_MIN_LENGTH):
            raise UsernameLengthError("Username less than", USERNAME_MIN_LENGTH, "characters or more than",
                                      USERNAME_MAX_LENGTH, "characters.")

    def isPasswordValid(self):
        passwordLength = len(self.playerData['username'])
        # A password is not valid if it has less than USERNAME_MIN_LENGTH characters or a more than
        # USERNAME_MAX_LENGTH characters
        if (passwordLength > PASSWORD_MAX_LENGTH) or (passwordLength < PASSWORD_MIN_LENGTH):
            raise PasswordLengthError("Password less than", PASSWORD_MIN_LENGTH, "characters or more than",
                                      PASSWORD_MAX_LENGTH, "characters.")
