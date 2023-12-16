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

from games import Player, Game
from msg import error_msg, MSG
import keyboards as kb

class FSMUser(StatesGroup):
    wait_name = State()
    wait_winner = State()

logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.INFO, filename='bot.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
PROXY_URL = None # os.getenv("TELEGRAM_PROXY_URL")
PROXY_AUTH = None
"""aiohttp.BasicAuth(
    login=os.getenv("TELEGRAM_PROXY_LOGIN"),
    password=os.getenv("TELEGRAM_PROXY_PASSWORD")
)"""
LNG = 'ru'

bot = Bot(token=API_TOKEN, proxy=PROXY_URL, proxy_auth=PROXY_AUTH)
dp = Dispatcher(bot, storage=MemoryStorage())
dp.middleware.setup(LoggingMiddleware())

@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """Отправляет приветственное сообщение и помощь по боту"""
    await message.answer(MSG[LNG]['msg_greeting'], reply_markup=kb.kbs[LNG]['kb_init'])


@dp.message_handler(commands=['new'])
async def new_game(message: types.Message):
    """Создает новую игру с названием Game"""
    cmnd = message.get_command(True)
    args = message.get_args().split()
    game_name = args[0] if len(args) > 0 else Game.suggest_name()
    pl = Player.auth(message.from_user)

    if error_message := error_msg(pl.check_command(cmnd, game_name)):
        await message.answer(error_message)
        return

    if pl.create_game(game_name):
        answer_message = f"Cоздал игру: {game_name}"
        if True:
            test_add_users(game_name)
    else:
        answer_message = f"Ой, не смог создать игру {game_name}. Спрошу у хозяина"

    await message.answer(answer_message, reply_markup=kb.kbs[LNG]['kb_admin'])


@dp.message_handler(state=FSMUser.wait_name)
async def process_name(message: types.Message, state: FSMContext):
    logging.info(f'State is {state}')
    pl = Player.auth(message.from_user)
    async with state.proxy() as data:
        cmd = data['cmd']
        if cmd == 'join':
            pl.join_game(message.text)

@dp.message_handler(commands=['join'], state=None)
async def join_game(message: types.Message, state: FSMContext):
    """Присоединиться к созданной игре с названием Game"""
    game_name = message.get_args()
    if not game_name:
        answer_message = "Укажите название игры, в которую хотите присоединиться"
        async with state.proxy() as data:
            data['cmd'] = 'join'
        await FSMUser.wait_name.set()
        await message.answer(answer_message)
        return


    pl = Player.auth(message.from_user)
    if error_message := error_msg(pl.check_command("join", game_name)):
        await message.answer(error_message)
        return

    if pl.join_game(game_name):
        answer_message = f"Не могу присоединить к игре {pl.game.name}, спрошу у менеджера"
        await message.answer(answer_message)
        return

    answer_message = f"Вы присоединились к игре {game_name}, дождитесь старта раунда. \
        Посмотреть кто в игре можно командой \game"
    await message.answer(answer_message, reply_markup=kb.kbs[LNG]['kb_player'])

@dp.message_handler(state=FSMUser.wait_name)
async def process_name(message: types.Message, state: FSMContext):
    """User write command without argument. Waiting them"""
    logging.info(f'State is {state}')
    pl = Player.auth(message.from_user)
    async with state.proxy() as data:
        cmd = data['cmd']
        if cmd == 'join':
            pl.join_game(message.text)
    await state.finish()

@dp.message_handler(commands=['quit'])
async def quit_game(message: types.Message):
    """Выйти из игры"""
    pl = Player.auth(message.from_user)
    if not pl.quit_game():
        answer_message = f"Вы вышли из игры"
    else:
        answer_message = f"Вы не были в игре"
    await message.answer(answer_message)


@dp.message_handler(commands=['round'])
async def start_round(message: types.Message):
    """Запускает новый раунд"""
    pl = Player.auth(message.from_user)
    if error_message := error_msg(pl.check_command("round")):
        await message.answer(error_message)
        return

    r = pl.game.start_round()
    start_str = r.started.strftime("%H:%M:%S")
    finish_str = r.finish.strftime("%H:%M:%S")
    msg = f"Раунд {r.round_nbr}: {start_str} - {finish_str}\n"

    """send to all players their private info about location and role"""
    for pl_id, role in r.roles.items():
        loc_name = "???" if r.spy == pl_id else r.location.name
        answer_message = msg + f"Место: {loc_name}\nВы: {role}"
        if pl_id > 100:
            await bot.send_message(pl_id, answer_message)
            logging.info(f"{pl_id}: {answer_message}")

    await asyncio.sleep(3)
    await message.answer("Кто победил?", reply_markup=kb.pl2kb(pl.game.players, LNG))

@dp.message_handler(commands=['finish'])
async def finish_round(message: types.Message):
    """Выбран победитель раунда"""
    pl = Player.auth(message.from_user)
    if error_message := error_msg(pl.check_command("finish")):
        await message.answer(error_message)
        return

    winner_type = int(random.random()*5)+1
    winner_str = "шпион" if 0 < winner_type < 4 else "антишпион"
    results = pl.game.finish_round(winner_type)
    answer_message = f"Раунд закончен, победил {winner_str}\n"
    for (name, sc, tsc) in results:
        answer_message += f"{name}: {sc} ({tsc})\n"

    await message.answer(answer_message)


@dp.message_handler(commands=['loc'])
async def list_loc(message: types.Message):
    """Выводит список локаций"""
    pl = Player.auth(message.from_user)
    if error_message := error_msg(pl.check_command("loc")):
        await message.answer(error_message)
        return

    answer_message = ", ".join(pl.game.get_locations())
    await message.answer(answer_message)


@dp.message_handler(commands=['game'])
async def game_info(message: types.Message):
    """Информация о текущей игре"""
    pl = Player.auth(message.from_user)
    if error_message := error_msg(pl.check_command("game")):
        await message.answer(error_message)
        return

    g = pl.game
    pl_nbr = len(g.players)
    info = g.get_info()
    answer_message = f'Игра {g.name}, раунд {g.round_nbr}, игроков {pl_nbr}, очки:\n'
    for (name, score) in info:
        answer_message += f"{name}: {score}\n"

    await message.answer(answer_message)


@dp.callback_query_handler(lambda c: c.data and c.data.startswith('ibtn'))
async def process_callback_kb1btn1(callback_query: types.CallbackQuery):
    """Handling all inline buttons"""
    print(callback_query.__dict__)
    await bot.edit_message_reply_markup(callback_query.from_user.id, callback_query.message.message_id, reply_markup=None)
    await bot.answer_callback_query(callback_query.id, text=f'Нажата кнопка {callback_query.data}')


"""Testing"""

@dp.message_handler(lambda message: message.text.startswith('test1'))
async def test_command2(message: types.Message):
    """Testing"""
    chat_id = message.from_user.id
    #await message.answer_dice(emoji="🎲")
    with open('res\hello.jpg', 'rb') as photo:
        await bot.send_photo(chat_id, photo)

@dp.message_handler()
async def test_command1(message: types.Message):
    pl = Player.auth(message.from_user)
        # await message.reply("Кто победил?", reply_markup=kbi_winner_l)
    # looking for command among button captions
    cmd = ''
    for k, v in MSG[LNG].items():
        if message.text.startswith(v):
            cmd = kb.btn2cmd[k]
            logging.info(f"{message.text} -> {cmd}")

    if cmd:
        if m := pl.check_state(cmd):
            await message.reply(m)
            return
        if cmd == 'new':
            await new_game(message)
        if cmd == 'join':
            await join_game(message)
        if cmd == 'quit':
            await quit_game(message)
        if cmd == 'loc':
            await list_loc(message)
        if cmd == 'game':
            await game_info(message)
        if cmd == 'round':
            await start_round(message)
        if cmd == 'finish':
            await finish_round(message)
        return


    for k in kb.kbs[LNG].keys():
        if k == message.text:
            await message.reply(f"Вы просили клавиатуру {k}", reply_markup=kb.kbs[LNG][k])
            return

    game_name = message.text.split(' ')[0]
    await join_game(message, game_name)

@dp.errors_handler()
async def errors_handler(update: types.Update, exception: Exception):
    logging.error(f'Ошибка при обработке запроса {update}: {exception}')


async def send_message(message: str):
    await bot.send_message(146076472, message)


def test_add_users(game_name: str):
    names = ["Oleg", "Ira", "Ivan", "Kirill"]
    admin = None
    for i in range(1, 5):
        pl = Player((i, names[i - 1], "ru"))
        if 100 == i:
            pl.create_game(game_name)
            admin = pl
        else:
            pl.join_game(game_name)
    return admin


if __name__ == '__main__':
   # asyncio.run(send_message('hi'))
    executor.start_polling(dp, skip_updates=True)

