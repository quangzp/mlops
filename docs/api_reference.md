# API Reference

## 1. FastAPI Endpoints

### `POST /predict/`

- **Mô tả:**
  Nhận một ảnh đầu vào (sketch hoặc label map), trả về ảnh đã được mô hình Pix2PixHD chuyển đổi.
- **Input:**
  - `file`: Ảnh (PNG/JPG) gửi dưới dạng form-data.
- **Output:**
  - Ảnh kết quả (PNG) trả về trực tiếp.
- **Ví dụ sử dụng với `curl`:**
  ```bash
  curl -X POST "http://localhost:8000/predict/" -F "file=@path/to/your/image.png" --output result.png
  ```
- **Thử trực tiếp:**
  Truy cập [http://localhost:8000/docs](http://localhost:8000/docs) để upload ảnh và nhận kết quả.

---

## 2. Các class và hàm chính

### `define_G`

- **Mô tả:**
  Hàm khởi tạo generator cho Pix2PixHD.
- **Tham số:**
  - `input_nc`: Số kênh đầu vào (thường là 3).
  - `output_nc`: Số kênh đầu ra (thường là 3).
  - `ngf`: Số lượng filter ở tầng đầu tiên.
  - `netG`: Loại generator ("global", ...).
  - `norm`: Loại normalization ("instance", ...).
  - `n_downsample_global`, `n_blocks_global`, `n_local_enhancers`, `n_blocks_local`, `gpu_ids`: Các tham số cấu hình khác.
- **Trả về:**
  - Một mô hình generator (PyTorch `nn.Module`).

---

### `Pix2PixHDDataset`

- **Mô tả:**
  Custom Dataset class cho PyTorch, dùng để load cặp ảnh (sketch, ground-truth).
- **Tham số khởi tạo:**
  - `images_dir`: Thư mục chứa dữ liệu.
  - `feature_fold`: Thư mục chứa ảnh đầu vào (sketch).
  - `label_fold`: Thư mục chứa ground-truth.
  - `img_size`: Kích thước ảnh.
- **Sử dụng:**
  ```python
  dataset = Pix2PixHDDataset(
      images_dir="data/processed/",
      feature_fold="sketches/",
      label_fold="images/",
      img_size=256,
  )
  ```

---

### `Pix2PixHD`

- **Mô tả:**
  Class quản lý toàn bộ pipeline huấn luyện Pix2PixHD (generator, discriminator, loss, checkpoint...).
- **Tham số khởi tạo:**
  - `generator`, `discriminator`, `criterion_gan`, `criterion_feat`, `criterion_vgg`, `replay_pool`, `device`, `checkpoint_dir`, `lambda_feat`, ...
- **Các phương thức chính:**
  - `train_epoch(...)`: Huấn luyện 1 epoch.
  - `load_checkpoint(path)`: Load checkpoint model.
  - `save_checkpoint(path)`: Lưu checkpoint model.

---

## 3. Hàm tiện ích trong serving

### `preprocess_image(image_bytes)`

- **Mô tả:**
  Chuyển ảnh bytes thành tensor đã chuẩn hóa, phù hợp với input của generator.
- **Input:**
  - `image_bytes`: Dữ liệu ảnh dạng bytes.
- **Output:**
  - Tensor PyTorch shape `[1, 3, H, W]`.

### `postprocess_tensor(tensor)`

- **Mô tả:**
  Chuyển tensor output của generator về ảnh PIL.
- **Input:**
  - Tensor PyTorch shape `[1, 3, H, W]` hoặc `[3, H, W]`.
- **Output:**
  - Ảnh PIL.

---

## 4. Tham khảo thêm

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PyTorch Documentation](https://pytorch.org/docs/stable/index.html)
- [Dự án Pix2PixHD gốc](https://github.com/NVIDIA/pix2pixHD)

---

> **Tip:**
> Đọc kỹ phần này để hiểu rõ cách sử dụng các thành phần chính của dự án, đặc biệt khi muốn mở rộng hoặc tích hợp vào hệ thống khác.
