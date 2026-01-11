# Checkpointing

## Tổng quan

Checkpointing là quá trình lưu trạng thái của model (weights, optimizer states, epoch, v.v.) trong quá trình training. Điều này cho phép:

- ✅ Resume training từ một điểm đã lưu
- ✅ Lưu model tốt nhất (best model)
- ✅ Phục hồi khi training bị gián đoạn
- ✅ Deploy model từ checkpoint

---

## 1. Checkpoint Structure

### File format

Checkpoints được lưu dưới dạng `.pt` (PyTorch format) chứa:

- **Generator weights**: State dict của generator
- **Discriminator weights**: State dict của discriminator
- **EMA Generator**: Exponential Moving Average của generator (nếu có)

### Ví dụ checkpoint

```python
{
    "G": generator.state_dict(),      # Generator weights
    "D": discriminator.state_dict(),  # Discriminator weights
    # Optional:
    "epoch": epoch_number,
    "loss": loss_value,
    "optimizer_g": optimizer_g.state_dict(),
    "optimizer_d": optimizer_d.state_dict(),
}
```

---

## 2. Checkpoint Directory

### Cấu trúc thư mục

Theo mặc định, checkpoints được lưu tại:

```
models/
└── checkpoints/
    ├── epoch_0_2024-01-01-12-00.pt
    ├── epoch_5_2024-01-01-12-30.pt
    ├── epoch_10_2024-01-01-13-00.pt
    └── ...
```

### Cấu hình đường dẫn

Trong `mlops/config/paths.yaml`:

```yaml
paths:
  checkpoints: models/checkpoints
```

Hoặc trong `mlops/config/config.yaml`:

```yaml
checkpoint_dir: models/checkpoints
```

---

## 3. Saving Checkpoints

### Tự động lưu trong training

Trong `train.py`, checkpoints được lưu tự động:

```python
# Save checkpoint every N epochs
if epoch % save_every == 0:
    model.save_checkpoint(epoch)
```

### Manual save

```python
from mlops.src.models.pix2pixhd_module import Pix2PixHD

model = Pix2PixHD(...)

# Save checkpoint
model.save_checkpoint(epoch=10)
```

### Checkpoint naming

Checkpoint được đặt tên theo format:

```
epoch_{epoch_number}_{timestamp}.pt
```

Ví dụ: `epoch_50_2024-01-01-12-00-30.pt`

---

## 4. Loading Checkpoints

### Resume training

Trong `train.py`:

```python
# Resume from checkpoint
if resume_from is not None:
    model.load_checkpoint(str(resume_from))
    start_epoch = extract_epoch(resume_from)
```

### Command line

```bash
python mlops/modeling/train.py \
    training.resume_from=models/checkpoints/epoch_50_2024-01-01-12-00.pt
```

### Programmatic load

```python
from mlops.src.models.pix2pixhd_module import Pix2PixHD

model = Pix2PixHD(...)

# Load checkpoint
model.load_checkpoint("models/checkpoints/epoch_50_2024-01-01-12-00.pt")
```

---

## 5. Best Model Saving

### Strategy

Có thể lưu best model dựa trên:

- **Lowest validation loss**: Model có validation loss thấp nhất
- **Highest metric**: Model có metric cao nhất (ví dụ: FID, SSIM)

### Implementation

```python
best_val_loss = float('inf')
best_model_path = None

for epoch in range(num_epochs):
    # Training...
    val_loss = validate(model, val_loader)

    if val_loss < best_val_loss:
        best_val_loss = val_loss
        best_model_path = f"models/checkpoints/best_epoch_{epoch}.pt"
        torch.save({
            "G": model.generator_ema.state_dict(),
            "D": model.discriminator.state_dict(),
            "epoch": epoch,
            "val_loss": val_loss
        }, best_model_path)
```

---

## 6. Checkpoint Configuration

### Training config

Trong `mlops/config/training.yaml`:

```yaml
training:
  save_every: 5              # Save checkpoint every N epochs
  resume_from: null          # Path to checkpoint to resume from

  checkpoint:
    monitor: "val/loss"      # Metric to monitor
    mode: "min"              # "min" or "max"
    save_top_k: 3            # Save top K checkpoints
    save_last: true          # Always save last checkpoint
```

---

## 7. Loading for Inference

### Load generator only

Cho inference, thường chỉ cần generator:

```python
import torch
from mlops.src.components.generator import define_G

# Initialize generator
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

# Load checkpoint
checkpoint = torch.load("models/checkpoints/epoch_50_2024-01-01-12-00.pt")
generator.load_state_dict(checkpoint["G"])
generator.eval()
```

### Load with device mapping

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
checkpoint = torch.load(
    "models/checkpoints/epoch_50_2024-01-01-12-00.pt",
    map_location=device
)
generator.load_state_dict(checkpoint["G"])
generator.to(device)
```

---

## 8. Checkpoint Management

### List checkpoints

```bash
# List all checkpoints
ls -lh models/checkpoints/

# List checkpoints by epoch
ls -lh models/checkpoints/ | grep "epoch_"
```

### Cleanup old checkpoints

```bash
# Keep only last 5 checkpoints
ls -t models/checkpoints/*.pt | tail -n +6 | xargs rm

# Or keep only best and last
rm models/checkpoints/epoch_*.pt
# Keep only: best_model.pt, last_model.pt
```

### Checkpoint size

```bash
# Check checkpoint size
du -sh models/checkpoints/*.pt

# Typically: 100-500MB per checkpoint
```

---

## 9. Best Practices

### ✅ Nên làm

- Lưu checkpoint thường xuyên (mỗi 5-10 epochs)
- Lưu best model dựa trên validation metric
- Lưu cả generator và discriminator (cho GAN)
- Sử dụng timestamp trong tên file để dễ quản lý
- Cleanup checkpoints cũ để tiết kiệm disk space

### ❌ Không nên

- Không lưu checkpoint quá thường xuyên (tốn disk)
- Không chỉ lưu generator (cần cả discriminator để resume)
- Không quên lưu optimizer states nếu cần resume chính xác
- Không commit checkpoints lên git (quá lớn)

---

## 10. Troubleshooting

### Lỗi: "KeyError: 'G'"

Checkpoint không có key 'G':

```python
# Check checkpoint keys
checkpoint = torch.load("path/to/checkpoint.pt")
print(checkpoint.keys())

# Fix: Load with correct key
generator.load_state_dict(checkpoint["generator"])  # Not "G"
```

### Lỗi: "RuntimeError: Error(s) in loading state_dict"

Shape mismatch giữa model và checkpoint:

```python
# Check model architecture matches checkpoint
print(generator.state_dict().keys())
print(checkpoint["G"].keys())
```

### Lỗi: Out of memory khi load

```python
# Load to CPU first
checkpoint = torch.load(
    "path/to/checkpoint.pt",
    map_location="cpu"
)
# Then move to GPU
model.load_state_dict(checkpoint["G"])
model.to(device)
```

---

## 11. Tham khảo

- [Training](training.md) - Training script và workflow
- [PyTorch Saving & Loading](https://pytorch.org/tutorials/beginner/saving_loading_models.html)
- [Model Architecture](model_architecture.md) - Model structure
