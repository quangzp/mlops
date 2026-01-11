# Data Overview

## Tổng quan

Dữ liệu là nền tảng quan trọng cho mọi dự án machine learning. Trong dự án Pix2PixHD này, dữ liệu bao gồm các cặp ảnh đầu vào (sketch hoặc label map) và ảnh ground-truth (ảnh thật), phục vụ cho bài toán image-to-image translation.

---

## 1. Loại dữ liệu

### Input (Ảnh đầu vào)

- **Sketch images**: Ảnh phác thảo, bản vẽ tay
- **Label maps**: Ảnh phân đoạn ngữ nghĩa
- **Định dạng**: RGB, kích thước đồng nhất (256x256, 512x512, hoặc cao hơn)
- **File format**: JPG, PNG

### Target (Ảnh đích)

- **Real images**: Ảnh thật tương ứng với input
- **Định dạng**: RGB, cùng kích thước với input
- **File format**: JPG, PNG

### Yêu cầu

- Mỗi ảnh input phải có **đúng một** ảnh target tương ứng
- Tên file phải **khớp nhau** (ví dụ: `001.jpg` và `001.jpg`)
- Kích thước ảnh nên **đồng nhất** (được resize về cùng kích thước)

---

## 2. Cấu trúc thư mục

### Cấu trúc chuẩn

```
data/
├── raw/
│   └── original/           # Ảnh gốc chưa xử lý (optional)
│
└── processed/
    ├── sketches/           # Ảnh sketch (input) - REQUIRED
    │   ├── 001.jpg
    │   ├── 002.jpg
    │   └── ...
    │
    └── images/             # Ảnh ground-truth (target) - REQUIRED
        ├── 001.jpg
        ├── 002.jpg
        └── ...
```

### Ý nghĩa các thư mục

- **`data/raw/`**: Lưu trữ dữ liệu gốc, chưa qua xử lý (backup, reference)
- **`data/processed/sketches/`**: Ảnh sketch đã được resize và chuẩn hóa, sẵn sàng cho training
- **`data/processed/images/`**: Ảnh ground-truth đã được resize và chuẩn hóa, sẵn sàng cho training

---

## 3. Đặc điểm dữ liệu

### Kích thước dataset

- **Tối thiểu**: 100-200 cặp ảnh (cho testing)
- **Khuyến nghị**: 1000+ cặp ảnh (cho training tốt)
- **Lý tưởng**: 5000+ cặp ảnh (cho high-quality results)

### Kích thước ảnh

- **Training size**: 256x256 (phổ biến), 512x512, hoặc cao hơn
- **Resolution**: Có thể resize từ ảnh gốc độ phân giải cao

### Định dạng file

- **Input**: JPG, PNG (RGB)
- **Output**: JPG, PNG (RGB)

### Data quality

- **Cặp ảnh phải tương ứng**: Sketch và image phải match về nội dung
- **Ảnh không bị corrupt**: Kiểm tra integrity trước khi training
- **Balance**: Tránh bias trong dataset (nếu có thể)

---

## 4. Data Pipeline

### Quy trình xử lý dữ liệu

```
Raw Data
  ↓
Preprocessing (resize, normalize)
  ↓
Split (train/val/test)
  ↓
DataLoader (augmentation, batching)
  ↓
Model Training
```

### Preprocessing

1. **Resize**: Đưa tất cả ảnh về cùng kích thước (256x256, 512x512, ...)
2. **Normalize**: Scale pixel values về [-1, 1] hoặc [0, 1]
3. **Format conversion**: Đảm bảo RGB format

### Train/Val/Test Split

Theo config mặc định:

- **Train**: 80%
- **Val**: 10%
- **Test**: 10%

Có thể tùy chỉnh trong `mlops/config/dataset.yaml`:

```yaml
dataset:
  train_split: 0.8
  val_split: 0.1
  test_split: 0.1
```

---

## 5. Data Loading

### Dataset Class

Dự án sử dụng `Pix2PixHDDataset` để load dữ liệu:

```python
from mlops.src.models.pix2pixhd_module import Pix2PixHDDataset

dataset = Pix2PixHDDataset(
    images_dir="data/processed/",
    feature_fold="sketches/",
    label_fold="images/",
    img_size=256
)
```

### DataLoader

```python
from torch.utils.data import DataLoader

dataloader = DataLoader(
    dataset,
    batch_size=4,
    shuffle=True,
    num_workers=4,
    pin_memory=True
)
```

Xem chi tiết trong [DataLoader & Augmentation](dataloader_augmentation.md).

---

## 6. Data Versioning với DVC

Dự án sử dụng DVC để quản lý version dữ liệu:

```bash
# Tải dữ liệu từ remote storage
dvc pull

# Upload dữ liệu mới
dvc add data/processed/
dvc push
```

### Lợi ích

- ✅ Version control cho dữ liệu lớn
- ✅ Dễ dàng chia sẻ và tái tạo experiments
- ✅ Tracking data changes

---

## 7. Data Augmentation

### Augmentation được sử dụng

Theo config:

```yaml
dataset:
  augmentation:
    enable: true
    horizontal_flip: 0.5
    rotation: 15
    brightness: 0.2
    contrast: 0.2
```

### Các augmentation phổ biến

- **Horizontal flip**: Lật ảnh ngang (probability: 0.5)
- **Rotation**: Xoay ảnh (±15 độ)
- **Brightness/Contrast**: Điều chỉnh độ sáng và độ tương phản
- **Color jitter**: Biến đổi màu sắc nhẹ

Xem chi tiết trong [DataLoader & Augmentation](dataloader_augmentation.md).

---

## 8. Kiểm tra dữ liệu

### Verify dataset

```bash
# Đếm số lượng ảnh
ls data/processed/sketches/ | wc -l
ls data/processed/images/ | wc -l

# Kiểm tra tên file khớp
python -c "
import os
sketches = set(os.listdir('data/processed/sketches/'))
images = set(os.listdir('data/processed/images/'))
print(f'Sketch files: {len(sketches)}')
print(f'Image files: {len(images)}')
print(f'Matched: {len(sketches & images)}')
"
```

### Visualize samples

```python
from PIL import Image
import matplotlib.pyplot as plt

# Load sample
sketch = Image.open('data/processed/sketches/001.jpg')
image = Image.open('data/processed/images/001.jpg')

# Display
fig, axes = plt.subplots(1, 2)
axes[0].imshow(sketch)
axes[0].set_title('Sketch')
axes[1].imshow(image)
axes[1].set_title('Ground-truth')
plt.show()
```

---

## 9. Best Practices

### ✅ Nên làm

- Chuẩn bị dữ liệu kỹ trước khi training
- Kiểm tra tính tương ứng của cặp ảnh
- Sử dụng DVC để quản lý version
- Split data một cách hợp lý (train/val/test)
- Sử dụng augmentation để tăng đa dạng dữ liệu

### ❌ Không nên

- Không chỉnh sửa dữ liệu trong `data/raw/` (immutable)
- Không commit dữ liệu lớn lên git (dùng DVC)
- Không bỏ qua bước kiểm tra dữ liệu
- Không train/val/test leak (đảm bảo split đúng)

---

## 10. Tham khảo

- [Dataset Preparation](dataset_preparation.md) - Hướng dẫn chuẩn bị dataset
- [DataLoader & Augmentation](dataloader_augmentation.md) - DataLoader và augmentation
- [DVC Documentation](https://dvc.org/doc) - Data Version Control
- [PyTorch Dataset](https://pytorch.org/tutorials/beginner/data_loading_tutorial.html)
