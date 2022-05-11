# MIT License
# 
# Copyright (c) 2022 MiscellaneousStuff
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
"""Define a TLoL League of Legends replay dataset."""

import os
import torch
import pandas as pd

from tlol.datasets  import lib

UNIT_FEATURE_COUNTS = {
    "champs":   65,
    "minions":  34,
    "turrets":  17,
    "jungle":   17,
    "others":   17,
    "missiles": 21
}

UNIT_COUNTS = {
    "champs":   5 * 2,
    "minions":  30,
    "turrets":  11 * 2,
    "jungle":   24,
    "others":   5,
    "missiles": 30
}

ACTION_FEATURE_COUNTS = {
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

GAME_TIME_COUNT   = 1
MINION_SPAWN_TIME = 1

UNIT_TYPES = UNIT_FEATURE_COUNTS.keys()
TOTAL_UNIT_FEATURES = [UNIT_FEATURE_COUNTS[t] * UNIT_COUNTS[t]
                             for t in UNIT_TYPES]
TOTAL_UNIT_FEATURES   = sum(TOTAL_UNIT_FEATURES)
TOTAL_ACTION_FEATURES = sum(ACTION_FEATURE_COUNTS.values())

OBS_FEATURES_TOTAL    = GAME_TIME_COUNT + \
                        MINION_SPAWN_TIME + \
                        TOTAL_UNIT_FEATURES 
ACTION_FEATURES_TOTAL = TOTAL_ACTION_FEATURES

TOTAL_FEATURES = OBS_FEATURES_TOTAL + ACTION_FEATURES_TOTAL


class TLoLReplayDataset(torch.utils.data.Dataset):
    """Encapsulation of a TLoL Replay Dataset used to train machine learning
    agents which can play League of Legends autonomously."""
    def __init__(self,
                 root_dir=None,
                 dataset_type=lib.TLoLDatasetType.TRAIN):
        self.dataset_type  = dataset_type
        self.root_dir = root_dir
        self.files = os.listdir(root_dir)

    def __len__(self):
        return len(self.files)
    
    def __getitem__(self, i):
        """Returns a NumPy array of the game at index `i`"""
        cur_path = os.path.join(
            self.root_dir, self.files[i])
        game_data   = pd.read_pickle(cur_path)
        game_object = {
            "raw": game_data,
            "obs": game_data.iloc[:, 0:OBS_FEATURES_TOTAL],
            "act": game_data.iloc[:, OBS_FEATURES_TOTAL:TOTAL_FEATURES]
        }
        return game_object