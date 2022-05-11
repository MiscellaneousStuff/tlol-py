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
"""Train a machine learning model to play as Jinx on blue side for the
first five minutes of a League of Legends match."""

import math
import random
import numpy as np

import torch

from absl import app
from absl import flags

from tlol.datasets.replay_dataset import TLoLReplayDataset

FLAGS = flags.FLAGS
flags.DEFINE_string("db_dir", None, "Directory of replay DBs to convert")
flags.mark_flag_as_required("db_dir")

def test(obs_s, act_s):
    pass

def train(obs_s, act_s):
    pass

def main(unused_argv):
    db_dir = FLAGS.db_dir
    
    seed = 1
    random.seed(seed)
    torch.manual_seed(seed)
    np.seed(seed)

    dataset = TLoLReplayDataset(db_dir)
    device = 'cuda' if torch.cuda.is_available() else "cpu"

    dataloader = torch.utils.data.DataLoader(
                    dataset,
                    shuffle=True,
                    pin_memory=(device=="cuda"),
                    num_workers=6,
                    batch_size=32,
                    collate_fn=dataset.collate_fixed_length)
    
    train_end = int(len(dataset) * 0.9)

    train_set = torch.utils.data.Subset(
        dataloader,
        list(range(0, train_end)))
    
    test_set = torch.utils.data.Subset(
        dataloader,
        list(range(train_end, len(dataset))))

    # batch = next(iter(dataloader))
    batch_count = math.ceil(len(dataset) / 32)
    for i, batch in enumerate(train_set):
        print(f"{i+1}/{batch_count}")

        batch_obs_s = batch["obs_s"]
        batch_act_s = batch["act_s"]

        obs_s = batch_obs_s[:, :, :].to(device)
        act_s = batch_act_s[:, :, :].to(device)

        train(obs_s, act_s)
        test(obs_s, act_s)

def entry_point():
    app.run(main)

if __name__ == "__main__":
    app.run(main)