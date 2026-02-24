"""
Train Random Forest model on draft data
Usage: python scripts/train_model.py
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from sklearn.preprocessing import MultiLabelBinarizer


class DraftPredictor:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.mlb_blue = MultiLabelBinarizer()
        self.mlb_red = MultiLabelBinarizer()
        self.all_champions = None

    def build_features(self, df):
        """One-hot encode champion picks into feature matrix"""
        blue_encoded = self.mlb_blue.fit_transform(df['blue_picks'])
        red_encoded = self.mlb_red.fit_transform(df['red_picks'])
        return np.hstack([blue_encoded, red_encoded])

    def train(self, df):
        """Train model on processed match dataframe"""
        print(f"Training on {len(df)} matches...")

        X = self.build_features(df)
        y = df['blue_win'].astype(int)

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        self.model.fit(X_train, y_train)

        # Evaluate
        y_pred = self.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Test Accuracy: {accuracy:.2%}")
        print(classification_report(y_test, y_pred, target_names=['Red Win', 'Blue Win']))

        return accuracy

    def predict(self, blue_picks, red_picks):
        """Predict win probability given picks"""
        blue_encoded = self.mlb_blue.transform([blue_picks])
        red_encoded = self.mlb_red.transform([red_picks])
        X = np.hstack([blue_encoded, red_encoded])
        prob = self.model.predict_proba(X)[0]
        return {'blue_win_prob': prob[1], 'red_win_prob': prob[0]}

    def save(self, path='models/draft_predictor.pkl'):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(self, f)
        print(f"Model saved to {path}")

    @classmethod
    def load(cls, path='models/draft_predictor.pkl'):
        with open(path, 'rb') as f:
            return pickle.load(f)

