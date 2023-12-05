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

import json
import sqlite3

import os

from absl import app
from absl import flags

from tlol.replays.scraper import ReplayScraper

FLAGS = flags.FLAGS
flags.DEFINE_string("replay_dir", None,  "League of Legends *.rofl replay directory")
flags.DEFINE_integer("max_games", -1,    "(Optional) Maximum number of replays to build metadata for")
flags.mark_flag_as_required('replay_dir')

SQL_TO_JSON_MAPPING = { "team": "TEAM", "seconds": "TIME_PLAYED", "kills": "CHAMPIONS_KILLED", "deaths": "NUM_DEATHS", "gold_earned": "GOLD_EARNED", "damage_dealt": "TOTAL_DAMAGE_DEALT_TO_CHAMPIONS", "time_spent_dead": "TOTAL_TIME_SPENT_DEAD", "win": "WIN", "all_in_pings": "ALL_IN_PINGS", "assists": "ASSISTS", "assist_me_pings": "ASSIST_ME_PINGS", "bait_pings": "BAIT_PINGS", "baron_kills": "BARON_KILLS", "barracks_killed": "BARRACKS_KILLED", "barracks_takedowns": "BARRACKS_TAKEDOWNS", "basic_pings": "BASIC_PINGS", "bounty_level": "BOUNTY_LEVEL", "champions_killed": "CHAMPIONS_KILLED", "champion_mission_stat_0": "CHAMPION_MISSION_STAT_0", "champion_mission_stat_1": "CHAMPION_MISSION_STAT_1", "champion_mission_stat_2": "CHAMPION_MISSION_STAT_2", "champion_mission_stat_3": "CHAMPION_MISSION_STAT_3", "champion_transform": "CHAMPION_TRANSFORM", "command_pings": "COMMAND_PINGS", "consumables_purchased": "CONSUMABLES_PURCHASED", "danger_pings": "DANGER_PINGS", "double_kills": "DOUBLE_KILLS", "dragon_kills": "DRAGON_KILLS", "enemy_missing_pings": "ENEMY_MISSING_PINGS", "enemy_vision_pings": "ENEMY_VISION_PINGS", "exp": "EXP", "friendly_dampen_lost": "FRIENDLY_DAMPEN_LOST", "friendly_hq_lost": "FRIENDLY_HQ_LOST", "friendly_turret_lost": "FRIENDLY_TURRET_LOST", "game_ended_in_early_surrender": "GAME_ENDED_IN_EARLY_SURRENDER", "game_ended_in_surrender": "GAME_ENDED_IN_SURRENDER", "get_back_pings": "GET_BACK_PINGS", "gold_spent": "GOLD_SPENT", "hold_pings": "HOLD_PINGS", "horde_kills": "HORDE_KILLS", "hq_killed": "HQ_KILLED", "hq_takedowns": "HQ_TAKEDOWNS", "id": "ID", "individual_position": "INDIVIDUAL_POSITION", "item0": "ITEM0", "item1": "ITEM1", "item2": "ITEM2", "item3": "ITEM3", "item4": "ITEM4", "item5": "ITEM5", "item6": "ITEM6", "items_purchased": "ITEMS_PURCHASED", "keystone_id": "KEYSTONE_ID", "killing_sprees": "KILLING_SPREES", "largest_ability_damage": "LARGEST_ABILITY_DAMAGE", "largest_attack_damage": "LARGEST_ATTACK_DAMAGE", "largest_critical_strike": "LARGEST_CRITICAL_STRIKE", "largest_killing_spree": "LARGEST_KILLING_SPREE", "largest_multi_kill": "LARGEST_MULTI_KILL", "last_takedown_time": "LAST_TAKEDOWN_TIME", "level": "LEVEL", "longest_time_spent_living": "LONGEST_TIME_SPENT_LIVING", "magic_damage_dealt_player": "MAGIC_DAMAGE_DEALT_PLAYER", "magic_damage_dealt_to_champions": "MAGIC_DAMAGE_DEALT_TO_CHAMPIONS", "magic_damage_taken": "MAGIC_DAMAGE_TAKEN", "minions_killed": "MINIONS_KILLED", "muted_all": "MUTED_ALL", "name": "NAME", "need_vision_pings": "NEED_VISION_PINGS", "neutral_minions_killed": "NEUTRAL_MINIONS_KILLED", "neutral_minions_killed_enemy_jungle": "NEUTRAL_MINIONS_KILLED_ENEMY_JUNGLE", "neutral_minions_killed_your_jungle": "NEUTRAL_MINIONS_KILLED_YOUR_JUNGLE", "node_capture": "NODE_CAPTURE", "node_capture_assist": "NODE_CAPTURE_ASSIST", "node_neutralize": "NODE_NEUTRALIZE", "node_neutralize_assist": "NODE_NEUTRALIZE_ASSIST", "num_deaths": "NUM_DEATHS", "objectives_stolen": "OBJECTIVES_STOLEN", "objectives_stolen_assists": "OBJECTIVES_STOLEN_ASSISTS", "on_my_way_pings": "ON_MY_WAY_PINGS", "penta_kills": "PENTA_KILLS", "perk0": "PERK0", "perk0_var1": "PERK0_VAR1", "perk0_var2": "PERK0_VAR2", "perk0_var3": "PERK0_VAR3", "perk1": "PERK1", "perk1_var1": "PERK1_VAR1", "perk1_var2": "PERK1_VAR2", "perk1_var3": "PERK1_VAR3", "perk2": "PERK2", "perk2_var1": "PERK2_VAR1", "perk2_var2": "PERK2_VAR2", "perk2_var3": "PERK2_VAR3", "perk3": "PERK3", "perk3_var1": "PERK3_VAR1", "perk3_var2": "PERK3_VAR2", "perk3_var3": "PERK3_VAR3", "perk4": "PERK4", "perk4_var1": "PERK4_VAR1", "perk4_var2": "PERK4_VAR2", "perk4_var3": "PERK4_VAR3", "perk5": "PERK5", "perk5_var1": "PERK5_VAR1", "perk5_var2": "PERK5_VAR2", "perk5_var3": "PERK5_VAR3", "perk_primary_style": "PERK_PRIMARY_STYLE", "perk_sub_style": "PERK_SUB_STYLE", "physical_damage_dealt_player": "PHYSICAL_DAMAGE_DEALT_PLAYER", "physical_damage_dealt_to_champions": "PHYSICAL_DAMAGE_DEALT_TO_CHAMPIONS", "physical_damage_taken": "PHYSICAL_DAMAGE_TAKEN", "ping": "PING", "players_i_muted": "PLAYERS_I_MUTED", "players_that_muted_me": "PLAYERS_THAT_MUTED_ME", "player_augment_1": "PLAYER_AUGMENT_1", "player_augment_2": "PLAYER_AUGMENT_2", "player_augment_3": "PLAYER_AUGMENT_3", "player_augment_4": "PLAYER_AUGMENT_4", "player_position": "PLAYER_POSITION", "player_role": "PLAYER_ROLE", "player_score_0": "PLAYER_SCORE_0", "player_score_1": "PLAYER_SCORE_1", "player_score_10": "PLAYER_SCORE_10", "player_score_11": "PLAYER_SCORE_11", "player_score_2": "PLAYER_SCORE_2", "player_score_3": "PLAYER_SCORE_3", "player_score_4": "PLAYER_SCORE_4", "player_score_5": "PLAYER_SCORE_5", "player_score_6": "PLAYER_SCORE_6", "player_score_7": "PLAYER_SCORE_7", "player_score_8": "PLAYER_SCORE_8", "player_score_9": "PLAYER_SCORE_9", "player_subteam": "PLAYER_SUBTEAM", "player_subteam_placement": "PLAYER_SUBTEAM_PLACEMENT", "push_pings": "PUSH_PINGS", "puuid": "PUUID", "quadra_kills": "QUADRA_KILLS", "retreat_pings": "RETREAT_PINGS", "rift_herald_kills": "RIFT_HERALD_KILLS", "sight_wards_bought_in_game": "SIGHT_WARDS_BOUGHT_IN_GAME", "skin": "SKIN", "spell1_cast": "SPELL1_CAST", "spell2_cast": "SPELL2_CAST", "spell3_cast": "SPELL3_CAST", "spell4_cast": "SPELL4_CAST", "stat_perk_0": "STAT_PERK_0", "stat_perk_1": "STAT_PERK_1", "stat_perk_2": "STAT_PERK_2", "summon_spell1_cast": "SUMMON_SPELL1_CAST", "summon_spell2_cast": "SUMMON_SPELL2_CAST", "team_early_surrendered": "TEAM_EARLY_SURRENDERED", "team_objective": "TEAM_OBJECTIVE", "team_position": "TEAM_POSITION", "time_ccing_others": "TIME_CCING_OTHERS", "time_of_from_last_disconnect": "TIME_OF_FROM_LAST_DISCONNECT", "time_played": "TIME_PLAYED", "time_spent_disconnected": "TIME_SPENT_DISCONNECTED", "total_damage_dealt": "TOTAL_DAMAGE_DEALT", "total_damage_dealt_to_buildings": "TOTAL_DAMAGE_DEALT_TO_BUILDINGS", "total_damage_dealt_to_champions": "TOTAL_DAMAGE_DEALT_TO_CHAMPIONS", "total_damage_dealt_to_objectives": "TOTAL_DAMAGE_DEALT_TO_OBJECTIVES", "total_damage_dealt_to_turrets": "TOTAL_DAMAGE_DEALT_TO_TURRETS", "total_damage_self_mitigated": "TOTAL_DAMAGE_SELF_MITIGATED", "total_damage_shielded_on_teammates": "TOTAL_DAMAGE_SHIELDED_ON_TEAMMATES", "total_damage_taken": "TOTAL_DAMAGE_TAKEN", "total_heal": "TOTAL_HEAL", "total_heal_on_teammates": "TOTAL_HEAL_ON_TEAMMATES", "total_time_crowd_control_dealt": "TOTAL_TIME_CROWD_CONTROL_DEALT", "total_time_crowd_control_dealt_to_champions": "TOTAL_TIME_CROWD_CONTROL_DEALT_TO_CHAMPIONS", "total_time_spent_dead": "TOTAL_TIME_SPENT_DEAD", "total_units_healed": "TOTAL_UNITS_HEALED", "triple_kills": "TRIPLE_KILLS", "true_damage_dealt_player": "TRUE_DAMAGE_DEALT_PLAYER", "true_damage_dealt_to_champions": "TRUE_DAMAGE_DEALT_TO_CHAMPIONS", "true_damage_taken": "TRUE_DAMAGE_TAKEN", "turrets_killed": "TURRETS_KILLED", "turret_takedowns": "TURRET_TAKEDOWNS", "unreal_kills": "UNREAL_KILLS", "victory_point_total": "VICTORY_POINT_TOTAL", "vision_cleared_pings": "VISION_CLEARED_PINGS", "vision_score": "VISION_SCORE", "vision_wards_bought_in_game": "VISION_WARDS_BOUGHT_IN_GAME", "ward_killed": "WARD_KILLED", "ward_placed": "WARD_PLACED", "ward_placed_detector": "WARD_PLACED_DETECTOR", "was_afk": "WAS_AFK", "was_afk_after_failed_surrender": "WAS_AFK_AFTER_FAILED_SURRENDER", "was_early_surrender_accomplice": "WAS_EARLY_SURRENDER_ACCOMPLICE", "was_leaver": "WAS_LEAVER", "was_surrender_due_to_afk": "WAS_SURRENDER_DUE_TO_AFK", "win": "WIN"}
SQL_FIELDS = ["game_id", "team", "seconds", "kills", "deaths", "gold_earned", "damage_dealt", "time_spent_dead", "win", "all_in_pings", "assists", "assist_me_pings", "bait_pings", "baron_kills", "barracks_killed", "barracks_takedowns", "basic_pings", "bounty_level", "champions_killed", "champion_mission_stat_0", "champion_mission_stat_1", "champion_mission_stat_2", "champion_mission_stat_3", "champion_transform", "command_pings", "consumables_purchased", "danger_pings", "double_kills", "dragon_kills", "enemy_missing_pings", "enemy_vision_pings", "exp", "friendly_dampen_lost", "friendly_hq_lost", "friendly_turret_lost", "game_ended_in_early_surrender", "game_ended_in_surrender", "get_back_pings", "gold_spent", "hold_pings", "horde_kills", "hq_killed", "hq_takedowns", "id", "individual_position", "item0", "item1", "item2", "item3", "item4", "item5", "item6", "items_purchased", "keystone_id", "killing_sprees", "largest_ability_damage", "largest_attack_damage", "largest_critical_strike", "largest_killing_spree", "largest_multi_kill", "last_takedown_time", "level", "longest_time_spent_living", "magic_damage_dealt_player", "magic_damage_dealt_to_champions", "magic_damage_taken", "minions_killed", "muted_all", "name", "need_vision_pings", "neutral_minions_killed", "neutral_minions_killed_enemy_jungle", "neutral_minions_killed_your_jungle", "node_capture", "node_capture_assist", "node_neutralize", "node_neutralize_assist", "num_deaths", "objectives_stolen", "objectives_stolen_assists", "on_my_way_pings", "penta_kills", "perk0", "perk0_var1", "perk0_var2", "perk0_var3", "perk1", "perk1_var1", "perk1_var2", "perk1_var3", "perk2", "perk2_var1", "perk2_var2", "perk2_var3", "perk3", "perk3_var1", "perk3_var2", "perk3_var3", "perk4", "perk4_var1", "perk4_var2", "perk4_var3", "perk5", "perk5_var1", "perk5_var2", "perk5_var3", "perk_primary_style", "perk_sub_style", "physical_damage_dealt_player", "physical_damage_dealt_to_champions", "physical_damage_taken", "ping", "players_i_muted", "players_that_muted_me", "player_augment_1", "player_augment_2", "player_augment_3", "player_augment_4", "player_position", "player_role", "player_score_0", "player_score_1", "player_score_10", "player_score_11", "player_score_2", "player_score_3", "player_score_4", "player_score_5", "player_score_6", "player_score_7", "player_score_8", "player_score_9", "player_subteam", "player_subteam_placement", "push_pings", "puuid", "quadra_kills", "retreat_pings", "rift_herald_kills", "sight_wards_bought_in_game", "skin", "spell1_cast", "spell2_cast", "spell3_cast", "spell4_cast", "stat_perk_0", "stat_perk_1", "stat_perk_2", "summon_spell1_cast", "summon_spell2_cast", "team_early_surrendered", "team_objective", "team_position", "time_ccing_others", "time_of_from_last_disconnect", "time_played", "time_spent_disconnected", "total_damage_dealt", "total_damage_dealt_to_buildings", "total_damage_dealt_to_champions", "total_damage_dealt_to_objectives", "total_damage_dealt_to_turrets", "total_damage_self_mitigated", "total_damage_shielded_on_teammates", "total_damage_taken", "total_heal", "total_heal_on_teammates", "total_time_crowd_control_dealt", "total_time_crowd_control_dealt_to_champions", "total_time_spent_dead", "total_units_healed", "triple_kills", "true_damage_dealt_player", "true_damage_dealt_to_champions", "true_damage_taken", "turrets_killed", "turret_takedowns", "unreal_kills", "victory_point_total", "vision_cleared_pings", "vision_score", "vision_wards_bought_in_game", "ward_killed", "ward_placed", "ward_placed_detector", "was_afk", "was_afk_after_failed_surrender", "was_early_surrender_accomplice", "was_leaver", "was_surrender_due_to_afk"]
SQL_TYPES  = ["TEXT", "INTEGER", "REAL", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "TEXT", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "TEXT", "TEXT", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "TEXT", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "TEXT", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "TEXT", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "TEXT", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER", "INTEGER"]
SQL_METADATA_TABLE = f"""CREATE TABLE IF NOT EXISTS players (
    {",".join([f"{field} {type}" for field, type in zip(SQL_FIELDS, SQL_TYPES)])}
)"""

def main(unused_argv):
    # Set up SQLite database
    conn = sqlite3.connect('ezreal_players.db')
    c = conn.cursor()
    
    c.execute(SQL_METADATA_TABLE)

    scraper = ReplayScraper(
        game_dir="",
        replay_dir=FLAGS.replay_dir,
        dataset_dir="",
        scraper_dir="",
        region="",
        replay_speed=0)

    replays = os.listdir(FLAGS.replay_dir)
    replays = replays[0:FLAGS.max_games]

    print('game_ids:', replays)
    for i, replay_path in enumerate(replays):
        print(f"SCRAPING {i}/{len(replays)}: {replay_path}")
        full_game_id = replay_path.replace(".rofl", "")
        metadata, _ = scraper.get_metadata(
            replay_path,
            path=True)
        if metadata == None:
            continue

         # Extract Ezreal player data
        stats = json.loads(metadata['statsJson'])
        for player in stats:
            if 'Ezreal' in player['SKIN']:
                vals = [full_game_id]

                for sql_field, sql_type in zip(SQL_FIELDS[1:], SQL_TYPES[1:]):
                    json_field = SQL_TO_JSON_MAPPING[sql_field]
                    placeholder = 0 if sql_type in ["REAL", "INTEGER"] else ""
                    val = player.get(json_field, placeholder)
                    vals.append(val)

                # # Insert into database
                question_marks = ",".join(["?" for f in range(len(SQL_FIELDS))])
                c.execute(f"INSERT INTO players VALUES ({question_marks})", tuple(vals))
                
                break
    
    # Save (commit) the changes and close the connection
    conn.commit()
    conn.close()

def entry_point():
    app.run(main)

if __name__ == "__main__":
    app.run(main)