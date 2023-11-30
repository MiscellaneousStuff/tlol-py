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
"""Custom u.gg API wrapper.

Provides methods to get players on the leaderboard, games which a player has
played, champion statistics and more.

u.gg season IDs:
17 - Season 12
16 - Season 11
"""

import os
import json
import requests
import time
import concurrent.futures


class U_GG_API(object):
    """
    Custom u.gg API wrapper.
    
    Provides methods to get players on the leaderboard, games which a player
    has played, champion statistics and more.
    """
    def __init__(self):
        cur_path = os.path.dirname(os.path.realpath(__file__))
        self.champ_ids = self.get_champ_ids(
            os.path.join(cur_path, "champ_ids.txt"))
        self.base_url = "https://u.gg/api"

    def get_champ_ids(self, path):
        """Returns champion name to ID mappings used within the Riot API."""
        champ_ids = {}
        with open(path) as f:
            for ln in f.read().split("\n"):
                id, champ = ln.split(": ")
                champ_ids[champ] = int(id)
        return champ_ids

    def get_leaderboard(self, page_start=1, page_end=1, region="euw1", max_workers=1, delay=0.5):
        """Returns a list of summoner names from the Ranked Solo/Duo
        leaderboard for a specified region. Supports multiple workers."""
        players = []
        req_body = lambda p: {
            "operationName": "getRankedLeaderboard",
            "query": "query getRankedLeaderboard($page: Int, $queueType: Int, $regionId: String!) {\n  leaderboardPage(page: $page, queueType: $queueType, regionId: $regionId) {\n    totalPlayerCount\n    topPlayerMostPlayedChamp\n    players {\n      iconId\n      losses\n      lp\n      overallRanking\n      rank\n      summonerLevel\n      summonerName\n      tier\n      wins\n      __typename\n    }\n    __typename\n  }\n}\n",
            "variables": {
                "page": p,
                "queueType": 420, # Ranked Solo/Duo
                "regionId": region
            }
        }

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_summoner_name = (executor.submit(
                self.handle_req,
                self.base_url,
                req_body(page),
                delay
            ) for page in range(page_start, page_end+1))
            for future in concurrent.futures.as_completed(future_to_summoner_name):
                try:
                    data = future.result()
                    data = json.loads(data.content)
                    data = data["data"]["leaderboardPage"]["players"]
                except Exception as exc:
                    data = str(type(exc))
                finally:
                    players += data

        return players
    
    def get_matches(self,
            summoner_names,
            champs,
            target_patch,
            outpath="",
            win_only=False,
            max_workers=1,
            seasonIds=[16],
            delay=0.5):
        """
        Returns a list of unique Game IDs matching the given criteria.
        Only checks the first page of search results to simply the requests.
        Beware: Deletes the outpath if it already exists!
        """
        match_ids = set()
        matches_req_body = lambda summoner_name: {
            "operationName": "FetchMatchSummaries",
            "query": "query FetchMatchSummaries($championId: [Int], $page: Int, $queueType: [Int], $regionId: String!, $role: [Int], $seasonIds: [Int]!, $summonerName: String!) {   fetchPlayerMatchSummaries(     championId: $championId     page: $page     queueType: $queueType     regionId: $regionId     role: $role     seasonIds: $seasonIds     summonerName: $summonerName   ) {     finishedMatchSummaries     totalNumMatches     matchSummaries {       assists       championId       cs       damage       deaths       gold       items       jungleCs       killParticipation       kills       level       matchCreationTime       matchDuration       matchId       maximumKillStreak       primaryStyle       queueType       regionId       role       runes       subStyle       summonerName       summonerSpells       psHardCarry       psTeamPlay       lpInfo {         lp         placement         promoProgress         promoTarget         promotedTo {           tier           rank           __typename         }         __typename       }       teamA {         championId         summonerName         teamId         role         hardCarry         teamplay         __typename       }       teamB {         championId         summonerName         teamId         role         hardCarry         teamplay         __typename       }       version       visionScore       win       __typename     }     __typename   } }",
            "variables": {
                "championId": [self.champ_ids[c] for c in champs],
                "page": 1, # Finds max of 20 games of a single champ per patch (people rarely play more than this so to keep the code much simpler, I'm only checking a maximum of 20 games of the same champion per summoner per patch.)
                "queueType": [420], # 420 = solo/duo
                "regionId": "euw1",
                "role": [],
                "seasonIds": seasonIds,
                "summonerName": summoner_name
            }
        }
        if outpath:
            if os.path.exists(outpath):
                os.remove(outpath)
            with open(outpath, "a+") as f:
                f.write(target_patch + "\n")
                f.write(",".join(champs) + "\n")
                f.write(f"top {len(summoner_names)} ranked summoners\n")
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_match_id = (executor.submit(
                self.handle_req,
                self.base_url,
                matches_req_body(name),
                delay
            ) for name in summoner_names)
            for future in concurrent.futures.as_completed(future_to_match_id):
                try:
                    a_data = future.result()
                    b_data = json.loads(a_data.content)
                    data = b_data["data"]["fetchPlayerMatchSummaries"]["matchSummaries"]
                except Exception as exc:
                    data = None
                finally:
                    if data == None:
                        pass
                    else:
                        for match in data:
                            if type(match) == dict:
                                if "version" in match:
                                    if match["version"] == target_patch:
                                        if (win_only and match["win"]) or (not win_only):
                                            match_ids.add(match["matchId"])
                                            if outpath:
                                                with open(outpath, "a+") as f:
                                                    f.write(str(match["matchId"]) + "\n")
        return match_ids

    def handle_req(self, url, body, delay=0.5):
        req = requests.request(
            'POST',
            url,
            data=json.dumps(body),
            headers={
                "Content-Type": "application/json"
            }
        )
        time.sleep(delay)
        return req