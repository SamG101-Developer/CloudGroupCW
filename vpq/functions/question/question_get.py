import azure.functions as func
import logging

function = func.Blueprint()


@function.route(route="questionGet", auth_level=func.AuthLevel.ANONYMOUS)
def questionGet(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
