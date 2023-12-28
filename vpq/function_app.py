# import os, sys
# sys.path.append(os.path.dirname(os.path.realpath(__file__)))
# folder = os.path.dirname(os.path.realpath(__file__))
# up_1_dir = os.path.dirname(folder)
# sys.path.append(up_1_dir)


import azure.functions as func

import sys, os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.append("hello")

# logging.info("Registering functions")
# logging.info(functions.functions)


app = func.FunctionApp()
bp = func.Blueprint("test")
error = "..."


@bp.route("test", methods=["GET"])
def test(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(body=f"{error}$${'$'.join(sys.path)}$${'$'.join(os.listdir('/home/site/wwwroot'))}".replace("$", "\n"), mimetype="text/plain")


app.register_blueprint(bp)


try:
    #
    # from vpq.shared_code import functions

    from functions import functions
    for function in functions:
        app.register_blueprint(function)

except Exception as e:
    import logging
    error = str(e)
