# Model Architecture

## Tổng quan

Pix2PixHD là một mô hình image-to-image translation nâng cao, mở rộng từ Pix2Pix truyền thống. Mô hình này được thiết kế để sinh ra ảnh có độ phân giải cao và chi tiết tốt hơn nhờ các cải tiến về kiến trúc generator, discriminator và loss function.

---

## 1. Sơ đồ tổng thể

```
Input (Sketch/Label Map)
   │
   ▼
[Generator (Global + Local Enhancer)]
   │
   ▼
Generated Image
   │
   ▼
[Multi-Scale Discriminator]
   │
   └──> Real/Fake Decision (cho từng scale)
```

---

## 2. Generator

- **Global Generator**:
  - Nhận ảnh đầu vào (sketch hoặc label map).
  - Gồm nhiều tầng downsampling, các block ResNet, và upsampling.
  - Sinh ra ảnh có kích thước lớn với cấu trúc tổng thể tốt.

- **Local Enhancer (tuỳ chọn)**:
  - Tăng cường chi tiết cho ảnh đầu ra.
  - Áp dụng thêm các block ResNet và upsampling ở các vùng nhỏ hơn.

- **Các thành phần chính**:
  - Convolutional layers (downsampling)
  - ResNet blocks
  - Transposed convolution (upsampling)
  - InstanceNorm, ReLU, Tanh

---

## 3. Discriminator

- **Multi-Scale PatchGAN**:
  - Sử dụng nhiều discriminator hoạt động trên các phiên bản ảnh với độ phân giải khác nhau (full, 1/2, 1/4).
  - Mỗi discriminator là một PatchGAN: đánh giá từng patch nhỏ thay vì toàn bộ ảnh.
  - Giúp mô hình học được cả đặc trưng tổng thể và chi tiết cục bộ.

- **Các thành phần chính**:
  - Convolutional layers
  - InstanceNorm, LeakyReLU
  - Không dùng pooling, chỉ stride và padding

---

## 4. Loss Functions

- **GAN Loss**:
  - Sử dụng Least Squares GAN (LSGAN) để ổn định quá trình huấn luyện.
- **Feature Matching Loss**:
  - So sánh đặc trưng trích xuất từ các tầng của discriminator giữa ảnh thật và ảnh sinh ra.
- **VGG Perceptual Loss**:
  - So sánh đặc trưng trích xuất từ mạng VGG19 pretrained giữa ảnh thật và ảnh sinh ra.

---

## 5. Sơ đồ chi tiết các module

### Generator (Global)
```
Input
 │
[Downsampling: Conv2d + InstanceNorm + ReLU] x N
 │
[ResNet Blocks] x M
 │
[Upsampling: ConvTranspose2d + InstanceNorm + ReLU] x N
 │
Output (Tanh)
```

### Discriminator (Multi-Scale PatchGAN)
```
Input (Image + Sketch)
 │
[Conv2d + InstanceNorm + LeakyReLU] x K
 │
[Output Patch Map]
```
Lặp lại cho từng scale (full, 1/2, 1/4).

---

## 6. Mã nguồn liên quan

- Generator: `mlops/src/components/generator.py`
- Discriminator: `mlops/src/components/discriminator.py`
- Loss: `mlops/src/components/losses.py`
- Training pipeline: `mlops/modeling/train.py`, `mlops/src/models/pix2pixhd_module.py`

---

## 7. Tham khảo

- [Pix2PixHD Paper](https://arxiv.org/abs/1711.11585)
- [Pix2PixHD Official Code](https://github.com/NVIDIA/pix2pixHD)
- [PyTorch Documentation](https://pytorch.org/docs/stable/index.html)

---
