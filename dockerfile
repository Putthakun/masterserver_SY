FROM python:3.9-slim

# กำหนด working directory ภายใน container
WORKDIR /app

# คัดลอกไฟล์ requirements.txt
COPY ./app ./app
COPY requirements.txt ./

# Install the necessary system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libx11-dev \
    libxext-dev \
    libxrender-dev \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libfontconfig1 \
    libice6 \
    cmake \
    build-essential \
    ffmpeg \
    libgtk2.0-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libv4l-dev \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Upgrade pip, setuptools, and wheel
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# ตั้งค่า PYTHONPATH
ENV PYTHONPATH=/app

# รันแอปพลิเคชัน FastAPI โดยใช้ Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
