"""
Process raw match data into clean features
"""

import pandas as pd
import json


class MatchProcessor:
    """Process raw match data"""

    def __init__(self, champion_mapping_path='data/external/champion_name_map.json'):
        with open(champion_mapping_path, 'r') as f:
            self.champion_map = json.load(f)

    def get_champion_name(self, champion_id):
        """Convert champion ID to name"""
        if champion_id == -1:
            return None
        return self.champion_map.get(str(champion_id), f"Unknown_{champion_id}")

    def extract_draft(self, match_data):
        """Extract draft information from match"""
        info = match_data['info']
        teams = info['teams']
        participants = info['participants']

        blue_team = [p for p in participants if p['teamId'] == 100]
        red_team = [p for p in participants if p['teamId'] == 200]

        return {
            'blue_picks': [p['championName'] for p in blue_team],
            'blue_bans': [
                self.get_champion_name(ban['championId'])
                for ban in teams[0]['bans']
                if ban['championId'] != -1
            ],
            'red_picks': [p['championName'] for p in red_team],
            'red_bans': [
                self.get_champion_name(ban['championId'])
                for ban in teams[1]['bans']
                if ban['championId'] != -1
            ],
            'blue_win': teams[0]['win'],
            'game_duration': info['gameDuration'],
            'match_id': match_data['metadata']['matchId']
        }

    def process_matches(self, matches):
        """Process list of matches into DataFrame"""
        drafts = [self.extract_draft(m) for m in matches]
        drafts = [d for d in drafts if d is not None]  # Remove failed
        return pd.DataFrame(drafts)