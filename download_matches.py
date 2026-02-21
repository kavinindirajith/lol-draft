"""
Download full match data for each match ID
"""

from riotwatcher import LolWatcher
import pandas as pd
import json
import time
from tqdm import tqdm

# PUT YOUR API KEY HERE
API_KEY = "RGAPI-03ddf5d1-c485-4d38-99b2-64ef1ae3bf32"  # Same key as before

lol_watcher = LolWatcher(API_KEY)

with open('champion_name_map.json', 'r') as f:
    CHAMPION_ID_TO_NAME = json.load(f)


def get_champion_name(champion_id):
    """Convert champion ID to name"""
    # Handle -1 (no ban)
    if champion_id == -1:
        return None

    # Convert to string
    champ_id_str = str(champion_id)

    # Return name or ID if not found
    return CHAMPION_ID_TO_NAME.get(champ_id_str, f"Unknown_{champion_id}")

def get_match_data(match_id):
    """Download detailed match data"""
    try:
        match = lol_watcher.match.by_id('americas', match_id)
        if match['info']['gameDuration'] > 600:
            return match
        else:
            return None
    except Exception as e:
        print(f"Error downloading {match_id}: {e}")
        return None

def extract_draft_info(match_data):
    """Extract just the important draft information"""

    if not match_data:
        return None

    try:
        info = match_data['info']

        # Get teams
        teams = info['teams']
        participants = info['participants']

        # Extract picks and bans
        blue_team = [p for p in participants if p['teamId'] == 100]
        red_team = [p for p in participants if p['teamId'] == 200]

        draft_data = {
            # Blue team (team 100)
            'blue_picks': [p['championName'] for p in blue_team],
            'blue_bans': [
                get_champion_name(ban['championId'])
                for ban in teams[0]['bans']
                if ban['championId'] != -1
            ],

            # Red team (team 200)
            'red_picks': [p['championName'] for p in red_team],
            'red_bans':[
                get_champion_name(ban['championId'])
                for ban in teams[1]['bans']
                if ban['championId'] != -1
            ],

            # Outcome
            'blue_win': teams[0]['win'],
            'red_win': teams[1]['win'],

            # Metadata
            'game_duration': info['gameDuration'],
            'game_version': info['gameVersion'],
            'match_id': match_data['metadata']['matchId']
        }

        return draft_data

    except Exception as e:
        print(f"Error extracting draft: {e}")
        return None

def main():
    """Download and process all matches"""

    # Load match IDs
    try:
        match_ids_df = pd.read_csv('match_ids.csv')
        match_ids = match_ids_df['match_id'].tolist()
        print(f"Found {len(match_ids)} match IDs to download")
    except FileNotFoundError:
        print("match_ids.csv not found. Run collect_match_ids.py first!")
        return

    # Download matches
    all_drafts = []

    print("\nDownloading match data...")
    for match_id in tqdm(match_ids[:100]):  # Start with 100 matches

        # Get match data
        match_data = get_match_data(match_id)

        # Extract draft info
        draft = extract_draft_info(match_data)

        if draft:
            all_drafts.append(draft)

        # Rate limit: 1.2 seconds between requests
        time.sleep(1.2)

    # Save to CSV
    if all_drafts:
        df = pd.DataFrame(all_drafts)
        df.to_csv('match_drafts.csv', index=False)
        print(f"\nDownloaded {len(all_drafts)} matches")
        print(f"Saved to match_drafts.csv")

        # Show sample
        print("\nSample data:")
        print(df.head(2))
    else:
        print("No matches downloaded successfully")

if __name__ == "__main__":
    main()