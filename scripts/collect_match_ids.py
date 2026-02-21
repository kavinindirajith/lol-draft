"""
Collect Match IDs from Challenger players
"""

from riotwatcher import LolWatcher
import pandas as pd
import time
from tqdm import tqdm

# PUT YOUR API KEY HERE
API_KEY = "RGAPI-03ddf5d1-c485-4d38-99b2-64ef1ae3bf32"  # Replace with your actual key

# Initialize the watcher
lol_watcher = LolWatcher(API_KEY)

# Choose region (na1, euw1, kr, etc.)
REGION = 'na1'


def get_challenger_players(region='na1'):
    """Get list of Challenger players"""
    print("Getting Challenger players...")

    try:
        challenger = lol_watcher.league.challenger_by_queue(region, 'RANKED_SOLO_5x5')
        player_ids = [entry['puuid'] for entry in challenger['entries']]
        print(f"Found {len(player_ids)} Challenger players")
        return player_ids[:10]  # Just use first 10 for now
    except Exception as e:
        print(f"Error getting Challenger players: {e}")
        return []


def get_match_ids_for_player(puuid, count=20):
    """Get recent match IDs for a player"""
    try:
        # Get last 20 ranked matches
        matches = lol_watcher.match.matchlist_by_puuid(
            'americas',  # Americas for NA server
            puuid,
            queue=420,
            type='ranked',
            count=count
        )
        return matches
    except Exception as e:
        print(f"Error getting matches: {e}")
        return []


def main():
    """Main function to collect match IDs"""

    # Get Challenger players
    summoner_ids = get_challenger_players(REGION)

    if not summoner_ids:
        print("❌ No players found. Check your API key and region.")
        return

    # Collect match IDs
    all_match_ids = set()  # Use set to avoid duplicates

    print("\nCollecting match IDs from players...")
    for puuid in tqdm(summoner_ids):
        # Get PUUID

        # Get their match history
        match_ids = get_match_ids_for_player(puuid, count=20)
        all_match_ids.update(match_ids)

        # Rate limit: wait 1.2 seconds between requests
        time.sleep(1.2)

    # Save to file
    match_ids_list = list(all_match_ids)
    df = pd.DataFrame({'match_id': match_ids_list})
    df.to_parquet('match_ids.parquet', index=False)

    print(f"\nCollected {len(match_ids_list)} unique match IDs")
    print(f"Saved to match_ids.parquet")


if __name__ == "__main__":
    main()