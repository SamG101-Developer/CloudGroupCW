import azure.functions as func
import logging

function = func.Blueprint()


@function.route(route="questionSet", auth_level=func.AuthLevel.ANONYMOUS)
def questionSet(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
