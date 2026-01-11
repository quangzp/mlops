# Training

## Mục tiêu

Hướng dẫn chi tiết quá trình huấn luyện mô hình Pix2PixHD cho bài toán image-to-image translation, bao gồm các bước chuẩn bị, cấu hình, chạy training, theo dõi tiến trình và lưu checkpoint.

---

## 1. Chuẩn bị dữ liệu

- Đảm bảo dữ liệu đã được chuẩn hóa và đặt đúng thư mục:
  - Ảnh gốc: `data/raw/original/`
  - Ảnh sketch: `data/processed/sketches/`
  - Ảnh ground-truth: `data/processed/images/`
- Cấu trúc thư mục dữ liệu phải khớp với config trong file cấu hình Hydra.

---

## 2. Cấu hình training

- Các tham số training được quản lý qua file config (Hydra/OmegaConf):
  - Số epoch: `training.num_epochs`
  - Batch size: `training.batch_size`
  - Learning rate: `training.learning_rate`
  - Đường dẫn checkpoint: `models/checkpoints/`
  - Tham số model: `model.generator`, `model.discriminator`
- Có thể chỉnh sửa các tham số này trong file `config/config.yaml` hoặc truyền qua dòng lệnh.

---

## 3. Chạy training

### Chạy bằng Python

```bash
python mlops/modeling/train.py
```

### Chạy bằng Docker (nếu có Dockerfile)

```bash
docker build -t pix2pixhd-mlops .
docker run --rm -v $(pwd)/data:/app/data pix2pixhd-mlops
```

---

## 4. Theo dõi tiến trình training

- **Loguru**: In thông tin tiến trình, loss, checkpoint ra console.
- **MLflow**: Theo dõi tham số, loss, metric, checkpoint qua giao diện web.
  - Chạy MLflow UI:
    ```bash
    mlflow ui
    ```
    Truy cập [http://localhost:5000](http://localhost:5000)
- **Weights & Biases (wandb)**: Theo dõi loss, metric, hình ảnh sinh ra, dashboard trực quan.
  - Đăng nhập wandb khi được yêu cầu, hoặc cấu hình API key.

---

## 5. Lưu và resume checkpoint

- Checkpoint được lưu tự động vào thư mục `models/checkpoints/`.
- Để tiếp tục training từ checkpoint, chỉnh `training.resume_from` trong config hoặc truyền qua dòng lệnh.

---

## 6. Kết thúc training

- Sau khi training hoàn tất, model và các metric sẽ được lưu lại.
- Có thể sử dụng script `predict.py` để kiểm tra kết quả inference.

---

## 7. Một số lưu ý

- Đảm bảo GPU đã được nhận diện nếu muốn training nhanh hơn (kiểm tra bằng `torch.cuda.is_available()`).
- Nếu gặp lỗi thiếu dữ liệu, kiểm tra lại đường dẫn và số lượng ảnh trong các thư mục dữ liệu.
- Nếu muốn thay đổi cấu trúc model, chỉnh sửa trong các file `mlops/src/components/` và cập nhật config.

---

## 8. Tham khảo

- [Pix2PixHD Paper](https://arxiv.org/abs/1711.11585)
- [PyTorch Documentation](https://pytorch.org/docs/stable/index.html)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [Weights & Biases Documentation](https://docs.wandb.ai/)

---
