"""Сервер Telegram бота, запускаемый непосредственно"""
import logging
import os, re
import asyncio
import random

from games import pls, games, Player

from aiogram import Bot, Dispatcher, executor, types

logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.INFO, filename='bot.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
PROXY_URL = None # os.getenv("TELEGRAM_PROXY_URL")
PROXY_AUTH = None
"""aiohttp.BasicAuth(
    login=os.getenv("TELEGRAM_PROXY_LOGIN"),
    password=os.getenv("TELEGRAM_PROXY_PASSWORD")
)"""

bot = Bot(token=API_TOKEN, proxy=PROXY_URL, proxy_auth=PROXY_AUTH)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """Отправляет приветственное сообщение и помощь по боту"""
    await message.answer(
        "Бот для игры в Находку для шпиона\n\n"
        "/new [Name] создать новую игру\n"
        "/join [Name] присоединиться к игре\n"
        "/round - запустить новый раунд\n"
        "/loc - вывести список локаций игры\n"
        "/game - вывести информацию о текущей игре и участниках\n"
    )

@dp.message_handler(lambda message: message.text.startswith('/new'))
async def new_game(message: types.Message):
    """Создает новую игру с названием Game"""
    regexp_result = re.match(r"/[^ ]+ (.*)", message.text)
    game_name = regexp_result[1]

    pl_id = message.from_user.id
    if pl_id not in pls.keys():
        npl = Player(pl_id, message.from_user.full_name, message.from_user.language_code)
    else:
        npl = pls[pl_id]
    if npl.game is not None:
        answer_message = "Вы уже в игре" + npl.game.name
    else:
        if npl.create_game(game_name):
            answer_message = "Cоздали игру: " + game_name
            if True:
                pl1 = Player(1, "Oleg")
                pl2 = Player(2, "Ira")
                pl3 = Player(3, "Borya")
                pl4 = Player(4, "Katya")
                pl1.join_game(game_name)
                pl2.join_game(game_name)
                pl3.join_game(game_name)
                pl4.join_game(game_name)

    await message.answer(answer_message)


@dp.message_handler(lambda message: message.text.startswith('/join'))
async def join_game(message: types.Message):
    """Присоединиться к созданной игре с названием Game"""
    regexp_result = re.match(r"/[^ ]+ (.*)", message.text)

    game_name = regexp_result[1]
    pl_id = message.from_user.id
    if pl_id in pls.keys() and pls[pl_id].game is not None:
        answer_message = "Вы еще в игре " + pls[pl_id].game.name
    else:
        npl = Player(pl_id, message.from_user.full_name, message.from_user.language_code)
        npl.join_game(game_name)
        answer_message = "Вы присоединились к игре " + game_name + ", дождитесь старта раунда"


    await message.answer(answer_message)


@dp.message_handler(lambda message: message.text.startswith('/round'))
async def new_round(message: types.Message):
    """Запускает новый раунд"""
    pl_id = message.from_user.id
    if pl_id in pls.keys() and pls[pl_id].game is not None:
        pls[pl_id].start_round()
        r = pls[pl_id].game.round

        for pl, role in r.roles.items():
            loc_name = "???" if r.spy == pl else r.location.name
            answer_message = f"Локация: {loc_name}\nРоль: {role}"
            pl_name = pls[pl].full_name
            logging.info(f"{pl} ({pl_name}): {answer_message}")
            if pl > 100:
                await bot.send_message(pl, answer_message)
    else:
        answer_message = "Вы еще не создали игру"
        await message.answer(answer_message)


@dp.message_handler(lambda message: message.text.startswith('/finish'))
async def finish_round(message: types.Message):
    """Выбран победитель раунда"""
    pl_id = message.from_user.id
    winner_type = int(random.random()*5)
    winner_str = "шпион" if winner_type < 4 else "антишпион"
    if pl_id in pls.keys() and pls[pl_id].game is not None:
        pls[pl_id].finish_round(winner_type)
        answer_message = f"Раунд закончен, победил {winner_str}"
    else:
        answer_message = "Вы еще не создали игру"

    await message.answer(answer_message)


@dp.message_handler(lambda message: message.text.startswith('/loc'))
async def list_locations(message: types.Message):
    """Выводит список локаций"""
    pl_id = message.from_user.id
    if pl_id in pls.keys() and pls[pl_id].game is not None:
        answer_message = pls[pl_id].get_game_locations()
    else:
        answer_message = "Вы еще не в игре"
    await message.answer(answer_message)


@dp.message_handler(lambda message: message.text.startswith('/game'))
async def game_stat(message: types.Message):
    """Информация о текущей игре"""
    pl_id = message.from_user.id
    if pl_id in pls.keys() and pls[pl_id].game is not None:
        answer_message = pls[pl_id].get_game_info()
    else:
        answer_message = "Вы еще не в игре"
    await message.answer(answer_message)


@dp.message_handler(lambda message: message.text.startswith('test'))
async def new_round(message: types.Message):
    """Testing"""
    chat_id = 146076472
    #await message.answer_dice(emoji="🎲")
    with open('hello.jpg', 'rb') as photo:
        await bot.send_photo(chat_id, photo)
    keyboard = types.InlineKeyboardMarkup()
    
    keyboard.add(types.InlineKeyboardButton(text='Нажми меня', callback_data='button_pressed'))
    await bot.send_message(chat_id, 'Привет, мир!', reply_markup=keyboard)

@dp.errors_handler()
async def errors_handler(update: types.Update, exception: Exception):
    logging.error(f'Ошибка при обработке запроса {update}: {exception}')


async def send_message(message: str):
    await bot.send_message(146076472, message)

def test_log():
    logging.debug('Отладочное сообщение')
    logging.warning('Предупреждение')
    logging.error('Ошибка')
    logging.critical('Критическая ошибка')

if __name__ == '__main__':
   # asyncio.run(send_message('hi'))
    executor.start_polling(dp, skip_updates=True)


"""
146076472 (Oleg Eremin): You get 2 scores in round 5. Total: 2
{"id": 146076472, "is_bot": false, "first_name": "Oleg", "last_name": "Eremin", "username": "Oeremin", "language_code": "ru"}
"""