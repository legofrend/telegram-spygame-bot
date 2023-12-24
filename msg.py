MSG = {'ru': {
    'IN_GAME': 'Вы уже в игре, нужно сперва выйти из нее командой /quit ',
    'GAME_NOT_FOUND': 'Не могу найти такую игру',
    'GAME_EXIST': 'Игра с таким именем уже существует',
    'NO_GAME': 'Вы еще не начали игру',
    'NOT_ADMIN': 'Вы не администратор игры. Чтобы управлять игрой, создайте свою с помощью /new <Name>',
    'emsg_unknown_winner_type': 'Не понимаю, кого вы указали победителем',
    'btn_create_game': 'Создать игру',
    'btn_join_game': 'Присоединиться',
    'btn_quit_game': 'Выйти из игры',
    'btn_close_game': 'Завершить игру',
    'btn_list_loc': 'Список мест',
    'btn_game_info': 'Игроки и счёт',
    'btn_start_round': 'Новый раунд',
    'btn_finish_round': 'Завершить раунд',
    'btn_change_loc_set': 'Сменить набор мест',
    'ibtn_win_nobody': 'Никто',
    'ibtn_win_spy_1': 'Шпион: не выдал себя +2',
    'ibtn_win_spy_2': 'Шпион: угадал место +4',
    'ibtn_win_spy_3': 'Шпион: подставил другого +4',
    'ibtn_win_not_spy': 'Не шпионы +1',
    'msg_greeting':
        'Привет, я бот Гамер (v2.0.0) для игры Найди шпиона, по мотивам Находки для шпиона '
        '(<a href="https://www.mosigra.ru/image/data/mosigra.product.other/543/674/SPY_rules_new.pdf">см. правила</a>).\n'
        'Для начала создайте новую игру или присоединитесь к существующей с помощью кнопок внизу. '
        '(Если кнопок нет, кликните на значок клавиатуры справа внизу или напишите любое сообщение)\n'
        'Если бот не работает или работет не так как надо, или для другой обратной связи пишите моему ' 
        '<a href="tg://user?id=146076472">боссу</a>\n'
}}

def error_msg(err: str, lang='ru') -> str:
    if not err:
        return ''
    return MSG[lang][err]


def _msg(code: str, lang='ru') -> str:
    lang = lang if isinstance(lang, str) else lang.language_code
    if not code:
        return ''
    return MSG[lang][code]
