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
"""Train a machine learning model to play as Jinx on blue side for the
first five minutes of a League of Legends match."""

import math
import random
import numpy as np

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from torch.cuda.amp.grad_scaler import GradScaler

from absl import app
from absl import flags

from tlol.datasets.replay_dataset import TLoLReplayDataset, decollate_tensor

FLAGS = flags.FLAGS
flags.DEFINE_string("db_dir", None, "Directory of replay DBs to convert")
flags.DEFINE_bool("amp", False, "Enable AMP training for PyTorch")
flags.mark_flag_as_required("db_dir")


class JinxPolicy(nn.Module):

    def __init__(self, in_dim, model_size, n_layers, out_dim, dropout=0.1):
        super(JinxPolicy, self).__init__()
        self.lstm = nn.LSTM(
            in_dim, model_size, batch_first=True,
            bidirectional=False, num_layers=n_layers,
            dropout=dropout)
        self.x_out = nn.Linear(model_size, out_dim)
        self.y_out = nn.Linear(model_size, out_dim)

    def forward(self, x):
        latent, _ = self.lstm(x)
        x = self.x_out(latent)
        y = self.y_out(latent)
        x = F.softmax(x, dim=-1)
        y = F.softmax(y, dim=-1)
        return x, y


def test(model, epoch, test_loader, device, batch_count, criterion, optimizer):
    model.eval()
    data_len = len(test_loader.dataset)

    batch_idx = 0

    scaler = GradScaler()

    losses = []
    acc_s = []

    with torch.no_grad():
        for batch in test_loader:
            # print(f"Epoch: {epoch+1}, Batch: {batch_idx+1}/{batch_count}")

            batch_obs_s = batch["obs_s"]
            batch_act_s = batch["act_s"]

            obs_s = batch_obs_s[:, :, 9:12]
            obs_s = obs_s.to(device)

            act_s = batch_act_s[:, :, -2:]
            act_s = act_s.to(device)

            x_ground = act_s[:, :, 0].cpu()
            x_ground = torch.LongTensor(x_ground)
            x_ground += 4 # (-4 to +4) => (0 to 9)
            # x_ground = F.softmax(x_ground, dim=-1)
            x_ground = F.one_hot(x_ground, num_classes=9)
            x_ground = x_ground.to(device)

            y_ground = act_s[:, :, 1].cpu()
            y_ground = torch.LongTensor(y_ground)
            y_ground += 4 # (-4 to +4) => (0 to 9)
            # y_ground = F.softmax(y_ground, dim=-1)
            y_ground = F.one_hot(y_ground, num_classes=9)
            y_ground = y_ground.to(device)

            with torch.autocast(
                enabled=FLAGS.amp,
                dtype=torch.bfloat16,
                device_type="cuda"):

                x_probs, y_probs = model(obs_s)

                # print("X PROBS:", x_probs.shape)

                # print("pre x pred, x ground:", x_probs.shape, x_ground.shape)

                x_ground = decollate_tensor(x_ground, batch["lengths"])
                x_probs  = decollate_tensor(x_probs, batch["lengths"])

                x_losses = []
                y_losses = []

                for x_preds, x_reals, y_preds, y_reals in \
                    zip(x_probs, x_ground, y_probs, y_ground):
                    
                    # print("INNER LOSS CALC:", x_preds.shape, x_reals.shape, x_preds[0], x_reals[0])

                    x_real = torch.clone(x_reals)
                    x_reals = x_reals.float()
                    x_reals = F.softmax(x_reals, dim=-1)

                    y_real = torch.clone(y_reals)
                    y_reals = y_reals.float()
                    y_reals = F.softmax(y_reals, dim=-1)

                    x_acc = torch.argmax(x_preds, dim=-1)
                    x_acc = (x_acc + 4) == torch.argmax(x_real, dim=-1)
                    x_acc = sum([1 for x in x_acc if x]) / len(x_acc)
                    
                    test_x_preds  = torch.argmax(x_preds, dim=-1)
                    test_x_ground = torch.argmax(x_real, dim=-1)
                    print(test_x_preds[0:10], test_x_ground[0:10])

                    y_acc = torch.argmax(y_preds, dim=-1)
                    y_acc = (y_acc + 4) == torch.argmax(y_real, dim=-1)
                    y_acc = sum([1 for y in y_acc if y]) / len(y_acc)

                    acc_s.append((x_acc + y_acc) / 2.0)

                    x_losses.append(criterion(x_preds, x_reals))
                    y_losses.append(criterion(y_preds, y_reals))

                x_losses = sum(x_losses) / len(x_losses)
                y_losses = sum(y_losses) / len(y_losses)

                loss = x_losses + y_losses
                losses.append(loss.item())

            batch_idx += 1

            if batch_idx % 1 == 0 or batch_idx == data_len:
                print('Test Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                    epoch, batch_idx * 32, data_len,
                    100. * batch_idx / len(test_loader), loss.item()))

    return sum(losses) / len(losses), sum(acc_s) / len(acc_s)

def train(model, epoch, train_loader, device, batch_count, criterion, optimizer):
    model.train()
    data_len = len(train_loader.dataset)

    batch_idx = 0

    scaler = GradScaler()

    for batch in train_loader:
        # print(f"Epoch: {epoch+1}, Batch: {batch_idx+1}/{batch_count}")

        # NOTE: COMMENT THIS OUT FOR LSTM MODEL => optimizer.zero_grad()

        batch_obs_s = batch["obs_s"]
        batch_act_s = batch["act_s"]

        obs_s = batch_obs_s[:, :, 9:12]
        obs_s = obs_s.to(device)

        act_s = batch_act_s[:, :, -2:]
        act_s = act_s.to(device)

        x_ground = act_s[:, :, 0].cpu()
        x_ground = torch.LongTensor(x_ground)
        x_ground += 4 # (-4 to +4) => (0 to 9)
        # x_ground = F.softmax(x_ground, dim=-1)
        x_ground = F.one_hot(x_ground, num_classes=9)
        x_ground = x_ground.to(device)

        y_ground = act_s[:, :, 1].cpu()
        y_ground = torch.LongTensor(y_ground)
        y_ground += 4 # (-4 to +4) => (0 to 9)
        # y_ground = F.softmax(y_ground, dim=-1)
        y_ground = F.one_hot(y_ground, num_classes=9)
        y_ground = y_ground.to(device)

        with torch.autocast(
            enabled=FLAGS.amp,
            dtype=torch.bfloat16,
            device_type="cuda"):

            x_probs, y_probs = model(obs_s)

            # print("X PROBS:", x_probs.shape)

            # print("pre x pred, x ground:", x_probs.shape, x_ground.shape)

            x_ground = decollate_tensor(x_ground, batch["lengths"])
            x_probs  = decollate_tensor(x_probs, batch["lengths"])

            x_losses = []
            y_losses = []

            for x_preds, x_reals, y_preds, y_reals in \
                zip(x_probs, x_ground, y_probs, y_ground):
                
                # print("INNER LOSS CALC:", x_preds.shape, x_reals.shape, x_preds[0], x_reals[0])

                x_reals = x_reals.float()
                x_reals = F.softmax(x_reals, dim=-1)

                y_reals = y_reals.float()
                y_reals = F.softmax(y_reals, dim=-1)

                x_losses.append(criterion(x_preds, x_reals))
                y_losses.append(criterion(y_preds, y_reals))

            x_losses = sum(x_losses) / len(x_losses)
            y_losses = sum(y_losses) / len(y_losses)

            loss = x_losses + y_losses

        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

        batch_idx += 1

        if batch_idx % 1 == 0 or batch_idx == data_len:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * 32, data_len,
                100. * batch_idx / len(train_loader), loss.item()))

def main(unused_argv):
    db_dir = FLAGS.db_dir
    batch_size = 32
    n_epochs = 10
    learning_rate = 0.001

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
    
    model     = JinxPolicy(in_dim=3, model_size=1, n_layers=1, out_dim=9).to(device)
    criterion = nn.CrossEntropyLoss(reduction="sum")
    optimizer = optim.AdamW(model.parameters(), learning_rate)

    for epoch in range(n_epochs):
        train(model, epoch, train_loader, device, batch_count, criterion, optimizer)
        loss, acc = test(model, epoch, test_loader, device, batch_count, criterion, optimizer)
        print(">>>", epoch, loss, acc)

def entry_point():
    app.run(main)

if __name__ == "__main__":
    app.run(main)