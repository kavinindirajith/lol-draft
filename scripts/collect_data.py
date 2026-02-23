"""
Collect match data from Riot API
Usage: python scripts/collect_data.py
"""

import sys
import yaml
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.collector import RiotDataCollector
from src.processor import MatchProcessor


def main():
    # Load config
    with open('../config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Initialize
    collector = RiotDataCollector(
        api_key=config['riot_api_key'],
        region=config['region']
    )
    processor = MatchProcessor()

    # Collect
    print("Step 1: Getting Challenger players...")
    puuids = collector.get_challenger_puuids(count=10)

    print("Step 2: Collecting match IDs...")
    match_ids = collector.get_match_ids(puuids, matches_per_player=20)

    print("Step 3: Downloading matches...")
    matches = collector.download_matches(match_ids[:100])

    print("Step 4: Processing matches...")
    df = processor.process_matches(matches)

    # Save
    output_path = Path('data/match_drafts.parquet')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path)

    print(f"✅ Saved {len(df)} matches to {output_path}")


if __name__ == "__main__":
    main()