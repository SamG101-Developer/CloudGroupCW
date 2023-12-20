# extend os.environ from local.settings.json
# import os
# local_settings_json = os.path.join(os.path.dirname(__file__), 'local.settings.json')
# if os.path.exists(local_settings_json):
#     import json
#     with open(local_settings_json) as f:
#         settings = json.load(f)
#     os.environ.update(settings['Values'])
# for k, v in os.environ.items():
#     print(f"{k}={v}")


import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
folder = os.path.dirname(os.path.realpath(__file__))
up_1_dir = os.path.dirname(folder)
sys.path.append(up_1_dir)


import azure.functions as func
import logging
import functions


logging.info("Registering functions")
logging.info(functions.functions)

app = func.FunctionApp()


for function in functions.functions:
    logging.info(f"Registering {function}")
    app.register_functions(function)
