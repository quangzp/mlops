# Data Overview

## Tổng quan

Dữ liệu là nền tảng quan trọng cho mọi dự án machine learning. Trong dự án Pix2PixHD này, dữ liệu bao gồm các cặp ảnh đầu vào (sketch hoặc label map) và ảnh ground-truth (ảnh thật), phục vụ cho bài toán image-to-image translation.

---

## 1. Loại dữ liệu sử dụng

- **Ảnh đầu vào (Input)**:
  - Thường là ảnh sketch, ảnh phác thảo, hoặc label map.
  - Định dạng: RGB, kích thước đồng nhất (ví dụ: 256x256 hoặc 512x512).
- **Ảnh ground-truth (Target)**:
  - Ảnh thật tương ứng với từng ảnh đầu vào.
  - Định dạng: RGB, cùng kích thước với ảnh đầu vào.

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

- **raw/**: Lưu trữ dữ liệu gốc, chưa qua xử lý.
- **processed/**: Lưu trữ dữ liệu đã resize, chuẩn hóa, sẵn sàng cho training.

---

## 3. Đặc điểm dữ liệu

- **Số lượng ảnh**:
  - Tùy theo dataset, thường từ vài trăm đến vài nghìn cặp ảnh.
- **Định dạng file**:
  - PNG, JPG hoặc JPEG.
- **Yêu cầu**:
  - Mỗi ảnh sketch phải có đúng một ảnh ground-truth tương ứng (trùng tên file).

---

## 4. Ví dụ minh họa

| Sketch (Input)         | Ground-truth (Target)   |
|------------------------|------------------------|
| ![sketch](images/sketch_example.png) | ![real](images/real_example.png) |

---

## 5. Chia tách dữ liệu

- **Train/Test Split**:
  - Thường chia 80% train, 20% test.
  - Có thể chia ngẫu nhiên hoặc theo thứ tự tên file.

---

## 6. Một số lưu ý

- Đảm bảo dữ liệu đã được resize và chuẩn hóa trước khi training.
- Kiểm tra kỹ số lượng và tên file giữa hai folder sketches và images để tránh mismatch.
- Có thể bổ sung thêm dữ liệu hoặc sử dụng augmentation để tăng hiệu quả huấn luyện.

---

## 7. Tham khảo

- [Pix2PixHD Dataset Example](https://github.com/NVIDIA/pix2pixHD/tree/master/datasets)
- [PyTorch Data Loading](https://pytorch.org/tutorials/beginner/data_loading_tutorial.html)

---
