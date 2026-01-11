# Weights & Biases (wandb)

## Tổng quan

[Weights & Biases (wandb)](https://wandb.ai/) là một nền tảng theo dõi và trực quan hóa quá trình huấn luyện mô hình machine learning. wandb giúp bạn log các tham số, metric, hình ảnh, mô hình, và dễ dàng so sánh các experiment thông qua dashboard trực quan.

---

## 1. Tích hợp wandb trong dự án

- wandb được import và sử dụng trong các script huấn luyện (`mlops/modeling/train.py`, `mlops/src/models/pix2pixhd_module.py`).
- Các thông số, metric, hình ảnh sinh ra trong quá trình training đều được log lên wandb.

Ví dụ đoạn code:
```python
import wandb

# Khởi tạo run
run = wandb.init(
    entity=cfg.logger.wandb.entity,
    project=cfg.logger.wandb.project,
    group=cfg.logger.wandb.group,
    name=cfg.logger.wandb.name,
    config=wandb_config,
    job_type="training",
)  # type: ignore[attr-defined]

# Log metric
wandb.log({"G_loss": g_loss, "D_loss": d_loss, "epoch": epoch})  # type: ignore[attr-defined]

# Log hình ảnh minh họa
wandb.log({"generated_examples": [wandb.Image(img, caption=f"Epoch {epoch}")]})  # type: ignore[attr-defined]

# Kết thúc run
wandb.finish()  # type: ignore[attr-defined]
```

---

## 2. Đăng nhập và cấu hình wandb

- Khi chạy lần đầu, bạn sẽ được yêu cầu đăng nhập hoặc nhập API key.
- Có thể lấy API key tại: [https://wandb.ai/authorize](https://wandb.ai/authorize)
- Có thể cấu hình entity, project, group, name trong file config hoặc truyền qua dòng lệnh.

---

## 3. Theo dõi và trực quan hóa

- Sau khi training, bạn có thể xem dashboard tại: [https://wandb.ai/](https://wandb.ai/)
- Dashboard hiển thị các metric, loss, hình ảnh sinh ra, so sánh các run, download model/artifact.

---

## 4. Một số lưu ý

- Đảm bảo đã cài đặt wandb:
  ```bash
  pip install wandb
  ```
- Nếu không muốn log lên server wandb, có thể chạy ở chế độ offline:
  ```bash
  wandb offline
  ```
- Có thể log thêm các artifact như checkpoint, file config, hình ảnh minh họa.

---

## 5. Mã nguồn liên quan

- Logging trong training:
  `mlops/modeling/train.py`
- Logging hình ảnh:
  `mlops/src/models/pix2pixhd_module.py`

---

## 6. Tham khảo

- [wandb Documentation](https://docs.wandb.ai/)
- [wandb Quickstart](https://docs.wandb.ai/quickstart)
- [wandb Python API](https://docs.wandb.ai/ref/python)

---
