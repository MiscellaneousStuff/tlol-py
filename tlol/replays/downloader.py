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
"""Uses a logged in League of Legends client to download replay files using
the LCU API."""

import base64
import requests
import json
import time
import psutil
import platform

class ReplayDownloader(object):
    def __init__(self, remoting_auth_token=None, app_port=None):
        self.remoting_auth_token = remoting_auth_token
        self.app_port = app_port
        if not remoting_auth_token or not app_port:
            self.remoting_auth_token, self.app_port = \
                self.get_lcu_params()
        
    def get_lcu_params(self):
        """Attempts to automatically acquire the `remoting_auth_token`
        and `app_port` from a running League of Legends client."""
        for proc in psutil.process_iter():
            try:
                n = proc.name()
                if "LeagueClientUx" in n:
                    cmdline = proc.cmdline()
                    port = None
                    tok = None
                    for arg in cmdline:
                        if "--app-port" in arg:
                            port = arg.split("=")[1]
                        elif "--remoting-auth-token" in arg:
                            tok = arg.split("=")[1]
                    return tok, port
            except:
                pass
        return None, None

    def download(self, game_id, delay=0.25):
        """Sends the HTTP POST request to the locally logged in
        League of Legends client to download the desired match."""
        auth_token = base64.b64encode(
            f"riot:{self.remoting_auth_token}".encode("utf-8"))
        auth_token = str(auth_token, encoding="utf-8")
        app_port = self.app_port
        url = \
            f"https://127.0.0.1:{app_port}/lol-replays/v1/rofls/{game_id}/download/graceful"
        req = requests.post(
            url=url,
            headers={
                "Authorization": f"Basic {auth_token}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "gameId": game_id
            }),
            verify=False)
        time.sleep(delay)
        return req