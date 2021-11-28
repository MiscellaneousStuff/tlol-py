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
"""Scrapes the observations from replays within a source directory and stores
those scraped observations as json in a target directory."""

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

    game_ids = scraper.get_replay_ids()
    print('game_ids:', game_ids)
    for game_id in game_ids:
        metadata, _ = scraper.get_metadata(game_id)
        seconds = metadata["gameLength"] / (1000) #  * 60)

        # NOTE: Change this to `end_time=seconds` to scrape the full replay
        #       This is the number of seconds of the replay to scrape
        end_time = seconds if FLAGS.end_time == -1 else FLAGS.end_time

        print('game_id:', game_id)
        scraper.scrape(
            game_id=game_id,
            end_time=end_time,
            delay=2)

def entry_point():
    app.run(main)

if __name__ == "__main__":
    app.run(main)