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
"""Gets a specified number of players starting from the top of the EUW Ranked
Solo/Duo ladder and gathers all of the games which those players have played
which match a certain criteria."""

from absl import app

from tlol.stats.u_gg         import U_GG_API
from tlol.replays.downloader import ReplayDownloader

def main(unused_argv):
    # Setup APIs
    u_gg       = U_GG_API()
    downloader = ReplayDownloader()

    # Get top players on EUW Ranked/Solo Duo leaderboard
    summoners = u_gg.get_leaderboard(
        page_start=1,
        page_end=2,
        region="euw1",
        max_workers=1)
    
    # Extract summoner names
    summoner_names = [s["summonerName"]
                      for s in summoners][0:1]
    print(summoner_names)

    # Get matches for above summoners matching specific criteria
    matches = u_gg.get_matches(
        summoner_names=summoner_names,
        champs=["Miss Fortune", "Nami"],
        target_patch="11_21",
        outpath="", # set the outfile to write the match ids to a file
        win_only=False,
        max_workers=10)
    
    print(matches)
    
def entry_point():
    app.run(main)

if __name__ == "__main__":
    app.run(main)