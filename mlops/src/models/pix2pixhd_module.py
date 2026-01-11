import datetime
from glob import glob
import os
from random import random
from typing import Optional

import cv2
import numpy as np
import pytorch_lightning as pl
import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import transforms
from tqdm import tqdm


class Pix2PixHDDataset(torch.utils.data.Dataset):
    """Dataset class for Pix2PixHD training with flexible folder structure."""

    def __init__(self, images_dir: str, feature_fold: str, label_fold: str, img_size: int = 256):
        """
        Initialize dataset.

        Args:
            images_dir: Root directory containing images
            feature_fold: Subfolder for input images (e.g., '/sketches/')
            label_fold: Subfolder for target images (e.g., '/photos/')
            img_size: Size to resize images to
        """
        self.to_tensor = transforms.Compose(
            [transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
        )
        self.imagesDir = images_dir
        self.feature_fold = feature_fold
        self.label_fold = label_fold
        self.img_size = img_size

        # Build search path
        search_path = os.path.join(images_dir, feature_fold, "*.jpg")
        # Also try without trailing slash
        if not os.path.exists(os.path.dirname(search_path)):
            search_path_alt = os.path.join(images_dir, feature_fold.rstrip("/"), "*.jpg")
            if os.path.exists(os.path.dirname(search_path_alt)):
                search_path = search_path_alt

        self.images = glob(search_path)

        # Debug logging
        if len(self.images) == 0:
            print(f"WARNING: No images found at: {search_path}")
            print(f"Images dir exists: {os.path.exists(images_dir)}")
            if os.path.exists(images_dir):
                print(f"Contents of {images_dir}: {os.listdir(images_dir)}")
            feature_dir = os.path.join(images_dir, feature_fold)
            print(f"Feature dir exists: {os.path.exists(feature_dir)}")
            if os.path.exists(feature_dir):
                print(f"Contents of {feature_dir}: {os.listdir(feature_dir)[:10]}")
        else:
            print(f"Found {len(self.images)} images in {search_path}")

    def __getitem__(self, idx):
        f_name = self.images[idx]

        # Load source image
        src = cv2.imread(f_name, 1)
        src = cv2.cvtColor(src, cv2.COLOR_BGR2RGB)

        # Load target image
        dst_f_name = (
            f_name.replace(self.feature_fold, self.label_fold)
            .replace("F2-", "f-")
            .replace("-sz1", "")
            .replace("M2-", "m-")
        )
        dst = cv2.imread(dst_f_name, 1)
        dst = cv2.cvtColor(dst, cv2.COLOR_BGR2RGB)

        # Resize images
        src = cv2.resize(src, (self.img_size, self.img_size))
        dst = cv2.resize(dst, (self.img_size, self.img_size))

        # Random horizontal flip
        if random() < 0.5:
            src = np.fliplr(src)
            dst = np.fliplr(dst)

        src_tensor = self.to_tensor(src.copy())
        dst_tensor = self.to_tensor(dst.copy())
        return src_tensor, dst_tensor

    def __len__(self):
        return len(self.images)


class Pix2PixHD(pl.LightningModule):
    """Pix2PixHD model implementation with full training pipeline."""

    def __init__(
        self,
        generator: nn.Module,
        discriminator: nn.Module,
        criterion_gan: nn.Module,
        criterion_feat: nn.Module,
        criterion_vgg: nn.Module,
        replay_pool,
        device: Optional[torch.device] = None,
        checkpoint_dir: str = "./checkpoints/",
        lambda_feat: float = 10.0,
    ):
        """
        Initialize Pix2PixHD model.

        Args:
            generator: Generator network
            discriminator: Discriminator network
            criterion_gan: GAN loss function
            criterion_feat: Feature matching loss
            criterion_vgg: VGG perceptual loss
            replay_pool: Replay buffer for fake samples
            device: Device to run on
            checkpoint_dir: Directory to save checkpoints
            lambda_feat: Weight for feature matching loss
        """
        super().__init__()

        self.generator = generator
        self.discriminator = discriminator
        self.criterion_gan = criterion_gan
        self.criterion_feat = criterion_feat
        self.criterion_vgg = criterion_vgg
        self.replay_pool = replay_pool
        self.device_to_use = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.checkpoint_dir = checkpoint_dir
        self.lambda_feat = lambda_feat

        # Create EMA generator
        self.generator_ema = self._create_ema_generator()

        # Loss tracking
        self.loss_log: dict[str, float] = {}

    def _create_ema_generator(self):
        """Create exponential moving average copy of generator."""
        import copy

        ema_gen = copy.deepcopy(self.generator)
        with torch.no_grad():
            for ema_p, gen_p in zip(ema_gen.parameters(), self.generator.parameters()):
                ema_p.data = gen_p.data.detach()
        return ema_gen

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through generator."""
        return self.generator(x)

    def configure_optimizers(self):
        """Configure optimizers for generator and discriminator."""
        g_optimizer = torch.optim.AdamW(self.generator.parameters(), lr=1e-4)
        d_optimizer = torch.optim.AdamW(self.discriminator.parameters(), lr=1e-4)
        return [g_optimizer, d_optimizer]

    def process_loss(self, losses: dict[str, torch.Tensor]) -> torch.Tensor:
        """
        Process and accumulate losses.

        Args:
            losses: Dictionary of loss components

        Returns:
            Total loss
        """
        loss = 0
        for k, v in losses.items():
            if k not in self.loss_log:
                self.loss_log[k] = 0
            self.loss_log[k] += v.item()
            loss = loss + v
        return loss

    def calc_G_losses(self, data: torch.Tensor, target: torch.Tensor) -> dict[str, torch.Tensor]:
        """
        Calculate generator losses.

        Args:
            data: Input images
            target: Target images

        Returns:
            Dictionary of loss components
        """
        fake = self.generator(data)
        loss_vgg = 1 * self.criterion_vgg(fake, target)

        pred_fake = self.discriminator(torch.cat([data, fake], axis=1))
        loss_adv = 1 * self.criterion_gan(pred_fake, 1)

        with torch.no_grad():
            pred_true = self.discriminator(torch.cat([data, target], axis=1))

        # Feature matching loss
        device = pred_fake[0][0].device if isinstance(pred_fake[0], list) else pred_fake[0].device
        loss_adv_feat = torch.tensor(0.0, device=device)
        adv_feats_count = 0
        for d_fake_out, d_true_out in zip(pred_fake, pred_true):
            for l_fake, l_true in zip(d_fake_out[:-1], d_true_out[:-1]):
                loss_adv_feat = loss_adv_feat + self.criterion_feat(l_fake, l_true)
                adv_feats_count += 1
        if adv_feats_count > 0:
            loss_adv_feat = 1 * (4.0 / adv_feats_count) * loss_adv_feat
        else:
            loss_adv_feat = torch.tensor(0.0, device=pred_fake[0].device)

        return {
            "G_vgg": loss_vgg,
            "G_adv": loss_adv,
            "G_adv_feat": self.lambda_feat * loss_adv_feat,
        }

    def calc_D_losses(self, data: torch.Tensor, target: torch.Tensor) -> dict[str, torch.Tensor]:
        """
        Calculate discriminator losses.

        Args:
            data: Input images
            target: Target images

        Returns:
            Dictionary of loss components
        """
        with torch.no_grad():
            gen_out = self.generator(data)
            fake = self.replay_pool.query({"input": data.detach(), "output": gen_out.detach()})

        pred_true = self.discriminator(torch.cat([data, target], axis=1))
        loss_true = self.criterion_gan(pred_true, 1)

        pred_fake = self.discriminator(torch.cat([fake["input"], fake["output"]], axis=1))
        loss_false = self.criterion_gan(pred_fake, 0)

        return {"D_true": loss_true, "D_false": loss_false}

    def update_ema(self, decay: float = 0.9999):
        """
        Update exponential moving average of generator weights.

        Args:
            decay: EMA decay rate
        """
        with torch.no_grad():
            for ema_p, gen_p in zip(self.generator_ema.parameters(), self.generator.parameters()):
                ema_p.data = decay * ema_p.data + (1 - decay) * gen_p.data.detach()

    def test_step(self, test_loader: DataLoader, epoch: int, iteration: int):
        """
        Generate test images and save them.

        Args:
            test_loader: Test data loader
            epoch: Current epoch
            iteration: Current iteration
        """
        os.makedirs(os.path.join(self.checkpoint_dir, "images"), exist_ok=True)

        with torch.no_grad():
            data, target = next(iter(test_loader))
            data = data.to(self.device_to_use)
            target = target.to(self.device_to_use)

            self.generator_ema.eval()
            out = self.generator_ema(data)
            self.generator_ema.train()

            matrix = []
            pairs = torch.cat([data, out, target], -1)
            for idx in range(data.shape[0]):
                img = 255 * (pairs[idx] + 1) / 2
                img = img.cpu().permute(1, 2, 0).clip(0, 255).numpy().astype(np.uint8)
                matrix.append(img)

            matrix = np.vstack(matrix)
            matrix = cv2.cvtColor(matrix, cv2.COLOR_RGB2BGR)

            out_file = os.path.join(self.checkpoint_dir, "images", f"{epoch}_{iteration}.jpg")
            cv2.imwrite(out_file, matrix)

            # try:
            #     matrix_rgb = cv2.cvtColor(matrix, cv2.COLOR_BGR2RGB)

            #     img = wandb.Image(matrix_rgb, caption=f"Epoch {epoch}")  # type: ignore[attr-defined]
            #     wandb.log({"generated_examples": [img]})  # type: ignore[attr-defined]
            # except Exception:
            #     pass

    def save_checkpoint(self, epoch: int):
        """
        Save model checkpoint.

        Args:
            epoch: Current epoch number
        """
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
        out_file = f"epoch_{epoch}_{timestamp}.pt"
        out_path = os.path.join(self.checkpoint_dir, out_file)

        torch.save(
            {"G": self.generator_ema.state_dict(), "D": self.discriminator.state_dict()}, out_path
        )
        print(f"Saved checkpoint to {out_path}")

    def load_checkpoint(self, ckpt_file: str):
        """
        Load model checkpoint.

        Args:
            ckpt_file: Path to checkpoint file
        """
        ckpt = torch.load(ckpt_file)
        self.generator.load_state_dict(ckpt["G"])
        self.generator_ema.load_state_dict(ckpt["G"])
        self.discriminator.load_state_dict(ckpt["D"])
        print(f"Loaded checkpoint from {ckpt_file}")

    def train_epoch(
        self,
        train_loader: DataLoader,
        test_loader: DataLoader,
        epoch: int,
        g_optimizer,
        d_optimizer,
    ):
        """
        Train for one epoch.

        Args:
            train_loader: Training data loader
            test_loader: Test data loader
            epoch: Current epoch number
            g_optimizer: Generator optimizer
            d_optimizer: Discriminator optimizer
        """
        print(f"Training epoch {epoch}...")
        self.generator.train()
        self.discriminator.train()
        self.loss_log = {}

        N = 0
        pbar = tqdm(train_loader)

        for data, target in pbar:
            with torch.no_grad():
                data = data.to(self.device_to_use)
                target = target.to(self.device_to_use)

            # Train Generator
            g_optimizer.zero_grad()
            self.generator.requires_grad_(True)
            self.discriminator.requires_grad_(False)
            g_losses = self.calc_G_losses(data, target)
            g_loss = self.process_loss(g_losses)
            g_loss.backward()
            g_optimizer.step()
            self.update_ema()

            # Train Discriminator
            d_optimizer.zero_grad()
            self.generator.requires_grad_(False)
            self.discriminator.requires_grad_(True)
            d_losses = self.calc_D_losses(data, target)
            d_loss = self.process_loss(d_losses)
            d_loss.backward()
            d_optimizer.step()

            N += 1

            # Test sampling
            if (N % 100 == 0) or (len(train_loader) <= N + 1):
                for i in range(3):
                    self.test_step(test_loader, epoch, N + i)

            # Update progress bar
            txt = " | ".join([f"{k}: {self.loss_log[k] / N:.3e}" for k in self.loss_log])
            pbar.set_description(txt)

            # Save checkpoint
            if (N % 1000 == 0) or (len(train_loader) <= N + 1):
                self.save_checkpoint(epoch)
