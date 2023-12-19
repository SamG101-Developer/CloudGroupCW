import azure.functions as func
import logging

function = func.Blueprint()


@function.route(route="playerAdd", auth_level=func.AuthLevel.ANONYMOUS, methods=["POST"])
def playerAdd(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
