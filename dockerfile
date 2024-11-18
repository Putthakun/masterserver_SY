# ใช้ base image ที่มี Python
FROM python:3.9-slim

# กำหนด working directory ภายใน container
WORKDIR /app

# คัดลอกไฟล์ requirements.txt และติดตั้ง dependencies
COPY ./app ./app
COPY requirements.txt ./

# Install the necessary dependencies including OpenGL and X11 libraries
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
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade -r requirements.txt

# คัดลอกโค้ดทั้งหมดไปยัง container

ENV PYTHONPATH=/app

# รันแอปพลิเคชัน FastAPI โดยใช้ Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]
