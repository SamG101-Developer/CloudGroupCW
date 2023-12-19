import azure.functions as func
import logging

function = func.Blueprint()


@function.route(route="roomSessionDel", auth_level=func.AuthLevel.ANONYMOUS)
def roomSessionDel(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
