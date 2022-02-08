# MIT License
# 
# Copyright (c) 2021 MiscellaneousStuff
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
SQLite database containing all replays."""

import os
import json
import sqlite3
import math

CREATE_GAME_TABLE  = """CREATE TABLE games(
                        game_id INTEGER PRIMARY KEY,
                        duration REAL
                        )"""

CREATE_CHAMP_TABLE = """CREATE TABLE champs (
                        game_id INTEGER,
                        time REAL,
                        obj_type TEXT,
                        net_id INTEGER,
                        obj_id INTEGER,
                        name TEXT,
                        health REAL,
                        max_health REAL,
                        team INTEGER,
                        armour REAL,
                        mr REAL,
                        movement_speed REAL,
                        is_alive INTEGER,
                        position_x REAL,
                        position_y REAL,
                        position_z REAL,

                        is_moving INTEGER,
                        targetable INTEGER,
                        invulnerable INTEGER,
                        recallState INTEGER,

                        q_name TEXT,
                        q_level INTEGER,
                        q_cd FLOAT,
                        w_name TEXT,
                        w_level INTEGER,
                        w_cd FLOAT,
                        e_name TEXT,
                        e_level INTEGER,
                        e_cd FLOAT,
                        r_name TEXT,
                        r_level INTEGER,
                        r_cd FLOAT,
                        d_name TEXT,
                        d_level INTEGER,
                        d_cd FLOAT,
                        d_summoner_spell_type INTEGER,
                        f_name TEXT,
                        f_level INTEGER,
                        f_cd FLOAT,
                        f_summoner_spell_type INTEGER,

                        crit REAL,
                        critMulti REAL,
                        level INTEGER,
                        mana REAL,
                        max_mana REAL,
                        ability_haste REAL,
                        ap REAL,
                        lethality REAL,
                        experience REAL,
                        mana_regen REAL,
                        health_regen REAL,
                        attack_range REAL,

                        current_gold REAL,
                        total_gold REAL
                        )"""

CREATE_OBJ_TABLE   = """CREATE TABLE objects (
                        game_id INTEGER,
                        time REAL,
                        obj_type TEXT,
                        net_id INTEGER,
                        obj_id INTEGER,
                        name TEXT,
                        health REAL,
                        max_health REAL,
                        team INTEGER,
                        armour REAL,
                        mr REAL,
                        movement_speed REAL,
                        is_alive INTEGER,
                        position_x REAL,
                        position_y REAL,
                        position_z REAL,

                        is_moving INTEGER,
                        targetable INTEGER,
                        invulnerable INTEGER,
                        recallState INTEGER
                        )"""

CREATE_MISSILE_TABLE = """CREATE TABLE missiles (
                        game_id INTEGER,
                        time REAL,
                        obj_type TEXT,
                        net_id INTEGER,
                        obj_id INTEGER,
                        name TEXT,
                        health REAL,
                        max_health REAL,
                        team INTEGER,
                        armour REAL,
                        mr REAL,
                        movement_speed REAL,
                        is_alive INTEGER,
                        position_x REAL,
                        position_y REAL,
                        position_z REAL,

                        start_position_x REAL,
                        start_position_y REAL,
                        start_position_z REAL,
                        end_position_x REAL,
                        end_position_y REAL,
                        end_position_z REAL,
                        source_idx INTEGER,
                        destination_idx INTEGER
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
                cur.execute(f"""INSERT INTO champs VALUES (
                   {game_id},
                    {time},
                    '{table}',
                    {c["net_id"]},
                    {c["obj_id"]},
                    '{handle_str(c["name"])}',
                    {handle_nan(c["health"])},
                    {handle_nan(c["max_health"])},
                    {int(c["team"])},
                    {handle_nan(c["armour"])},
                    {handle_nan(c["mr"])},
                    {handle_nan(c["movement_speed"])},
                    {1 if c["is_alive"] else 0},
                    {handle_nan(c["position"]["x"])},
                    {handle_nan(c["position"]["y"])},
                    {handle_nan(c["position"]["z"])},

                    {1 if c["is_moving"] else 0},
                    {1 if c["targetable"] else 0},
                    {1 if c["invulnerable"] else 0},
                    {c["recallState"]},

                    '{c["Q"]["name"]}',
                    {c["Q"]["level"]},
                    {c["Q"]["cd"]},
                    '{c["W"]["name"]}',
                    {c["W"]["level"]},
                    {c["W"]["cd"]},
                    '{c["E"]["name"]}',
                    {c["E"]["level"]},
                    {c["E"]["cd"]},
                    '{c["R"]["name"]}',
                    {c["R"]["level"]},
                    {c["R"]["cd"]},
                    '{c["D"]["name"]}',
                    {c["D"]["level"]},
                    {c["D"]["cd"]},
                    {c["D"]["summoner_spell_type"]},
                    '{c["F"]["name"]}',
                    {c["F"]["level"]},
                    {c["F"]["cd"]},
                    {c["F"]["summoner_spell_type"]},
                    
                    {handle_nan(c["crit"])},
                    {handle_nan(c["crit_multi"])},
                    {handle_nan(c["level"])},
                    {handle_nan(c["mana"])},
                    {handle_nan(c["max_mana"])},
                    {handle_nan(c["ability_haste"])},
                    {handle_nan(c["ap"])},
                    {handle_nan(c["lethality"])},
                    {handle_nan(c["experience"])},
                    {handle_nan(c["mana_regen"])},
                    {handle_nan(c["health_regen"])},
                    {handle_nan(c["attack_range"])},

                    {handle_nan(c["current_gold"])},
                    {handle_nan(c["total_gold"])}
                    )""")
            
            elif table == "missiles":
                cur.execute(f"""INSERT INTO missiles VALUES (
                    {game_id},
                    {time},
                    '{table}',
                    {c["net_id"]},
                    {c["obj_id"]},
                    '{handle_str(c["name"])}',
                    {handle_nan(c["health"])},
                    {handle_nan(c["max_health"])},
                    {int(c["team"])},
                    {handle_nan(c["armour"])},
                    {handle_nan(c["mr"])},
                    {handle_nan(c["movement_speed"])},
                    {1 if c["is_alive"] else 0},
                    {handle_nan(c["position"]["x"])},
                    {handle_nan(c["position"]["y"])},
                    {handle_nan(c["position"]["z"])},

                    {handle_nan(c["start_pos"]["x"])},
                    {handle_nan(c["start_pos"]["y"])},
                    {handle_nan(c["start_pos"]["z"])},
                    {handle_nan(c["end_pos"]["x"])},
                    {handle_nan(c["end_pos"]["y"])},
                    {handle_nan(c["end_pos"]["z"])},
                    {int(c["src_id"])},
                    {int(c["dest_id"])}
                    )""")
            
            else:
                cur.execute(f"""INSERT INTO objects VALUES (
                    {game_id},
                    {time},
                    '{table}',
                    {c["net_id"]},
                    {c["obj_id"]},
                    '{handle_str(c["name"])}',
                    {handle_nan(c["health"])},
                    {handle_nan(c["max_health"])},
                    {int(c["team"])},
                    {handle_nan(c["armour"])},
                    {handle_nan(c["mr"])},
                    {handle_nan(c["movement_speed"])},
                    {1 if c["is_alive"] else 0},
                    {handle_nan(c["position"]["x"])},
                    {handle_nan(c["position"]["y"])},
                    {handle_nan(c["position"]["z"])},
                    {1 if c["is_moving"] else 0},
                    {1 if c["targetable"] else 0},
                    {1 if c["invulnerable"] else 0},
                    {c["recallState"]}
                    )""")

        except Exception as e:
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
            insert_objs(game_id, obs, cur, time, "turrets")
            insert_objs(game_id, obs, cur, time, "jungle")
            insert_objs(game_id, obs, cur, time, "missiles")
            insert_objs(game_id, obs, cur, time, "others")

def convert_dataset(json_path, db_dir):
    region, game_id = \
        os.path.basename(json_path).split(".json")[0].split("-")
    db_path = os.path.join(db_dir, f"{region}-{game_id}.db")

    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(CREATE_GAME_TABLE)
    cur.execute(CREATE_CHAMP_TABLE)
    cur.execute(CREATE_MISSILE_TABLE)
    cur.execute(CREATE_OBJ_TABLE)

    cur.execute("BEGIN;")

    try:
        insert_game(json_path, cur)
    except Exception as e:
        print(e)
    
    cur.execute("COMMIT;")

    con.close()