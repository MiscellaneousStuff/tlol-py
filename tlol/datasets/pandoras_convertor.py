# MIT License
# 
# Copyright (c) 2023 MiscellaneousStuff
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
"""Converts a directory of json replay files into either a single massive
SQLite database containing all replays. This script is for the T_T-Pandoras-Box
schema json replay files."""

import os
import json
import sqlite3
import math

CREATE_GAME_TABLE  = """CREATE TABLE games (
                        game_id INTEGER PRIMARY KEY,
                        duration REAL
                        )"""

CREATE_CHAMP_TABLE = """CREATE TABLE champs (
                        game_id INTEGER,
                        time REAL,
                        name TEXT,
                        hp REAL,
                        max_hp REAL,
                        mana REAL,
                        max_mana REAL,
                        armor REAL,
                        mr REAL,
                        ad REAL,
                        ap REAL,
                        level INTEGER,
                        atk_range REAL,
                        visible INTEGER,
                        team INTEGER,
                        pos_x REAL,
                        pos_z REAL,

                        q_name TEXT,
                        q_cd REAL,
                        w_name TEXT,
                        w_cd REAL,
                        e_name TEXT,
                        e_cd REAL,
                        r_name TEXT,
                        r_cd REAL,
                        d_name TEXT,
                        d_cd REAL,
                        f_name TEXT,
                        f_cd REAL
                        )"""

CREATE_MINIONS_TABLE = """CREATE TABLE minions (
                        game_id INTEGER,
                        time REAL,
                        name TEXT,
                        hp REAL,
                        max_hp REAL,
                        mana REAL,
                        max_mana REAL,
                        armor REAL,
                        mr REAL,
                        ad REAL,
                        ap REAL,
                        level INTEGER,
                        atk_range REAL,
                        visible INTEGER,
                        team INTEGER,
                        pos_x REAL,
                        pos_z REAL
                        )"""

CREATE_MISSILES_TABLE = """CREATE TABLE missiles (
                        game_id INTEGER,
                        time REAL,
                        name TEXT,
                        missile_name TEXT,
                        spell_name TEXT,
                        src_idx INTEGER,
                        dst_idx INTEGER,
                        start_pos_x REAL,
                        start_pos_z REAL,
                        end_pos_x REAL,
                        end_pos_z REAL,
                        pos_x REAL,
                        pos_z REAL
                        )"""

CREATE_TURRETS_TABLE = """CREATE TABLE turrets (
                        game_id INTEGER,
                        time REAL,
                        name TEXT,
                        hp REAL,
                        max_hp REAL,
                        mana REAL,
                        max_mana REAL,
                        armor REAL,
                        mr REAL,
                        ad REAL,
                        ap REAL,
                        level INTEGER,
                        atk_range REAL,
                        visible INTEGER,
                        team INTEGER,
                        pos_x REAL,
                        pos_z REAL
                        )"""

CREATE_MONSTERS_TABLE = """CREATE TABLE monsters (
                        game_id INTEGER,
                        time REAL,
                        name TEXT,
                        hp REAL,
                        max_hp REAL,
                        mana REAL,
                        max_mana REAL,
                        armor REAL,
                        mr REAL,
                        ad REAL,
                        ap REAL,
                        level INTEGER,
                        atk_range REAL,
                        visible INTEGER,
                        team INTEGER,
                        pos_x REAL,
                        pos_z REAL
                        )"""

def handle_nan(x):
    return 0 if math.isnan(x) else x
    
def handle_str(x):
    try:
        a = x.encode('ascii').decode('ascii')
        a = a.replace("'", "") # Sanitise 'others' objects with weird names
        return a
    except:
        return "N/A"

def insert_objs(game_id, obs, cur, time, table):
    for c in obs[table]:
        try:
            if table == "champs":
                s = f"""INSERT INTO champs VALUES (
                    {game_id},
                    {time},
                    '{handle_str(c["name"])}',
                    {handle_nan(c["hp"])},
                    {handle_nan(c["max_hp"])},
                    {handle_nan(c["mana"])},
                    {handle_nan(c["max_mana"])},
                    {handle_nan(c["armor"])},
                    {handle_nan(c["mr"])},
                    {handle_nan(c["ad"])},
                    {handle_nan(c["ap"])},
                    {handle_nan(c["level"])},
                    {handle_nan(c["atk_range"])},
                    {(1 if c["visible"] else 0)},
                    {handle_nan(c["team"])},
                    {handle_nan(c["pos_x"])},
                    {handle_nan(c["pos_z"])},
                    '{handle_str(c["q_name"])}',
                    {handle_nan(c["q_cd"])},
                    '{handle_str(c["w_name"])}',
                    {handle_nan(c["w_cd"])},
                    '{handle_str(c["e_name"])}',
                    {handle_nan(c["e_cd"])},
                    '{handle_str(c["r_name"])}',
                    {handle_nan(c["r_cd"])},
                    '{handle_str(c["d_name"])}',
                    {handle_nan(c["d_cd"])},
                    '{handle_str(c["f_name"])}',
                    {handle_nan(c["f_cd"])}
                    )"""
                cur.execute(s)
            elif table == "minions":
                s = f"""INSERT INTO minions VALUES (
                    {game_id},
                    {time},
                    '{handle_str(c["name"])}',
                    {handle_nan(c["hp"])},
                    {handle_nan(c["max_hp"])},
                    {handle_nan(c["mana"])},
                    {handle_nan(c["max_mana"])},
                    {handle_nan(c["armor"])},
                    {handle_nan(c["mr"])},
                    {handle_nan(c["ad"])},
                    {handle_nan(c["ap"])},
                    {handle_nan(c["level"])},
                    {handle_nan(c["atk_range"])},
                    {(1 if c["visible"] else 0)},
                    {handle_nan(c["team"])},
                    {handle_nan(c["pos_x"])},
                    {handle_nan(c["pos_z"])}
                    )"""
                cur.execute(s)
            elif table == "missiles":
                s = f"""INSERT INTO missiles VALUES (
                    {game_id},
                    {time},
                    '{handle_str(c["name"])}',
                    '{handle_str(c["missile_name"])}',
                    '{handle_str(c["spell_name"])}',
                    {handle_nan(c["src_idx"])},
                    {handle_nan(c["dst_idx"])},
                    {handle_nan(c["start_pos_x"])},
                    {handle_nan(c["start_pos_z"])},
                    {handle_nan(c["end_pos_x"])},
                    {handle_nan(c["end_pos_z"])},
                    {handle_nan(c["pos_x"])},
                    {handle_nan(c["pos_z"])}
                    )"""
                cur.execute(s)
            elif table == "turrets":
                s = f"""INSERT INTO turrets VALUES (
                    {game_id},
                    {time},
                    '{handle_str(c["name"])}',
                    {handle_nan(c["hp"])},
                    {handle_nan(c["max_hp"])},
                    {handle_nan(c["mana"])},
                    {handle_nan(c["max_mana"])},
                    {handle_nan(c["armor"])},
                    {handle_nan(c["mr"])},
                    {handle_nan(c["ad"])},
                    {handle_nan(c["ap"])},
                    {handle_nan(c["level"])},
                    {handle_nan(c["atk_range"])},
                    {(1 if c["visible"] else 0)},
                    {handle_nan(c["team"])},
                    {handle_nan(c["pos_x"])},
                    {handle_nan(c["pos_z"])}
                    )"""
                cur.execute(s)
            elif table == "monsters":
                s = f"""INSERT INTO monsters VALUES (
                    {game_id},
                    {time},
                    '{handle_str(c["name"])}',
                    {handle_nan(c["hp"])},
                    {handle_nan(c["max_hp"])},
                    {handle_nan(c["mana"])},
                    {handle_nan(c["max_mana"])},
                    {handle_nan(c["armor"])},
                    {handle_nan(c["mr"])},
                    {handle_nan(c["ad"])},
                    {handle_nan(c["ap"])},
                    {handle_nan(c["level"])},
                    {handle_nan(c["atk_range"])},
                    {(1 if c["visible"] else 0)},
                    {handle_nan(c["team"])},
                    {handle_nan(c["pos_x"])},
                    {handle_nan(c["pos_z"])}
                    )"""
                cur.execute(s)

        except Exception as e:
            print("ERR:", s)
            print(e, handle_str(c["name"]))
            print('check for \\u:', "\\u" in c["name"])
            print(json.dumps(c, indent=4, sort_keys=True))
            
def insert_game(cur_fi, cur):
    game_id = os.path.basename(cur_fi).split(".")[0].split("-")[1]

    with open(cur_fi, encoding="latin-1") as f:
        obj = json.loads(f.read())

        duration = obj[-1]["time"]
        cur.execute(f'INSERT INTO games VALUES({game_id}, {duration})')

        for obs in obj:
            time = obs["time"]
            insert_objs(game_id, obs, cur, time, "champs")
            insert_objs(game_id, obs, cur, time, "minions")
            insert_objs(game_id, obs, cur, time, "missiles")
            insert_objs(game_id, obs, cur, time, "turrets")
            insert_objs(game_id, obs, cur, time, "monsters")

def convert_dataset(json_path, db_dir, big_int=False):
    region, game_id = \
        os.path.basename(json_path).split(".json")[0].split("-")
    db_path = os.path.join(db_dir, f"{region}-{game_id}.db")

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    cur.execute(CREATE_GAME_TABLE)
    cur.execute(CREATE_CHAMP_TABLE)
    cur.execute(CREATE_MINIONS_TABLE)
    cur.execute(CREATE_MISSILES_TABLE)
    cur.execute(CREATE_TURRETS_TABLE)
    cur.execute(CREATE_MONSTERS_TABLE)

    cur.execute("BEGIN;")

    try:
        insert_game(json_path, cur)
    except Exception as e:
        import traceback
        print("Err:", e, traceback.format_exc())
    
    cur.execute("COMMIT;")

    con.close()