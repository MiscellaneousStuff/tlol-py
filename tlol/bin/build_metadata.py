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
"""Builds an SQLite database from ROFL file embedded JSON data for analysis."""

from absl import app
from absl import flags

from tlol.replays.scraper import ReplayScraper

FLAGS = flags.FLAGS
flags.DEFINE_string("replay_dir", None,  "League of Legends *.rofl replay directory")
flags.DEFINE_string("region",     "EUW", "Region of the replay files")
flags.mark_flag_as_required('replay_dir')

def main(unused_argv):
    scraper = ReplayScraper(
        game_dir="",
        replay_dir=FLAGS.replay_dir,
        dataset_dir="",
        scraper_dir="",
        region=FLAGS.region,
        replay_speed=0)

    game_ids = scraper.get_replay_ids()

    print('game_ids:', game_ids)
    for game_id in game_ids:
        metadata, _ = scraper.get_metadata(game_id)
        seconds = (metadata["gameLength"] // 1000) - 1

        print("metadata:", metadata)

def entry_point():
    app.run(main)

if __name__ == "__main__":
    app.run(main)