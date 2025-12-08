# LeRobot 학습 가이드 (Training Guide)

이 문서는 **ACT (Action Chunking Transformer)** 모델을 포함한 LeRobot 모델을 학습(Fine-tuning)시키는 방법을 안내합니다. Jetson은 추론(Inference) 전용으로 사용하며, 학습은 **Google Colab** 또는 **고성능 PC (NVIDIA GPU)** 에서 수행하는 것을 권장합니다.

## 1. 데이터 수집 (Data Collection)
학습을 위해서는 로봇의 상태(Observation)와 행동(Action)이 기록된 데이터셋이 필요합니다.

### 1.1 데이터셋 구조
LeRobot은 Hugging Face Dataset 포맷을 따릅니다.
- **Observation**: 이미지 (카메라), 관절 상태 (Joint positions/velocities)
- **Action**: 관절 제어 값 (Joint targets)

### 1.2 데이터 수집 및 업로드
Jetson에서 수집한 데이터를 Hugging Face Hub에 업로드하여 학습 환경에서 사용할 수 있게 합니다.

```bash
# (Jetson) 데이터셋 업로드 예시
huggingface-cli upload your-username/your-dataset-name ./data/collected_episodes --repo-type dataset
```

---

## 2. 학습 환경 설정 (Training Setup)

### 옵션 A: Google Colab (무료/Pro)
별도의 장비 없이 브라우저에서 바로 학습할 수 있습니다. (T4 GPU 이상 권장)

1. [LeRobot Colab 예제](https://github.com/huggingface/lerobot/blob/main/examples/1_train_policy.ipynb)를 엽니다.
2. 런타임 유형을 **GPU**로 변경합니다.
3. 라이브러리를 설치합니다:
    ```python
    !pip install lerobot
    !pip install diffusers
    ```

### 옵션 B: 로컬 PC (RTX 3090/4090)
대규모 학습이나 장시간 학습에 적합합니다.

1. 가상환경 생성 및 활성화:
    ```bash
    conda create -n lerobot python=3.10
    conda activate lerobot
    ```
2. LeRobot 설치:
    ```bash
    git clone https://github.com/huggingface/lerobot.git
    cd lerobot
    pip install -e .
    ```

---

## 3. ACT 모델 학습 (Training ACT)

**ACT**는 로봇의 행동을 청크(Chunk) 단위로 예측하여 부드러운 움직임을 생성하는 모델입니다.

### 3.1 학습 명령어
`lerobot-train` 명령어를 사용하여 학습을 시작합니다.

```bash
python lerobot/scripts/train.py \
  policy=act \
  env=your_env_name \
  dataset_repo_id=your-username/your-dataset-name \
  hydra.run.dir=outputs/train/act_my_robot
```

### 3.2 주요 파라미터 설명
- `policy=act`: 사용할 모델 아키텍처 (ACT). `diffusion` 등 다른 모델도 가능.
- `dataset_repo_id`: Hugging Face Hub에 업로드한 데이터셋 ID.
- `training.batch_size`: GPU 메모리에 맞춰 조절 (기본: 8 또는 16).
- `training.steps`: 총 학습 스텝 수 (데이터 양에 따라 조절, 보통 50,000~100,000).

### 3.3 학습 모니터링
WandB(Weights & Biases)를 사용하면 학습 과정을 그래프로 확인할 수 있습니다.
```bash
wandb login
# 학습 명령어에 wandb.enable=true 추가
```

---

## 4. 모델 배포 (Deployment)

학습이 완료된 모델을 Jetson으로 배포하는 과정입니다.

### 4.1 모델 업로드 (Push)
학습된 체크포인트를 Hugging Face Hub에 업로드합니다.

```bash
# (학습 환경)
huggingface-cli upload your-username/act-my-robot ./outputs/train/act_my_robot/checkpoints/last --repo-type model
```

### 4.2 모델 다운로드 (Pull on Jetson)
Jetson Orin Nano에서 모델을 다운로드하여 추론에 사용합니다.

```bash
# (Jetson 컨테이너 내부)
python3 scripts/download_models.py --repo_id your-username/act-my-robot
```

이제 `src/inference.py`를 실행하여 내 로봇이 학습한 대로 움직이는지 확인하세요!
