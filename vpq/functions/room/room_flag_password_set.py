import azure.functions as func
import logging

function = func.Blueprint()

from vpq.helper.player import Player,PasswordLengthError

@function.route(route="roomFlagPasswordSet", auth_level=func.AuthLevel.ANONYMOUS)
def roomFlagPasswordSet(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    try:
        #lock the room with a password to the room

        reqJson = req.get_json()
        adminUsername = reqJson['adminUsername']
        password = reqJson['valueToSet']


        passwordCheck = Player({'password':password})
        passwordCheck.isPasswordValid()


    except PasswordLengthError:
        message = PasswordLengthError.getMessage()
        return func.HttpResponse(body=json.dumps({'result': False, "msg": message}),mimetype="application/json")
