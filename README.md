# NSM Lerobot Project (Jetson Orin Nano Edition)

## 1. 프로젝트 목적 (Project Purpose)
본 프로젝트는 **NVIDIA Jetson Orin Nano** 엣지 디바이스에서 **Hugging Face Lerobot** 프레임워크를 활용하여 로봇 제어 모델(ACT, Diffusion Policy 등)을 구동하고, 지속적인 데이터 수집 및 학습 파이프라인을 구축하는 것을 목표로 합니다.

주요 목표는 다음과 같습니다:
- **엣지 추론**: Jetson Orin Nano의 GPU 가속을 활용한 실시간 로봇 제어.
- **데이터 파이프라인**: 로봇의 상태 및 카메라 이미지를 수집하여 HDF5 포맷으로 자동 로깅.
- **자동화**: Docker 컨테이너 기반의 자동 실행 및 배포 환경 구축.

## 2. 아키텍처 (Architecture)
이 프로젝트는 **Jetson AI Lab** 및 **Hugging Face Lerobot**의 최신 가이드(최근 7일 기준 반영)를 기반으로 설계되었습니다.

### 시스템 구조
```mermaid
graph TD
    A[Jetson Orin Nano Host] -->|System Configuration| B(Setup Scripts);
    B -->|PulseAudio, Swap, Dir| C[Docker Container];
    C -->|Run| D[Lerobot Inference Engine];
    D -->|Load| E[Models (ACT, so-101)];
    D -->|Input| F[Camera & Robot State];
    D -->|Output| G[Action Control];
    D -->|Log| H[HDF5 Data Logger];
```

### 주요 컴포넌트
- **Docker Environment**: `jetson-containers` (L4T PyTorch) 기반의 격리된 실행 환경.
- **Inference Engine**: `src/inference.py` - 모델 로드, 전처리, 추론, 후처리 담당.
- **Data Logger**: `src/logger.py` - 에피소드 단위 데이터 저장.
- **Automation**: `scripts/setup_jetson.sh`, `scripts/start_container.sh` - 시스템 설정 및 실행 자동화.

## 3. 아키텍처 설계 사유 (Architecture Rationale)

### 왜 Jetson Orin Nano인가? (vs PC 3090/4090)
본 프로젝트가 고성능 PC 대신 Jetson Orin Nano를 엣지 디바이스로 채택한 이유는 다음과 같습니다:

1.  **현장성 (On-Device Processing)**:
    - 로봇에 직접 탑재되어 네트워크 지연 없이 실시간 추론이 가능합니다. (PC 스트리밍 방식 대비 안정성 우수)
    - 외부 네트워크 단절 시에도 독립적인 동작을 보장합니다.
2.  **저전력 및 휴대성 (SWaP)**:
    - 3090/4090 PC는 수백 와트의 전력을 소모하고 부피가 크지만, Jetson은 15W~40W 수준으로 배터리 구동 로봇에 적합합니다.
3.  **비용 효율성**:
    - 별도의 고가 워크스테이션 없이 로봇 자체에서 추론을 수행하여 전체 시스템 비용을 절감합니다.

> [!NOTE]
> **PC (3090/4090)의 역할**: PC는 대규모 데이터셋을 이용한 **모델 학습(Training)** 및 **파인튜닝**에 활용하며, 학습된 모델을 Hugging Face Hub를 통해 Jetson으로 배포하는 구조를 권장합니다.

## 4. 백엔드 아키텍처 및 DB 연동 (Backend Architecture)

본 프로젝트는 단순한 로컬 로깅을 넘어 확장 가능한 백엔드 시스템을 도입했습니다.

### 시스템 구성
- **FastAPI (Backend)**: Python 기반의 고성능 비동기 웹 프레임워크.
- **PostgreSQL (Database)**: JSONB를 지원하는 관계형 데이터베이스로, 정형 데이터(에피소드 메타데이터)와 비정형 데이터(로그)를 효율적으로 관리.
- **SQLAlchemy (ORM)**: 비동기(AsyncIO) DB 접근을 통해 추론 루프의 지연을 최소화.

### 설계 의도 (Design Rationale)
1.  **Decoupling (결합도 감소)**:
    - 추론 엔진(`inference.py`)은 오직 "로봇 제어"에만 집중합니다.
    - 데이터 저장 및 관리는 백엔드 API로 위임하여, DB 장애가 발생하더라도 로봇 제어에는 영향을 주지 않도록 설계했습니다.
2.  **Scalability (확장성)**:
    - 초기에는 Jetson 내부(Localhost)에서 동작하지만, 설정 변경만으로 원격 클라우드 서버로 데이터를 전송할 수 있습니다.
    - 여러 대의 로봇 데이터를 중앙 서버에서 통합 관리하기 용이합니다.
3.  **Data Integrity (데이터 무결성)**:
    - 파일 기반 로깅(HDF5)의 단점(파일 깨짐, 동시 쓰기 불가)을 DB 트랜잭션으로 보완합니다.

### 원격 vs 로컬 설정 가이드 (Remote vs Local)

#### 로컬 실행 (기본값)
Jetson Orin Nano 하나에서 모든 시스템(추론 + 백엔드 + DB)을 구동합니다.
- **설정**: `docker-compose.yml` 사용.
- **실행**: `docker-compose up -d`
- **특징**: 네트워크 연결 없이 독립 동작 가능.

#### 원격 실행 (Remote Logging)
Jetson은 추론만 수행하고, 데이터는 별도의 고성능 서버(PC/Cloud)에 저장합니다.
1.  **서버 설정**: 원격 PC에서 `docker-compose.yml`의 `backend`와 `db` 서비스만 실행.
2.  **Jetson 설정**: `docker-compose.yml`의 `lerobot-inference` 환경 변수 수정.
    ```yaml
    environment:
      - BACKEND_API_URL=http://<REMOTE_SERVER_IP>:8000
    ```
3.  **장점**: Jetson의 저장 공간 절약 및 중앙 집중식 데이터 분석 가능.

## 5. 배포 및 실행 가이드 (Deployment Guide)

### 5.1 사전 준비
- **하드웨어**: Jetson Orin Nano (NVMe SSD 권장)
- **소프트웨어**: JetPack 6.x 설치 완료
- **필수 레포지토리**: `jetson-containers`가 설치되어 있어야 합니다.
    ```bash
    cd /opt  # 또는 SSD 경로
    git clone https://github.com/dusty-nv/jetson-containers
    cd jetson-containers
    ./install.sh
    ```

### 5.2 프로젝트 설정
프로젝트 폴더(`NSM_Lerobot_Project`)로 이동하여 설정 스크립트를 실행합니다. 이 스크립트는 필요한 디렉토리를 생성하고 시스템 설정(PulseAudio, Swap)을 점검합니다.

```bash
cd NSM_Lerobot_Project
chmod +x scripts/*.sh
./scripts/setup_jetson.sh
```

### 5.3 컨테이너 실행
다음 스크립트를 사용하여 Lerobot 컨테이너를 시작합니다. `jetson-containers`의 `run.sh`를 래핑하여 필요한 볼륨과 디바이스를 자동으로 연결합니다.

```bash
./scripts/start_container.sh
```

### 5.4 모델 다운로드
컨테이너 내부 쉘에 진입한 상태에서 모델 다운로드 스크립트를 실행합니다.

```bash
# (컨테이너 내부)
python3 scripts/download_models.py
```

### 5.5 추론 테스트
모델 다운로드가 완료되면 추론 스크립트를 실행하여 동작을 확인합니다.

```bash
# (컨테이너 내부)
# so-101 모델 테스트
python3 src/inference.py --model_path /opt/lerobot/models/so-101 --model_type so-101

# ACT 모델 테스트
python3 src/inference.py --model_path /opt/lerobot/models/act_model --model_type act
```

### 5.6 Colab 파인튜닝 모델 가져오기 (Hugging Face Hub 활용)
Google Colab에서 학습한 모델을 Hugging Face Hub에 업로드하고, Jetson에서 다운로드하는 권장 방식입니다.

#### 1단계: Colab에서 모델 업로드 (Push)
Colab에서 학습이 완료되면 `huggingface_hub`를 사용하여 모델을 업로드합니다.
```python
# Colab 노트북 셀
from huggingface_hub import HfApi, login

# 1. 로그인 (토큰 필요)
login(token="YOUR_HF_WRITE_TOKEN")

# 2. 모델 업로드
api = HfApi()
repo_id = "your-username/lerobot-jetson-finetuned" # 레포지토리 ID 설정

# 레포지토리 생성 (없을 경우)
api.create_repo(repo_id=repo_id, exist_ok=True)

# 폴더 전체 업로드
api.upload_folder(
    folder_path="/content/lerobot/outputs/train/my_model",
    repo_id=repo_id,
    path_in_repo=".",
)
print(f"모델 업로드 완료: https://huggingface.co/{repo_id}")
```

#### 2단계: Jetson에서 모델 다운로드 (Pull)
Jetson 컨테이너 내부에서 스크립트를 사용하여 모델을 다운로드합니다.

```bash
# (컨테이너 내부)
# download_models.py 스크립트 수정 또는 직접 다운로드
huggingface-cli download your-username/lerobot-jetson-finetuned --local-dir /opt/lerobot/models/my_finetuned_model --local-dir-use-symlinks False
```

## 6. 학습 가이드 (Training)
ACT 모델 파인튜닝 및 데이터 수집에 대한 자세한 내용은 [학습 가이드 (training_guide.md)](./training_guide.md)를 참고하세요.

## 7. 트러블슈팅
실행 중 문제가 발생하거나 로봇 팔 떨림 등의 현상이 관찰되면 `troubleshooting.md` 파일을 참고하여 해결책을 적용하고 기록하세요.

## 8. 참조 (References)
본 프로젝트는 다음의 공식 가이드를 준수하여 구축되었습니다:
- **NVIDIA Jetson AI Lab - LeRobot**: [https://www.jetson-ai-lab.com/archive/lerobot.html](https://www.jetson-ai-lab.com/archive/lerobot.html)
- **Hugging Face LeRobot**: [https://github.com/huggingface/lerobot](https://github.com/huggingface/lerobot)

## 4. 시작하기 (Getting Started)
자세한 배포 및 실행 방법은 [walkthrough.md](walkthrough.md)를 참고하세요.