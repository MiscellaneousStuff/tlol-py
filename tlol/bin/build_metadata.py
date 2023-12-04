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
"""Builds an SQLite database from ROFL file embedded JSON data for analysis."""

import json
import sqlite3

import os

from absl import app
from absl import flags

from tlol.replays.scraper import ReplayScraper

FLAGS = flags.FLAGS
flags.DEFINE_string("replay_dir", None,  "League of Legends *.rofl replay directory")
flags.DEFINE_integer("max_games", -1,    "(Optional) Maximum number of replays to build metadata for")
flags.mark_flag_as_required('replay_dir')

def main(unused_argv):
    # Set up SQLite database
    conn = sqlite3.connect('ezreal_players.db')
    c = conn.cursor()

    # Create table
    c.execute('''CREATE TABLE IF NOT EXISTS players
                 (game_id text, kills integer, deaths integer, gold_earned integer, damage_dealt integer, time_spent_dead integer)''')
    
    scraper = ReplayScraper(
        game_dir="",
        replay_dir=FLAGS.replay_dir,
        dataset_dir="",
        scraper_dir="",
        region="",
        replay_speed=0)

    replays = os.listdir(FLAGS.replay_dir)
    replays = replays[0:FLAGS.max_games]

    print('game_ids:', replays)
    for replay_path in replays:
        full_game_id = replay_path.replace(".rofl", "")
        metadata, _ = scraper.get_metadata(
            replay_path,
            path=True)
        seconds = (metadata["gameLength"] // 1000) - 1

         # Extract Ezreal player data
        stats = json.loads(metadata['statsJson'])
        for player in stats:
            if 'Ezreal' in player['SKIN']:
                # Extract relevant fields
                kills = player.get('CHAMPIONS_KILLED', 0)
                deaths = player.get('NUM_DEATHS', 0)
                gold_earned = player.get('GOLD_EARNED', 0)
                damage_dealt = player.get('PHYSICAL_DAMAGE_DEALT_TO_CHAMPIONS', 0)
                time_spent_dead = player.get('TOTAL_TIME_SPENT_DEAD', 0)

                # Insert into database
                c.execute("INSERT INTO players VALUES (?, ?, ?, ?, ?, ?)",
                          (full_game_id, kills, deaths, gold_earned, damage_dealt, time_spent_dead))
                
        # print("metadata:", seconds, metadata, "\n\n")
    
    # Save (commit) the changes and close the connection
    conn.commit()
    conn.close()

def entry_point():
    app.run(main)

if __name__ == "__main__":
    app.run(main)