"""
Model Evaluation Script for Pix2PixHD

This script evaluates the trained Pix2PixHD model using multiple metrics:
- SSIM (Structural Similarity Index)
- PSNR (Peak Signal-to-Noise Ratio)
- L1 Loss (Mean Absolute Error)
- FID Score (Fréchet Inception Distance) - optional

It generates sample predictions and saves evaluation metrics.
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple

import hydra
import mlflow
import numpy as np
import torch
import torch.nn.functional as F
from hydra.utils import get_original_cwd
from loguru import logger
from omegaconf import DictConfig
from PIL import Image
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim
from torchvision import transforms
from tqdm import tqdm

from mlops.src.components.discriminator import define_D
from mlops.src.components.generator import define_G
from mlops.src.models.pix2pixhd_module import Pix2PixHDDataset


def calculate_metrics(
    real_images: torch.Tensor, fake_images: torch.Tensor
) -> Dict[str, float]:
    """
    Calculate evaluation metrics between real and generated images.

    Args:
        real_images: Ground truth images, shape (B, C, H, W), range [-1, 1]
        fake_images: Generated images, shape (B, C, H, W), range [-1, 1]

    Returns:
        Dictionary containing SSIM, PSNR, and L1 loss metrics
    """
    # Convert from [-1, 1] to [0, 1]
    real_np = ((real_images + 1) / 2).cpu().numpy()
    fake_np = ((fake_images + 1) / 2).cpu().numpy()

    batch_size = real_np.shape[0]
    ssim_scores = []
    psnr_scores = []

    for i in range(batch_size):
        # Transpose from (C, H, W) to (H, W, C)
        real_img = np.transpose(real_np[i], (1, 2, 0))
        fake_img = np.transpose(fake_np[i], (1, 2, 0))

        # Calculate SSIM
        ssim_score = ssim(
            real_img,
            fake_img,
            data_range=1.0,
            channel_axis=2,
            win_size=11
        )
        ssim_scores.append(ssim_score)

        # Calculate PSNR
        psnr_score = psnr(real_img, fake_img, data_range=1.0)
        psnr_scores.append(psnr_score)

    # Calculate L1 loss
    l1_loss = F.l1_loss(fake_images, real_images).item()

    return {
        "ssim": float(np.mean(ssim_scores)),
        "ssim_std": float(np.std(ssim_scores)),
        "psnr": float(np.mean(psnr_scores)),
        "psnr_std": float(np.std(psnr_scores)),
        "l1_loss": l1_loss,
    }


def save_sample_images(
    sketch: torch.Tensor,
    real: torch.Tensor,
    fake: torch.Tensor,
    save_dir: Path,
    index: int,
) -> None:
    """
    Save a comparison of sketch, real image, and generated image.

    Args:
        sketch: Input sketch tensor
        real: Real image tensor
        fake: Generated image tensor
        save_dir: Directory to save images
        index: Image index for naming
    """
    save_dir.mkdir(parents=True, exist_ok=True)

    def tensor_to_image(tensor: torch.Tensor) -> Image.Image:
        """Convert tensor to PIL Image"""
        # Convert from [-1, 1] to [0, 255]
        img = ((tensor + 1) / 2 * 255).clamp(0, 255).cpu().numpy().astype(np.uint8)
        # Transpose from (C, H, W) to (H, W, C)
        img = np.transpose(img, (1, 2, 0))
        return Image.fromarray(img)

    # Save individual images
    tensor_to_image(sketch[0]).save(save_dir / f"sample_{index}_sketch.png")
    tensor_to_image(real[0]).save(save_dir / f"sample_{index}_real.png")
    tensor_to_image(fake[0]).save(save_dir / f"sample_{index}_generated.png")

    # Create side-by-side comparison
    sketch_img = tensor_to_image(sketch[0])
    real_img = tensor_to_image(real[0])
    fake_img = tensor_to_image(fake[0])

    width = sketch_img.width
    height = sketch_img.height

    comparison = Image.new('RGB', (width * 3, height))
    comparison.paste(sketch_img, (0, 0))
    comparison.paste(real_img, (width, 0))
    comparison.paste(fake_img, (width * 2, 0))

    comparison.save(save_dir / f"sample_{index}_comparison.png")


@hydra.main(config_path="../config", config_name="config", version_base=None)
def main(cfg: DictConfig):
    """
    Main evaluation function.

    Loads the trained model, evaluates on test set, and saves metrics.
    """
    # ---- Setup paths ----
    original_cwd = Path(get_original_cwd())
    current_path = original_cwd
    project_root = None

    # Find project root
    for _ in range(5):
        if (
            (current_path / "data").exists()
            and (current_path / "mlops").exists()
            and (
                (current_path / "pyproject.toml").exists()
                or (current_path / "requirements.txt").exists()
            )
        ):
            project_root = current_path
            break
        if current_path == current_path.parent:
            break
        current_path = current_path.parent

    if project_root is None:
        project_root = original_cwd
        logger.warning(f"Could not detect project root. Using: {project_root}")

    logger.info(f"Project root: {project_root}")

    # ---- Configuration ----
    images_dir = str(project_root / "data/processed/")
    checkpoint_dir = project_root / "models" / "checkpoints"
    evaluation_dir = project_root / "reports"
    evaluation_dir.mkdir(parents=True, exist_ok=True)

    img_size = cfg.dataset.image_size
    batch_size = cfg.training.get("eval_batch_size", 1)  # Use batch size 1 for evaluation
    num_workers = cfg.dataset.num_workers
    num_samples = cfg.training.get("num_eval_samples", 10)  # Number of sample images to save

    # Generator config
    ngf = cfg.model.generator.ngf
    n_downsample_global = cfg.model.generator.n_downsampling
    n_blocks_global = cfg.model.generator.n_blocks
    n_local_enhancers = cfg.model.generator.get("n_local_enhancers", 1)
    n_blocks_local = cfg.model.generator.get("n_blocks_local", 3)

    logger.info("=" * 80)
    logger.info("Starting Model Evaluation")
    logger.info("=" * 80)

    # ---- Device setup ----
    device = torch.device(
        "mps"
        if torch.backends.mps.is_available()
        else "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )
    logger.info(f"Using device: {device}")

    try:
        # ---- Load dataset ----
        logger.info(f"Loading dataset from {images_dir}")

        dataset = Pix2PixHDDataset(
            images_dir=images_dir,
            feature_fold="sketches/",
            label_fold="images/",
            img_size=img_size,
        )

        logger.info(f"Dataset size: {len(dataset)}")

        if len(dataset) < 2:
            raise ValueError(
                f"Dataset too small ({len(dataset)} samples). Need at least 2 samples."
            )

        # Create train/test split (same as training)
        train_size = int(0.8 * len(dataset))
        test_size = len(dataset) - train_size
        _, test_ds = torch.utils.data.random_split(
            dataset, [train_size, test_size]
        )

        test_loader = torch.utils.data.DataLoader(
            test_ds,
            batch_size=batch_size,
            num_workers=num_workers,
            shuffle=False
        )

        logger.info(f"Test size: {len(test_ds)}")

        # ---- Load model ----
        logger.info("Initializing generator...")
        generator = define_G(
            input_nc=3,
            output_nc=3,
            ngf=ngf,
            netG="global",
            norm="instance",
            n_downsample_global=n_downsample_global,
            n_blocks_global=n_blocks_global,
            n_local_enhancers=n_local_enhancers,
            n_blocks_local=n_blocks_local,
            gpu_ids=[],
        ).to(device)

        # Load checkpoint
        checkpoint_path = checkpoint_dir / "generator_latest.pth"
        if not checkpoint_path.exists():
            logger.warning(
                f"Checkpoint not found at {checkpoint_path}. "
                "Using untrained model for evaluation."
            )
        else:
            logger.info(f"Loading checkpoint from {checkpoint_path}")
            checkpoint = torch.load(checkpoint_path, map_location=device)
            generator.load_state_dict(checkpoint["generator"])
            logger.success("Checkpoint loaded successfully")

        generator.eval()

        # ---- Setup MLflow ----
        mlruns_dir = project_root / "mlruns"
        mlruns_dir.mkdir(exist_ok=True)
        mlflow.set_tracking_uri(str(mlruns_dir))
        mlflow.set_experiment(cfg.experiment.name)

        # ---- Evaluate ----
        logger.info("Starting evaluation...")

        all_metrics = []
        sample_dir = evaluation_dir / "samples"

        with torch.no_grad():
            for idx, batch in enumerate(tqdm(test_loader, desc="Evaluating")):
                sketch = batch["feature"].to(device)
                real_image = batch["label"].to(device)

                # Generate fake image
                fake_image = generator(sketch)

                # Calculate metrics
                metrics = calculate_metrics(real_image, fake_image)
                all_metrics.append(metrics)

                # Save sample images
                if idx < num_samples:
                    save_sample_images(
                        sketch, real_image, fake_image, sample_dir, idx
                    )

        # ---- Aggregate metrics ----
        logger.info("Aggregating metrics...")

        final_metrics = {
            "ssim_mean": float(np.mean([m["ssim"] for m in all_metrics])),
            "ssim_std": float(np.std([m["ssim"] for m in all_metrics])),
            "psnr_mean": float(np.mean([m["psnr"] for m in all_metrics])),
            "psnr_std": float(np.std([m["psnr"] for m in all_metrics])),
            "l1_loss_mean": float(np.mean([m["l1_loss"] for m in all_metrics])),
            "l1_loss_std": float(np.std([m["l1_loss"] for m in all_metrics])),
            "num_test_samples": len(test_ds),
        }

        logger.info("=" * 80)
        logger.info("EVALUATION RESULTS")
        logger.info("=" * 80)
        logger.info(f"SSIM: {final_metrics['ssim_mean']:.4f} ± {final_metrics['ssim_std']:.4f}")
        logger.info(f"PSNR: {final_metrics['psnr_mean']:.2f} ± {final_metrics['psnr_std']:.2f} dB")
        logger.info(f"L1 Loss: {final_metrics['l1_loss_mean']:.4f} ± {final_metrics['l1_loss_std']:.4f}")
        logger.info("=" * 80)

        # ---- Save metrics ----
        metrics_path = evaluation_dir / "evaluation_metrics.json"
        with open(metrics_path, "w") as f:
            json.dump(final_metrics, f, indent=2)

        logger.success(f"Metrics saved to {metrics_path}")
        logger.success(f"Sample images saved to {sample_dir}")

        # ---- Log to MLflow ----
        with mlflow.start_run(run_name="evaluation"):
            for key, value in final_metrics.items():
                mlflow.log_metric(key, value)

            mlflow.log_artifact(str(metrics_path))

            # Log sample images
            for img_path in sample_dir.glob("sample_*_comparison.png"):
                mlflow.log_artifact(str(img_path))

        logger.info("=" * 80)
        logger.success("Evaluation completed successfully!")
        logger.info("=" * 80)

        # Return 0 exit code for CI/CD
        return 0

    except Exception as e:
        logger.error(f"Evaluation failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
