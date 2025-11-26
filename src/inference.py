import torch
import numpy as np
import time
import argparse
import sys
import os

# src 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.logger import DataLogger

# Lerobot 관련 임포트 (실제 환경에 맞게 주석 해제 필요)
# from lerobot.common.policies.act.modeling_act import ACTPolicy
# from lerobot.common.policies.diffusion.modeling_diffusion import DiffusionPolicy

import cv2

# ... (imports)

class InferenceEngine:
    def __init__(self, model_path, model_type="act", device="cuda", cam_id=0):
        """
        추론 엔진 초기화
        :param model_path: 모델 가중치 파일 경로
        :param model_type: 모델 유형 ("act" 또는 "so-101")
        :param device: 실행 디바이스 ("cuda" 또는 "cpu")
        :param cam_id: 카메라 디바이스 ID (기본값: 0)
        """
        self.device = device
        self.model_type = model_type
        self.model = self.load_model(model_path, model_type)
        self.logger = DataLogger()
        
        # 카메라 초기화
        self.cap = cv2.VideoCapture(cam_id)
        if not self.cap.isOpened():
            print(f"[경고] 카메라 {cam_id}를 열 수 없습니다. 더미 데이터를 사용합니다.")
            self.use_dummy_camera = True
        else:
            print(f"카메라 {cam_id} 초기화 성공")
            self.use_dummy_camera = False
            
        print(f"모델 {model_type}이(가) {device}에서 로드되었습니다.")

    # ... (load_model)

    def get_observation(self):
        """
        현재 상태(이미지, 관절 값 등)를 가져오는 함수
        """
        if self.use_dummy_camera:
            return {"image": np.random.rand(3, 480, 640), "state": np.random.rand(6)}
        
        ret, frame = self.cap.read()
        if not ret:
            print("[오류] 프레임을 읽을 수 없습니다.")
            return {"image": np.zeros((3, 480, 640)), "state": np.random.rand(6)}
            
        # BGR -> RGB 변환 및 전처리 (모델에 맞게 리사이즈 필요)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # frame = cv2.resize(frame, (640, 480)) 
        
        # PyTorch Tensor 변환 (C, H, W)
        image_tensor = torch.from_numpy(frame).permute(2, 0, 1).float() / 255.0
        
        return {"image": image_tensor, "state": np.random.rand(6)} # state는 로봇 연동 필요

    def predict_action(self, observation):
        """
        관측된 상태를 기반으로 다음 액션을 예측하는 함수
        """
        # input_tensor = torch.from_numpy(observation['image']).to(self.device)
        # action = self.model(input_tensor)
        return np.random.rand(14) # 예시 액션 차원

    def run_loop(self, duration_sec=10):
        """
        메인 추론 루프
        :param duration_sec: 실행 지속 시간 (초)
        """
        self.logger.start_episode()
        start_time = time.time()
        
        try:
            while time.time() - start_time < duration_sec:
                obs = self.get_observation()
                action = self.predict_action(obs)
                
                # 액션 실행 (로봇 제어 코드로 대체)
                # robot.move(action)
                
                # 데이터 로깅
                self.logger.log_step(obs, action)
                time.sleep(0.1) # 10Hz 루프 (필요에 따라 조정)
                
        except KeyboardInterrupt:
            print("사용자에 의해 추론이 중단되었습니다.")
        finally:
            self.logger.end_episode()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lerobot 추론 스크립트")
    parser.add_argument("--model_path", type=str, required=True, help="모델 경로")
    parser.add_argument("--model_type", type=str, default="act", choices=["act", "so-101", "custom"], help="모델 유형")
    args = parser.parse_args()

    engine = InferenceEngine(args.model_path, args.model_type)
    engine.run_loop()
