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
"""Gets a specified number of players starting from the top of the EUW Ranked
Solo/Duo ladder and gathers all of the games which those players have played
which match a certain criteria."""

from absl import app
from absl import flags

from tlol.stats.u_gg         import U_GG_API
from tlol.replays.downloader import ReplayDownloader

FLAGS = flags.FLAGS
flags.DEFINE_string("champs", "", \
    """(Default: "", any champion)
    Comma-separated list of champions.
    Logical OR search term, so if any of them are present the game is returned.""")
flags.DEFINE_string("target_patch", "11_23", "U.GG formatted target League patch")
flags.DEFINE_integer("max_games", -1, \
    """(Default: Max returned games)
    Limits the number of replay files downloaded up to a maximum number of games.""")
flags.DEFINE_integer("max_workers", 10, "Max workers per process")
flags.DEFINE_float("delay", 0.5, "Request delay")
flags.DEFINE_string("outfile", "", "(Optional) Save match ID list to a text file")
flags.DEFINE_string("infile", "", "(Optional) Use a text file of match IDs")

flags.DEFINE_integer("start_page", 1, \
    "Sets the first leaderboard page which is scraped")
flags.DEFINE_integer("last_page", None, \
    "Sets the last leaderboard page which is scraped")

flags.mark_flag_as_required("last_page")

def main(unused_argv):
    # Setup APIs
    u_gg       = U_GG_API()
    downloader = ReplayDownloader()
    
     # Get top players on EUW Ranked/Solo Duo leaderboard
    summoners = u_gg.get_leaderboard(
        page_start=FLAGS.start_page,
        page_end=FLAGS.last_page,
        region="euw1",
        max_workers=FLAGS.max_workers,
        delay=FLAGS.delay)
    
    # Extract summoner names
    print('Summoner count:', len(summoners))
    summoner_names = [s["summonerName"] if "summonerName" in s else ""
                    for s in summoners]

    print("Summoner names:", summoner_names)

    if not FLAGS.infile:
        # Get matches for above summoners matching specific criteria
        matches = u_gg.get_matches(
            summoner_names=summoner_names,
            champs=FLAGS.champs.split(","), # ["Caitlyn"],
            target_patch=FLAGS.target_patch,
            outpath="", # set the outfile to write the match ids to a file
            win_only=False,
            max_workers=FLAGS.max_workers,
            seasonIds=[20, 21],
            delay=FLAGS.delay)
        matches = list(matches)
    else:
        with open(FLAGS.infile) as f:
            matches = f.read().split("\n")

    if FLAGS.outfile:
        with open(FLAGS.outfile, "w+") as f:
            f.write("\n".join([str(m) for m in matches]))

    if FLAGS.max_games != -1:
        matches = matches[0:FLAGS.max_games]

    print(matches)

    # Download all games
    for i, game_id in enumerate(matches):
        req = downloader.download(game_id)
        print(f'{i}/{len(matches)} Replay DL Status:', game_id, req.content, req.status_code)

def entry_point():
    app.run(main)

if __name__ == "__main__":
    app.run(main)