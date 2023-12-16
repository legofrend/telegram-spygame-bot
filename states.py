states = {
    'init': {'code': 0,
             'descr': 'User only enter, he is not in game yet',
             'kb': 'kb_init',
             'cmd': ['new', 'join']
             },
    'creaing_game_need_name': {
             'code': 101,
             'descr': 'User is in process of creating game, we need a game name',
             'kb': 'kb_init',
             'cmd': ['join']
             },
    'creating_game_need_set': {
        'code': 102,
        'descr': 'User is in process of creating game, we need a set name for the game', # not in this version
        'kb': 'kb_init',
        'cmd': ['join']
    },
    'joining_game_need_name': {
        'code': 201,
        'descr': 'User is in process of joining game, we need a game name',
        'kb': 'kb_init',
        'cmd': []
    },
    'joined_game': {
        'code': 210,
        'descr': 'User joined game',
        'kb': 'kb_player',
        'cmd': ['quit', 'loc', 'game']
    },
    'admin_game_created_round_no': {
        'code': 110,
        'descr': 'User created game and is admin. A round is not started yet',
        'kb': 'kb_admin',
        'cmd': ['close', 'loc', 'game', 'round']
    },
    'admin_game_created_round_process': {
        'code': 111,
        'descr': 'User created game and is admin. A round is in process',
        'kb': 'kb_admin_2',
        'cmd': ['close', 'loc', 'game', 'finish']
    },
    'admin_game_created_round_need_results': {
        'code': 112,
        'descr': 'The round was stopped. Waiting for its results',
        'kb': None,
        'cmd': []
    },
    'admin_game_created_round_need_results_2': {
        'code': 113,
        'descr': 'The round was stopped. Spy lost, and a winner is ambiguous',
        'kb': None,
        'cmd': []
    },
}
