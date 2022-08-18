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
"""The library and base class for defining TLoL Replay Datasets.

This generic class is provided for other datasets to inherit from as future
datasets might have different characteristics among different TLoL Replay datasets.
"""

import enum
import math

class TLoLDatasetType(enum.IntEnum):
    """Inteded usage of the dataset."""
    TRAIN = 0
    DEV   = 1
    TEST  = 2


class AutoTargetType(enum.IntEnum):
    CHAMP=0
    MINION=1
    TURRET=2
    JUNGLE=3
    OTHER=4


class Scene(enum.IntEnum):
    PUSH_TURRET=0
    COMBAT=1
    LANE_FARM=2
    JUNGLE_FARM=3
    RETURN=4
    NAVIGATION=5


def identify_row(row):
    using_auto = row["using_auto"]
    using_combat_spell = row[["using_w", "using_e", "using_d", "using_f"]].any()
    target_type = row["target_type"]

    if using_auto and target_type == AutoTargetType.TURRET:
        return Scene.PUSH_TURRET
    elif (using_auto and target_type == AutoTargetType.CHAMP) or using_combat_spell:
        return Scene.COMBAT
    elif using_auto:
        if target_type == AutoTargetType.CHAMP or \
             target_type == AutoTargetType.OTHER:
            return Scene.COMBAT
        if target_type == AutoTargetType.MINION:
            return Scene.LANE_FARM
        if target_type == AutoTargetType.JUNGLE:
            return Scene.JUNGLE_FARM
    elif row["using_recall"]:
        return Scene.RETURN
    else:
        return Scene.NAVIGATION

def identify_rows(rows, i, j):
    data = rows[i:j]
    if Scene.PUSH_TURRET in data:
        return Scene.PUSH_TURRET
    elif Scene.COMBAT in data:
        return Scene.COMBAT
    elif Scene.LANE_FARM in data:
        return Scene.LANE_FARM
    elif Scene.JUNGLE_FARM in data:
        return Scene.JUNGLE_FARM
    elif Scene.RETURN in data:
        return Scene.RETURN
    else:
        return Scene.NAVIGATION

def get_scenes(data, obs_per_scene):
    cur_acts   = data["act"]
    act_flags  = cur_acts[["using_auto", "target_type", "using_q", "using_w", "using_e", "using_d", "using_f", "using_ward", "using_recall", "movement_x_delta_digital", "movement_z_delta_digital"]]

    # identify each observation as scene
    scenes_obs = act_flags.apply(lambda row: identify_row(row), axis=1)

    # windowed scenes
    scenes_s   = list(scenes_obs)
    scenes_win = [identify_rows(scenes_s, i*obs_per_scene, (i+1)*obs_per_scene)
                  for i in range(0, int(math.ceil(len(scenes_s) / obs_per_scene)))]

    return scenes_win