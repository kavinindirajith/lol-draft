"""
Feature engineering for draft prediction
Computes pairwise synergies and counter matchups from training data
"""

import numpy as np
import pandas as pd
from itertools import combinations


class DraftFeatureEngineer:
    def __init__(self):
        self.synergy_stats = {}   # (champ_a, champ_b) -> {'wins': int, 'games': int}
        self.counter_stats = {}   # (champ_a, champ_b) -> {'wins': int, 'games': int}

    def fit(self, df):
        """Learn synergy and counter stats from training data"""
        self.synergy_stats = {}
        self.counter_stats = {}

        for _, row in df.iterrows():
            blue_win = row['blue_win']
            blue_picks = row['blue_picks']
            red_picks = row['red_picks']

            # Pairwise synergies - same team duos
            for champ_a, champ_b in combinations(sorted(blue_picks), 2):
                key = (champ_a, champ_b)
                if key not in self.synergy_stats:
                    self.synergy_stats[key] = {'wins': 0, 'games': 0}
                self.synergy_stats[key]['games'] += 1
                if blue_win:
                    self.synergy_stats[key]['wins'] += 1

            for champ_a, champ_b in combinations(sorted(red_picks), 2):
                key = (champ_a, champ_b)
                if key not in self.synergy_stats:
                    self.synergy_stats[key] = {'wins': 0, 'games': 0}
                self.synergy_stats[key]['games'] += 1
                if not blue_win:
                    self.synergy_stats[key]['wins'] += 1

            # Counter matchups - cross team
            for blue_champ in blue_picks:
                for red_champ in red_picks:
                    key = (blue_champ, red_champ)
                    if key not in self.counter_stats:
                        self.counter_stats[key] = {'wins': 0, 'games': 0}
                    self.counter_stats[key]['games'] += 1
                    if blue_win:
                        self.counter_stats[key]['wins'] += 1

        return self

    def _get_synergy_score(self, champ_a, champ_b, min_games=3):
        """Get win rate for a champion duo, default 0.5 if insufficient data"""
        key = tuple(sorted([champ_a, champ_b]))
        stats = self.synergy_stats.get(key)
        if not stats or stats['games'] < min_games:
            return 0.5
        return stats['wins'] / stats['games']

    def _get_counter_score(self, blue_champ, red_champ, min_games=3):
        """Get win rate for blue_champ vs red_champ matchup"""
        key = (blue_champ, red_champ)
        stats = self.counter_stats.get(key)
        if not stats or stats['games'] < min_games:
            return 0.5
        return stats['wins'] / stats['games']

    def transform(self, df):
        """Transform dataframe into synergy/counter feature matrix"""
        features = []

        for _, row in df.iterrows():
            blue_picks = row['blue_picks']
            red_picks = row['red_picks']

            # Average synergy score for each team
            blue_synergies = [
                self._get_synergy_score(a, b)
                for a, b in combinations(blue_picks, 2)
            ]
            red_synergies = [
                self._get_synergy_score(a, b)
                for a, b in combinations(red_picks, 2)
            ]

            # Average counter score across all matchups
            counter_scores = [
                self._get_counter_score(bc, rc)
                for bc in blue_picks
                for rc in red_picks
            ]

            features.append({
                'blue_avg_synergy': np.mean(blue_synergies),
                'red_avg_synergy': np.mean(red_synergies),
                'synergy_diff': np.mean(blue_synergies) - np.mean(red_synergies),
                'avg_counter_score': np.mean(counter_scores),
                'min_counter_score': np.min(counter_scores),
                'max_counter_score': np.max(counter_scores),
            })

        return pd.DataFrame(features)