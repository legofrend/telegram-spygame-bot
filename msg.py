__version__ = '2.0.1'
MSG = {
    'ru': {
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
        'emsg_already_in_game': 'Вы уже в игре, нужно сперва выйти из нее',
        'emsg_game_not_found': 'Не могу найти такую игру',
        'emsg_game_exist': 'Игра с таким именем уже существует',
        'emsg_not_in_game': 'Вы еще не начали игру',
        'emsg_not_admin': 'Вы не администратор игры. Чтобы управлять игрой, создайте свою',
        'emsg_unknown_winner_type': 'Не понимаю, кого вы указали победителем',
        'msg_greeting':
            f'Привет, я бот Гамер ({__version__}) для игры Найди шпиона, по мотивам Находки для шпиона '
            '(<a href="https://www.mosigra.ru/image/data/mosigra.product.other/543/674/SPY_rules_new.pdf">'
            'см. правила</a>).\n'
            'Для начала создайте новую игру или присоединитесь к существующей с помощью кнопок внизу. '
            '(Если кнопок нет, кликните на значок клавиатуры справа внизу или напишите любое сообщение)\n'
            'Если бот не работает или работет не так как надо, или для другой обратной связи пишите моему '
            '<a href="tg://user?id=146076472">боссу</a>\n Если захотите купить оригинальную карточную игру от'
            'HobbyGames, то кликайте <a href="https://hobbygames.ru/nahodka-dlja-shpiona-category">сюда</a>',
        'msg_choose_game_name': 'Укажите название игры, к которой хотите присоединиться',
        'msg_pl_join_your_game': 'Игрок {pl.full_name} присоединился к вашей игре',
        'msg_time_left': 'Осталось минут: {timer}',
        'msg_winner_is': 'Победил',
        'msg_choose_set_name': 'Выберите набор?',
        'spy_role': 'шпион',
        'msg_create_game': 'Cоздал игру: `{game_name}`',
        'msg_you_join_game': 'Вы присоединились к игре {game_name}, дождитесь старта раунда. \
                Посмотреть кто в игре можно командой /game',
        'msg_you_quit_game': 'Вы вышли из игры',
        'msg_round': 'Раунд',
        'msg_your_location_role': 'Место: {loc_name}\nВы: {role}',
        'msg_round_finished_who_win': 'Раунд {round_nbr} закончен\nКто победил?',
        'msg_winner_is_spy_1': 'Шпион победил, остался неизвестен',
        'msg_winner_is_spy_2': 'Шпион победил, угадал место',
        'msg_winner_is_spy_3': 'Шпион победил, подставил другого',
        'msg_winner_is_not_spy': 'Шпион проиграл',
        'msg_loc_info {n1, l1, n2, l2}': 'Список мест\nБыли {n1}: {l1}\nОстались {n2}: {l2}',
        'msg_change_set': 'Изменил набор мест: {set_name}',
        'msg_game_stat {name, r, n}': 'Игра {name}, раунд {r}, игроков {n}, очки:\n',
        'msg_unknown_command': 'Не пойму о чем Вы. Используйте кнопки',
        'msg_ask_nps_score': 'Пожалуйста, оцените по шкале от 1 до 10, насколько вероятно, что Вы '
                             'порекомендуете бота друзьям?',
        'msg_nps_score_high': 'Спасибо за высокую оценку\. Если захотите поддержать проект, можете перевести любую '
                              'сумму по СБП на счет автора в Тинькофф по номеру телефона ||79262830634||',
        'msg_nps_score_low': 'Какие изменения Вы бы предложили для улучшения бота?',
        'msg_': 'msg'
},
    'en': {
        'btn_create_game': 'Create game',
        'btn_join_game': 'Join game',
        'btn_quit_game': 'Quit',
        'btn_close_game': 'Close game',
        'btn_list_loc': 'Locations',
        'btn_game_info': 'Scores info',
        'btn_start_round': 'New round',
        'btn_finish_round': 'Finish round',
        'btn_change_loc_set': 'Change locations',
        'ibtn_win_nobody': 'Noone',
        'ibtn_win_spy_1': 'Spy: stay uncovered +2',
        'ibtn_win_spy_2': 'Spy: know location +4',
        'ibtn_win_spy_3': 'Spy: framed someone else +4',
        'ibtn_win_not_spy': 'Non spy +1',
        'emsg_already_in_game': 'You are already in a game, quit it first',
        'emsg_game_not_found': 'Can\'t find this game',
        'emsg_game_exist': 'There is a game with this name',
        'emsg_not_in_game': 'You haven\'t started a game yet',
        'emsg_not_admin': 'You are not an admin of the game. Create your own to manage it',
        'emsg_unknown_winner_type': 'Don\'t understand who is the winner',
        'msg_greeting':
            f'Hi, I am bot Gamer ({__version__}) for the game Find Spy. You may find rules, e.g. '
            '(<a href="https://www.spyfall.app/gamerules">here</a>).\n'
            'Create new game or join one for start playing using buttons below.\n'
            'If something goes wrong or you want to write feedback then feel free to write to my '
            '<a href="tg://user?id=146076472">boss</a>\n'
            'If you want to buy original card game, click '
            '<a href="https://hobbyworldint.com/portfolio-item/spyfall/">here</a>',
        'msg_choose_game_name': 'Type a game name you want to join',
        'msg_pl_join_your_game': 'Player {pl.full_name} has joined your game',
        'msg_time_left': 'Time left: {timer}',
        'msg_winner_is': 'The winner is',
        'msg_choose_set_name': 'Choose set name',
        'spy_role': 'spy',
        'msg_create_game': 'Game was created: `{game_name}`',
        'msg_you_join_game': 'You join game {game_name}, wait when admin start new round.',
        'msg_you_quit_game': 'You quit game',
        'msg_round': 'Round',
        'msg_your_location_role': 'Location: {loc_name}\nYou: {role}',
        'msg_round_finished_who_win': 'Round {round_nbr} is finished\nWho win?',
        'msg_winner_is_spy_1': 'Spy wins, stay uncovered',
        'msg_winner_is_spy_2': 'Spy wins, know location',
        'msg_winner_is_spy_3': 'Spy wins, framed someone else',
        'msg_winner_is_not_spy': 'Spy lost',
        'msg_loc_info {n1, l1, n2, l2}': 'Locations:\nPast {n1}: {l1}\nRemain {n2}: {l2}',
        'msg_change_set': 'Locations set was changed: {set_name}',
        'msg_game_stat {name, r, n}': 'Game {name}, round {r}, players {n}, scores:\n',
        'msg_unknown_command': 'Don\'t understand you. Please use keyboards',
        'msg_ask_nps_score': 'On a scale from 0 to 10, how likely are you to recommend the bot to your friends?',
        'msg_nps_score_high': 'Fantastic\! Thanks for the score\! If you want to support the project you are welcome '
                              'to use SBP money tramsfer to the author on Tinkoff bank account by phone number '
                              '||79262830634||',
        'msg_nps_score_low': 'Help us improve. Would you mind telling us why such a score?',
        'msg_': 'msg'
    }
}


def _msg(code: str, lang='ru') -> str:
    lang = lang if isinstance(lang, str) else lang.language_code
    if not code:
        return ''
    try:
        return MSG[lang][code]
    except KeyError:
        return f'{lang}:{code}'
