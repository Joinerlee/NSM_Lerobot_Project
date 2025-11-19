# Base image for Jetson Orin Nano (JetPack 6 / L4T r36.3.0)
# Using dusty-nv's optimized containers which are standard for Jetson
FROM dusty-nv/l4t-pytorch:r36.3.0

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/usr/local/bin:${PATH}"
ENV LD_LIBRARY_PATH="/usr/lib/aarch64-linux-gnu:${LD_LIBRARY_PATH}"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    cmake \
    build-essential \
    libopencv-dev \
    python3-opencv \
    libhdf5-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Note: PyTorch is already installed in the base image
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt

# Install Lerobot from source (recommended for latest features/fixes)
WORKDIR /app
RUN git clone https://github.com/huggingface/lerobot.git && \
    cd lerobot && \
    pip3 install -e .

# Create directories for data and models
RUN mkdir -p /app/data /app/models /app/scripts

# Copy project scripts
COPY scripts/ /app/scripts/
COPY src/ /app/src/

# Set working directory
WORKDIR /app

# Default command (can be overridden by docker-compose)
CMD ["python3", "scripts/auto_start.py"]
