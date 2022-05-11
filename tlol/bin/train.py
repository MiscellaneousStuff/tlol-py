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
import torch.nn as nn
import torch.nn.functional as F

from absl import app
from absl import flags

from tlol.datasets.replay_dataset import TLoLReplayDataset

FLAGS = flags.FLAGS
flags.DEFINE_string("db_dir", None, "Directory of replay DBs to convert")
flags.mark_flag_as_required("db_dir")


class JinxPolicy(nn.Module):

    def __init__(self, in_dim, out_dim):
        super(JinxPolicy, self).__init__()
        self.out_dim = out_dim
        self.fc1 = nn.Linear(in_dim, in_dim // 2)
        self.fc2 = nn.Linear(in_dim // 2, in_dim // 4)
        self.fc3 = nn.Linear(in_dim // 4, out_dim)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        x = F.log_softmax(x, dim=1)
        return x


def test(model, epoch, test_loader, device, batch_count):
    model.eval()
    return 0

def train(model, epoch, train_loader, device, batch_count):
    model.train()
    batch_idx = 0

    for batch in train_loader:
        print(f"Epoch: {epoch+1}, Batch: {batch_idx+1}/{batch_count}")

        batch_obs_s = batch["obs_s"]
        batch_act_s = batch["act_s"]

        obs_s = batch_obs_s[:, :, 9:12].to(device)
        act_s = batch_act_s[:, :, -2:].to(device)

        batch_idx += 1

def main(unused_argv):
    db_dir = FLAGS.db_dir
    batch_size = 32
    n_epochs = 1
    
    seed = 1
    random.seed(seed)
    torch.manual_seed(seed)
    np.random.seed(seed)

    dataset = TLoLReplayDataset(db_dir)
    device = 'cuda' if torch.cuda.is_available() else "cpu"

    train_end = int(len(dataset) * 0.9)

    train_set = torch.utils.data.Subset(
        dataset,
        list(range(0, train_end)))

    test_set = torch.utils.data.Subset(
        dataset,
        list(range(train_end, len(dataset))))

    train_loader = torch.utils.data.DataLoader(
                    train_set,
                    shuffle=True,
                    pin_memory=(device=="cuda"),
                    num_workers=6,
                    batch_size=batch_size,
                    collate_fn=dataset.collate_fixed_length)

    test_loader = torch.utils.data.DataLoader(
                    test_set,
                    shuffle=False,
                    pin_memory=(device=="cuda"),
                    num_workers=6,
                    batch_size=batch_size,
                    collate_fn=dataset.collate_fixed_length)

    # batch = next(iter(train_loader))
    batch_count = math.ceil(len(train_set) / batch_size)
    
    model = JinxPolicy(in_dim=2, out_dim=2)

    for epoch in range(n_epochs):
        train(model, epoch, train_loader, device, batch_count)
        loss = test(model, epoch, test_loader, device, batch_count)

def entry_point():
    app.run(main)

if __name__ == "__main__":
    app.run(main)