"""
V6 Ensemble Predictor Tool
Combines Dixon-Coles, XGBoost (optional), and NB Simulation models.
"""

import numpy as np
from modules.dixon_coles_model import DixonColesModel
from modules.predictor_soccer_v3 import SoccerEngineV4
from modules.calibration import ProbabilityCalibrator
from modules.feature_engine import FeatureEngine
import os
import pickle

class EnsemblePredictorV6:
    def __init__(self, league="EPL"):
        self.league = league
        self.dc_model = DixonColesModel(league)
        self.nb_engine = SoccerEngineV4()
        self.calibrator = ProbabilityCalibrator(league)
        self.feature_engine = FeatureEngine(league)
        
        # XGBoost model placeholder
        self.xgb_model = None
        self._load_xgb_model()

    def _load_xgb_model(self):
        model_path = f"models/xgboost/xgb_{self.league}.pkl"
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                self.xgb_model = pickle.load(f)

    def predict(self, home_data, away_data, context):
        """
        Produce a weighted ensemble prediction.
        """
        # 1. Feature Extraction (includes DC rating updates)
        features_dict = self.feature_engine.extract_features(home_data, away_data, context)
        features_arr = self.feature_engine.features_to_array(features_dict)
        
        # 2. Dixon-Coles Prediction (Analytical Poisson)
        dc_res = self.dc_model.predict_score_probs(home_data['team_name'], away_data['team_name'])
        p_dc = np.array([dc_res['home_win'], dc_res['draw'], dc_res['away_win']])
        
        # 3. NB Simulation Prediction (V5 logic)
        # We pass the DC-derived xG to the NB simulator for consistency
        nb_res = self.nb_engine.predict_match(
            self.league, home_data, away_data, context, 
            xg_override={'home_xg': dc_res['home_xg'], 'away_xg': dc_res['away_xg']}
        )
        p_nb = np.array([
            nb_res['win_probabilities']['home'], 
            nb_res['win_probabilities']['draw'], 
            nb_res['win_probabilities']['away']
        ])
        
        # 4. XGBoost Prediction (ML)
        p_xgb = None
        if self.xgb_model:
            p_xgb = self.xgb_model.predict_proba([features_arr])[0]
        
        # 5. Ensemble Weighting
        # Default Weights: DC 0.4, NB 0.3, XGB 0.3 (if available)
        if p_xgb is not None:
            final_p = (0.35 * p_dc) + (0.25 * p_nb) + (0.40 * p_xgb)
        else:
            final_p = (0.55 * p_dc) + (0.45 * p_nb)
            
        # 6. Apply Probability Calibration
        calibrated_p = self.calibrator.calibrate(final_p)
        
        # Final result structure
        return {
            'win_probabilities': {
                'home': float(calibrated_p[0]),
                'draw': float(calibrated_p[1]),
                'away': float(calibrated_p[2])
            },
            'expected_goals': {
                'home': dc_res['home_xg'],
                'away': dc_res['away_xg']
            },
            'nb_simulation': nb_res, # Keep for score distribution details
            'features': features_dict,
            'model_weights': {
                'dc': 0.35 if p_xgb is not None else 0.55,
                'nb': 0.25 if p_xgb is not None else 0.45,
                'xgb': 0.40 if p_xgb is not None else 0.0
            }
        }
