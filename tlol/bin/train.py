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

import numpy as np
import random
import time
import os

import torch
import torch.nn.functional as F
from torch.cuda.amp.grad_scaler import GradScaler

from absl import flags
from absl import app

from tlol.datasets.replay_dataset import TLoLReplayDataset, load_replay
from tlol.datasets.lib import TLoLDatasetType
from tlol.models.mf_model import MFModel

FLAGS = flags.FLAGS

flags.DEFINE_string("root_dir", None, "Root directory of the TLoL replay dataset")
flags.DEFINE_integer("random_seed", 1, "Seed value for all libraries")
flags.DEFINE_string("checkpoint_path", "", "(Optional) Existing model to continue training")
flags.mark_flag_as_required("root_dir")

def test(model, devset, device, epoch_idx):
    pass

def train(trainset, devset, device, n_epochs=100, checkpoint_path=None):
    training_subset = torch.utils.data.Subset(
        trainset,
        list(range(int(len(trainset) * FLAGS.datasize_fraction))))
    
    dataloader = torch.utils.data.DataLoader(
        training_subset,
        shuffle=True,
        pin_memory=(device=="cuda"),
        collate_fn=devset.collate_fixed_length,
        batch_size=FLAGS.batch_size,
        num_workers=FLAGS.num_workers)
    
    model = MFModel(
        ins=devset.num_features,
        model_size=FLAGS.model_size,
        n_layers=FLAGS.n_layers,
        dropout=FLAGS.dropout,
        outs=devset.num_out_features).to(device)

    optim = torch.optim.Adam(model.parameters(), lr=FLAGS.learning_rate)

    best_validation = float("inf")

    scaler = GradScaler()

    losses_s = []
    for epoch_idx in range(n_epochs):
        losses = []
        start = time.time()
        for batch in dataloader:
            optim.zero_grad()
            X = batch[""].to(device)
            y = batch[""]

            with torch.autocast(
                enabled=FLAGS.amp,
                dtype=torch.bfloat16,
                device_type="cuda"):
                pred = model(X)

                loss = F.mse_loss(pred, y)
                losses.append(loss.item())
            
            scaler.scale(loss).backward()
            scaler.step(optim)
            scaler.update()

        val_start = time.time()
        val = test(model, devset, device, epoch_idx)

        train_loss = np.mean(losses)

        end = time.time() - start
        val_end = time.time() - val_start
        print(f"epoch: {epoch_idx+1}, vloss: {val}, loss: {train_loss}, tm: {end:.4f}, val_tm: {val_end:.4f}")

        losses_s.append(train_loss)
        
def main(unused_argv):
    # Set random seed using NumPy and Torch
    random.seed(FLAGS.random_seed)
    np.random.seed(FLAGS.random_seed)
    torch.manual_seed(FLAGS.random_seed)

    # Get training device
    device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    
    db_s = [fi if fi.endswith(".db") else None
            for fi in os.listdir(FLAGS.root_dir)]
    db_s = list(filter(lambda x: x != None, db_s))
    example = os.path.join(FLAGS.root_dir, db_s[0])

    replay = load_replay(example)
    print('replay:', len(replay))

    """
    trainset = TLoLReplayDataset(
        root_dir=FLAGS.root_dir,
        dataset_type=TLoLDatasetType.TRAIN)
    
    devset = TLoLReplayDataset(
        root_dir=FLAGS.root_dir,
        dataset_type=TLoLDatasetType.TRAIN)

    train(trainset=trainset,
          devset=devset,
          device=device,
          n_epochs=FLAGS.n_epochs,
          checkpoint_path=FLAGS.checkpoint_path)
    """

def entry_point():
    app.run(main)

if __name__ == "__main__":
    app.run(main)