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
"""Scrapes the observations from replays within a source directory and stores
those scraped observations as json in a target directory."""

import os
from pathlib import Path

from absl import app
from absl import flags

from tlol.replays.scraper import ReplayScraper

FLAGS = flags.FLAGS
flags.DEFINE_string("game_dir",      None,  "League of Legends game directory")
flags.DEFINE_string("replay_dir",    None,  "League of Legends *.rofl replay directory")
flags.DEFINE_string("dataset_dir",   None,  "JSON replay files output directory")
flags.DEFINE_string("scraper_dir",   None,  "Path to the scraper program")
flags.DEFINE_string("region",        "EUW", "Region of the replay files")
flags.DEFINE_integer("replay_speed", 8,     "League client replay speed multiplier")
flags.DEFINE_integer("end_time",     "-1",  "(Default: Full game) Set maximum replay length in seconds")
flags.DEFINE_string("replay_list",   "",    "(Optional) File containing replay IDs to scrape")
flags.DEFINE_bool("use_scraper",     True,  "(Optional) Disable the scraper for debugging")
flags.mark_flag_as_required('game_dir')
flags.mark_flag_as_required('replay_dir')
flags.mark_flag_as_required('dataset_dir')
flags.mark_flag_as_required('scraper_dir')

def main(unused_argv):
    scraper = ReplayScraper(
        game_dir=FLAGS.game_dir,
        replay_dir=FLAGS.replay_dir,
        dataset_dir=FLAGS.dataset_dir,
        scraper_dir=FLAGS.scraper_dir,
        region=FLAGS.region,
        replay_speed=FLAGS.replay_speed)

    completed_replays = os.listdir(FLAGS.dataset_dir)
    completed_replays = [replay.replace(".json", "") for replay in completed_replays]

    # Remove completed replays
    original_replay_paths = [r.replace(".rofl", "") for r in scraper.get_replay_paths()]
    replay_paths = [r.replace(".rofl", "") for r in scraper.get_replay_paths()]
    print("replay_paths:", len(set(replay_paths)), len(set(completed_replays)))

    if FLAGS.replay_list:
        with open(FLAGS.replay_list) as f:
            replay_list = [r.replace(".rofl", "") for r in f.read().split("\n")]
            print("replay_list:", len(replay_list), replay_list[0], completed_replays[0])
            replay_list = list(set(original_replay_paths).intersection(set(replay_list)))
            replay_paths = replay_list

    filtered_replay_paths = list(set(replay_paths) - set(completed_replays))

    print("replay_paths:", len(filtered_replay_paths), len(original_replay_paths), len(replay_paths), len(completed_replays))

    for replay_path in filtered_replay_paths:
        full_replay_path = str(Path(FLAGS.replay_dir) / f"{replay_path}.rofl")
        metadata, _ = scraper.get_metadata(full_replay_path, path=True)
        seconds = (metadata["gameLength"] // 1000) - 1

        # NOTE: Change this to `end_time=seconds` to scrape the full replay
        #       This is the number of seconds of the replay to scrape
        end_time = seconds if FLAGS.end_time == -1 else FLAGS.end_time

        print('GameID:', full_replay_path, metadata["gameLength"])
        scraper.scrape(
            game_id=full_replay_path,
            end_time=end_time,
            delay=2,
            scraper=FLAGS.use_scraper)

def entry_point():
    app.run(main)

if __name__ == "__main__":
    app.run(main)