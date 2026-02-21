"""
Data collection from Riot API
"""

from riotwatcher import LolWatcher
import pandas as pd
import time
from tqdm import tqdm


class RiotDataCollector:
    """Collect match data from Riot API"""

    def __init__(self, api_key, region='na1'):
        self.lol_watcher = LolWatcher(api_key)
        self.region = region
        self.routing = 'americas'  # For NA region

    def get_challenger_puuids(self, count=10):
        """Get PUUIDs of Challenger players"""
        try:
            challenger = self.lol_watcher.league.challenger_by_queue(
                self.region, 'RANKED_SOLO_5x5'
            )
            puuids = [entry['puuid'] for entry in challenger['entries']]
            return puuids[:count]
        except Exception as e:
            print(f"Error: {e}")
            return []

    def get_match_ids(self, puuids, matches_per_player=20):
        """Get ranked match IDs from players"""
        all_match_ids = set()

        for puuid in tqdm(puuids, desc="Collecting match IDs"):
            try:
                matches = self.lol_watcher.match.matchlist_by_puuid(
                    self.routing,
                    puuid,
                    queue=420,
                    type='ranked',
                    count=matches_per_player
                )
                all_match_ids.update(matches)
                time.sleep(1.2)
            except Exception as e:
                print(f"Error: {e}")
                continue

        return list(all_match_ids)

    def download_match(self, match_id):
        """Download single match with validation"""
        try:
            match = self.lol_watcher.match.by_id(self.routing, match_id)

            # Validate
            info = match['info']
            if info['queueId'] != 420:
                return None
            if info['gameDuration'] < 600:
                return None

            return match
        except Exception as e:
            print(f"Error: {e}")
            return None

    def download_matches(self, match_ids):
        """Download multiple matches"""
        matches = []

        for match_id in tqdm(match_ids, desc="Downloading matches"):
            match = self.download_match(match_id)
            if match:
                matches.append(match)
            time.sleep(1.2)

        return matches