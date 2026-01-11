# Project Structure

## Tổng quan

Dự án được tổ chức theo chuẩn MLOps hiện đại, tách biệt rõ ràng giữa các thành phần: code nguồn, dữ liệu, cấu hình, tài liệu, kết quả huấn luyện và các công cụ tracking.
Cấu trúc này giúp dự án dễ mở rộng, bảo trì, kiểm thử và triển khai.

---

## 1. Sơ đồ cấu trúc thư mục

```
mlops/
├── mlops/
│   ├── modeling/
│   │   ├── train.py
│   │   ├── predict.py
│   │   └── ...
│   ├── src/
│   │   ├── components/
│   │   │   ├── generator.py
│   │   │   ├── discriminator.py
│   │   │   ├── losses.py
│   │   │   └── replay_pool.py
│   │   └── models/
│   │       └── pix2pixhd_module.py
│   └── ...
├── data/
│   ├── raw/
│   ├── processed/
│   └── ...
├── models/
│   └── checkpoints/
├── reports/
│   └── metrics.json
├── mlruns/
│   └── ... (MLflow tracking)
├── wandb/
│   └── ... (Weights & Biases tracking)
├── config/
│   └── config.yaml
├── requirements.txt
├── pyproject.toml
├── Dockerfile
├── docs/
│   ├── mkdocs.yml
│   └── ... (các file tài liệu .md)
└── README.md
```

---

## 2. Ý nghĩa các thư mục và file chính

- **mlops/modeling/**
  Chứa các script chính để huấn luyện (`train.py`), dự đoán (`predict.py`), và các pipeline liên quan.

- **mlops/src/components/**
  Chứa các thành phần cốt lõi của mô hình: generator, discriminator, loss, replay buffer...

- **mlops/src/models/**
  Chứa các module quản lý pipeline huấn luyện, đóng gói mô hình (ví dụ: `pix2pixhd_module.py`).

- **data/raw/**
  Dữ liệu gốc, chưa qua xử lý.

- **data/processed/**
  Dữ liệu đã qua xử lý, sẵn sàng cho huấn luyện.

- **models/checkpoints/**
  Lưu checkpoint của mô hình trong quá trình huấn luyện.

- **reports/**
  Lưu các báo cáo, kết quả cuối cùng (ví dụ: metrics, hình ảnh minh họa).

- **mlruns/**
  Thư mục tracking của MLflow (tự động sinh ra khi chạy MLflow).

- **wandb/**
  Thư mục tracking của Weights & Biases (tự động sinh ra khi dùng wandb).

- **config/config.yaml**
  File cấu hình chính cho toàn bộ pipeline (dùng Hydra/OmegaConf).

- **requirements.txt**
  Danh sách các package Python cần thiết.

- **pyproject.toml**
  Cấu hình cho các công cụ dev như ruff, mypy, pytest...

- **Dockerfile**
  Định nghĩa môi trường Docker để đóng gói và triển khai dự án.

- **docs/**
  Chứa tài liệu dự án (MkDocs).

- **README.md**
  Giới thiệu tổng quan dự án, hướng dẫn cài đặt nhanh.

---

## 3. Một số lưu ý

- **Không chỉnh sửa trực tiếp dữ liệu trong `data/raw/`**.
  Hãy xử lý và lưu vào `data/processed/` để đảm bảo reproducibility.
- **Không commit các file lớn, checkpoint, hoặc dữ liệu cá nhân lên git**.
- **Thư mục tracking (`mlruns/`, `wandb/`) có thể thêm vào `.gitignore`** nếu không cần lưu lịch sử trên git.
- **Tài liệu nên cập nhật thường xuyên trong `docs/`** để hỗ trợ phát triển và bảo trì.

---

## 4. Tham khảo

- [Cookiecutter Data Science](https://drivendata.github.io/cookiecutter-data-science/)
- [MLOps Best Practices](https://ml-ops.org/)
- [PyTorch Project Structure](https://pytorch.org/tutorials/beginner/nn_tutorial.html)

---
