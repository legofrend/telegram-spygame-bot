""" Работа с пользователем и механика игры"""
import datetime as dt
import logging
import string

import pytz
import re
import random

import db
import exceptions
from states import states

CONST_SPY = 'шпион'
DEFAULT_SET = 'Основной'
commands = {'new', 'join', 'quit', 'close', 'round', 'finish', 'loc', 'game', 'stat'}
winner_type_spy = {'spy_1', 'spy_2', 'spy_3'}
winner_type = winner_type_spy.union({'not_spy', 'pl_id', 'nobody'})
WINNER_TYPE_SPY = 1  # spy wasn't uncovered
WINNER_TYPE_SPY_GL = 2  # spy wasn't uncovered and he guested location
WINNER_TYPE_SPY_WS = 3  # spy wasn't uncovered and people chose wrong spy
WINNER_TYPE_PLP_NO = 4  # spy was uncovered by himself choosing wrong location
WINNER_TYPE_PLP_YES = 5  # spy was uncovered by a player

logging.basicConfig(level=logging.INFO)
#games = {}
#pls = {}


def _is_spy_win(winner_type: int) -> bool:
    return winner_type < 4


def _win_score(winner_type: int, is_spy: bool, winner=False) -> int:
    if is_spy:
        if WINNER_TYPE_SPY == winner_type:
            score = 2
        elif WINNER_TYPE_SPY_GL == winner_type:
            score = 4
        elif WINNER_TYPE_SPY_WS == winner_type:
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


class Location():
    """Структура локации"""

    def __init__(self, id: int):
        """Создаем из БД инфо по локации """
        l = db.fetchone('location', 'id location roles pic'.split(), id)
        self.id = l['id']
        self.name = l['location']
        self.roles = l['roles'].split(',')
        self.pic = l['pic']

        random.shuffle(self.roles)


class Round():
    """Структура раунда игры"""

    #    game: Game
    def __init__(self, game: str, round_nbr: int, location: Location, spy: int):
        self.round_nbr = round_nbr
        self.game_name = game
        self.started = _get_now_datetime()
        self.location = location
        self.spy = spy
        self.roles = {}
        self.dur_min = 7
        self.finish = self.started + dt.timedelta(minutes=self.dur_min)
        self.in_progress = 1
        self.winner_type = 0
        self.winner = 0

    def log(self):
        """Save round results to DB"""


class Game():
    """Структура игры"""
    _games = {}

    @classmethod
    def find(cls, game_name: str):
        if not game_name or game_name not in cls._games.keys():
            return None
        return cls._games[game_name]

    @staticmethod
    def suggest_name(game_name='', n=6) -> str:
        suggested_name = game_name + ''.join(random.choices(string.ascii_uppercase + string.digits, k=n))
        return suggested_name

    def __init__(self, name: str, admin, set_name=None):
        """Create new game"""
        self.name = name
        self.players = {admin.id: admin}
        self.scores = {admin.id: 0}
        self.set_name = set_name if set_name else DEFAULT_SET
        l = db.fetchuniq('location', ['id'], 'set_name', set_name)
        self.loc_list = [item['id'] for item in l]
        random.shuffle(self.loc_list)
        self.round_nbr = 0
        self.round = None
        self._games[name] = self

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
        loc_id = self.loc_list[self.round_nbr - 1]
        loc = Location(loc_id)
        spy = random.choice(list(self.players.keys()))
        self.round = Round(self.name, self.round_nbr, loc, spy)
        start_str = self.round.started.strftime('%Y-%m-%d %H:%M:%S')
        spy_name = self.players[spy].full_name
        logging.info(f'Starting new round at {start_str}, location {loc.name}, spy is {spy_name}')
        role_index = 0
        for pl in self.players.keys():
            pl_name = self.players[pl].full_name
            if pl == spy:
                role = CONST_SPY
            else:
                if role_index > len(loc.roles): role_index = 0
                role = loc.roles[role_index]
                role_index += 1
            self.round.roles[pl] = role

            logging.info(f'{pl} ({pl_name}): role is {role}')
        return self.round

    def finish_round(self, winner_type: int, winner=0) -> list:
        """Round is finished"""
        logging.info(f'Finishing round with winner_type = {winner_type} and winner = {winner}')
        self.round.finished = _get_now_datetime()
        self.round.in_progress = 0
        self.round.winner_type = winner_type
        self.round.winner = winner
        spy = self.round.spy
        results = []
        for pl in self.players.keys():
            pl_name = self.players[pl].full_name
            score = _win_score(winner_type, pl == spy, pl == winner)
            self.scores[pl] += score
            results.append((self.players[pl].full_name, score, self.scores[pl]))
            logging.info(
                f'{pl} ({pl_name}): get {score} scores in round {self.round_nbr}. Total: {self.scores[pl]}')
        return results

    def get_info(self) -> list:
        """Get info about game: players with scores, current round"""
        spls = {k: v for k, v in sorted(self.scores.items(), key=lambda item: item[1], reverse=True)}

        result = list((self.players[k].full_name, v) for (k, v) in spls.items())
        return result


    def get_locations(self) -> list:
        """Get all locations in a game"""
        l = db.fetchuniq('location', ['location'], 'set_name', self.set_name)
        loc_list = [item['location'] for item in l]
        loc_list.sort()
        return loc_list


class Player():
    """Структура игрока"""
    _pls = {}

    @classmethod
    def auth(cls, user):
        if user.id in cls._pls.keys():
            return cls._pls[user.id]
        else:
            return cls(user)

    def __init__(self, user):
        (self.id, self.full_name, self.language_code) = user if isinstance(user, tuple) \
            else (user.id, user.full_name, user.language_code)
        self.state = 'init'
        self.game = None
        self.is_admin = False
        self._pls[self.id] = self

    def create_game(self, game_name: str, set_name=DEFAULT_SET) -> Game:
        self.game = Game(game_name, self, set_name)
        self.is_admin = True
        self.state = 'admin_game_created_round_no'
        return self.game

    def join_game(self, game_name: str) -> int:
        if not game_name:
            self.state = 'joining_game_need_name'
            return 1

        game = Game.find(game_name)
        if not game:
            logging.warning(f'Can\'t find game {game_name}')
            return 1

        self.game = game
        self.is_admin = False
        self.game.join(self)
        self.state = 'joined_game'
        logging.info(f'{self.full_name} joined the game {game_name}')
        return 0

    def quit_game(self):
        """Quit from the game for a player"""
        if self.game is None:
            logging.warning('{self.id} {self.full_name} trying to quit from a game, when it\'s None')
            return 1

        if self.is_admin:
            self.game.close()
        else:
            self.game.quit(self.id)
        return 0

    def check_command(self, comm: str, arg=None):
        if comm in ['new', 'create', 'join']:
            if self.game is not None:
                return 'IN_GAME'
            g = Game.find(arg)
            if comm == 'join' and g is None:
                return 'GAME_NOT_FOUND'
            elif comm in ['new', 'create'] and g is not None:
                return 'GAME_EXIST'
            else:
                return ''
        elif comm in ['loc', 'game', 'quit']:
            return 'NO_GAME' if self.game is None else ''
        elif comm in ['round', 'finish']:
            if self.game is None:
                return 'NO_GAME'
            if not self.is_admin:
                return 'NOT_ADMIN'
            return ''

    def check_state(self, cmd: str):
        state = states[self.state]
        if cmd not in state['cmd']:
            return "You can't do this"
        else:
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
        pl = Player((i, names[i-1], 'ru'))
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



test()

