#!/bin/bash

# Jetson AI Lab 가이드 기반 설정 스크립트
# https://www.jetson-ai-lab.com/archive/lerobot.html

set -e

echo "=== Jetson Orin Nano 환경 설정 시작 ==="

# 1. jetson-containers 디렉토리 확인
JETSON_CONTAINERS_DIR="/opt/jetson-containers" # 권장 위치 (SSD)
if [ ! -d "$JETSON_CONTAINERS_DIR" ]; then
    echo "[경고] $JETSON_CONTAINERS_DIR 디렉토리가 없습니다."
    echo "SSD에 jetson-containers를 클론하는 것을 권장합니다."
    echo "예: cd /ssd && git clone https://github.com/dusty-nv/jetson-containers"
    # 강제 종료하지 않고 진행 (사용자가 다른 곳에 설치했을 수 있음)
fi

# 2. Lerobot 데이터 디렉토리 생성
DATA_DIR="./data"
mkdir -p "$DATA_DIR"
echo "[완료] 데이터 디렉토리 생성: $DATA_DIR"

# 3. PulseAudio 설정 (오디오 큐 사용 시 필요)
# /etc/pulse/default.pa 파일에 auth-anonymous=1 추가
PULSE_CONFIG="/etc/pulse/default.pa"
if grep -q "auth-anonymous=1" "$PULSE_CONFIG"; then
    echo "[완료] PulseAudio 이미 설정됨."
else
    echo "[설정] PulseAudio 설정 수정 중..."
    # 백업 생성
    sudo cp "$PULSE_CONFIG" "${PULSE_CONFIG}.bak"
    # 모듈 로드 부분 수정 (sed 사용 시 주의 필요, 여기서는 안내 메시지로 대체하거나 안전하게 추가)
    # 가이드에 따라 module-native-protocol-unix 뒤에 auth-anonymous=1 추가가 필요함.
    # 자동화가 까다로울 수 있으므로 사용자에게 알림.
    echo "[주의] /etc/pulse/default.pa 파일을 열어 'load-module module-native-protocol-unix' 라인 뒤에 'auth-anonymous=1'을 추가해야 할 수 있습니다."
    echo "자동 스크립트에서는 안전을 위해 이 단계를 건너뜁니다. 필요 시 수동으로 진행하세요."
fi

# 4. Swap 파일 설정 (8GB 권장)
SWAP_FILE="/ssd/8GB.swap"
if [ -f "$SWAP_FILE" ]; then
    echo "[완료] Swap 파일이 이미 존재합니다."
else
    echo "[설정] Swap 파일 생성 (8GB)... 시간이 걸릴 수 있습니다."
    # SSD 경로가 존재하는지 확인
    if [ -d "/ssd" ]; then
        sudo fallocate -l 8G "$SWAP_FILE"
        sudo chmod 600 "$SWAP_FILE"
        sudo mkswap "$SWAP_FILE"
        sudo swapon "$SWAP_FILE"
        echo "/ssd/8GB.swap swap swap defaults 0 0" | sudo tee -a /etc/fstab
        echo "[완료] Swap 파일 생성 및 활성화 완료."
    else
        echo "[오류] /ssd 디렉토리를 찾을 수 없어 Swap 생성을 건너뜁니다."
    fi
fi

echo "=== 설정 완료 ==="
echo "이제 scripts/start_container.sh를 실행하여 컨테이너를 시작하세요."
