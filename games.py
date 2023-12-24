""" Работа с пользователем и механика игры"""
import datetime as dt
import logging
import string

import pytz
import re
import random

import db
from msg import _msg
import keyboards as kb
import exceptions

CONST_SPY = 'шпион'
DEFAULT_SET = 'Основной'
MAX_LOC_SET_SIZE = 30
ROUND_TIME_MIN = 7
SUPPORT_LANGUAGES = {'ru'}
commands = {'new', 'join', 'quit', 'close', 'round', 'finish', 'winner', 'loc', 'game', 'stat', 'change'}
_winner_type_spy = {'spy_1', 'spy_2', 'spy_3'}
_winner_type = _winner_type_spy.union({'not_spy', 'pl_id', 'nobody'})

logging.basicConfig(level=logging.INFO)


def _is_spy_win(winner_type: str) -> bool:
    return winner_type in _winner_type_spy


def _win_score(winner_type: str, is_spy: bool, winner=False) -> int:
    if is_spy:
        if winner_type in ['spy_1']:
            score = 2
        elif winner_type in ['spy_2', 'spy_3']:
            score = 4
        else:
            score = 0
    elif winner:
        score = 2
    else:
        if _is_spy_win(winner_type):
            score = 0
        else:
            score = 1
    return score


class Location:
    """Структура локации"""

    def __init__(self, id: int):
        """Создаем из БД инфо по локации """
        l = db.fetchall('location', 'id location roles filename file_id'.split(), {'id': id})[0]
        self.id = l['id']
        self.name = l['location']
        self.roles = l['roles'].split(', ')
        self.pic = l['filename']
        self.pic_id = l['file_id']

        random.shuffle(self.roles)

    def load_from_file(self, filename: str):
        db.load_from_file(filename)

    def update_pic_id(self, pic_id: str):
        db.update('location', {'file_id': pic_id}, {'filename': self.pic})
        self.pic_id = pic_id

class Round():
    """Структура раунда игры"""

    #    game: Game
    def __init__(self, game, location: Location, spy: int):
        self.game = game
        self.round_nbr = game.round_nbr
        self.started = _get_now_datetime()
        self.location = location
        self.spy = spy
        self.roles = {}
        self.dur_min = ROUND_TIME_MIN
        self.finished = self.started + dt.timedelta(minutes=self.dur_min)
        self.in_progress = 1
        self.winner_type = 0
        self.details = ''

    def finish(self):
        logging.info(f'Finishing round')
        self.finished = _get_now_datetime()
        self.in_progress = 0

    def set_winner(self, winner_type: str):
        self.winner_type = winner_type
        winner = int(winner_type) if winner_type.isdigit() else 0
        results = []
        game = self.game
        for pl in game.players.keys():
            pl_name = game.players[pl].full_name
            score = _win_score(winner_type, pl == self.spy, pl == winner)
            game.scores[pl] += score
            results.append((pl_name, score, game.scores[pl]))
            logging.info(
                f'{pl} ({pl_name}): get {score} scores in round {self.round_nbr}. Total: {game.scores[pl]}')
            self.details += f'{pl}\t{pl_name}\t{score}\t{game.scores[pl]}\n'
        self.save_to_db()
        return results

    def save_to_db(self):
        """Save round results to DB"""
        inserted_row_id = db.insert('round', {
            'admin_id': self.game.admin.id,
            'game_id': self.game.name_id,
            'round_nbr': self.round_nbr,
            'started': self.started,
            'finished': self.finished,
            'location_id': self.location.id,
            'spy_id': self.spy,
            'winner_type': self.winner_type,
            'details': self.details
        })


class Game():
    """Структура игры"""
    _games = {}

    @classmethod
    def find(cls, game_name: str):
        if not game_name or game_name not in cls._games.keys():
            return None
        return cls._games[game_name]

    def __init__(self, name: str, admin, set_name=None):
        """Create new game"""
        self.name = name
        self.name_id = f'{name}:{_get_now_formatted()}'
        self.admin = admin
        self.players = {admin.id: admin}
        self.scores = {admin.id: 0}
        self.round_nbr = 0
        self.round = None
        self._games[name] = self
        self.loc_list = []
        self.set_name = ''
        self.load_locations(set_name)

    def load_locations(self, set_name):
        self.set_name = set_name
        loc_list = db.fetchall('location', ['id', 'location'], {'set_name': set_name})
        # loc_list = [item['id'] for item in l]
        random.shuffle(loc_list)
        self.loc_list = self.loc_list[:self.round_nbr] + loc_list[:MAX_LOC_SET_SIZE]


    def __del__(self):
        n = len(Game._games)
        logging.info(f'Game {self.name} deleted. Keep in memory {n} games')

    def join(self, pl):
        """Join to the game player with id"""
        self.players[pl.id] = pl
        if pl.id not in self.scores.keys():
            self.scores[pl.id] = 0

    def quit(self, pl):
        """Quit from the game for player with id"""
        del self.players[pl]
        del Player._pls[pl]

    def close(self):
        """Close game for all players in it"""
        for id in self.players.keys():
            del Player._pls[id]

        del self._games[self.name]

    def start_round(self):
        """Start new round"""
        self.round_nbr += 1
        i = (self.round_nbr - 1) % len(self.loc_list)
        loc_id = self.loc_list[i]['id']
        loc = Location(loc_id)
        spy = random.choice(list(self.players.keys()))
        self.round = Round(self, loc, spy)
        role_index = 0
        for pl in self.players.keys():
            if pl == spy:
                role = CONST_SPY
            else:
                if role_index >= len(loc.roles): role_index = 0
                role = loc.roles[role_index]
                role_index += 1
            self.round.roles[pl] = role

            logging.debug(f'{pl} ({self.players[pl].full_name}): role is {role}')

        start_str = self.round.started.strftime('%Y-%m-%d %H:%M:%S')
        logging.debug(f'Started new round at {start_str}, location {loc.name}, spy is {self.players[spy].full_name}')
        return self.round

    def finish_round(self, winner_type: str, winner=0) -> list:
        """Round is finished"""
        logging.info(f'Finishing round with winner_type = {winner_type} and winner = {winner}')
        self.round.finished = _get_now_datetime()
        self.round.in_progress = 0
        self.round.winner_type = winner_type
        winner = int(winner_type) if winner_type.isdigit() else 0
        spy = self.round.spy
        results = []
        for pl in self.players.keys():
            pl_name = self.players[pl].full_name
            score = _win_score(winner_type, pl == spy, pl == winner)
            self.scores[pl] += score
            results.append((pl_name, score, self.scores[pl]))
            logging.info(
                f'{pl} ({pl_name}): get {score} scores in round {self.round_nbr}. Total: {self.scores[pl]}')
            self.round.details += f'{pl}:{pl_name}:{score}:{self.scores[pl]}\n'
        self.round.save_to_db()
        return results

    def get_info(self) -> list:
        """Get info about game: players with scores, current round"""
        spls = {k: v for k, v in sorted(self.scores.items(), key=lambda item: item[1], reverse=True)}

        result = list((self.players[k].full_name, v) for (k, v) in spls.items())
        return result

    def get_locations(self) -> tuple:
        """Get all locations in a game"""
        loc_list = [item['location'] for item in self.loc_list]
        loc_past = loc_list[:self.round_nbr]
        loc_future = loc_list[self.round_nbr:]
        loc_future.sort()
        return loc_past, loc_future

    def get_locations_old(self) -> list:
        """Get all locations in a game"""
        # ToDo fix bug for countries, there is limit locations in a game, not all needed
        l = db.fetchall('location', ['location'], {'set_name': self.set_name})
        loc_list = [item['location'] for item in l]
        loc_list.sort()
        return loc_list

    def get_loc_sets(self, lng: str = 'ru'):
        l = db.fetchall('location', ['set_name'], {'lang': lng}, True)
        loc_set_list = [item['set_name'] for item in l]
        loc_set_list.sort()
        return loc_set_list

    def change_loc_set(self, set_name: str):
        self.load_locations(set_name)

class Player():
    """Структура игрока"""
    _pls = {}

    @staticmethod
    def suggest_name(game_name='', n=6) -> str:
        suggested_name = game_name + ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))
        return suggested_name

    @classmethod
    def auth(cls, user):
        if isinstance(user, int):
            return cls._pls[user]
        if user.id in cls._pls.keys():
            return cls._pls[user.id]
        else:
            return cls(user)

    def __init__(self, user):
        (self.id, self.full_name, self.language_code) = user if isinstance(user, tuple) \
            else (user.id, user.full_name, user.language_code)
        if self.language_code not in SUPPORT_LANGUAGES:
            self.language_code = 'ru'
        self.game = None
        self.is_admin = False
        self._pls[self.id] = self
        self.kb = kb.kbs[self.language_code]['kb_init']

    def create_game(self, game_name: str, set_name=DEFAULT_SET) -> str:
        """Creating new game"""
        if err_msg := self.check_command('new', game_name):
            return err_msg

        self.game = Game(game_name, self, set_name)
        self.is_admin = True
        self.kb = kb.kbs[self.language_code]['kb_admin']
        return f"Cоздал игру: `{game_name}`"

    def join_game(self, game_name: str) -> str:
        if err_msg := self.check_command("join", game_name):
            return err_msg

        self.game = Game.find(game_name)
        self.is_admin = False
        self.game.join(self)
        logging.info(f'{self.full_name} joined the game {game_name}')
        self.kb = kb.kbs[self.language_code]['kb_player']
        return f'Вы присоединились к игре {game_name}, дождитесь старта раунда. \
            Посмотреть кто в игре можно командой /game'

    def quit_game(self):
        """Quit from the game for a player"""
        if err_msg := self.check_command("quit"):
            return err_msg

        self.game.close() if self.is_admin else self.game.quit(self.id)
        self.kb = kb.kbs[self.language_code]['kb_init']
        return f'Вы вышли из игры'

    def start_round(self):
        """Запускает новый раунд"""
        if err_msg := self.check_command("round"):
            return err_msg

        r = self.game.start_round()
        start_str = r.started.strftime("%H:%M:%S")
        finish_str = r.finished.strftime("%H:%M:%S")
        msg = f"Раунд {r.round_nbr}: {start_str} - {finish_str}\n"

        # prepare messages for all players as list
        msg_list = {}
        for pl_id, role in r.roles.items():
            loc_name = "???" if r.spy == pl_id else r.location.name
            msg_list[pl_id] = msg + f"Место: {loc_name}\nВы: {role}"
            logging.info(f"{pl_id}: {msg_list[pl_id]}")
        self.kb = kb.kbs[self.language_code]['kb_admin_2']
        return msg_list

    def finish_round(self):
        """Round finish Player class"""
        if err_msg := self.check_command("finish"):
            return err_msg

        self.game.round.finish()
        answer_message = f"Раунд {self.game.round_nbr} закончен\nКто победил?"
        self.kb = kb.pl2kb(self.game.players, self.language_code)
        return answer_message

    def set_winner(self, winner_type: str):
        """Round finish Player class"""
        if err_msg := self.check_command("winner", winner_type):
            return err_msg

        results = self.game.round.set_winner(winner_type)
        answer_message = ('Шпион победил' if _is_spy_win(winner_type) else 'Шпион проиграл') + '\n'
        for (name, sc, tsc) in results:
            answer_message += f"{name}: {sc} ({tsc})\n"
        self.kb = kb.kbs[self.language_code]['kb_admin']
        return answer_message

    def list_loc(self):
        """Выводит список локаций"""
        if err_msg := self.check_command("loc"):
            return err_msg
        (loc_past, loc_future) = self.game.get_locations()
        return (f'Список мест\nБыли {len(loc_past)}: ' + ', '.join(loc_past) +
                f'\nОстались {len(loc_future)}: ' + ', '.join(loc_future))


    def list_loc_set(self):
        """Выводит список локаций"""
        if err_msg := self.check_command("change"):
            return

        return self.game.get_loc_sets()

    def change_loc_set(self, set_name: str):
        self.game.change_loc_set(set_name)
        return f'Изменил набор мест: {set_name}'

    def game_info(self):
        """Информация о текущей игре"""
        if err_msg := self.check_command('game'):
            return err_msg

        g = self.game
        pl_nbr = len(g.players)
        info = g.get_info()
        answer_message = f'Игра {g.name}, раунд {g.round_nbr}, игроков {pl_nbr}, очки:\n'
        for (name, score) in info:
            answer_message += f"{name}: {score}\n"
        return answer_message

    def _log_action(self, comm: str):
        """Save round results to DB"""
        name_id = self.game.name_id if self.game else ''
        inserted_row_id = db.insert('log', {
            'datetime_stamp': _get_now_datetime(),
            'user_id': self.id,
            'game_id': name_id,
            'action': comm
        })

    def check_command(self, comm: str, arg=None):
        self._log_action(comm)
        if comm in ['new', 'create', 'join']:
            if self.game is not None:
                return _msg('IN_GAME', self)
            g = Game.find(arg)
            if comm == 'join' and g is None:
                return _msg('GAME_NOT_FOUND', self)
            elif comm in ['new', 'create'] and g is not None:
                return _msg('GAME_EXIST', self)
            else:
                return ''
        elif comm in ['loc', 'game', 'quit']:
            return _msg('NO_GAME', self) if self.game is None else ''
        elif comm in ['change']:
            return _msg('NOT_ADMIN', self) if not self.is_admin else ''
        elif comm in ['round', 'finish', 'winner']:
            if self.game is None:
                return _msg('NO_GAME', self)
            if not self.is_admin:
                return _msg('NOT_ADMIN', self)
            if comm == 'winner' and not (arg in _winner_type or arg.isdigit()):
                return _msg('emsg_unknown_winner_type', self)
            return ''


def _get_now_formatted() -> str:
    """Возвращает сегодняшнюю дату строкой"""
    return _get_now_datetime().strftime('%Y-%m-%d %H:%M:%S')


def _get_now_datetime() -> dt.datetime:
    """Возвращает сегодняшний datetime с учётом времненной зоны Мск."""
    tz = pytz.timezone('Europe/Moscow')
    now = dt.datetime.now(tz)
    return now


def test():
    names = ['Viktor', 'Ira', 'Ivan', 'Kirill']
    admin = None
    for i in range(1, 5):
        pl = Player((i, names[i - 1], 'ru'))
        if 1 == i:
            pl.create_game('test')
            admin = pl
        else:
            pl.join_game('test')

    print(admin.game.get_locations())

    for i in range(1, 6):
        admin.game.start_round()
        admin.game.finish_round(i)

    print(admin.game.get_info())

# test()
