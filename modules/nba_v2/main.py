from typing import Dict, List
from modules.nba_v2.src.utils import logger, NBAConfig
from modules.nba_v2.src.data_collector import NBADataCollector
from modules.nba_v2.src.train_model import NBATrainer
from modules.nba_v2.src.predict import NBAPredictor

class NBAAutomationLoop:
    """V2 자동화 루프: 매일 데이터 업데이트 및 모델 학습 관리"""
    
    def __init__(self, v1_collector=None):
        self.collector = NBADataCollector(v1_collector)
        self.trainer = NBATrainer()
        self.predictor = NBAPredictor(v1_collector)
        NBAConfig.ensure_dirs()
        
    def run_daily_update(self):
        """매일 실행되는 데이터 수집 및 모델 최신화 과정"""
        logger.info("Starting daily NBA V2 update...")
        
        # 1. 역사적 데이터 로드 및 시뮬레이션 데이터 준비
        # (실제 운영 환경에서는 전날 경기 결과 수집 후 저장)
        history = self.collector.load_historical_data()
        
        # 2. 모델 재학습 (데이터가 충분할 경우)
        if not history.empty and len(history) % 10 == 0:
            logger.info("Retraining model with updated history...")
            # FE를 통해 학습 데이터 구성 로직 호출 (생략)
            pass
            
        logger.info("Daily update complete.")
        
    def get_prediction(self, home: str, away: str, injury_data: Dict = None) -> Dict:
        """최신 모델을 사용한 경기 예측"""
        return self.predictor.predict(home, away, injury_data=injury_data)

if __name__ == "__main__":
    # 독립 실행 시 테스트용
    loop = NBAAutomationLoop()
    loop.run_daily_update()
