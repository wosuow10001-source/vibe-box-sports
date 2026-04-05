"""
V6 Probability Calibration Module
Uses Isotonic Regression to map raw model probabilities to well-calibrated ones.
"""

import numpy as np
from sklearn.isotonic import IsotonicRegression
import pickle
import os
from pathlib import Path

class ProbabilityCalibrator:
    def __init__(self, league="EPL"):
        self.league = league
        self.calibrators = {
            'home': IsotonicRegression(out_of_bounds='clip'),
            'draw': IsotonicRegression(out_of_bounds='clip'),
            'away': IsotonicRegression(out_of_bounds='clip')
        }
        self.fitted = False
        self.model_dir = Path("models/calibration")
        self.model_dir.mkdir(parents=True, exist_ok=True)

    def fit(self, y_true_labels, y_probs_matrix):
        """
        Fit calibrators using historical predictions and actual results.
        y_true_labels: list of actual outcomes (0: home win, 1: draw, 2: away win)
        y_probs_matrix: Nx3 matrix of predicted probabilities [P_home, P_draw, P_away]
        """
        # Convert labels to binary for each class
        y_true_home = (np.array(y_true_labels) == 0).astype(int)
        y_true_draw = (np.array(y_true_labels) == 1).astype(int)
        y_true_away = (np.array(y_true_labels) == 2).astype(int)

        self.calibrators['home'].fit(y_probs_matrix[:, 0], y_true_home)
        self.calibrators['draw'].fit(y_probs_matrix[:, 1], y_true_draw)
        self.calibrators['away'].fit(y_probs_matrix[:, 2], y_true_away)
        
        self.fitted = True
        self.save()

    def calibrate(self, raw_probs):
        """
        Calibrate a single set of probabilities.
        raw_probs: [P_home, P_draw, P_away]
        """
        if not self.fitted:
            if not self.load():
                return raw_probs # Return as-is if no calibration data

        c_home = self.calibrators['home'].transform([raw_probs[0]])[0]
        c_draw = self.calibrators['draw'].transform([raw_probs[1]])[0]
        c_away = self.calibrators['away'].transform([raw_probs[2]])[0]

        # Re-normalize to sum to 1
        total = c_home + c_draw + c_away
        if total > 0:
            return [c_home/total, c_draw/total, c_away/total]
        return raw_probs

    def save(self):
        with open(self.model_dir / f"calibrator_{self.league}.pkl", 'wb') as f:
            pickle.dump(self.calibrators, f)

    def load(self):
        path = self.model_dir / f"calibrator_{self.league}.pkl"
        if path.exists():
            with open(path, 'rb') as f:
                self.calibrators = pickle.dump(self.calibrators, f)
            self.fitted = True
            return True
        return False
