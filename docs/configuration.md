# Configuration

## Tổng quan

Dự án sử dụng [Hydra](https://hydra.cc/) và [OmegaConf](https://omegaconf.readthedocs.io/) để quản lý cấu hình. Việc này giúp bạn dễ dàng thay đổi các tham số huấn luyện, đường dẫn dữ liệu, cấu trúc mô hình, logging, v.v. mà không cần sửa trực tiếp vào code.

---

## 1. Vị trí file cấu hình

- File cấu hình chính thường đặt tại:
  `config/config.yaml`
- Có thể có thêm các file cấu hình phụ cho từng module hoặc môi trường.

---

## 2. Các nhóm tham số chính

Ví dụ cấu trúc file `config.yaml`:

```yaml
paths:
  raw: data/raw/original
  processed: data/processed

dataset:
  processed_sketch_dir: data/processed/sketches
  processed_image_dir: data/processed/images
  image_size: 256
  num_workers: 4

training:
  num_epochs: 100
  batch_size: 8
  learning_rate: 0.0002
  lambda_feat: 10.0
  replay_pool_size: 10000
  resume_from: null

model:
  generator:
    ngf: 64
    n_downsampling: 4
    n_blocks: 9
    n_local_enhancers: 1
    n_blocks_local: 3
  discriminator_channels: 64
  discriminator:
    n_layers: 4
    num_D: 2

experiment:
  name: pix2pixhd_experiment

logger:
  wandb:
    entity: your-entity
    project: your-project
    group: default
    name: run-name
```

---

## 3. Cách sử dụng Hydra trong code

- Định nghĩa hàm main với decorator `@hydra.main`:
```python
@hydra.main(config_path="../config", config_name="config", version_base=None)
def main(cfg: DictConfig):
    # Truy cập tham số: cfg.training.num_epochs, cfg.model.generator.ngf, ...
```

- Truy cập các tham số cấu hình qua biến `cfg`.

---

## 4. Ghi đè cấu hình qua dòng lệnh

Bạn có thể ghi đè bất kỳ tham số nào khi chạy script:
```bash
python mlops/modeling/train.py training.num_epochs=50 training.batch_size=16
```

---

## 5. Một số lưu ý

- Luôn giữ file cấu hình sạch, dễ đọc, có chú thích rõ ràng.
- Có thể tách cấu hình thành nhiều file nhỏ (theo môi trường, theo module) nếu dự án lớn.
- Hydra sẽ tự động lưu lại cấu hình thực tế đã dùng trong mỗi lần chạy tại thư mục `outputs/`.

---

## 6. Tham khảo

- [Hydra Documentation](https://hydra.cc/docs/intro/)
- [OmegaConf Documentation](https://omegaconf.readthedocs.io/en/latest/)
- [Configuring ML Experiments](https://mlflow.org/docs/latest/projects.html#yaml-configuration)

---
