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
"""Gets the schema for an ML format game replay. This schema is specific
to the Early Game Jinx ML dataset."""

import os
import pandas as pd

from absl import app
from absl import flags

FLAGS = flags.FLAGS
flags.DEFINE_string("db_path", None, \
    "Path to single ML format replay to get schema for")
flags.mark_flag_as_required("db_path")

def main(unused_argv):
    db_path = FLAGS.db_path
    game_data = pd.read_pickle(db_path)

    unit_feature_counts = {
        "champs":   65,
        "minions":  34,
        "turrets":  17,
        "jungle":   17,
        "others":   17,
        "missiles": 21
    }

    unit_counts = {
        "champs":   5 * 2,
        "minions":  30,
        "turrets":  11 * 2,
        "jungle":   24,
        "others":   5,
        "missiles": 30
    }

    action_feature_counts = {
        "auto_attack":     3,
        "q_spell":         1,
        "w_spell":         3,
        "e_spell":         3,
        "flash_summoner":  3,
        "alt_summoner":    1,
        "warding":         3,
        "recall":          1,
        "moving":          2
    }

    # Global observation values
    game_time = 1
    minion_spawn_time = 1

    # Obs / Act types
    unit_types   = unit_feature_counts.keys()

    # Obs / Act feature counts
    total_unit_features   = [unit_feature_counts[t] * unit_counts[t]
                             for t in unit_types]
    total_unit_features   = sum(total_unit_features)
    total_action_features = sum(action_feature_counts.values())

    # Single observation feature total
    observation_features_total = game_time + \
                                 minion_spawn_time + \
                                 total_unit_features 
    action_features_total      = total_action_features

    total_features = observation_features_total + action_features_total

    print(total_features)

def entry_point():
    app.run(main)

if __name__ == "__main__":
    app.run(main)