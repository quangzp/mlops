# Generator

## Tổng quan

Generator trong Pix2PixHD là thành phần tạo ra ảnh mới từ ảnh đầu vào (ví dụ: từ sketch sang ảnh thật). Generator của Pix2PixHD có kiến trúc phức tạp hơn Pix2Pix truyền thống, sử dụng nhiều tầng ResNet và hỗ trợ multi-scale để sinh ảnh chất lượng cao, giàu chi tiết.

---

## 1. Kiến trúc tổng thể

- **Global Generator**: Xử lý toàn bộ ảnh, gồm nhiều tầng convolution, normalization, activation và các block ResNet.
- **Local Enhancer (tuỳ chọn)**: Tăng cường chi tiết cho ảnh ở các vùng nhỏ, giúp ảnh đầu ra sắc nét hơn.
- **Downsampling**: Giảm kích thước ảnh qua các tầng convolution stride 2.
- **ResNet Blocks**: Giữ nguyên thông tin và giúp mô hình học được các đặc trưng phức tạp.
- **Upsampling**: Dùng ConvTranspose2d để tăng kích thước ảnh về lại kích thước gốc.

### Sơ đồ tổng quát

```
Input (sketch)
   │
[Downsampling]
   │
[ResNet Blocks]
   │
[Upsampling]
   │
Output (generated image)
```

---

## 2. Cấu hình trong dự án

Các tham số cấu hình chính:
- `input_nc`: Số kênh đầu vào (thường là 3, ví dụ ảnh RGB).
- `output_nc`: Số kênh đầu ra (thường là 3).
- `ngf`: Số lượng filter ở tầng đầu tiên.
- `n_downsample_global`: Số tầng downsampling.
- `n_blocks_global`: Số block ResNet ở global generator.
- `n_local_enhancers`: Số local enhancer (nếu dùng).
- `n_blocks_local`: Số block ResNet ở local enhancer.

Ví dụ khởi tạo trong code:
```python
generator = define_G(
    input_nc=3,
    output_nc=3,
    ngf=64,
    netG="global",
    norm="instance",
    n_downsample_global=4,
    n_blocks_global=9,
    n_local_enhancers=1,
    n_blocks_local=3,
    gpu_ids=[],
)
```

---

## 3. Vai trò trong huấn luyện

- Nhận ảnh sketch (hoặc ảnh đầu vào) và sinh ra ảnh giả (fake image).
- Cố gắng đánh lừa discriminator để ảnh sinh ra càng giống ảnh thật càng tốt.
- Được tối ưu qua các loss: GAN loss, Feature loss, VGG perceptual loss.

---

## 4. Loss Function liên quan

- **GAN Loss**: Khiến ảnh sinh ra giống ảnh thật.
- **Feature Loss**: So sánh đặc trưng trích xuất từ discriminator.
- **VGG Loss**: So sánh đặc trưng trích xuất từ mạng VGG19 pretrained.

---

## 5. Mã nguồn liên quan

- Định nghĩa generator:
  `mlops/src/components/generator.py`
- Sử dụng trong training:
  `mlops/modeling/train.py`
  `mlops/src/models/pix2pixhd_module.py`

---

## 6. Tham khảo

- [Pix2PixHD Paper](https://arxiv.org/abs/1711.11585)
- [ResNet](https://arxiv.org/abs/1512.03385)
- [PyTorch nn.Module](https://pytorch.org/docs/stable/nn.html)

---
