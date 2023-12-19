import azure.functions as func
import logging

function = func.Blueprint()


@function.route(route="playerInfoGet", auth_level=func.AuthLevel.ANONYMOUS, methods=["GET"])
def playerInfoGet(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request for player::playerInfoGet.")

    json = req.get_json()
    assert json is not None, "JSON body is required."
    assert "username" in json, "JSON body must contain 'username'."
