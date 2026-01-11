# Fix: Changed "ROM" to "FROM"
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

# 1️⃣ System + Python 3.10
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3.10-distutils \
    python3-pip \
    git \
    ca-certificates \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*


# 2️⃣ Fix symlinks (Ubuntu 22.04 usually already has python3 -> python3.10)
RUN ln -sf /usr/bin/python3.10 /usr/bin/python3 && \
    ln -sf /usr/bin/python3 /usr/bin/python

# 3️⃣ Upgrade pip
RUN pip install --upgrade pip setuptools wheel

# 4️⃣ Copy requirements (Cache optimized)
COPY requirements.txt .

# 5️⃣ Install deps
RUN pip install --no-cache-dir -r requirements.txt

# 6️⃣ Copy source code
COPY . .

ENTRYPOINT ["python", "mlops/modeling/train.py"]
