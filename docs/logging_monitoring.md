# Logging & Monitoring

## Tổng quan

Việc logging và monitoring giúp bạn theo dõi tiến trình huấn luyện, phát hiện lỗi sớm, kiểm soát chất lượng mô hình và dễ dàng so sánh các experiment. Dự án sử dụng kết hợp **Loguru** (logging ra console), **MLflow** và **Weights & Biases (wandb)** để log và trực quan hóa toàn bộ quá trình training.

---

## 1. Logging với Loguru

- **Loguru** là thư viện logging mạnh mẽ, dễ dùng, thay thế cho logging chuẩn của Python.
- Được sử dụng để in thông tin tiến trình, trạng thái, lỗi, checkpoint ra console.

Ví dụ:
```python
from loguru import logger

logger.info("Starting Pix2PixHD Training")
logger.success("Generator initialized")
logger.error(f"Training failed: {str(e)}")
```

- Các mức độ log: `info`, `success`, `warning`, `error`, `debug`.

---

## 2. Monitoring với MLflow

- **MLflow** giúp tracking các tham số, metric, artifact, checkpoint trong quá trình training.
- Có thể xem lại lịch sử các run, so sánh các experiment qua giao diện web.

Các bước sử dụng:
1. Log tham số và metric trong code:
    ```python
    mlflow.log_param("num_epochs", num_epochs)
    mlflow.log_metric("G_loss", g_loss, step=epoch)
    ```
2. Chạy MLflow UI:
    ```bash
    mlflow ui
    ```
3. Truy cập [http://localhost:5000](http://localhost:5000) để xem dashboard.

---

## 3. Monitoring với Weights & Biases (wandb)

- **wandb** giúp trực quan hóa loss, metric, hình ảnh sinh ra, và so sánh các run trên dashboard online.
- Log metric, hình ảnh, artifact trong quá trình training.

Ví dụ:
```python
wandb.log({"G_loss": g_loss, "D_loss": d_loss, "epoch": epoch})  # type: ignore[attr-defined]
wandb.log({"generated_examples": [wandb.Image(img, caption=f"Epoch {epoch}")]} )  # type: ignore[attr-defined]
```
- Dashboard: [https://wandb.ai/](https://wandb.ai/)

---

## 4. Một số lưu ý khi logging & monitoring

- Luôn log đầy đủ các tham số, metric quan trọng (loss, learning rate, epoch, ...).
- Log hình ảnh minh họa để kiểm tra chất lượng ảnh sinh ra qua từng epoch.
- Nếu training nhiều lần, hãy đặt tên run/experiment rõ ràng để dễ so sánh.
- Có thể log thêm các artifact như checkpoint, file config, hình ảnh đầu ra.

---

## 5. Tham khảo

- [Loguru Documentation](https://loguru.readthedocs.io/en/stable/)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [wandb Documentation](https://docs.wandb.ai/)

---
