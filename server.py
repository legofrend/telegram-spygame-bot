"""Сервер Telegram бота, запускаемый непосредственно"""

import logging
import os, re, copy
import asyncio
import random
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from games import Player, SUPPORT_LANGUAGES
from msg import MSG, _msg
import keyboards as kb


class FSMUser(StatesGroup):
    wait_name = State()
    wait_comment = State()


logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.INFO, filename='bot.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
PROXY_URL = None  # os.getenv("TELEGRAM_PROXY_URL")
PROXY_AUTH = None
"""aiohttp.BasicAuth(
    login=os.getenv("TELEGRAM_PROXY_LOGIN"),
    password=os.getenv("TELEGRAM_PROXY_PASSWORD")
)"""
SUPERUSER_TG_ID = 146076472
SLEEP_BTW_UPDATE = 60

bot = Bot(token=API_TOKEN, proxy=PROXY_URL, proxy_auth=PROXY_AUTH)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

async def send_notification_suser(msg: str):
    await bot.send_message(SUPERUSER_TG_ID, msg)



@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """Отправляет приветственное сообщение и помощь по боту"""
    pl = Player.auth(message.from_user)
    # ToDo remove this command into Player class, get read of using _log and _msg here
    pl._log_action(message.get_command(True))
    await message.answer(pl.msg('msg_greeting'), reply_markup=pl.kb, parse_mode='HTML')
    if pl.id != SUPERUSER_TG_ID and message.get_command(True) == 'start':
        await send_notification_suser(f'Новый пользователь {pl.full_name} запустил бота')


@dp.message_handler(commands=['new'])
async def new_game(message: types.Message):
    """Создает новую игру с названием Game"""
    game_name = message.get_args() or Player.suggest_name()
    pl = Player.auth(message.from_user)
    answer_message = pl.create_game(game_name)
    await message.answer(answer_message, reply_markup=pl.kb, parse_mode='MarkdownV2')
    if pl.id != SUPERUSER_TG_ID:
        await send_notification_suser(f'{pl.full_name} создал игру')


@dp.message_handler(commands=['join'])
async def join_game(message: types.Message):
    """Присоединиться к созданной игре с названием Game"""
    pl = Player.auth(message.from_user)
    game_name = message.get_args()
    if not game_name:
        await FSMUser.wait_name.set()
        await message.answer(_msg('msg_choose_game_name', pl))
        return

    answer_message = pl.join_game(game_name)
    await message.answer(answer_message, reply_markup=pl.kb)


@dp.message_handler(state=FSMUser.wait_name)
async def join_game_get_name(message: types.Message, state: FSMContext):
    """User write command without argument. Waiting them"""
    pl = Player.auth(message.from_user)
    answer_message = pl.join_game(message.text)
    await message.answer(answer_message, reply_markup=pl.kb)
    await bot.send_message(pl.game.admin.id, _msg('msg_pl_join_your_game', pl).format(pl=pl))
    await state.finish()


@dp.message_handler(commands=['quit', 'close'])
async def quit_game(message: types.Message):
    """Выйти из игры"""
    pl = Player.auth(message.from_user)
    round_nbr = pl.game.round_nbr
    answer_message = pl.quit_game()
    await message.answer(answer_message, reply_markup=pl.kb)

    if round_nbr > 5 and not pl.get_nps():
        await message.answer(pl.msg('msg_ask_nps_score'), reply_markup=kb.nps)


@dp.message_handler(commands=['round'])
async def start_round(message: types.Message):
    """Запускает новый раунд"""
    pl = Player.auth(message.from_user)
    result = pl.start_round()
    if isinstance(result, str):
        await message.answer(result, reply_markup=pl.kb)

    for pl_id, m in result.items():
        if pl_id < 100:
            continue
        if pl_id != pl.game.round.spy:
            await send_loc_image_to_pl(Player.auth(pl_id))
        if pl_id == pl.id:
            await bot.send_message(pl_id, m, reply_markup=pl.kb)
        else:
            await bot.send_message(pl_id, m)

    timer = pl.game.round.dur_min
    timer_msg = await message.answer(_msg('msg_time_left', pl).format(timer=timer))
    while True:
        await asyncio.sleep(SLEEP_BTW_UPDATE)
        timer -= 1
        await bot.edit_message_text(_msg('msg_time_left', pl).format(timer=timer), pl.id, timer_msg.message_id)
        if timer <= 0 or pl.game.round.in_progress == 0:
            break
    if pl.game.round.in_progress == 1:
        pl.game.round.in_progress = 0
        await bot.delete_message(pl.id, timer_msg.message_id)
        await finish_round(message)


@dp.message_handler(commands=['finish'])
async def finish_round(message: types.Message):
    """Нажали кнопку завершить раунд"""
    pl = Player.auth(message.from_user)
    answer_message = pl.finish_round()
    await message.answer(answer_message, reply_markup=pl.kb)


@dp.callback_query_handler(lambda c: c.data.startswith('ibtn_win'))
async def ibtn_clc_get_winner(callback_query: types.CallbackQuery):
    """When round is finished handling all inline buttons with winner name"""
    pl = Player.auth(callback_query.from_user)
    await bot.answer_callback_query(callback_query.id, text=_msg('msg_winner_is', pl) + f' {callback_query.data}')

    l: int = len('ibtn_win_')
    winner_type = callback_query.data[l:]  # get XXX from data as ibtn_win_XXX
    answer_message = pl.set_winner(winner_type)
    await bot.edit_message_reply_markup(callback_query.from_user.id, callback_query.message.message_id,
                                        reply_markup=None)
    await bot.send_message(callback_query.from_user.id, answer_message, reply_markup=pl.kb)


@dp.message_handler(commands=['loc'])
async def list_loc(message: types.Message):
    """Выводит список локаций"""
    pl = Player.auth(message.from_user)
    answer_message = pl.list_loc()
    await message.answer(answer_message)


@dp.message_handler(commands=['game'])
async def game_info(message: types.Message):
    """Информация о текущей игре"""
    pl = Player.auth(message.from_user)
    answer_message = pl.game_info()
    await message.answer(answer_message)


@dp.message_handler(lambda message: message.text.startswith(_msg('btn_change_loc_set')))
@dp.message_handler(commands=['change'])
async def change_loc_set(message: types.Message):
    """Администратор меняет набор мест в игре"""
    pl = Player.auth(message.from_user)
    set_names = pl.list_loc_set()
    if not set_names:
        return
    await message.answer(_msg('msg_choose_set_name', pl), reply_markup=kb.locset2kb(set_names))


@dp.callback_query_handler(lambda c: c.data.startswith('ibtn_loc_set'))
async def ibtn_clc_get_winner(callback_query: types.CallbackQuery):
    """When round is finished handling all inline buttons with winner name"""
    await bot.answer_callback_query(callback_query.id, text=f'{callback_query.data}')
    await bot.edit_message_reply_markup(callback_query.from_user.id, callback_query.message.message_id,
                                        reply_markup=None)

    pl = Player.auth(callback_query.from_user)
    l = len('ibtn_loc_set_')
    set_name = callback_query.data[l:]
    answer_message = pl.change_loc_set(set_name)
    answer_message += '\n'+pl.list_loc()
    await bot.send_message(callback_query.from_user.id, answer_message, reply_markup=pl.kb)


@dp.callback_query_handler(lambda c: c.data.isdigit())
async def ibtn_clc_nps_score(callback_query: types.CallbackQuery, state: FSMContext):
    """When user click on button with number with NPS score 1-10"""
    await bot.answer_callback_query(callback_query.id, text=f'{callback_query.data}')
    await bot.edit_message_reply_markup(callback_query.from_user.id, callback_query.message.message_id,
                                        reply_markup=None)
    pl = Player.auth(callback_query.from_user)
    nps = int(callback_query.data)
    msg = pl.set_nps(nps)
    if nps < 9:
        await FSMUser.wait_comment.set()
    await bot.send_message(pl.id, msg, parse_mode='MarkdownV2')


@dp.message_handler(state=FSMUser.wait_comment)
async def nps_get_comment(message: types.Message, state: FSMContext):
    """User write command without argument. Waiting them"""
    pl = Player.auth(message.from_user)
    await bot.send_message(SUPERUSER_TG_ID, f'{pl.full_name} ({pl.id}) NPS score {pl.nps}, comment: {message.text}')
    await state.finish()


"""Testing"""


@dp.message_handler(lambda message: message.text.startswith('test'))
async def add_test_users(message: types.Message):
    pl = Player.auth(message.from_user)
    game_name : str
    admin = None
    if pl.game is None:
        game_name = 'test_game'
        admin = Player((99, 'Admin Adminov', "ru"))
        admin.create_game(game_name)
        pl.join_game(game_name)
        await message.answer(f'Создал игру {game_name} и добавил вас туда', reply_markup=pl.kb)
    else:
        game_name = pl.game.name

    names = ["Oleg", "Ira", "Ivan", "Kirill"]
    for i in range(1, 5):
        pl_bot = Player((i, names[i - 1], "ru"))
        pl_bot.join_game(game_name)
    await message.answer('Добавил ботов')
    return admin


@dp.message_handler(lambda message: message.text.startswith('mem'))
async def send_image(message: types.Message):
    """Testing"""
    pl = Player.auth(message.from_user)
    if pl.id == SUPERUSER_TG_ID:
        await message.answer(pl.stat())


@dp.message_handler(lambda message: message.text.startswith('nps'))
async def test_nps_kb(message: types.Message):
    pl = Player.auth(message.from_user)
    await message.answer('Пожалуйста, оцените по шкале от 1 до 10, насколько вероятно, '
                         'что Вы порекомендуете нас другу или коллеге?', reply_markup=kb.nps)


@dp.message_handler(lambda message: message.text.startswith('photo'))
async def send_image(message: types.Message):
    """Testing"""
    pl = Player.auth(message.from_user)
    await send_loc_image_to_pl(pl)


async def send_loc_image_to_pl(pl: Player):
    """Send image of current location to player"""
    try:
        if pl.game is None:
            return
        l = pl.game.round.location
        if l.pic_id:
            msg = await bot.send_photo(pl.id, l.pic_id)
            return
        if l.pic:
            with open(os.path.join('pics', l.pic), 'rb') as photo:
                msg = await bot.send_photo(pl.id, photo)
                file_id = msg.photo[-1].file_id
                logging.info(file_id)
                l.update_pic_id(file_id)
            return
    except:
        logging.error(f'Не получилось отправить картинку для локации {l.id} {l.name}, {l.pic}')


@dp.message_handler()
async def parse_command(message: types.Message, state: FSMContext):
    cmd2fnc = {'new': new_game,
                'join': join_game,
                'quit': quit_game,
                'close': quit_game,
                'loc': list_loc,
                'game': game_info,
                'round': start_round,
                'finish': finish_round,
                'change': change_loc_set
                }

    pl = Player.auth(message.from_user)
    # looking for command among button captions
    cmd = kb.text2cmd(message.text)
    if cmd == 'join':
        return await cmd2fnc[cmd](message)  # , state
    elif cmd:
        return await cmd2fnc[cmd](message)

    for k in kb.kbs[pl.language_code].keys():
        if k == message.text:
            await message.reply(f"Вы просили клавиатуру {k}", reply_markup=kb.kbs[pl.language_code][k])
            return

    if message.text in SUPPORT_LANGUAGES:
        pl.language_code = message.text
        return await message.reply('Поменял ваш язык:' + pl.language_code, reply_markup=pl.kb)

    await message.reply(pl.msg('msg_unknown_command'), reply_markup=pl.kb)


@dp.errors_handler()
async def errors_handler(update: types.Update, exception: Exception):
    logging.error(f'Ошибка при обработке запроса {update}: {exception}')


async def shutdown(dispatcher: Dispatcher):
    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


if __name__ == '__main__':
    # asyncio.run(send_message('hi'))
    executor.start_polling(dp, skip_updates=True, on_shutdown=shutdown)
