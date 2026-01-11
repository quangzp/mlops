# Deployment

## Tổng quan

Hướng dẫn này mô tả các cách triển khai (deploy) model Pix2PixHD cho inference, bao gồm:

- ✅ FastAPI REST API
- ✅ Docker containerization
- ✅ Cloud deployment (optional)

---

## 1. FastAPI Deployment

### Chuẩn bị

1. **Load model checkpoint**: Đảm bảo có checkpoint đã train
2. **Cấu hình**: Chỉnh sửa `CHECKPOINT_PATH` trong `mlops/serving/api.py`

### Local Deployment

#### Cài đặt dependencies

```bash
# Cài đặt FastAPI và uvicorn
pip install fastapi uvicorn python-multipart

# Hoặc cài từ requirements.txt
pip install -r requirements.txt
```

#### Chạy server

```bash
# Chạy với uvicorn
uvicorn mlops.serving.api:app --host 0.0.0.0 --port 8000

# Hoặc với reload (development)
uvicorn mlops.serving.api:app --host 0.0.0.0 --port 8000 --reload
```

#### Test API

```bash
# Health check
curl http://localhost:8000/docs

# Predict
curl -X POST "http://localhost:8000/predict/" \
    -F "file=@data/test/sample.jpg" \
    --output result.png

# Hoặc dùng Swagger UI
# Truy cập http://localhost:8000/docs
```

### API Endpoints

#### `POST /predict/`

- **Input**: File image (form-data)
- **Output**: Image (PNG)
- **Example**:

```python
import requests

url = "http://localhost:8000/predict/"
with open("input.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)
    with open("output.png", "wb") as out:
        out.write(response.content)
```

Xem chi tiết trong [API Reference](api_reference.md).

---

## 2. Docker Deployment

### Build Docker Image

#### Training Image

```bash
# Build image
docker build -t pix2pixhd-mlops:latest .

# Run training
docker run --rm --gpus all \
    -v $(pwd)/data:/app/data \
    -v $(pwd)/models:/app/models \
    pix2pixhd-mlops:latest
```

#### Serving Image

Tạo `Dockerfile.serving`:

```dockerfile
FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3.10 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install fastapi uvicorn python-multipart

# Copy code
COPY . .

# Expose port
EXPOSE 8000

# Run API server
CMD ["uvicorn", "mlops.serving.api:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build và run:

```bash
# Build serving image
docker build -f Dockerfile.serving -t pix2pixhd-api:latest .

# Run serving container
docker run --rm --gpus all \
    -p 8000:8000 \
    -v $(pwd)/models:/app/models \
    pix2pixhd-api:latest
```

### Docker Compose

Tạo `docker-compose.serving.yml`:

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: Dockerfile.serving
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models
      - ./data:/app/data
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    restart: unless-stopped

  # Optional: Add monitoring
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
```

Run:

```bash
docker-compose -f docker-compose.serving.yml up -d
```

---

## 3. Production Considerations

### Performance Optimization

#### 1. Model Optimization

```python
# Use half precision (FP16)
generator = generator.half()

# Or use TensorRT (NVIDIA)
# torch_tensorrt.compile(generator, ...)
```

#### 2. Batch Processing

```python
@app.post("/predict/batch")
async def predict_batch(files: List[UploadFile] = File(...)):
    # Process multiple images at once
    batch_tensors = [preprocess_image(await f.read()) for f in files]
    batch = torch.cat(batch_tensors, dim=0)
    with torch.no_grad():
        outputs = generator(batch)
    # Post-process and return
```

#### 3. Caching

```python
from functools import lru_cache

@lru_cache(maxsize=1)
def load_model():
    # Load model once
    generator = define_G(...)
    generator.load_state_dict(torch.load(CHECKPOINT_PATH))
    return generator
```

### Security

#### 1. Input Validation

```python
from PIL import Image
import io

def validate_image(image_bytes: bytes, max_size: int = 10 * 1024 * 1024):
    # Check file size
    if len(image_bytes) > max_size:
        raise ValueError(f"Image too large (max {max_size} bytes)")

    # Check image format
    try:
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()
    except Exception as e:
        raise ValueError(f"Invalid image: {e}")

    return True
```

#### 2. Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/predict/")
@limiter.limit("10/minute")
async def predict(...):
    ...
```

#### 3. Authentication

```python
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

@app.post("/predict/")
async def predict(
    credentials: HTTPAuthorizationCredentials = Security(security),
    file: UploadFile = File(...)
):
    # Verify token
    token = credentials.credentials
    if not verify_token(token):
        raise HTTPException(status_code=401, detail="Invalid token")
    ...
```

### Monitoring

#### 1. Logging

```python
import logging
from loguru import logger

# Configure logging
logger.add("logs/api.log", rotation="100 MB")

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    logger.info(f"Received request from {request.client.host}")
    try:
        # Process
        ...
        logger.success("Prediction completed")
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
```

#### 2. Metrics

```python
from prometheus_client import Counter, Histogram
import time

request_count = Counter('api_requests_total', 'Total API requests')
request_duration = Histogram('api_request_duration_seconds', 'Request duration')

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    request_count.inc()
    start_time = time.time()
    try:
        # Process
        ...
    finally:
        request_duration.observe(time.time() - start_time)
```

#### 3. Health Check

```python
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "gpu_available": torch.cuda.is_available(),
        "model_loaded": generator is not None
    }
```

---

## 4. Cloud Deployment

### AWS

#### EC2 + Docker

```bash
# SSH into EC2
ssh -i key.pem ec2-user@your-ec2-ip

# Install Docker
sudo yum install docker
sudo service docker start

# Pull and run
docker pull your-registry/pix2pixhd-api:latest
docker run -d -p 8000:8000 --gpus all your-registry/pix2pixhd-api:latest
```

#### ECS/Fargate

```yaml
# task-definition.json
{
  "family": "pix2pixhd-api",
  "containerDefinitions": [{
    "name": "api",
    "image": "your-registry/pix2pixhd-api:latest",
    "portMappings": [{
      "containerPort": 8000
    }]
  }]
}
```

### Google Cloud Platform

#### Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/pix2pixhd-api

# Deploy
gcloud run deploy pix2pixhd-api \
    --image gcr.io/PROJECT_ID/pix2pixhd-api \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

### Azure

#### Container Instances

```bash
# Build and push
az acr build --registry your-registry --image pix2pixhd-api:latest .

# Deploy
az container create \
    --resource-group your-rg \
    --name pix2pixhd-api \
    --image your-registry.azurecr.io/pix2pixhd-api:latest \
    --ports 8000
```

---

## 5. CI/CD Integration

### GitHub Actions

Xem `.github/workflows/python-app.yml` cho CI/CD pipeline:

```yaml
# Build and push Docker image
- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: ${{ secrets.DOCKERHUB_USERNAME }}/sketch2image-mlops:latest
```

### Deployment Workflow

1. **Build**: Docker image được build trong CI
2. **Push**: Push lên Docker Hub / Container Registry
3. **Deploy**: Pull và run trên server

---

## 6. Best Practices

### ✅ Nên làm

- Sử dụng Docker để đảm bảo consistency
- Implement health checks
- Add logging và monitoring
- Sử dụng GPU nếu có (faster inference)
- Cache model loading
- Validate input
- Implement rate limiting
- Use HTTPS trong production

### ❌ Không nên

- Không hardcode paths (dùng environment variables)
- Không expose debug mode trong production
- Không commit credentials
- Không skip input validation
- Không run với root user

---

## 7. Troubleshooting

### Lỗi: "CUDA out of memory"

```python
# Reduce batch size
# Or use CPU
DEVICE = torch.device("cpu")
```

### Lỗi: "Model not found"

```python
# Check checkpoint path
CHECKPOINT_PATH = os.getenv("CHECKPOINT_PATH", "models/checkpoints/best_model.pt")
assert os.path.exists(CHECKPOINT_PATH), f"Checkpoint not found: {CHECKPOINT_PATH}"
```

### Lỗi: "Port already in use"

```bash
# Find process using port
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
uvicorn mlops.serving.api:app --port 8001
```

---

## 8. Tham khảo

- [API Reference](api_reference.md) - API documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Docker Documentation](https://docs.docker.com/)
- [PyTorch Production](https://pytorch.org/tutorials/intermediate/torchscript_tutorial.html)
