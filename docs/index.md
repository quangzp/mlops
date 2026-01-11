# 🎨 Pix2PixHD MLOps Project

> **End-to-end MLOps pipeline for Pix2PixHD image-to-image translation**

---

## 📖 Giới thiệu

Dự án này triển khai thuật toán **Pix2PixHD** (sử dụng *Global Generator* và *Multiscale Discriminator*) để tạo ra hình ảnh độ phân giải cao từ bản vẽ sketch hoặc label map.

Điểm đặc biệt của dự án không nằm ở thuật toán mới, mà ở việc **chuẩn hóa quy trình phát triển theo tiêu chuẩn MLOps**, giải quyết các vấn đề thực tế:

- ✅ **Quản lý dữ liệu**: Xử lý versioning cho dữ liệu ảnh lớn bằng DVC
- ✅ **Module hóa**: Tách biệt code nghiên cứu và code sản phẩm
- ✅ **Hybrid Training**: Phát triển trên local, huấn luyện trên GPU server
- ✅ **CI/CD**: Tự động kiểm tra lỗi code và tích hợp quy trình đóng gói
- ✅ **Experiment Tracking**: Theo dõi thí nghiệm với MLflow và WandB
- ✅ **Deployment**: API serving với FastAPI

---

## 🚀 Bắt đầu nhanh

### Cài đặt

```bash
# Clone dự án
git clone https://github.com/quangzp/pix2pix-mlops.git
cd pix2pix-mlops

# Tạo môi trường ảo
conda create -n pix2pix python=3.10
conda activate pix2pix

# Cài đặt dependencies
pip install -r requirements.txt
```

### Chuẩn bị dữ liệu

```bash
# Tải dữ liệu (nếu dùng DVC)
dvc pull
```

### Huấn luyện

```bash
# Chạy training với config mặc định
python mlops/modeling/train.py

# Hoặc tùy chỉnh parameters
python mlops/modeling/train.py training.num_epochs=100 training.batch_size=8
```

### Inference

```bash
# Sinh ảnh từ model đã train
python mlops/modeling/predict.py \
    --ckpt_path models/checkpoints/best_model.pt \
    --input_path data/test/sample.jpg \
    --output_path results/output.jpg
```

---

## 📚 Tài liệu

### Hướng dẫn cơ bản

- [Getting Started](getting_started.md) - Hướng dẫn chi tiết để bắt đầu với dự án
- [Requirements](requirements.md) - Yêu cầu hệ thống và dependencies
- [Project Structure](project_structure.md) - Cấu trúc thư mục dự án
- [Configuration](configuration.md) - Quản lý cấu hình với Hydra

### Data Pipeline

- [Data Overview](data_overview.md) - Tổng quan về dữ liệu
- [Dataset Preparation](dataset_preparation.md) - Chuẩn bị dataset
- [DataLoader & Augmentation](dataloader_augmentation.md) - DataLoader và augmentation

### Model

- [Model Architecture](model_architecture.md) - Kiến trúc tổng thể của mô hình
- [Generator](generator.md) - Generator architecture
- [Discriminator](discriminator.md) - Discriminator architecture
- [Loss Functions](loss_functions.md) - Các hàm loss được sử dụng

### Training

- [Training Script](training.md) - Hướng dẫn huấn luyện
- [Checkpointing](checkpointing.md) - Lưu và load checkpoint
- [Logging & Monitoring](logging_monitoring.md) - Theo dõi training

### Experiment Tracking

- [MLflow](mlflow.md) - Sử dụng MLflow để track experiments
- [Weights & Biases](wandb.md) - Sử dụng WandB để visualize

### Deployment

- [Deployment](deployment.md) - Triển khai model với FastAPI

### Development

- [Testing & Linting](dev_tools.md) - Công cụ phát triển
- [Troubleshooting](troubleshooting.md) - Xử lý sự cố thường gặp

### Tham khảo

- [API Reference](api_reference.md) - Tài liệu API
- [Changelog](changelog.md) - Lịch sử thay đổi

---

## 🛠 Tech Stack

| Thành phần | Công nghệ | Mục đích |
| :--- | :--- | :--- |
| **Language** | Python 3.10 | Ngôn ngữ lập trình chính |
| **Core Framework** | PyTorch, PyTorch Lightning | Xây dựng Model và Training Loop |
| **Data Management** | DVC | Quản lý version dữ liệu |
| **Config Management** | Hydra | Quản lý Hyperparameters |
| **Experiment Tracking** | MLflow, WandB | Theo dõi experiments |
| **CI/CD** | GitHub Actions | Tự động test và build Docker |
| **Environment** | Docker | Đóng gói môi trường |
| **Serving** | FastAPI | API deployment |

---

## 📊 Kết quả

Dự án đã được triển khai thành công với khả năng:

- ✅ Training ổn định với checkpoint/resume
- ✅ Experiment tracking đầy đủ với MLflow và WandB
- ✅ CI/CD pipeline hoàn chỉnh
- ✅ Docker containerization
- ✅ FastAPI serving

---

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng xem [GitHub Repository](https://github.com/quangzp/pix2pix-mlops) để biết thêm chi tiết.

---

## 📄 License

Dự án này được phân phối dưới license MIT. Xem file `LICENSE` để biết thêm chi tiết.

---

## 👥 Tác giả

**Nhóm 11** - Đại học Bách Khoa Hà Nội

---

## 🔗 Liên kết

- [GitHub Repository](https://github.com/quangzp/pix2pix-mlops)
- [Documentation](https://quangzp.github.io/pix2pix-mlops/)
