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
        cur_path = os.path.join(
            self.root_dir, self.files[i])
        game_data   = pd.read_pickle(cur_path)
        game_object = {
            "raw": game_data
        }
        return game_object