import io

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from PIL import Image
import torch
import torchvision.transforms as T

from mlops.src.components.generator import define_G

app = FastAPI(
    title="Pix2PixHD Inference API",
    description="REST API for Pix2PixHD image-to-image translation",
    version="1.0.0",
)

# Load generator khi khởi động server
CHECKPOINT_PATH = "models/checkpoints/.pth"  # Đổi path cho đúng checkpoint của bạn
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Khởi tạo generator đúng với config đã train
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
generator.load_state_dict(torch.load(CHECKPOINT_PATH, map_location=DEVICE))
generator.to(DEVICE)
generator.eval()


def preprocess_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    transform = T.Compose([T.Resize((256, 256)), T.ToTensor(), T.Normalize([0.5] * 3, [0.5] * 3)])
    return transform(image).unsqueeze(0).to(DEVICE)


def postprocess_tensor(tensor):
    tensor = tensor.squeeze(0).detach().cpu()
    tensor = (tensor * 0.5 + 0.5).clamp(0, 1)
    image = T.ToPILImage()(tensor)
    return image


@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    image_bytes = await file.read()
    input_tensor = preprocess_image(image_bytes)
    with torch.no_grad():
        output_tensor = generator(input_tensor)
    output_image = postprocess_tensor(output_tensor)
    buf = io.BytesIO()
    output_image.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
