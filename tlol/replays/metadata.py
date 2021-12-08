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
"""Creates an SQLite database filled with the metadata of all of the replay
files within a directory."""

import json
import os
import sqlite3

CREATE_GAME_TABLE = """CREATE TABLE games
                      (game_id INTEGER PRIMARY KEY,
                       game_length REAL,
                       game_mins REAL,
                       surrender INTEGER,
                       early_surrender INTEGER
                       )"""
CREATE_PLAYER_TABLE = """CREATE TABLE playerGame
                      (player_id TEXT,
                       game_id TEXT,
                       champ TEXT,
                       win INTEGER,
                       team TEXT,
                       team_position TEXT,
                       name TEXT,
                       assists INTEGER,
                       kills INTEGER,
                       exp REAL,
                       early_surrender INTEGER,
                       surrender INTEGER,
                       gold_earned REAL,
                       gold_spent REAL,
                       level INTEGER,
                       longest_time_spent_living REAL,
                       cs INTEGER,
                       deaths INTEGER,
                       dmg_dealt FLOAT,
                       vision_score INTEGER
                       )"""

POSITIONS = ["TOP", "JUNGLE", "MID", "ADC", "SUPPORT"]

def get_metadata(filename):
    with open(filename, "rb") as f:
        # Magic
        magic = str(f.read(4), encoding="utf-8")

        # Length fields
        lengths_buffer = []
        f.seek(262)
        length_field_buffer = f.read(26)
        metadata_offset = length_field_buffer[6:10]
        metadata_length = length_field_buffer[10:14]

        metadata_offset = int.from_bytes(metadata_offset, byteorder='little')
        metadata_length = int.from_bytes(metadata_length, byteorder='little')

        # Metadata
        f.seek(metadata_offset)
        replay_metadata = f.read(metadata_length)
        replay_metadata = json.loads(str(replay_metadata, encoding="utf-8"))
        stats_json = json.loads(replay_metadata["statsJson"])

        #champs = [s["SKIN"] for s in stats_json]

        return replay_metadata, stats_json

def insert_game(cur, org, metadata, game_id):
    surrender = any([m["GAME_ENDED_IN_SURRENDER"] for m in metadata])
    surrender = 1 if surrender else 0
    early_surrender = any([m["GAME_ENDED_IN_EARLY_SURRENDER"] for m in metadata])
    early_surrender = 1 if early_surrender else 0

    cur.execute(f"""INSERT INTO games VALUES(
        {game_id},
        {org["gameLength"]},
        {org["gameLength"] / (1000 * 60)},
        {surrender},
        {early_surrender})""")

    for i, player in enumerate(metadata):
        player_id = player["ID"]
        champ = player["SKIN"]
        win = player["WIN"]
        team = player["TEAM"]
        team_position = POSITIONS[i % 5]
        name = player["NAME"]
        assists = player["ASSISTS"]
        kills = player["CHAMPIONS_KILLED"]
        exp = player["EXP"]
        early_surrender = player["GAME_ENDED_IN_EARLY_SURRENDER"]
        surrender = player["GAME_ENDED_IN_SURRENDER"]
        gold_earned = player["GOLD_EARNED"]
        gold_spent = player["GOLD_SPENT"]
        level = player["LEVEL"]
        longest_time_spent_living = player["LONGEST_TIME_SPENT_LIVING"]
        cs = player["MINIONS_KILLED"] + player["NEUTRAL_MINIONS_KILLED"]
        deaths = player["NUM_DEATHS"]
        dmg_dealt = player["TOTAL_DAMAGE_DEALT_TO_CHAMPIONS"]
        vision_score = player["VISION_SCORE"]
        
        cur.execute(f"""INSERT INTO playerGame VALUES(
            {player_id},
            '{game_id}',
            '{champ}',
            {1 if win == "Win" else 0},
            '{team}',
            '{team_position}',
            '{name}',
            {assists},
            {kills},
            {exp},
            {1 if early_surrender == "1" else 0},
            {1 if surrender == "1" else 0},
            {gold_earned},
            {gold_spent},
            {level},
            {longest_time_spent_living},
            {cs},
            {deaths},
            {dmg_dealt},
            {vision_score})""")

def gen_metadata(root_dir, outpath):
    i = 0

    con = sqlite3.connect(outpath)
    cur = con.cursor()

    cur.execute(CREATE_GAME_TABLE)
    cur.execute(CREATE_PLAYER_TABLE)

    files = [os.path.join(root_dir, f) for f in os.listdir(root_dir)]
    cur.execute("BEGIN;")

    for fname in files:
        game_id = os.path.basename(fname).split(".")[0].split("-")[1]
        org, metadata = get_metadata(fname)
        insert_game(cur, org, metadata, game_id)
        print(f"{i}/{len(files)}")
        i+= 1
    cur.execute("COMMIT;")
    con.close()