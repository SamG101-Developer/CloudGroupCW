import os
import json

from azure.cosmos import CosmosClient


def _loadEnvFromJson():
    local_settings_json = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'local.settings.json')
    if os.path.exists(local_settings_json):
        with open(local_settings_json) as f:
            settings = json.load(f)
        os.environ.update(settings['Values'])
    else:
        raise FileNotFoundError("local.settings.json not found")


class MetaTest:
    _loadEnvFromJson()

    key = os.environ["FunctionAppKey"]
    cosmos = CosmosClient.from_connection_string(os.environ['AzureCosmosDBConnectionString'])
    database = cosmos.get_database_client(os.environ['DatabaseName'])
    playerContainer = database.get_container_client(os.environ['Container_Players'])
    questionContainer = database.get_container_client(os.environ['Container_Questions'])
    questionSetContainer = database.get_container_client(os.environ['Container_QuestionSets'])
    roomContainer = database.get_container_client(os.environ['Container_Rooms'])

    PUBLIC_URL: str
    LOCAL_URL: str
    TEST_URL: str

    DEFAULT_QUESTION_JSON = {
        "id": "1",
        "question": "What is the capital of France?",
        "answers": ["Paris", "London", "Madrid", "Berlin"],
        "correct_answer": 1,
        "author": "bsab1g21"
    }

    DEFAULT_PLAYER_JSON = {
        'username': "bsab1g21",
        'password': "myTestPassword2",
        'firstname': "Ben",
        'lastname': "Burbridge",
        'dob': "06/02/2003",
        'currency': 0,
        'premium_currency': 0,
        'overall_score': 0,
        'friends': [],
        'fave_quizzes': []
    }

    DEFAULT_PLAYER_JSON_2 = {
        "username": "player1",
        "password": "pass123",
        "firstname": "John",
        "lastname": "Doe",
        "currency": 0,
        "premium_currency": 0,
        "overall_score": 0,
        "friends": [],
        "fave_quizzes": [],
    }

    DEFAULT_ROOM_JSON = {
        'room_admin': 'ethan',
        'players_in_room': [1,2],
        'question_set_id': '',
        'adult_only': False,
        'password': '',
    }

    DEFAULT_QUESTION_SET_JSON = {
        'username':'bsab1g21',
        'questions':[],
    }
