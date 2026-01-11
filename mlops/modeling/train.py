import json
from pathlib import Path
from typing import Optional

import hydra
from hydra.utils import get_original_cwd
from loguru import logger
import mlflow
from omegaconf import DictConfig
import torch

from mlops.src.components.discriminator import define_D
from mlops.src.components.generator import define_G
from mlops.src.components.losses import GANLoss, VGGLoss
from mlops.src.components.replay_pool import ReplayPool
from mlops.src.models.pix2pixhd_module import Pix2PixHD, Pix2PixHDDataset


@hydra.main(config_path="../config", config_name="config", version_base=None)
def main(cfg: DictConfig):
    # ---- Dataset paths ----
    # Get project root - handle both running from root and from subdirectories
    original_cwd = Path(get_original_cwd())

    # Find project root by going up the directory tree
    # Project root should have both "data/" and "mlops/" directories
    current_path = original_cwd
    project_root = None

    # Go up max 5 levels to find project root
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
        if current_path == current_path.parent:  # Reached filesystem root
            break
        current_path = current_path.parent

    # Fallback: use original_cwd if not found
    if project_root is None:
        project_root = original_cwd
        logger.warning(
            f"Could not detect project root. Using: {project_root}\n"
            f"Please ensure you're running from project root or a subdirectory."
        )

    logger.info(f"Project root: {project_root}")
    logger.info(f"Original CWD: {original_cwd}")

    dataset_path = project_root / cfg.paths.raw
    feature_folder = str(project_root / cfg.dataset.processed_sketch_dir)
    label_folder = str(project_root / cfg.dataset.processed_image_dir)
    images_dir = str(project_root / "data/processed/")
    # ---- Model configuration ----
    checkpoint_dir: Path = project_root / "models" / "checkpoints"
    num_epochs: int = cfg.training.num_epochs
    batch_size: int = cfg.training.batch_size
    # ---- Generator config ----
    ngf = cfg.model.generator.ngf
    n_downsample_global: int = cfg.model.generator.n_downsampling
    n_blocks_global: int = cfg.model.generator.n_blocks
    n_local_enhancers: int = cfg.model.generator.get("n_local_enhancers", 1)
    n_blocks_local: int = cfg.model.generator.get("n_blocks_local", 3)
    # ---- Discriminator config ----
    ndf = cfg.model.discriminator_channels
    n_layers_D: int = cfg.model.discriminator.n_layers
    num_D: int = cfg.model.discriminator.num_D
    # ---- Training config ----
    learning_rate: float = cfg.training.learning_rate
    lambda_feat: float = cfg.training.lambda_feat
    replay_pool_size: int = cfg.training.replay_pool_size
    # ema_decay: float = cfg.training.ema_decay
    # ---- Data config ----
    img_size: int = cfg.dataset.image_size
    num_workers: int = cfg.dataset.num_workers
    # ---- Training control ----
    # test_interval: int = cfg.training.test_interval
    # save_interval: int = cfg.training.save_interval
    resume_from: Optional[Path] = cfg.training.resume_from

    """
    Train Pix2PixHD model for image-to-image translation.

    This training script initializes the generator and discriminator networks,
    sets up loss functions, and trains the model using the Pix2PixHD training pipeline.
    """

    # Setup logging
    logger.info("=" * 80)
    logger.info("Starting Pix2PixHD Training")
    logger.info("=" * 80)

    # Device selection
    device = torch.device(
        "mps"
        if torch.backends.mps.is_available()
        else "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )
    logger.info(f"Using device: {device}")

    try:
        # ---- Create dataset and dataloaders ----
        logger.info(f"Loading dataset from {dataset_path}")
        logger.info(f"Images directory: {images_dir}")
        logger.info(f"Feature folder: {feature_folder}")
        logger.info(f"Label folder: {label_folder}")

        # Validate paths exist
        images_dir_path = Path(images_dir)
        sketches_dir = images_dir_path / "sketches"
        images_dir_check = images_dir_path / "images"

        if not images_dir_path.exists():
            raise FileNotFoundError(
                f"Images directory does not exist: {images_dir_path}\n"
                f"Please ensure data is processed and available at this path."
            )
        if not sketches_dir.exists():
            raise FileNotFoundError(
                f"Sketches directory does not exist: {sketches_dir}\n"
                f"Please run data processing script first."
            )
        if not images_dir_check.exists():
            raise FileNotFoundError(
                f"Images directory does not exist: {images_dir_check}\n"
                f"Please run data processing script first."
            )

        # Check for image files
        sketch_files = list(sketches_dir.glob("*.jpg"))
        image_files = list(images_dir_check.glob("*.jpg"))

        logger.info(f"Found {len(sketch_files)} sketch files and {len(image_files)} image files")

        if len(sketch_files) == 0:
            raise ValueError(
                f"No .jpg files found in {sketches_dir}\n"
                f"Please ensure data processing has been completed."
            )
        if len(image_files) == 0:
            raise ValueError(
                f"No .jpg files found in {images_dir_check}\n"
                f"Please ensure data processing has been completed."
            )

        train_dataset = Pix2PixHDDataset(
            images_dir=images_dir,
            feature_fold="sketches/",
            label_fold="images/",
            img_size=img_size,
        )
        logger.info(f"Dataset size: {len(train_dataset)}")

        if len(train_dataset) == 0:
            raise ValueError(
                "Dataset is empty! Please check:\n"
                f"1. Data exists in {sketches_dir}\n"
                f"2. File naming matches between sketches and images\n"
                f"3. Files are .jpg format"
            )

        # Create train/test split
        if len(train_dataset) < 2:
            raise ValueError(
                f"Dataset too small ({len(train_dataset)} samples). Need at least 2 samples for train/test split."
            )

        train_size = int(0.8 * len(train_dataset))
        test_size = len(train_dataset) - train_size
        train_ds, test_ds = torch.utils.data.random_split(train_dataset, [train_size, test_size])

        train_loader = torch.utils.data.DataLoader(
            train_ds, batch_size=batch_size, num_workers=num_workers, shuffle=True, drop_last=True
        )
        test_loader = torch.utils.data.DataLoader(
            test_ds, batch_size=batch_size, num_workers=num_workers, shuffle=True
        )
        logger.info(f"Train size: {len(train_ds)}, Test size: {len(test_ds)}")

        # ---- Create generator networks ----
        logger.info("Initializing generator networks...")
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
        logger.success("Generator initialized")

        # ---- Create discriminator network ----
        logger.info("Initializing discriminator network...")
        discriminator = define_D(
            input_nc=6,  # 3 (input) + 3 (output)
            ndf=ndf,
            n_layers_D=n_layers_D,
            norm="instance",
            use_sigmoid=False,
            num_D=num_D,
            getIntermFeat=True,
            gpu_ids=[],
            num_outputs=1,
        ).to(device)
        logger.success("Discriminator initialized")

        # ---- Create loss functions ----
        logger.info("Initializing loss functions...")
        criterion_gan = GANLoss(use_lsgan=True).to(device)
        criterion_feat = torch.nn.L1Loss().to(device)
        criterion_vgg = VGGLoss().to(device)
        logger.success("Loss functions initialized")

        # ---- Create replay buffer ----
        logger.info(f"Initializing replay pool with size {replay_pool_size}...")
        replay_pool = ReplayPool(replay_pool_size)
        logger.success("Replay pool initialized")

        # ---- Initialize Pix2PixHD model ----
        logger.info("Initializing Pix2PixHD model...")
        model = Pix2PixHD(
            generator=generator,
            discriminator=discriminator,
            criterion_gan=criterion_gan,
            criterion_feat=criterion_feat,
            criterion_vgg=criterion_vgg,
            replay_pool=replay_pool,
            device=device,
            checkpoint_dir=str(checkpoint_dir),
            lambda_feat=lambda_feat,
        )
        logger.success("Pix2PixHD model initialized")

        # ---- Create optimizers ----
        logger.info(f"Creating optimizers with learning rate {learning_rate}...")
        g_optimizer = torch.optim.AdamW(generator.parameters(), lr=learning_rate)
        d_optimizer = torch.optim.AdamW(discriminator.parameters(), lr=learning_rate)
        logger.success("Optimizers created")

        # ---- Load checkpoint if resuming ----
        start_epoch = 0
        if resume_from is not None:
            logger.info(f"Resuming training from checkpoint: {resume_from}")
            model.load_checkpoint(str(resume_from))
            logger.success("Checkpoint loaded")

        # ---- Training loop ----
        # 1. Setup MLflow
        # Set MLflow tracking URI to project root
        mlruns_dir = project_root / "mlruns"
        mlruns_dir.mkdir(exist_ok=True)
        mlflow.set_tracking_uri(str(mlruns_dir))
        logger.info(f"MLflow tracking URI: {mlflow.get_tracking_uri()}")

        mlflow.set_experiment(cfg.experiment.name)
        logger.info(f"MLflow experiment: {cfg.experiment.name}")

        # 2. Setup WandB
        # wandb_config = OmegaConf.to_container(cfg, resolve=True, throw_on_missing=True)

        # # Khởi tạo run
        # run = wandb.init(
        #     entity=cfg.logger.wandb.entity,
        #     project=cfg.logger.wandb.project,
        #     group=cfg.logger.wandb.group,
        #     name=cfg.logger.wandb.name,
        #     config=wandb_config,
        #     job_type="training",
        # )  # type: ignore[attr-defined]

        # run_url = run.get_url()  # type: ignore[attr-defined]

        # logger.info("=" * 80)
        # logger.success(f"🚀 WANDB DASHBOARD IS LIVE AT: {run_url}")
        # logger.info("=" * 80)

        with mlflow.start_run():
            mlflow.log_param("num_epochs", num_epochs)
            mlflow.log_param("batch_size", batch_size)
            mlflow.log_param("learning_rate", learning_rate)
            mlflow.log_param("ngf", ngf)
            mlflow.log_param("ndf", ndf)
            logger.info("=" * 80)
            logger.info("Starting training loop")
            logger.info("=" * 80)

            for epoch in range(start_epoch, num_epochs):
                logger.info(f"\nEpoch {epoch + 1}/{num_epochs}")

                try:
                    model.train_epoch(
                        train_loader=train_loader,
                        test_loader=test_loader,
                        epoch=epoch,
                        g_optimizer=g_optimizer,
                        d_optimizer=d_optimizer,
                    )

                    # 1. Log for MLflow
                    for k, v in model.loss_log.items():
                        mlflow.log_metric(k, v / len(train_loader), step=epoch)

                    # 2. Log for WandB
                    # wandb_metrics = {k: v / len(train_loader) for k, v in model.loss_log.items()}
                    # wandb_metrics["epoch"] = epoch

                    # wandb.log(wandb_metrics)  # type: ignore[attr-defined]

                except Exception as e:
                    logger.error(f"Error during epoch {epoch + 1}: {str(e)}")
                    # wandb.finish()  # type: ignore[attr-defined]
                    raise

            logger.info("=" * 80)
            logger.success("Training completed successfully!")
            logger.info(f"Checkpoints saved to: {checkpoint_dir}")
            logger.info("=" * 80)

            # Save metrics
            metrics = {
                "final_g_loss": float(model.loss_log.get("G_adv", 0)),
                "final_d_loss": float(model.loss_log.get("D_true", 0)),
            }
            metrics_path = project_root / "reports" / "metrics.json"
            metrics_path.parent.mkdir(parents=True, exist_ok=True)
            with open(metrics_path, "w") as f:
                json.dump(metrics, f)

            # End Wandb run
            # wandb.finish()  # type: ignore[attr-defined]

    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
