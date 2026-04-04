import os
# joblib is imported lazily to avoid startup crashes in static environments without heavy ML libs
import pandas as pd
import numpy as np
# sklearn is imported lazily to avoid startup crashes in static environments without heavy ML libs
from modules.nba_v2.src.utils import logger, NBAConfig

class NBATrainer:
    """V2 모델 트레이너: 수집된 데이터를 바탕으로 승패 예측 모델 학습"""
    
    def __init__(self):
        self.model_path = os.path.join(NBAConfig.MODEL_DIR, "win_predictor.joblib")
        self.model = None
        
    def train(self, X: pd.DataFrame, y: pd.Series):
        """GradientBoosting 모델 학습"""
        from sklearn.ensemble import GradientBoostingClassifier
        if X.empty or len(X) < 10:
            logger.warning("Insufficient data for training. Using synthetic initialization.")
            self._initialize_bootstrap_model()
            return
            
        logger.info(f"Training model with {len(X)} samples...")
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=3,
            random_state=42
        )
        self.model.fit(X, y)
        self.save_model()
        
    def save_model(self):
        import joblib
        joblib.dump(self.model, self.model_path)
        logger.info(f"Model saved to {self.model_path}")
        
    def load_model(self):
        if os.path.exists(self.model_path):
            import joblib
            self.model = joblib.load(self.model_path)
            return True
        return False
        
    def _initialize_bootstrap_model(self):
        """데이터가 부족할 때 초기 모델 생성 (부트스트랩 용도)"""
        from sklearn.ensemble import GradientBoostingClassifier
        # 임의의 데이터로 초기화하여 파이프라인 작동 보장
        X_mock = pd.DataFrame(np.random.rand(20, 13)) # 13 features
        y_mock = pd.Series(np.random.randint(0, 2, 20))
        self.model = GradientBoostingClassifier()
        self.model.fit(X_mock, y_mock)
        self.save_model()
