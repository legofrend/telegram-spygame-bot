import os
import re
from typing import Dict, List, Tuple

import sqlite3

BASE_RES_PATH = 'res'

conn = sqlite3.connect(os.path.join("db", "spygame.db"))
cursor = conn.cursor()


def insert(table: str, column_values: Dict):
    columns = ', '.join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholders = ", ".join("?" * len(column_values.keys()))
    cursor.executemany(
        f"INSERT INTO {table} "
        f"({columns}) "
        f"VALUES ({placeholders})",
        values)
    conn.commit()


def fetchall(table: str, columns: List[str], where=None, distinct=False) -> List[Tuple]:
    columns_joined = ", ".join(columns)
    sql = f"SELECT {'DISTINCT' if distinct else ''} {columns_joined} FROM {table}"
    if where:
        sql += ' WHERE ' + ' AND '.join(list(f'{k} = "{v}"' for k, v in where.items()))
    cursor.execute(sql)
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    return result


def delete(table: str, row_id: int) -> None:
    row_id = int(row_id)
    cursor.execute(f"delete from {table} where id={row_id}")
    conn.commit()


def get_cursor():
    return cursor


def load_from_file(filename: str):
    """Инициализирует БД"""
    sql = 'INSERT INTO location  (set_name, lang, location, roles) VALUES \n'
    values = []
    with open(filename, "r", encoding="utf-8") as f:
        l1 = f.readline().strip()
        sep = ': ' if re.search(': ', l1) else '\t'
        (lang, set_name) = l1.split(sep)
        for line in f:
            (loc, roles) = line.strip().split(sep)
            values.append(f'("{set_name}", "{lang}", "{loc}", "{roles}")')
    sql += ',\n'.join(values) + ';'
    print(sql)
    cursor.executescript(sql)
    conn.commit()


def _init_db():
    """Инициализирует БД"""
    with open("createdb.sql", "r", encoding="utf-8") as f:
        sql = f.read()
    # print(sql)
    cursor.executescript(sql)
    conn.commit()


def check_db_exists():
    """Проверяет, инициализирована ли БД, если нет — инициализирует"""
    cursor.execute("SELECT name FROM sqlite_master "
                   "WHERE type='table' AND name='round'")
    table_exists = cursor.fetchall()
    if table_exists:
        return
    _init_db()
    for filename in os.listdir(BASE_RES_PATH):
        if filename.startswith('.'):
            continue
        load_from_file(os.path.join(BASE_RES_PATH, filename))

def load_all_files():
    for filename in os.listdir(BASE_RES_PATH):
        if filename.startswith('.'):
            continue
        print(os.path.join(BASE_RES_PATH, filename))
        load_from_file(os.path.join(BASE_RES_PATH, filename))

# test()

check_db_exists()

