""" Работа с пользователем и механика игры"""
import datetime
import logging

import pytz
#import re
import random

import db
import exceptions

CONST_SPY = 'шпион'
WINNER_TYPE_SPY = 1   # spy wasn't uncovered
WINNER_TYPE_SPY_GL = 2   # spy wasn't uncovered and he guested location
WINNER_TYPE_SPY_WS = 3   # spy wasn't uncovered and people chose wrong spy
WINNER_TYPE_PLP_NO = 4   # spy was uncovered by himself choosing wrong location
WINNER_TYPE_PLP_YES = 5   # spy was uncovered by a player

def _is_spy_win(winner_type: int) -> bool:
    return winner_type < 4

def _win_score(winner_type: int, is_spy: bool, winner = False) -> int:
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

DEFAULT_SET = 'Основной'

games = {}
pls = {}

class Location():
    """Структура локации"""
    def __init__(self, id:int):
        """Создаем из БД инфо по локации """
        l = db.fetchone("location", "id location roles pic".split(), id)
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
        self.finished = None
        self.winner_type = 0
        self.winner = 0

    def log(self):
        """Save round results to DB"""


class Game():
    """Структура игры"""

    def __init__(self, name: str, owner: int, set_name: str):
        """Create new game"""
        self.name = name
        self.owner = owner
        self.players = {owner: 0}
        self.set_name = set_name
        l = db.fetchuniq("location", ["id"], "set_name", set_name)
        self.loc_list = [item['id'] for item in l]
        random.shuffle(self.loc_list)
        self.round_nbr = 0
        self.round = None
        games[name] = self

    def __del__(self):
        print(f"Game {self.name} deleted")

    def join(self, pl_id: int):
        """Join to the game player with id"""
        self.players[pl_id] = 0

    def quit(self, pl_id: int):
        """Quit from the game for player with id"""
        del self.players[pl_id]
        del pls[pl_id]

    def close(self):
        """Close game for all players in it"""
        for id in self.players.keys():
            del pls[id]

        del games[self.name]

    def start_round(self):
        """Quit from the game for player with id"""
        self.round_nbr += 1
        loc_id = self.loc_list[self.round_nbr-1]
        loc = Location(loc_id)
        spy = random.choice(list(self.players.keys()))
        self.round = Round(self.name, self.round_nbr, loc, spy)
        start_str = self.round.started.strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"Starting new round at {start_str}, location {loc.name}, spy is {pls[spy].full_name}")
        role_index = 0
        for pl in self.players.keys():
            pl_name = pls[pl].full_name
            if pl == spy:
                role = CONST_SPY
            else:
                if role_index > len(loc.roles): role_index = 0
                role = loc.roles[role_index]
                role_index += 1
            self.round.roles[pl] = role
#            print(f"{pl} ({pl_name}): You are {role} in {loc.name}")


    def finish_round(self, winner_type: int, winner = 0):
        """Round is finished"""
        print("Finishing round")
        self.round.finished = _get_now_datetime()
        self.round.winner_type = winner_type
        self.round.winner = winner
        spy = self.round.spy
        for pl in self.players.keys():
            pl_name = pls[pl].full_name
            score = _win_score(winner_type, pl == spy, pl == winner)
            self.players[pl] += score
            logging.info(f"{pl} ({pl_name}): You get {score} scores in round {self.round_nbr}. Total: {self.players[pl]}")

    def get_info(self) -> str:
        """Get info about game: players with scores, current round"""
        pl_nbr = len(self.players)
        msg = f'Игра {self.name}, раунд {self.round_nbr}, игроков {pl_nbr}, очки:\n'
        spls = {k: v for k, v in sorted(self.players.items(), key=lambda item: item[1], reverse=True)}

        for (k, v) in spls.items():
            msg += f'{pls[k].full_name}: {v}\n'

        return msg

    def get_locations(self) -> str:
        """Get all locations in a game"""
        l = db.fetchuniq("location", ["location"], "set_name", self.set_name)
        loc_list = [item['location'] for item in l]
        loc_list.sort()
        return ", ".join(loc_list)


class Player():
    """Структура игрока"""

    def __init__(self, tg_id: int, full_name: str, lang = "RU"):
        self.tg_id = tg_id
        self.full_name = full_name
        self.lang = lang
        self.game = None
        self.is_owner = False
        pls[tg_id] = self

    def create_game(self, game_name: str, set_name = DEFAULT_SET) -> Game:
        self.game = Game(game_name, self.tg_id, set_name)
        self.is_owner = True
        return self.game

    def join_game(self, game_name: str) -> str:
        if game_name in games:
            self.game = games[game_name]
            self.game.join(self.tg_id)
            msg = "Вы присоединились к игре: " + game_name
        else:
            msg = "Не найду игры: "+game_name
        return msg

    def quit(self):
        """Quit from the game for a player"""
        if self.game is None:
            print("You are not in any game yet")
            return 0

        if self.is_owner:
            self.game.close()
        else:
            self.game.quit(self.tg_id)


    def start_round(self):
        """Start new round"""
        if self.game is None or self.is_owner == 0:
            print("Create a game first")
            return
        self.game.start_round()


    def finish_round(self, winner_type: int, winner = 0):
        """Round is finished"""
        if self.game is None or self.is_owner == 0:
            print("Create a game first")
            return
        self.game.finish_round(winner_type, winner)

    def get_game_info(self):
        """Send to player info about game"""
        if self.game is None:
            print("Create a game first")
            return
        return self.game.get_info()

    def get_game_locations(self):
        """Send to player info about available locations in the game"""
        if self.game is None:
            print("Create a game first")
            return
        return self.game.get_locations()

def _get_now_formatted() -> str:
    """Возвращает сегодняшнюю дату строкой"""
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")


def _get_now_datetime() -> datetime.datetime:
    """Возвращает сегодняшний datetime с учётом времненной зоны Мск."""
    tz = pytz.timezone("Europe/Moscow")
    now = datetime.datetime.now(tz)
    return now

def test():
    pl1 = Player(1, "Oleg")
    pl2 = Player(2, "Ira")
    pl3 = Player(3, "Borya")
    pl4 = Player(4, "Katya")
    pl1.create_game("test")
    pl2.join_game("test")
    pl3.join_game("test")
    pl4.join_game("test")

    pl1.start_round()
    pl1.finish_round(WINNER_TYPE_SPY_GL)
    pl1.start_round()
    pl1.finish_round(WINNER_TYPE_SPY)
    pl1.start_round()
    pl1.finish_round(WINNER_TYPE_PLP_NO)
    pl1.start_round()
    pl1.finish_round(WINNER_TYPE_PLP_YES, 2)

#    msg = pl1.get_game_info()
    msg = pl2.get_game_locations()
    print(msg)

#test()

