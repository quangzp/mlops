# Dataset Preparation

## Tổng quan

Việc chuẩn bị dữ liệu là bước quan trọng để đảm bảo mô hình Pix2PixHD học hiệu quả. Dữ liệu cần được tổ chức, xử lý và chia tách hợp lý trước khi đưa vào pipeline huấn luyện.

---

## 1. Yêu cầu dữ liệu

- **Ảnh đầu vào**: Thường là ảnh sketch, label map hoặc ảnh đã qua xử lý.
- **Ảnh ground-truth**: Ảnh thật tương ứng với ảnh đầu vào.
- **Định dạng**: Ảnh màu (RGB), kích thước đồng nhất (ví dụ: 256x256 hoặc 512x512).
- **Cặp ảnh**: Mỗi ảnh đầu vào phải có đúng một ảnh ground-truth tương ứng.

---

## 2. Cấu trúc thư mục dữ liệu

Ví dụ:
```
data/
├── raw/
│   ├── original/           # Ảnh gốc chưa xử lý
│   └── ...
├── processed/
│   ├── sketches/           # Ảnh sketch (input)
│   └── images/             # Ảnh ground-truth (output)
```

---

## 3. Tiền xử lý dữ liệu

- **Resize**: Đưa tất cả ảnh về cùng kích thước (dùng OpenCV, PIL hoặc torchvision).
- **Chuẩn hóa**: Chuyển ảnh về dạng tensor, scale giá trị pixel về [0, 1] hoặc [-1, 1].
- **Kiểm tra cặp ảnh**: Đảm bảo số lượng và thứ tự ảnh sketch và ảnh ground-truth khớp nhau.
- **Chia train/test**: Thường chia 80% train, 20% test (có thể random hoặc theo tên file).

Ví dụ code tiền xử lý:
```python
from PIL import Image
import os

input_dir = "data/raw/original"
output_dir = "data/processed/sketches"
size = (256, 256)

for fname in os.listdir(input_dir):
    img = Image.open(os.path.join(input_dir, fname)).convert("RGB")
    img = img.resize(size)
    img.save(os.path.join(output_dir, fname))
```

---

## 4. Tích hợp với DataLoader

- Dự án sử dụng class `Pix2PixHDDataset` để load dữ liệu đã xử lý.
- Đảm bảo truyền đúng đường dẫn tới folder sketches và images trong config.

Ví dụ:
```python
train_dataset = Pix2PixHDDataset(
    images_dir="data/processed/",
    feature_fold="sketches/",
    label_fold="images/",
    img_size=256,
)
```

---

## 5. Một số lưu ý

- Không nên chỉnh sửa dữ liệu gốc trong `data/raw/`, hãy lưu dữ liệu đã xử lý vào `data/processed/`.
- Có thể sử dụng các augmentation (xoay, lật, crop) để tăng đa dạng dữ liệu.
- Kiểm tra kỹ dữ liệu đầu vào để tránh lỗi khi training (thiếu ảnh, sai tên file, ...).

---

## 6. Tham khảo

- [PyTorch Dataset & DataLoader](https://pytorch.org/tutorials/beginner/data_loading_tutorial.html)
- [Pillow Documentation](https://pillow.readthedocs.io/en/stable/)
- [OpenCV Documentation](https://docs.opencv.org/)

---
