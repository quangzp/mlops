# Discriminator

## Tổng quan

Discriminator trong Pix2PixHD là một thành phần quan trọng giúp mô hình học được sự khác biệt giữa ảnh thật và ảnh sinh ra. Trong dự án này, discriminator được xây dựng theo kiến trúc **Multi-Scale PatchGAN**, giúp đánh giá chất lượng ảnh ở nhiều cấp độ khác nhau.

---

## 1. Kiến trúc Multi-Scale Discriminator

- **Multi-Scale**: Sử dụng nhiều discriminator hoạt động trên các phiên bản ảnh với độ phân giải khác nhau (ví dụ: gốc, giảm 1/2, giảm 1/4).
- **PatchGAN**: Thay vì đánh giá toàn bộ ảnh, discriminator đánh giá từng patch nhỏ, giúp tập trung vào chi tiết cục bộ.

### Sơ đồ tổng quát

```
Input (real or fake image + sketch)
   │
   ├──> Discriminator 1 (full scale)
   ├──> Discriminator 2 (downsampled 1/2)
   └──> Discriminator 3 (downsampled 1/4)
```

Mỗi discriminator đều có cấu trúc nhiều tầng convolution, normalization và activation (LeakyReLU).

---

## 2. Cấu hình trong dự án

Các tham số cấu hình chính:
- `input_nc`: Số kênh đầu vào (thường là 6: 3 kênh sketch + 3 kênh ảnh).
- `ndf`: Số lượng filter ở tầng đầu tiên.
- `n_layers_D`: Số tầng convolution.
- `num_D`: Số lượng discriminator (scale).
- `norm`: Loại normalization (thường là InstanceNorm).
- `use_sigmoid`: Có dùng sigmoid ở output không (thường là False với LSGAN).

Ví dụ khởi tạo trong code:
```python
discriminator = define_D(
    input_nc=6,
    ndf=64,
    n_layers_D=4,
    norm="instance",
    use_sigmoid=False,
    num_D=2,
    getIntermFeat=True,
    gpu_ids=[],
    num_outputs=1,
)
```

---

## 3. Vai trò trong huấn luyện

- Phân biệt ảnh thật và ảnh sinh ra từ generator.
- Cung cấp tín hiệu gradient cho generator thông qua loss GAN.
- Multi-scale giúp mô hình học được cả đặc trưng tổng thể và chi tiết cục bộ.

---

## 4. Loss Function

- Sử dụng **GANLoss** (LSGAN hoặc BCE).
- Loss tổng hợp từ tất cả các scale.

---

## 5. Mã nguồn liên quan

- Định nghĩa discriminator:
  `mlops/src/components/discriminator.py`
- Sử dụng trong training:
  `mlops/modeling/train.py`
  `mlops/src/models/pix2pixhd_module.py`

---

## 6. Tham khảo

- [Pix2PixHD Paper](https://arxiv.org/abs/1711.11585)
- [PatchGAN](https://phillipi.github.io/pix2pix/)
- [PyTorch nn.Module](https://pytorch.org/docs/stable/nn.html)

---
