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
"""Scrapes observations from a replay file by replaying a match using
the League game client and storing the observations in a json file."""

import os
import time
import json
import subprocess


class ReplayScraper(object):
    """League of Legends replay scraper class.
    
    This class handles executing the League of Legends client in
    replay mode and the scraping application in the correct order.

    Args:
        game_dir: League of Legends game directory.
        replay_dir: League of Legends *.rofl replay directory.
        dataset_dir: JSON replay files output directory.
        replay_speed: League of Legends client replay speed multiplier.
        scraper_path: Directory of the scraper program.
    """
    def __init__(self,
            game_dir,
            replay_dir,
            dataset_dir,
            scraper_dir,
            replay_speed=8,
            region="EUW"):
        self.game_dir = game_dir
        self.replay_dir = replay_dir
        self.dataset_dir = dataset_dir
        self.scraper_dir = scraper_dir
        self.replay_speed = replay_speed
        self.region = region

    def run_client(self, replay_path):
        args = [
            str(os.path.join(self.game_dir, "League of Legends.exe")),
            replay_path,
            self.game_dir,
            "-Region=EUW",
            "-PlatformID=EUW1",
            "-Locale=en_GB",
            "-SkipBuild",
            "-EnableCrashpad=true",
            "-EnableLNP",
            "-UseDX11=1:1",
            "-UseMetal=0:1",
            "-UseNewX3D",
            "-UseNewX3DFramebuffers"
        ]
        print('run lol client:', args)
        subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.game_dir)

    def run_scraper(self, output_path, end_time):
        replay_script_path = os.path.dirname(os.path.abspath(__file__))
        replay_script_path = os.path.join(replay_script_path, "set_replay.py")
        replay_script_path = replay_script_path.replace("\\", "/")

        replay_script_cmd  = replay_script_path
        replay_script_cmd  = "python " + replay_script_cmd

        args = [
            os.path.join(self.scraper_dir, "T_T Pandoras Box.exe"),
            f'replay_file={str(output_path)}',
            f'end_time={str(end_time)}',
            f'replay_mult={str(self.replay_speed)}',
            f'replay_cmd={str(replay_script_cmd)}']
        print('scraper args:', args)
        subprocess.call(
            args,
            cwd=self.scraper_dir)

    def scrape(self, replay_path, end_time, delay=2, scraper=True):
        """Scrapes a *.rofl file.
        
        Scrapes an individual replay file using the League of Legends
        game client. Scrapes the replay at faster than real-time speed.
        
        Args:
            replay_path: Full replay filename.
            end_time: Number of seconds to scrape within replay.
            delay: Number of seconds to wait before ending.
        """
        replay_fname = replay_path
        replay_path = os.path.join(self.replay_dir, replay_fname)

        output_fname = os.path.basename(replay_path).replace(".rofl", ".json")
        output_path = os.path.join(self.dataset_dir, output_fname)

        self.run_client(replay_path)
        if scraper:
            self.run_scraper(output_path, end_time)

        if scraper:
            os.system("taskkill /f /im \"T_T Pandoras Box.exe\"")
        else:
            time.sleep(60 * 10) # Go to sleep for 10 mins during testing
        os.system("taskkill /f /im \"League of Legends.exe\"")
        time.sleep(delay)

    def get_replay_paths(self):
        """Returns all of the *.rofl files within the `replay_dir`."""
        replay_paths = os.listdir(self.replay_dir)
        replay_paths = [fname if fname.endswith(".rofl") else None
                         for fname in replay_paths]
        replay_paths = [path for path in replay_paths if path]
        return replay_paths
    
    def get_metadata(self, game_id, path=False):
        try:
            if path:
                replay_fname = game_id
                replay_path  = game_id
                print(replay_fname)
            else:    
                replay_fname = f"{self.region}1-{game_id}.rofl"
                replay_path  = os.path.join(self.replay_dir, replay_fname)
                print(os.path.join(self.replay_dir, replay_fname))

            with open(replay_path, "rb") as f:
                f.seek(262)
                length_field_buffer = f.read(26)
                metadata_offset = length_field_buffer[6:10]
                metadata_length = length_field_buffer[10:14]

                metadata_offset = int.from_bytes(metadata_offset, byteorder='little')
                metadata_length = int.from_bytes(metadata_length, byteorder='little')

                f.seek(metadata_offset)
                replay_metadata = f.read(metadata_length)
                replay_metadata = json.loads(str(replay_metadata, encoding="utf-8"))
                stats_json = json.loads(replay_metadata["statsJson"])

                return replay_metadata, stats_json
            
        except Exception as e:
            print("ERR PROCESSING REPLAY FILE:", str(e))
            return None, None