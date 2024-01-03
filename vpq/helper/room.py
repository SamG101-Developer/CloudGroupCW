import json

class UserDoesNotExist(ValueError):
    @staticmethod
    def getMessage():
        return "Admin username does not exist in the database."

class UserInRoomAlready(ValueError):
    @staticmethod
    def getMessage():
        return "User is already in another room."


class Room:

    def __init__(self,roomData):
        """""
        Constructor for room object

            :param
            questionData(dict): Contains all the room data store in the database format
            {
                'room_admin': (string),
                'players_in_room': ([string]),
                'question_set_id': (string),
                'adult_only': (boolean),
                'password': (string)
            }
        """
        self.roomData = roomData

    def roomToJson(self):
        return json.dumps(self.roomData)
