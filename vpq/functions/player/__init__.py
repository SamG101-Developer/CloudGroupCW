from player_add import function as player_add
from player_del import function as player_del
from player_fave_quiz_add import function as player_fave_quiz_add
from player_fave_quiz_del import function as player_fave_quiz_del
from player_friend_add import function as player_friend_add
from player_friend_del import function as player_friend_del
from player_info_get import function as player_info_get
from player_info_set import function as player_info_set
from player_question_groups_get import function as player_question_groups_get


player_functions = [
    player_add,
    player_del,
    player_fave_quiz_add,
    player_fave_quiz_del,
    player_friend_add,
    player_friend_del,
    player_info_get,
    player_info_set,
    player_question_groups_get
]
