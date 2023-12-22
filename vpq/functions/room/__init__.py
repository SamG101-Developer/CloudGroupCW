from vpq.functions.room.room_admin_set import function as room_admin_set
from vpq.functions.room.room_flag_adultonly_set import function as room_flag_adultonly_set
from vpq.functions.room.room_flag_password_set import function as room_flag_password_set
from vpq.functions.room.room_player_add import function as room_player_add
from vpq.functions.room.room_player_del import function as room_player_del
from vpq.functions.room.room_question_group_set import function as room_question_group_set
from vpq.functions.room.room_session_add import function as room_session_add
from vpq.functions.room.room_session_del import function as room_session_del

room_functions = [
    room_admin_set,
    room_flag_adultonly_set,
    room_flag_password_set,
    room_player_add,
    room_player_del,
    room_question_group_set,
    room_session_add,
    room_session_del
]
