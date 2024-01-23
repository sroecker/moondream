import torch
from PIL import Image
from einops import rearrange
from torchvision.transforms.v2 import (
    Compose,
    Resize,
    InterpolationMode,
    ToImage,
    ToDtype,
    Normalize,
)


class VisionEncoder:
    def __init__(self, model_path: str = "model") -> None:
        self.model = torch.jit.load(f"{model_path}/vision.pt").to(device="cuda", dtype=torch.float32)
        self.preprocess = Compose(
            [
                Resize(size=(384, 384), interpolation=InterpolationMode.BICUBIC),
                ToImage(),
                ToDtype(torch.float32, scale=True),
                Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5]),
            ]
        )

    def __call__(self, image: Image) -> torch.Tensor:
        with torch.no_grad():
            image_vec = self.preprocess(image.convert("RGB")).unsqueeze(0).to(device="cuda")
            image_vec = image_vec[:, :, :-6, :-6]
            image_vec = rearrange(
                image_vec, "b c (h p1) (w p2) -> b (h w) (c p1 p2)", p1=14, p2=14
            )

            return self.model(image_vec)
