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
"""Converts a SQLite database replay into a Numpy Array suitable for
training machine learning models or performing bulk analysis."""

from absl import app
from absl import flags
import os

from tlol.datasets.builder import go

FLAGS = flags.FLAGS
flags.DEFINE_string("db_path", None,  "Path to replay")
flags.DEFINE_string("out_path", None, "Output directory")
flags.DEFINE_string("player", "jinx", "Player to tailor observations towards")
flags.DEFINE_float("cutoff",  5.0,    "Timestep to start dataset from")
flags.mark_flag_as_required("db_path")
flags.mark_flag_as_required("out_path")

def main(unused_argv):
    # DB construction settings
    db_path  = FLAGS.db_path
    player   = FLAGS.player
    cutoff   = FLAGS.cutoff
    out_path = FLAGS.out_path

    res = go(db_path, player, cutoff, out_path)
    if res == -1:
        print("Invalid replay:", os.path.basename(db_path))
    else:
        print("Valid replay")

def entry_point():
    app.run(main)

if __name__ == "__main__":
    app.run(main)