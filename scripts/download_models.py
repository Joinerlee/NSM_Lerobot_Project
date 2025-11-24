import os
import argparse
from huggingface_hub import snapshot_download, hf_hub_download

def download_lerobot_model(model_id, save_dir):
    """
    Lerobot 모델 다운로드 함수
    """
    print(f"{model_id} 모델을 {save_dir}로 다운로드 중...")
    try:
        snapshot_download(repo_id=model_id, local_dir=save_dir, local_dir_use_symlinks=False)
        print(f"{model_id} 다운로드 성공")
    except Exception as e:
        print(f"{model_id} 다운로드 오류: {e}")

def download_act_model(save_dir):
    """
    ACT 모델 다운로드 함수 (예시)
    """
    model_id = "lerobot/act-aloha-sim-transfer-cube-human" # 예시 ID
    print(f"ACT 모델 ({model_id}) 다운로드 중...")
    try:
        snapshot_download(repo_id=model_id, local_dir=os.path.join(save_dir, "act_model"), local_dir_use_symlinks=False)
        print("ACT 모델 다운로드 성공")
    except Exception as e:
        print(f"ACT 모델 다운로드 오류: {e}")

def import_colab_model(source_path, save_dir):
    """
    로컬(Colab 마운트 등)에서 파인튜닝된 모델 가져오기
    """
    print(f"{source_path}에서 Colab 모델을 가져오는 중...")
    if not os.path.exists(source_path):
        print(f"오류: 소스 경로 {source_path}가 존재하지 않습니다.")
        return
    
    target_path = os.path.join(save_dir, "colab_finetuned")
    os.makedirs(target_path, exist_ok=True)
    os.system(f"cp -r {source_path}/* {target_path}/")
    print(f"모델이 {target_path}로 가져와졌습니다.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lerobot 프로젝트 모델 다운로드 스크립트")
    parser.add_argument("--models_dir", type=str, default="/opt/lerobot/models", help="모델 저장 경로")
    parser.add_argument("--colab_path", type=str, help="로컬 Colab 모델 경로 (예: 마운트된 드라이브)")
    
    args = parser.parse_args()
    
    os.makedirs(args.models_dir, exist_ok=True)
    
    # 1. Lerobot so-101 다운로드
    download_lerobot_model("lerobot/so-101", os.path.join(args.models_dir, "so-101"))
    
    # 2. ACT 모델 다운로드
    download_act_model(args.models_dir)
    
    # 3. Colab 모델 가져오기 (경로가 제공된 경우)
    if args.colab_path:
        import_colab_model(args.colab_path, args.models_dir)
