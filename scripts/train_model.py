"""
Train model on collected match data
Usage: python scripts/train_model.py
"""

import pandas as pd
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from src.trainer import DraftPredictor

def main():
    predictor = DraftPredictor()
    print("Loading data...")
    df = pd.read_parquet("data/match_drafts.parquet")
    print(f"Loaded {len(df)} matches")

    print("Training model...")
    predictor.train(df)

    print("Training complete")
    print("Saving model...")
    predictor.save()

if __name__ == "__main__":
    main()