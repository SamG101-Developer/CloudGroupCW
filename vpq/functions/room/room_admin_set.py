import azure.functions as func
import logging

function = func.Blueprint()

# sets the admin of the room to a player's username.
# this is the player that creates the lobby (or can become admin if the current admin leaves).
# they will start the game, advance the stages etc

@function.route(route="roomAdminSet", auth_level=func.AuthLevel.ANONYMOUS)
def roomAdminSet(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
