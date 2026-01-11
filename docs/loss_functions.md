# Loss Functions

## Tổng quan

Pix2PixHD sử dụng nhiều hàm loss khác nhau để tối ưu hóa chất lượng ảnh sinh ra. Việc kết hợp các loss này giúp mô hình không chỉ sinh ra ảnh giống thật về mặt tổng thể mà còn giữ được các chi tiết và đặc trưng quan trọng.

---

## 1. GAN Loss (Adversarial Loss)

- **Mục đích:**
  Giúp generator sinh ra ảnh mà discriminator không thể phân biệt được với ảnh thật.
- **Cách dùng:**
  Dự án sử dụng **Least Squares GAN (LSGAN)** thay vì Binary Cross Entropy truyền thống để ổn định quá trình huấn luyện.
- **Công thức:**
  - Discriminator:
    ![D_loss = 0.5 * E[(D(x) - 1)^2] + 0.5 * E[(D(G(z)))^2]]
  - Generator:
    ![G_loss = 0.5 * E[(D(G(z)) - 1)^2]]

---

## 2. Feature Matching Loss

- **Mục đích:**
  Giúp generator sinh ra ảnh có đặc trưng trung gian (intermediate features) giống với ảnh thật, không chỉ đánh lừa discriminator ở output cuối.
- **Cách dùng:**
  So sánh các đặc trưng trích xuất từ các tầng của discriminator giữa ảnh thật và ảnh sinh ra.
- **Công thức:**
  ![L_FM(G, D) = E_{x, y} \sum_{i=1}^T \frac{1}{N_i} \| D^{(i)}(x, y) - D^{(i)}(x, G(x)) \|_1]
  - Với \( D^{(i)} \) là output của tầng thứ i trong discriminator.

---

## 3. VGG Perceptual Loss

- **Mục đích:**
  Đảm bảo ảnh sinh ra giống ảnh thật về mặt đặc trưng thị giác (perceptual features).
- **Cách dùng:**
  So sánh đặc trưng trích xuất từ mạng VGG19 pretrained giữa ảnh thật và ảnh sinh ra.
- **Công thức:**
  ![L_{VGG}(G) = \| \phi(y) - \phi(G(x)) \|_1]
  - Với \( \phi \) là feature map của VGG19.

---

## 4. Tổng hợp loss trong training

Loss tổng của generator:
```
L_G = L_GAN + λ_feat * L_FM + λ_vgg * L_VGG
```
- Trong đó:
  - `L_GAN`: GAN loss
  - `L_FM`: Feature matching loss
  - `L_VGG`: VGG perceptual loss
  - `λ_feat`, `λ_vgg`: Hệ số điều chỉnh (cấu hình trong file config)

Loss tổng của discriminator:
```
L_D = LSGAN loss
```

---

## 5. Mã nguồn liên quan

- Định nghĩa loss:
  `mlops/src/components/losses.py`
- Sử dụng trong training:
  `mlops/modeling/train.py`
  `mlops/src/models/pix2pixhd_module.py`

---

## 6. Tham khảo

- [Pix2PixHD Paper](https://arxiv.org/abs/1711.11585)
- [LSGAN Paper](https://arxiv.org/abs/1611.04076)
- [Perceptual Losses for Real-Time Style Transfer and Super-Resolution](https://arxiv.org/abs/1603.08155)
- [PyTorch Loss Functions](https://pytorch.org/docs/stable/nn.html#loss-functions)

---
