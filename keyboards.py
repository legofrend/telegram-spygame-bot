from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

from msg import MSG

btns = {}

for lang, d in MSG.items():
    btns[lang] = {}
    for k, v in MSG[lang].items():
        if k.startswith('btn'):
            btns[lang][k] = KeyboardButton(v)
        if k.startswith('ibtn'):
            btns[lang][k] = InlineKeyboardButton(v, callback_data=k)

kbs = {
    'ru':
           {'kb_init': ReplyKeyboardMarkup(resize_keyboard=True).add(btns['ru']['btn_create_game']). \
               add(btns['ru']['btn_join_game']),
            'kb_player': ReplyKeyboardMarkup(resize_keyboard=True).row(btns['ru']['btn_list_loc'],
                                                                       btns['ru']['btn_game_info']).add(
                btns['ru']['btn_quit_game']),
            'kb_admin': ReplyKeyboardMarkup(resize_keyboard=True).add(btns['ru']['btn_start_round']). \
                row(btns['ru']['btn_list_loc'], btns['ru']['btn_game_info']).
            add(btns['ru']['btn_change_loc_set']).add(btns['ru']['btn_close_game']),
            'kb_admin_2': ReplyKeyboardMarkup(resize_keyboard=True).add(btns['ru']['btn_finish_round']). \
                row(btns['ru']['btn_list_loc'], btns['ru']['btn_game_info']). \
                add(btns['ru']['btn_change_loc_set']).add(btns['ru']['btn_close_game'])
            },
    'en':
        {'kb_init': ReplyKeyboardMarkup(resize_keyboard=True).add(btns['en']['btn_create_game']). \
            add(btns['en']['btn_join_game']),
         'kb_player': ReplyKeyboardMarkup(resize_keyboard=True).row(btns['en']['btn_list_loc'],
                                                                    btns['en']['btn_game_info']).add(
             btns['en']['btn_quit_game']),
         'kb_admin': ReplyKeyboardMarkup(resize_keyboard=True).add(btns['en']['btn_start_round']). \
             row(btns['en']['btn_list_loc'], btns['en']['btn_game_info']).
         add(btns['en']['btn_change_loc_set']).add(btns['en']['btn_close_game']),
         'kb_admin_2': ReplyKeyboardMarkup(resize_keyboard=True).add(btns['en']['btn_finish_round']). \
             row(btns['en']['btn_list_loc'], btns['en']['btn_game_info']). \
             add(btns['en']['btn_change_loc_set']).add(btns['en']['btn_close_game'])
         }
}

def nps2kb():
    nbrs = ('1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟')  # '0️⃣',
    kb = InlineKeyboardMarkup(row_width=5)
    for i, v in enumerate(nbrs, start=1):
        kb.insert(InlineKeyboardButton(text=v, callback_data=f'{i}'))
    return kb


nps = nps2kb()

btn2cmd = {
    'btn_create_game': 'new',
    'btn_join_game': 'join',
    'btn_quit_game': 'quit',
    'btn_close_game': 'close',
    'btn_list_loc': 'loc',
    'btn_game_info': 'game',
    'btn_start_round': 'round',
    'btn_finish_round': 'finish',
    'btn_change_loc_set': 'change'
}


def text2cmd(text: str) -> str:
    cmd = ''
    for lang, msg_lang in MSG.items():
        for k, v in msg_lang.items():
            if text.startswith(v):
                cmd = btn2cmd[k]
    return cmd


def pl2kb(pls, lang='ru'):
    kb = InlineKeyboardMarkup()
    # add basic buttons
    for k in ('spy_1', 'spy_2', 'spy_3', 'not_spy'):
        kb.add(btns[lang]['ibtn_win_' + k])
    # add buttons with players name and id
    for i, pl in pls.items():
        kb.insert(InlineKeyboardButton(text=pl.full_name, callback_data=f'ibtn_win_{i}'))
    kb.add(btns[lang]['ibtn_win_nobody'])
    return kb


def locset2kb(set_names: list):
    kb = InlineKeyboardMarkup()
    for i in set_names:
        kb.insert(InlineKeyboardButton(text=i, callback_data=f'ibtn_loc_set_{i}'))
    return kb
