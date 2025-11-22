#!/bin/bash

# Jetson AI Lab 가이드 기반 컨테이너 실행 스크립트
# jetson-containers의 run.sh를 래핑하여 필요한 옵션을 자동으로 적용합니다.

# jetson-containers 경로 (사용자 환경에 맞게 수정 필요)
JETSON_CONTAINERS_DIR=${JETSON_CONTAINERS_DIR:-"/opt/jetson-containers"}

if [ ! -d "$JETSON_CONTAINERS_DIR" ]; then
    echo "오류: jetson-containers 디렉토리를 찾을 수 없습니다."
    echo "JETSON_CONTAINERS_DIR 환경 변수를 설정하거나 스크립트를 수정하세요."
    exit 1
fi

# 프로젝트 데이터 경로
PROJECT_ROOT=$(pwd)
DATA_DIR="$PROJECT_ROOT/data"
MODELS_DIR="$PROJECT_ROOT/models"

# Docker 이미지 태그 (자동 감지 또는 지정)
# 가이드에서는 $(./autotag lerobot)을 사용하지만, 여기서는 명시적으로 지정하거나 기본값 사용
IMAGE_TAG="lerobot" 

echo "=== Lerobot 컨테이너 시작 ==="
echo "데이터 경로: $DATA_DIR"

# 실행 명령어 구성
# --csi2webcam: CSI 카메라 사용 시 필요 (USB 웹캠처럼 보이게 함)
# -v ...: 데이터 및 모델 디렉토리 마운트
# --device /dev/snd: 오디오 사용
CMD="$JETSON_CONTAINERS_DIR/run.sh \
    --workdir /opt/lerobot \
    --volume $DATA_DIR:/opt/lerobot/data \
    --volume $MODELS_DIR:/opt/lerobot/models \
    --volume $PROJECT_ROOT/src:/opt/lerobot/src \
    --volume $PROJECT_ROOT/scripts:/opt/lerobot/scripts \
    --device /dev/snd \
    --device /dev/video0 \
    --env PULSE_SERVER=unix:${XDG_RUNTIME_DIR}/pulse/native \
    --volume ${XDG_RUNTIME_DIR}/pulse:${XDG_RUNTIME_DIR}/pulse \
    $IMAGE_TAG \
    /bin/bash"

echo "실행 명령: $CMD"
eval $CMD
