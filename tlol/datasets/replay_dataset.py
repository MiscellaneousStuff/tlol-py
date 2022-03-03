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
"""Define a TLoL League of Legends replay dataset."""

import os
import torch
import sqlite3
import pandas as pd

from tlol.lib.utils import split_fixed_length
from tlol.datasets  import lib

def load_replay(replay_path):
    """Returns a replay as a pandas dataframe."""
    con = sqlite3.connect(replay_path)
    df = pd.read_sql(\
        """SELECT
        time, obj_type, name, health, max_health, max_mana, team, crit,
        ap, armour, mr, movement_speed, is_alive, position_x, position_z,
        prev_position_x, prev_position_z, experience, mana_regen, health_regen,
        targetable, recallState
        FROM objects""",
        con)
    con.close()
    return df


class TLoLReplayObs(object):
    """Encapsulation of a TLoL Replay Dataset observation. This will
    contain at least the in-game actions and observations during a period
    of time.
    
    Attributes:
        obs:  In-game observations recorded during the entire observation
        acts: Actions taken by players during the entire observation
    
    May contain other attributes as well depending on the dataset. This is
    just the list of minimal attributes per observation."""
    def __init__(self, obs, acts):
        self._obs  = obs
        self._acts = acts

    def get_dict(self):
        return {
            "obs":  self._obs,
            "acts": self._acts
        }

    @property
    def obs(self):
        return self._obs

    @property
    def acts(self):
        return self._acts


class TLoLReplayDataset(torch.utils.data.Dataset):
    """Encapsulation of a TLoL Replay Dataset used to train machine learning
    agents which can play League of Legends autonomously."""
    def __init__(self,
                 root_dir=None,
                 idx_only=None,
                 dataset_type=lib.TLoLDatasetType.TRAIN):
        self.dataset_type   = dataset_type

        files = os.listdir(root_dir)

        for fi in files:
            cur_path = os.path.join(root_dir, fi)

    def __len__(self):
        return len(self.obs)
    
    def __getitem__(self, i):
        return self.obs[i]
    
    @staticmethod
    def collate_fixed_length(batch):
        batch_size = len(batch)
        obs  = torch.cat([torch.from_numpy(obs["obs"])  for obs in batch], 0)
        acts = torch.cat([torch.from_numpy(obs["acts"]) for obs in batch], 0)
        mb = batch_size * 8

        return {
            "obs":  split_fixed_length(obs, 1)[:mb],
            "acts": split_fixed_length(acts, 1)[:mb]}