#!/bin/bash

# Define project directory
PROJECT_DIR="/home/nsm_industry_technology_team/Desktop/NSM_Lerobot_Project"

# Navigate to project directory
cd "$PROJECT_DIR" || exit

# Check if Docker is running
if ! systemctl is-active --quiet docker; then
    echo "Docker is not running. Waiting..."
    sleep 10
fi

# Start Docker Compose service
echo "Starting Lerobot Inference Service..."
docker-compose up -d

# Check status
if [ $? -eq 0 ]; then
    echo "Service started successfully."
else
    echo "Failed to start service."
    exit 1
fi
