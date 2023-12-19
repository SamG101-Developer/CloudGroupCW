import azure.functions as func
import functions

app = func.FunctionApp()
app.register_functions(functions.functions)
