# MLflow

## Tổng quan

[MLflow](https://mlflow.org/) là một nền tảng mã nguồn mở giúp quản lý vòng đời của các mô hình machine learning, bao gồm tracking các tham số, metrics, artifacts và quản lý mô hình.
Trong dự án này, MLflow được sử dụng để theo dõi quá trình huấn luyện Pix2PixHD, lưu lại các thông số, kết quả và checkpoint.

---

## 1. Cách tích hợp MLflow trong dự án

- MLflow được sử dụng trực tiếp trong file `mlops/modeling/train.py`.
- Các tham số, metrics và artifacts được log tự động trong mỗi lần huấn luyện.

Ví dụ đoạn code:
```python
import mlflow

mlflow.set_experiment(cfg.experiment.name)

with mlflow.start_run():
    mlflow.log_param("num_epochs", num_epochs)
    mlflow.log_param("batch_size", batch_size)
    mlflow.log_param("learning_rate", learning_rate)
    # ...
    mlflow.log_metric("G_loss", g_loss, step=epoch)
    mlflow.log_metric("D_loss", d_loss, step=epoch)
```

---

## 2. Các thành phần được log

- **Parameters**: Số epoch, batch size, learning rate, cấu hình model,...
- **Metrics**: Loss của generator, discriminator, các chỉ số đánh giá khác.
- **Artifacts**: Checkpoint model, file metrics, hình ảnh minh họa (nếu có).
- **Tags**: Thông tin về experiment, version, user.

---

## 3. Cách sử dụng MLflow UI

### Khởi động giao diện web:
```bash
mlflow ui
```
- Mặc định truy cập tại: [http://localhost:5000](http://localhost:5000)
- Có thể xem lại lịch sử các lần train, so sánh các run, tải về model/checkpoint.

---

## 4. Lưu và tải lại mô hình

- MLflow hỗ trợ lưu và tải lại mô hình qua API hoặc giao diện web.
- Có thể dùng cho việc deploy hoặc inference sau này.

---

## 5. Cấu hình nâng cao

- Có thể thay đổi nơi lưu trữ tracking server (local, remote, S3, GCS, ...).
- Có thể tích hợp với CI/CD để tự động log khi train trên server.

---

## 6. Một số lưu ý

- Đảm bảo thư mục `mlruns/` không bị xóa để giữ lịch sử các lần train.
- Nếu gặp lỗi về file meta.yaml, hãy xóa folder `mlruns/0` để MLflow tự tạo lại.

---

## 7. Tham khảo

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [MLflow Tracking Quickstart](https://mlflow.org/docs/latest/quickstart.html)
- [MLflow Python API](https://mlflow.org/docs/latest/python_api/index.html)

---
