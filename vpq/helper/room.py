import json


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
