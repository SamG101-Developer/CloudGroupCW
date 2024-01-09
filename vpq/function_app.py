import azure.functions as func
import sys, os


app = func.FunctionApp()
bp = func.Blueprint("test")
error = "..."


app.register_blueprint(bp)

try:
    #
    # from vpq.shared_code import functions
    # from functions import functions_list  # this is good now (imports that are imported are erroneous still -> causes error)

    from functions.player.player_add import function as player_add
    from functions.player.player_del import function as player_del
    from functions.player.player_fave_quiz_add import function as player_fave_quiz_add
    from functions.player.player_fave_quiz_del import function as player_fave_quiz_del
    from functions.player.player_friend_add import function as player_friend_add
    from functions.player.player_friend_del import function as player_friend_del
    from functions.player.player_info_get import function as player_info_get
    from functions.player.player_info_set import function as player_info_set
    from functions.player.player_question_groups_get import function as player_question_groups_get
    from functions.player.player_login import function as player_login
    from functions.question.question_add import function as question_add
    from functions.question.question_del import function as question_del
    from functions.question.question_get import function as question_get
    from functions.question.question_set import function as question_set
    from functions.question_set.question_set_add import function as question_set_add
    from functions.question_set.question_set_del import function as question_set_del
    from functions.question_set.question_set_questions_get import function as question_set_questions_get
    from functions.question_set.question_set_set import function as question_set_set
    from functions.room.room_admin_set import function as room_admin_set
    from functions.room.room_all_get import function as room_all_get
    from functions.room.room_adultonly_set import function as room_adultonly_set
    from functions.room.room_flag_password_set import function as room_flag_password_set
    from functions.room.room_player_add import function as room_player_add
    from functions.room.room_player_del import function as room_player_del
    from functions.room.room_info_get import function as room_info_get
    from functions.room.room_question_group_set import function as room_question_group_set
    from functions.room.room_session_add import function as room_session_add
    from functions.room.room_session_del import function as room_session_del

    function_list = [
        player_add,
        player_del,
        player_fave_quiz_add,
        player_fave_quiz_del,
        player_friend_add,
        player_friend_del,
        player_info_get,
        player_info_set,
        player_question_groups_get,
        player_login,
        question_add,
        question_del,
        question_get,
        question_set,
        question_set_questions_get,
        question_set_add,
        question_set_del,
        question_set_set,
        room_admin_set,
        room_all_get,
        room_adultonly_set,
        room_adultonly_set,
        room_flag_password_set,
        room_player_add,
        room_player_del,
        room_info_get,
        room_question_group_set,
        room_session_add,
        room_session_del
    ]

    for function in function_list:
        app.register_blueprint(function)


except Exception as e:
    import logging
    error = str(e)
