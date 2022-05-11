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
"""Converts an SQLite database replays into Numpy Arrays suitable for
training machine learning models or performing bulk analysis."""

import os

from absl import app
from absl import flags

from tlol.datasets.builder import go

import concurrent.futures

FLAGS = flags.FLAGS
flags.DEFINE_string("db_dir",   None,  "Directory of replay DBs to convert")
flags.DEFINE_string("out_path", None,  "Output directory")
flags.DEFINE_string("player", "jinx",  "Player to tailor observations towards")
flags.DEFINE_float("cutoff",  5.0,     "Timestep to start dataset from")
flags.DEFINE_integer("max_workers", 4, "Maximum number of workers to generate dataset")

def go_wrapper(fi, db_dir, player, cutoff, out_path):
    db_path = os.path.join(db_dir, fi)
    print(f"Started: {db_path}")
    res = go(db_path, player, cutoff, out_path)
    if res == -1:
        print("Invalid replay:", os.path.basename(db_path))
    else:
        print("Valid replay:", os.path.basename(db_path))
    return res

def main(unused_argv):
    fi_s     = os.listdir(FLAGS.db_dir)
    player   = FLAGS.player
    cutoff   = FLAGS.cutoff
    out_path = FLAGS.out_path

    with concurrent.futures.ProcessPoolExecutor(max_workers=FLAGS.max_workers) as executor:
        future_res = (executor.submit(
            go_wrapper,
            fi,
            FLAGS.db_dir,
            player,
            cutoff,
            out_path
        ) for fi in fi_s)
        for future in concurrent.futures.as_completed(future_res):
            print(future.result())
            try:
                print(future.result())
            except Exception as exc:
                import traceback
                print("GLOBAL EXCEPTION:", traceback.format_exc())
            finally:
                print("Cur replay done!")

def entry_point():
    app.run(main)

if __name__ == "__main__":
    app.run(main)