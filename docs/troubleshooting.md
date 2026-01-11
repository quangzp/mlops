# Troubleshooting

## Tổng quan

Tài liệu này liệt kê các lỗi thường gặp và cách xử lý khi làm việc với dự án Pix2PixHD MLOps.

---

## 1. Installation Issues

### Lỗi: Python version không đúng

**Triệu chứng**:
```
RuntimeError: Python 3.10+ is required
```

**Giải pháp**:
```bash
# Kiểm tra Python version
python --version

# Tạo environment với Python 3.10
conda create -n pix2pix python=3.10
conda activate pix2pix
```

---

### Lỗi: PyTorch không tìm thấy CUDA

**Triệu chứng**:
```python
>>> import torch
>>> torch.cuda.is_available()
False
```

**Giải pháp**:

1. **Kiểm tra CUDA**:
```bash
nvidia-smi
```

2. **Cài đặt PyTorch với CUDA**:
```bash
# CUDA 11.8
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia

# Hoặc
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

3. **Verify**:
```python
import torch
print(torch.cuda.is_available())  # Should be True
print(torch.version.cuda)
```

---

### Lỗi: CMake version quá cũ (pyarrow)

**Triệu chứng**:
```
CMake 3.25 or higher is required. You are running version 3.22.1
```

**Giải pháp**:

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install cmake

# macOS
brew install cmake

# Verify
cmake --version
```

---

### Lỗi: Dependencies conflicts

**Triệu chứng**:
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed.
```

**Giải pháp**:

```bash
# Tạo environment mới
conda create -n pix2pix python=3.10 --clear
conda activate pix2pix

# Hoặc
python3.10 -m venv venv --clear
source venv/bin/activate

# Cài đặt lại
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 2. Data Issues

### Lỗi: Dataset size = 0

**Triệu chứng**:
```
ValueError: num_samples should be a positive integer value, but got num_samples=0
```

**Nguyên nhân**: Không tìm thấy ảnh trong thư mục dữ liệu.

**Giải pháp**:

1. **Kiểm tra đường dẫn**:
```bash
ls data/processed/sketches/
ls data/processed/images/
```

2. **Kiểm tra config**:
```yaml
# mlops/config/dataset.yaml
dataset:
  processed_sketch_dir: data/processed/sketches
  processed_image_dir: data/processed/images
```

3. **Kiểm tra tên file**:
```python
# Đảm bảo tên file khớp nhau
import os
sketches = set(os.listdir('data/processed/sketches/'))
images = set(os.listdir('data/processed/images/'))
print(f"Matched: {len(sketches & images)}")
```

---

### Lỗi: FileNotFoundError

**Triệu chứng**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'data/processed/sketches/'
```

**Giải pháp**:

1. **Tạo thư mục**:
```bash
mkdir -p data/processed/sketches
mkdir -p data/processed/images
```

2. **Kiểm tra permissions**:
```bash
ls -la data/processed/
```

---

### Lỗi: Images không khớp

**Triệu chứng**:
```
RuntimeError: Sizes of tensors must match
```

**Nguyên nhân**: Kích thước ảnh không đồng nhất.

**Giải pháp**:

```python
# Resize tất cả ảnh về cùng kích thước
from PIL import Image
import os

size = (256, 256)
for fname in os.listdir('data/processed/sketches/'):
    img = Image.open(f'data/processed/sketches/{fname}').convert('RGB')
    img = img.resize(size)
    img.save(f'data/processed/sketches/{fname}')
```

---

## 3. Training Issues

### Lỗi: CUDA out of memory

**Triệu chứng**:
```
RuntimeError: CUDA out of memory. Tried to allocate ...
```

**Giải pháp**:

1. **Giảm batch size**:
```yaml
# mlops/config/training.yaml
training:
  batch_size: 4  # Giảm từ 8 xuống 4
```

2. **Giảm image size**:
```yaml
dataset:
  image_size: 256  # Giảm từ 512 xuống 256
```

3. **Gradient accumulation**:
```yaml
training:
  accumulate_grad_batches: 2  # Accumulate 2 batches
  batch_size: 4  # Effective batch size = 4 * 2 = 8
```

4. **Clear cache**:
```python
torch.cuda.empty_cache()
```

---

### Lỗi: Loss NaN

**Triệu chứng**:
```
loss: nan
```

**Nguyên nhân**: Learning rate quá cao, gradient explosion.

**Giải pháp**:

1. **Giảm learning rate**:
```yaml
training:
  learning_rate: 0.0001  # Giảm từ 0.0002
```

2. **Gradient clipping**:
```yaml
training:
  gradient_clip_val: 1.0
```

3. **Kiểm tra dữ liệu**:
```python
# Đảm bảo dữ liệu không có NaN
import numpy as np
for img in dataset:
    assert not np.isnan(img['sketch'].numpy()).any()
```

---

### Lỗi: Model không hội tụ

**Triệu chứng**: Loss không giảm, ảnh sinh ra không tốt.

**Giải pháp**:

1. **Kiểm tra learning rate**:
```yaml
training:
  learning_rate: 0.0002  # Thử 0.0001 hoặc 0.0005
```

2. **Kiểm tra loss weights**:
```yaml
training:
  lambda_feat: 10.0  # Feature matching loss weight
```

3. **Kiểm tra dữ liệu**:
- Đảm bảo cặp ảnh tương ứng
- Đảm bảo chất lượng ảnh tốt

4. **Tăng số epochs**:
```yaml
training:
  num_epochs: 200  # Tăng từ 100
```

---

## 4. Checkpoint Issues

### Lỗi: Checkpoint không tìm thấy

**Triệu chứng**:
```
FileNotFoundError: [Errno 2] No such file or directory: 'models/checkpoints/epoch_50.pt'
```

**Giải pháp**:

1. **Kiểm tra đường dẫn**:
```bash
ls models/checkpoints/
```

2. **Kiểm tra config**:
```yaml
training:
  resume_from: models/checkpoints/epoch_50_2024-01-01-12-00.pt  # Đúng tên file
```

---

### Lỗi: KeyError khi load checkpoint

**Triệu chứng**:
```
KeyError: 'G'
```

**Giải pháp**:

```python
# Kiểm tra keys trong checkpoint
checkpoint = torch.load('path/to/checkpoint.pt')
print(checkpoint.keys())

# Load với đúng key
generator.load_state_dict(checkpoint['generator'])  # Not 'G'
```

---

### Lỗi: Shape mismatch

**Triệu chứng**:
```
RuntimeError: Error(s) in loading state_dict: size mismatch
```

**Nguyên nhân**: Model architecture khác với checkpoint.

**Giải pháp**:

```python
# Kiểm tra model architecture
print(generator.state_dict().keys())
print(checkpoint['G'].keys())

# Đảm bảo config khớp với checkpoint đã train
```

---

## 5. MLflow Issues

### Lỗi: MLflow không log

**Triệu chứng**:
```
Malformed experiment '0'. Detailed error Yaml file '.../mlruns/0/meta.yaml' does not exist.
```

**Giải pháp**:

1. **Set tracking URI**:
```python
import mlflow
mlflow.set_tracking_uri("file:///absolute/path/to/mlruns")
```

2. **Tạo experiment**:
```python
mlflow.set_experiment("my_experiment")
```

3. **Xóa mlruns cũ**:
```bash
rm -rf mlruns/
```

---

### Lỗi: MLflow UI không chạy

**Triệu chứng**:
```
Error: [Errno 48] Address already in use
```

**Giải pháp**:

```bash
# Tìm process sử dụng port 5000
lsof -i :5000

# Kill process
kill -9 <PID>

# Hoặc dùng port khác
mlflow ui --port 5001
```

---

## 6. WandB Issues

### Lỗi: WandB login failed

**Triệu chứng**:
```
wandb: ERROR Authentication failed
```

**Giải pháp**:

```bash
# Login lại
wandb login

# Hoặc set API key
export WANDB_API_KEY=your_api_key

# Hoặc disable WandB
export WANDB_MODE=disabled
```

---

## 7. Docker Issues

### Lỗi: Docker build failed

**Triệu chứng**:
```
ERROR: failed to build: failed to solve: process "/bin/sh -c pip install..." did not complete successfully
```

**Giải pháp**:

1. **Kiểm tra Dockerfile**:
- Đảm bảo COPY đúng thứ tự
- Đảm bảo requirements.txt tồn tại

2. **Clear Docker cache**:
```bash
docker system prune -a
docker build --no-cache -t pix2pixhd-mlops .
```

---

### Lỗi: CUDA trong Docker

**Triệu chứng**:
```
RuntimeError: CUDA error: no CUDA-capable device is detected
```

**Giải pháp**:

```bash
# Install nvidia-docker
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Run với --gpus
docker run --rm --gpus all pix2pixhd-mlops:latest
```

---

## 8. API Issues

### Lỗi: Port already in use

**Triệu chứng**:
```
ERROR: [Errno 48] Address already in use
```

**Giải pháp**:

```bash
# Tìm process
lsof -i :8000

# Kill process
kill -9 <PID>

# Hoặc dùng port khác
uvicorn mlops.serving.api:app --port 8001
```

---

### Lỗi: Model not loaded

**Triệu chứng**:
```
RuntimeError: Model not initialized
```

**Giải pháp**:

```python
# Kiểm tra CHECKPOINT_PATH trong api.py
CHECKPOINT_PATH = "models/checkpoints/best_model.pt"
assert os.path.exists(CHECKPOINT_PATH)
```

---

## 9. General Debugging Tips

### Logging

```python
from loguru import logger

# Add file logging
logger.add("logs/debug.log", rotation="100 MB")

# Use in code
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

### Check GPU

```python
import torch

print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
```

### Check Dependencies

```bash
# List installed packages
pip list

# Check specific package
pip show torch

# Check versions
python -c "import torch; print(torch.__version__)"
```

---

## 10. Tham khảo

- [Getting Started](getting_started.md) - Setup guide
- [Requirements](requirements.md) - System requirements
- [Training](training.md) - Training guide
- [PyTorch Troubleshooting](https://pytorch.org/docs/stable/notes/faq.html)
- [MLflow Issues](https://mlflow.org/docs/latest/tracking.html#troubleshooting)
