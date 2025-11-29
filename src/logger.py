import h5py
import os
import time
import numpy as np
import requests
import json
import traceback
from datetime import datetime

class CustomErrorLogger:
    def __init__(self, log_dir="/opt/lerobot/logs"):
        """
        커스텀 에러 로거 초기화
        :param log_dir: 로그 파일 저장 경로
        """
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)
        self.log_file = os.path.join(self.log_dir, "error_log.json")

    def log_error(self, error_type, message, details=None):
        """
        에러 발생 시 상세 정보를 JSON 파일에 기록
        """
        timestamp = datetime.now().isoformat()
        error_entry = {
            "timestamp": timestamp,
            "type": error_type,
            "message": str(message),
            "traceback": traceback.format_exc(),
            "details": details or {}
        }
        
        # JSON 파일에 추가 (Append 모드)
        try:
            # 기존 로그 읽기 (파일이 존재하고 비어있지 않은 경우)
            logs = []
            if os.path.exists(self.log_file) and os.path.getsize(self.log_file) > 0:
                with open(self.log_file, 'r') as f:
                    try:
                        logs = json.load(f)
                    except json.JSONDecodeError:
                        logs = [] # 파일 깨짐 방지
            
            logs.append(error_entry)
            
            with open(self.log_file, 'w') as f:
                json.dump(logs, f, indent=4)
                
            print(f"[ERROR LOGGED] {error_type}: {message}")
            
        except Exception as e:
            print(f"CRITICAL: Failed to write error log: {e}")

class DataLogger:
    def __init__(self, save_dir="/opt/lerobot/data", api_url=None):
        """
        데이터 로거 초기화
        :param save_dir: 데이터 저장 경로
        :param api_url: 백엔드 API URL
        """
        self.save_dir = save_dir
        self.api_url = api_url or os.getenv("BACKEND_API_URL")
        self.robot_id = os.getenv("ROBOT_ID", "unknown_robot") # 로봇 식별 ID
        
        os.makedirs(self.save_dir, exist_ok=True)
        
        self.current_episode_file = None
        self.current_episode_id = None
        
        self.observations = []
        self.actions = []
        self.rewards = []
        
        self.error_logger = CustomErrorLogger()

    def start_episode(self, model_type="unknown"):
        """
        새로운 에피소드 기록 시작
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.robot_id}_episode_{timestamp}.h5" # 파일명에 로봇 ID 포함
        self.file_path = os.path.join(self.save_dir, filename)
        
        self.observations = []
        self.actions = []
        self.rewards = []
        
        print(f"새 에피소드 시작: {filename} (Robot: {self.robot_id})")
        
        # API로 에피소드 생성 요청
        if self.api_url:
            try:
                payload = {
                    "client_id": self.robot_id,
                    "model_type": model_type
                }
                response = requests.post(f"{self.api_url}/episodes/", json=payload)
                if response.status_code == 200:
                    self.current_episode_id = response.json()["id"]
                    print(f"API 에피소드 생성 성공 (ID: {self.current_episode_id})")
                else:
                    self.error_logger.log_error("API_ERROR", f"Episode creation failed: {response.status_code}", {"payload": payload})
            except Exception as e:
                self.error_logger.log_error("CONNECTION_ERROR", f"Failed to connect to API: {e}")

    def log_step(self, observation, action, reward=0.0, step=0):
        """
        매 스텝의 데이터 기록
        """
        try:
            # 로컬 버퍼에 저장
            self.observations.append(observation)
            self.actions.append(action)
            self.rewards.append(reward)
            
            # API로 로그 전송
            if self.api_url and self.current_episode_id:
                # (성능을 위해 실제 구현 시에는 비동기 큐 사용 권장)
                pass 
                
        except Exception as e:
            self.error_logger.log_error("LOGGING_ERROR", f"Failed to log step: {e}", {"step": step})

    def end_episode(self):
        """
        에피소드 종료 및 파일 저장
        """
        if not self.observations:
            print("저장할 데이터가 없습니다.")
            return

        print(f"에피소드를 {self.file_path}에 저장 중...")
        try:
            with h5py.File(self.file_path, 'w') as f:
                f.create_dataset('action', data=np.array(self.actions))
                f.create_dataset('reward', data=np.array(self.rewards))
                
                obs_group = f.create_group('observations')
                if self.observations:
                    keys = self.observations[0].keys()
                    for k in keys:
                        data_list = [obs[k] for obs in self.observations]
                        obs_group.create_dataset(k, data=np.array(data_list))
            
            print("에피소드 저장 완료.")
            
        except Exception as e:
            self.error_logger.log_error("FILE_IO_ERROR", f"Failed to save HDF5 file: {e}", {"file_path": self.file_path})
            
        finally:
            self.observations = []
            self.actions = []
            self.rewards = []
            self.current_episode_id = None

    def _convert_numpy(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: self._convert_numpy(v) for k, v in obj.items()}
        return obj
