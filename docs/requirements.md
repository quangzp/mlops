# Requirements

## Tổng quan

Tài liệu này liệt kê các yêu cầu hệ thống, dependencies và môi trường cần thiết để chạy dự án Pix2PixHD MLOps.

---

## 1. Hệ điều hành

### Hỗ trợ

- ✅ **Linux**: Ubuntu 20.04+, Debian 11+, CentOS 8+
- ✅ **macOS**: macOS 12+ (Monterey+)
- ✅ **Windows**: Windows 10/11 với WSL2

### Khuyến nghị

- Ubuntu 22.04 LTS (cho production)
- macOS 13+ (cho development)

---

## 2. Phần cứng

### CPU

- **Tối thiểu**: 4 cores
- **Khuyến nghị**: 8+ cores

### RAM

- **Tối thiểu**: 8GB
- **Khuyến nghị**: 16GB+
- **Training**: 32GB+ (tùy dataset size)

### GPU (Tùy chọn nhưng khuyến nghị)

- **NVIDIA GPU** với CUDA support:
  - Tối thiểu: 6GB VRAM (GTX 1060, RTX 2060)
  - Khuyến nghị: 8GB+ VRAM (RTX 3070, RTX 4080, A100)
- **CUDA Version**: 11.7+ hoặc 12.1+

### Storage

- **Tối thiểu**: 20GB
- **Khuyến nghị**: 100GB+ (cho data và models)
- **SSD**: Khuyến nghị cho tốc độ I/O

---

## 3. Software

### Python

- **Version**: Python 3.10 hoặc 3.11
- **Không hỗ trợ**: Python 3.9 trở xuống, Python 3.12+

### CUDA & cuDNN (nếu dùng GPU)

- **CUDA**: 11.7+ hoặc 12.1+
- **cuDNN**: 8.0+ (tự động với PyTorch)

### Git

- Version 2.30+

### Docker (Tùy chọn)

- Docker 20.10+
- Docker Compose 2.0+ (nếu dùng docker-compose)

---

## 4. Python Dependencies

### Core Dependencies

Tất cả dependencies được liệt kê trong `requirements.txt`:

```txt
# Core ML Framework
torch>=2.0.0
torchvision>=0.15.0
pytorch-lightning>=2.0.0
torchmetrics>=1.0.0

# Data Processing
pillow>=10.0.0
opencv-python>=4.8.0
albumentations>=1.3.0
pandas>=2.0.0
numpy>=1.24.0
pyarrow>=10.0.1

# Configuration
hydra-core==1.3.2
omegaconf==2.3.0
python-dotenv>=1.0.0

# Experiment Tracking
mlflow>=2.0.0
wandb==0.15.10

# Data Version Control
dvc>=2.0.0

# Logging
loguru>=0.6.0

# Local package
-e .
```

### Development Dependencies

Cài đặt với:

```bash
pip install -e ".[dev]"
```

Hoặc từ `requirements-dev.txt`:

- `ruff==0.1.9` - Linting và formatting
- `mypy==1.8.0` - Type checking
- `pytest==7.4.3` - Testing
- `pytest-cov==4.1.0` - Coverage
- `pytest-mock==3.12.0` - Mocking
- `pytest-xdist==3.5.0` - Parallel testing
- `pytest-timeout==2.2.0` - Timeout
- `ipython==8.18.1` - Interactive Python
- `ipdb==0.13.13` - Debugging

### Documentation Dependencies

Cài đặt với:

```bash
pip install -e ".[docs]"
```

Hoặc:

- `mkdocs==1.5.3` - Documentation generator
- `mkdocs-material==9.5.3` - Material theme
- `mkdocstrings[python]==0.24.0` - API documentation

---

## 5. Cài đặt

### Quick Install

```bash
# Clone repository
git clone https://github.com/quangzp/pix2pix-mlops.git
cd pix2pix-mlops

# Tạo virtual environment
python3.10 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Cài đặt dependencies
pip install -r requirements.txt
```

### Install với Conda

```bash
# Tạo conda environment
conda create -n pix2pix python=3.10
conda activate pix2pix

# Cài đặt PyTorch với CUDA
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia

# Cài đặt dependencies
pip install -r requirements.txt
```

### Install Development Dependencies

```bash
# Cài đặt dev dependencies
pip install -e ".[dev]"

# Hoặc
pip install -r requirements-dev.txt
```

### Install Documentation Dependencies

```bash
# Cài đặt docs dependencies
pip install -e ".[docs]"

# Hoặc
pip install mkdocs==1.5.3 mkdocs-material==9.5.3 "mkdocstrings[python]==0.24.0"
```

---

## 6. Verify Installation

### Kiểm tra Python

```bash
python --version
# Output: Python 3.10.x hoặc 3.11.x
```

### Kiểm tra PyTorch

```python
import torch
print(f"PyTorch: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"CUDA version: {torch.version.cuda}")
    print(f"cuDNN version: {torch.backends.cudnn.version()}")
    print(f"GPU: {torch.cuda.get_device_name(0)}")
```

### Kiểm tra Dependencies

```bash
# Kiểm tra imports
python -c "import mlops; print('OK')"

# Chạy tests
pytest tests/ -v
```

---

## 7. Platform-specific Notes

### Linux

- Đảm bảo có `build-essential` cho compilation:
  ```bash
  sudo apt-get update
  sudo apt-get install build-essential
  ```

### macOS

- Có thể cần Xcode Command Line Tools:
  ```bash
  xcode-select --install
  ```
- Với Apple Silicon (M1/M2/M3):
  - PyTorch sẽ sử dụng MPS backend
  - Không cần CUDA

### Windows

- Khuyến nghị dùng WSL2
- Hoặc cài đặt Visual C++ Build Tools
- PyTorch có thể không hỗ trợ CUDA trên Windows (dùng CPU hoặc WSL2)

---

## 8. Version Compatibility

### PyTorch & CUDA

| PyTorch | CUDA | Notes |
| :--- | :--- | :--- |
| 2.0.0 | 11.7, 11.8 | Stable |
| 2.1.0 | 11.8, 12.1 | Recommended |
| 2.2.0 | 11.8, 12.1 | Latest |

### Python & Dependencies

- Python 3.10: ✅ Fully supported
- Python 3.11: ✅ Fully supported
- Python 3.9: ❌ Not supported (type hints)
- Python 3.12: ⚠️ May have issues with some dependencies

---

## 9. Troubleshooting

### Lỗi cài đặt pyarrow

```bash
# Cần CMake 3.25+
# Ubuntu/Debian
sudo apt-get install cmake

# macOS
brew install cmake
```

### Lỗi CUDA

```bash
# Kiểm tra CUDA
nvidia-smi

# Kiểm tra PyTorch CUDA
python -c "import torch; print(torch.cuda.is_available())"
```

### Lỗi dependencies conflicts

```bash
# Tạo environment mới
conda create -n pix2pix python=3.10
conda activate pix2pix

# Hoặc
python3.10 -m venv venv --clear
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Xem thêm trong [Troubleshooting](troubleshooting.md).

---

## 10. Tham khảo

- [PyTorch Installation](https://pytorch.org/get-started/locally/)
- [CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)
- [Python Documentation](https://docs.python.org/3/)
- [pip Documentation](https://pip.pypa.io/en/stable/)
