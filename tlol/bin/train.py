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

import os

from absl import app
from absl import flags

from tlol.datasets.replay_dataset import TLoLReplayDataset

FLAGS = flags.FLAGS
flags.DEFINE_string("db_dir", None, "Directory of replay DBs to convert")
flags.mark_flag_as_required("db_dir")

def main(unused_argv):
    db_dir = FLAGS.db_dir
    
    dataset = TLoLReplayDataset(db_dir)

    ds = dataset[0]
    obs   = ds["obs"]
    act   = ds["act"]
    total = ds["raw"]

    print(act.columns.values)

    # print(obs, act, total)

def entry_point():
    app.run(main)

if __name__ == "__main__":
    app.run(main)