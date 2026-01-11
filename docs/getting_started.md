# Getting Started

## Tổng quan

Hướng dẫn này sẽ giúp bạn thiết lập và chạy dự án Pix2PixHD MLOps từ đầu. Chúng ta sẽ đi qua các bước: cài đặt môi trường, chuẩn bị dữ liệu, chạy training và inference.

---

## 1. Yêu cầu hệ thống

### Hệ điều hành

- Linux, macOS, hoặc Windows (với WSL2)
- Khuyến nghị: Ubuntu 20.04+ hoặc macOS 12+

### Phần cứng

- **CPU**: Ít nhất 4 cores
- **RAM**: Tối thiểu 8GB, khuyến nghị 16GB+
- **GPU**: NVIDIA GPU với CUDA support (tùy chọn nhưng khuyến nghị cho training)
- **Disk**: Ít nhất 20GB dung lượng trống

### Software

- Python 3.10+
- CUDA 11.7+ (nếu dùng GPU)
- Git
- Docker (tùy chọn, cho containerization)

Xem chi tiết trong [Requirements](requirements.md).

---

## 2. Cài đặt môi trường

### Option 1: Sử dụng Conda (Khuyến nghị)

```bash
# Clone repository
git clone https://github.com/quangzp/pix2pix-mlops.git
cd pix2pix-mlops

# Tạo môi trường conda
conda create -n pix2pix python=3.10
conda activate pix2pix

# Cài đặt PyTorch với CUDA (nếu có GPU)
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia

# Cài đặt dependencies
pip install -r requirements.txt
```

### Option 2: Sử dụng venv

```bash
# Clone repository
git clone https://github.com/quangzp/pix2pix-mlops.git
cd pix2pix-mlops

# Tạo virtual environment
python3.10 -m venv venv
source venv/bin/activate  # Trên Windows: venv\Scripts\activate

# Cài đặt dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Option 3: Sử dụng Docker

```bash
# Build Docker image
docker build -t pix2pixhd-mlops .

# Chạy container
docker run --rm --gpus all -v $(pwd)/data:/app/data pix2pixhd-mlops
```

---

## 3. Cấu hình DVC (Data Version Control)

Nếu dự án sử dụng DVC để quản lý dữ liệu:

```bash
# Cấu hình remote storage (nếu chưa có)
dvc remote add -d myremote /path/to/storage
# Hoặc với Google Drive
dvc remote add -d myremote gdrive://your-drive-id

# Tải dữ liệu
dvc pull
```

Xem thêm trong [Dataset Preparation](dataset_preparation.md).

---

## 4. Chuẩn bị dữ liệu

### Cấu trúc thư mục

Dữ liệu cần được tổ chức như sau:

```
data/
├── raw/
│   └── original/        # Ảnh gốc chưa xử lý
├── processed/
│   ├── sketches/        # Ảnh sketch (input)
│   └── images/          # Ảnh ground-truth (target)
```

### Kiểm tra dữ liệu

```bash
# Kiểm tra số lượng ảnh
ls data/processed/sketches/ | wc -l
ls data/processed/images/ | wc -l

# Đảm bảo số lượng khớp nhau
```

Xem chi tiết trong [Dataset Preparation](dataset_preparation.md).

---

## 5. Cấu hình

### Kiểm tra config file

File cấu hình chính: `mlops/config/config.yaml`

```bash
# Xem cấu hình mặc định
cat mlops/config/config.yaml
```

Các tham số quan trọng:

- `training.num_epochs`: Số epoch
- `training.batch_size`: Batch size
- `training.learning_rate`: Learning rate
- `dataset.processed_sketch_dir`: Đường dẫn sketch
- `dataset.processed_image_dir`: Đường dẫn images

Xem chi tiết trong [Configuration](configuration.md).

---

## 6. Chạy Training

### Training cơ bản

```bash
# Chạy với config mặc định
python mlops/modeling/train.py
```

### Training với parameters tùy chỉnh

```bash
# Thay đổi số epoch và batch size
python mlops/modeling/train.py \
    training.num_epochs=100 \
    training.batch_size=8 \
    training.learning_rate=0.0002
```

### Training với WandB

```bash
# Đăng nhập WandB trước (nếu chưa)
wandb login

# Chạy training với WandB logging
python mlops/modeling/train.py logger=wandb
```

### Resume từ checkpoint

```bash
python mlops/modeling/train.py \
    training.resume_from=models/checkpoints/epoch_50_2024-01-01-12-00.pt
```

Xem chi tiết trong [Training](training.md).

---

## 7. Theo dõi Training

### MLflow UI

```bash
# Chạy MLflow UI
mlflow ui

# Truy cập http://localhost:5000
```

### WandB Dashboard

Tự động mở khi training với WandB enabled, hoặc truy cập [wandb.ai](https://wandb.ai).

### Console Logging

Training sẽ in log ra console với:
- Progress bars
- Loss values
- Checkpoint information

Xem chi tiết trong [Logging & Monitoring](logging_monitoring.md).

---

## 8. Chạy Inference

### Inference đơn giản

```bash
python mlops/modeling/predict.py \
    --ckpt_path models/checkpoints/best_model.pt \
    --input_path data/test/sample_sketch.jpg \
    --output_path results/output.jpg
```

### Inference với config

```bash
python mlops/modeling/predict.py \
    --config mlops/config/config.yaml \
    --ckpt_path models/checkpoints/best_model.pt \
    --input_path data/test/ \
    --output_path results/
```

---

## 9. Chạy API Server

### Khởi động FastAPI server

```bash
# Chỉnh sửa CHECKPOINT_PATH trong mlops/serving/api.py
# Sau đó chạy:
uvicorn mlops.serving.api:app --host 0.0.0.0 --port 8000

# Hoặc với Docker
docker run -p 8000:8000 pix2pixhd-mlops
```

### Sử dụng API

```bash
# Test với curl
curl -X POST "http://localhost:8000/predict/" \
    -F "file=@data/test/sample.jpg" \
    --output result.png

# Hoặc truy cập Swagger UI
# http://localhost:8000/docs
```

Xem chi tiết trong [Deployment](deployment.md) và [API Reference](api_reference.md).

---

## 10. Kiểm tra Installation

### Verify PyTorch

```python
import torch
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
```

### Verify Dependencies

```bash
# Chạy tests
pytest tests/

# Hoặc kiểm tra imports
python -c "import mlops; print('OK')"
```

---

## 11. Tiếp theo

Sau khi đã setup xong, bạn có thể:

1. 📖 Đọc [Configuration](configuration.md) để tùy chỉnh training
2. 📊 Xem [Model Architecture](model_architecture.md) để hiểu model
3. 🔧 Xem [Training](training.md) để tối ưu training process
4. 📈 Xem [Experiment Tracking](mlflow.md) để track experiments
5. 🚀 Xem [Deployment](deployment.md) để deploy model

---

## 12. Xử lý sự cố

Nếu gặp lỗi, xem [Troubleshooting](troubleshooting.md) hoặc:

1. Kiểm tra Python version: `python --version` (cần 3.10+)
2. Kiểm tra CUDA (nếu dùng GPU): `nvidia-smi`
3. Kiểm tra dependencies: `pip list`
4. Xem logs chi tiết trong `logs/`

---

## Tham khảo

- [PyTorch Documentation](https://pytorch.org/docs/stable/index.html)
- [Hydra Documentation](https://hydra.cc/docs/intro/)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Weights & Biases Documentation](https://docs.wandb.ai/)
