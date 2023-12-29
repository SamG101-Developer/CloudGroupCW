import json


class Room:

    def __init__(self,roomData):
        """""
        Constructor for room object

            :param
            questionData(dict): Contains all the room data store in the database format
            {
                'roomAdmin': (string),
                'playersInRoom': ([string]),
                'questionSetId': (string),
                'adultOnly': (boolean),
                'password': (string)
            }
        """
        self.roomData = roomData

    def roomToJson(self):
        return json.dumps(self.roomData)
