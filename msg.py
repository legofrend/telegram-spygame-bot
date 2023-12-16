MSG = {'ru': {
    "IN_GAME": "Вы уже в игре, нужно сперва выйти из нее командой /quit ",
    "GAME_NOT_FOUND": "Не могу найти такую игру",
    "GAME_EXIST": "Игра с таким именем уже существует",
    "NO_GAME": "Вы еще не начали игру",
    "NOT_ADMIN": "Вы не администратор игры. Чтобы управлять игрой, создайте свою с помощью /new <Name>",
    'btn_create_game': 'Создать игру',
    'btn_join_game': 'Присоединиться',
    'btn_quit_game': 'Выйти из игры',
    'btn_close_game': 'Завершить игру',
    'btn_list_loc': 'Список мест',
    'btn_game_info': 'Игроки и счёт',
    'btn_start_round': 'Новый раунд',
    'btn_finish_round': 'Завершить раунд',
    'ibtn_win_nobody': 'Никто',
    'ibtn_win_spy_1': 'Шпион: не выдал себя +2',
    'ibtn_win_spy_2': 'Шпион: угадал место +4',
    'ibtn_win_spy_3': 'Шпион: подставил другого +4',
    'ibtn_win_people': 'Не шпионы +1',
    'msg_greeting':
        "Бот для игры в Находку для шпиона\n\n"
        "/new [Name] создать новую игру\n"
        "/join [Name] присоединиться к игре\n"
        "/round - запустить новый раунд\n"
        "/loc - вывести список локаций игры\n"
        "/game - вывести информацию о текущей игре и участниках\n"
}}

def error_msg(err: str, lang='ru') -> str:
    if not err:
        return ''
    return MSG[lang][err]
