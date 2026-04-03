import os
import joblib
import numpy as np
from sklearn.isotonic import IsotonicRegression
from modules.nba_v2.src.utils import logger, NBAConfig

class NBACalibrator:
    """V2 캘리브레이터: Isotonic Regression을 이용한 확률 편향 수정"""
    
    def __init__(self):
        self.path = os.path.join(NBAConfig.MODEL_DIR, "calibrator.joblib")
        self.calibrator = None
        
    def train(self, predicted_probs: np.array, actual_outcomes: np.array):
        """실제 결과를 바탕으로 캘리브레이션 모델 학습"""
        if len(predicted_probs) < 5:
            return
            
        logger.info("Training Isotonic Regression calibrator...")
        self.calibrator = IsotonicRegression(out_of_bounds='clip')
        self.calibrator.fit(predicted_probs, actual_outcomes)
        joblib.dump(self.calibrator, self.path)
        
    def calibrate(self, prob: float) -> float:
        """기존 확률을 실제 결과와 일치하도록 보정"""
        if not self.calibrator and os.path.exists(self.path):
            self.calibrator = joblib.load(self.path)
            
        if self.calibrator:
            return float(self.calibrator.predict([prob])[0])
        return prob
