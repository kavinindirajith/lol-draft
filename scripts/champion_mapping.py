"""
Download champion data from Riot Data Dragon
Run this once to get champion ID mapped to name
"""

import requests
import json


def get_latest_version():
    """Get latest game version"""
    url = "https://ddragon.leagueoflegends.com/api/versions.json"
    versions = requests.get(url).json()
    return versions[0]


def download_champion_data():
    """Download all champion data"""

    version = get_latest_version()
    print(f"Downloading champion data for patch {version}...")

    url = f"http://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
    response = requests.get(url)
    data = response.json()

    # Create ID to Name mapping
    champion_id_to_name = {}

    for champ_name, champ_data in data['data'].items():
        champ_id = int(champ_data['key'])  # 'key' is the ID
        champ_name = champ_data['name']  # Full name (e.g., "Twisted Fate")

        champion_id_to_name[champ_id] = champ_name

    # Save to JSON
    with open('../champion_name_map.json', 'w') as f:
        json.dump(champion_id_to_name, f, indent=2)

    print(f"Downloaded {len(champion_id_to_name)} champions")
    print(f"Saved to champion_name_map.json")

    # Show sample
    print("\nSample mappings:")
    for champ_id, name in list(champion_id_to_name.items())[:5]:
        print(f"  {champ_id}: {name}")


if __name__ == "__main__":
    download_champion_data()