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
"""Counts the total number of frames for a converted ML dataset."""

import os
import pickle
import pandas as pd

from absl import app
from absl import flags

FLAGS = flags.FLAGS
flags.DEFINE_string("db_dir", None, "Directory of replay DBs to convert")
flags.mark_flag_as_required("db_dir")

def main(unused_argv):
    db_dir = FLAGS.db_dir
    files  = os.listdir(db_dir)

    total_frames = 0
    for i, fi in enumerate(files):
        cur_path = os.path.join(db_dir, fi)
        game_data = pd.read_pickle(cur_path)
        cur_frames, cols = game_data.shape
        print(f"Game {i} frames: {cur_frames}, cols: {cols}")
        total_frames += cur_frames
    print(f"Total frames: {total_frames}")
    print(f"Mean frames:  {total_frames / len(files)}")

def entry_point():
    app.run(main)

if __name__ == "__main__":
    app.run(main)