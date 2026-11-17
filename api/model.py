import torch
from random import choice
from pathlib import Path
from PIL.Image import Image
from numpy import ndarray
from mix import justify, slide_ellipsis
from stylegan.networks import Generator
from utilities.image import to_pil_image
from api import config, logger
from api.array import to_npy_base64
from api.image import to_png_base64, to_jpeg_base64, png_mime_type, jpeg_mime_type
from api.schemas import Model
from api.types import Base64

type Device = torch.device


def get_device(gpu: bool | int | None = None) -> Device:
    gpu = config.server.gpu if gpu is None else gpu
    match gpu:
        case True:
            return torch.device("cuda", 0)
        case False:
            return torch.device("cpu")
        case int() if gpu == -1:
            return torch.device("cpu")
        case int() if gpu >= 0:
            return torch.device("cuda", gpu)
    raise ValueError()


class GeneratorModel:

    @torch.inference_mode()
    def __init__(self, generator: Generator, id: str, name: str, description: str, *, lossy: bool = False, device: Device = torch.device("cpu")) -> None:
        self.generator = generator
        self.id = id
        self.name = name
        self.description = description
        self.lossy = lossy
        logger.info(f"Transfer '{name}' model to '{device}' backend ...")
        generator.to(device).eval().requires_grad_(False)
        self.device = device
        logger.info(f"Calculating the mean W for '{name}' ...")
        self.mean_ws = [generator.calculate_mean_w(categories=[c]) for c in range(self.generator.categories)]
        self.examples = [self.generate_encoded()[2] for _ in range(5)]

    def generate_latent(self, *, mean: ndarray | None = None, sd: float = 1.0) -> torch.Tensor:
        return self.generator.generate_latents(1, center=None if mean is None else self.wrap_tensor(mean), sd=sd)

    def generate_condition(self, *, category: int | None) -> tuple[torch.Tensor, str, int] | tuple[None, None, int]:
        if self.generator.conditional:
            k, c = self.generator.generate_conditions(1, categories=(None if category is None else [category]))
            return c, self.generator.labels[k[0]], k[0]
        return None, None, 0

    @torch.inference_mode()
    def generate(self, *, category: int | None = None, psi: float = 1.0, mean: ndarray | None = None, sd: float = 1.0) -> tuple[ndarray, ndarray, Image, str | None]:
        z = self.generate_latent(mean=mean, sd=sd)
        c, label, k = self.generate_condition(category=category)
        (w, *ws), y = self.generator(z, c, psi=psi, mean_w=self.mean_ws[k])
        return z[0].cpu().numpy(), w[0].cpu().numpy(), to_pil_image(y[0].cpu().numpy()), label

    def generate_encoded(self, *, category: int | None = None, psi: float = 1.0, mean: ndarray | None = None, sd: float = 1.0) -> tuple[Base64, Base64, Base64, str | None]:
        z, w, image, label = self.generate(category=category, psi=psi, mean=mean, sd=sd)
        return to_npy_base64(z), to_npy_base64(w), self.encode_image(image), label

    @torch.inference_mode()
    def combine_styles(self, styles: list[ndarray]) -> tuple[ndarray, Image]:
        n = len(styles)
        if n == 0:
            raise ValueError()
        w = sum(self.wrap_tensor(s) for s in styles) / n
        y = self.generator.synthesizer([w.unsqueeze(0)] * self.generator.levels)
        return w.cpu().numpy(), to_pil_image(y[0].cpu().numpy())

    def combine_styles_encoded(self, styles: list[ndarray]) -> tuple[Base64, Base64]:
        w, image = self.combine_styles(styles)
        return to_npy_base64(w), self.encode_image(image)

    @torch.inference_mode()
    def mix_styles(self, styles: list[ndarray]) -> tuple[list[ndarray], Image]:
        if not styles:
            raise ValueError()
        ws = [self.wrap_tensor(w) for w in styles]
        ws = justify(ws, self.generator.levels, align_end=False)
        ws = slide_ellipsis(ws)
        y = self.generator.synthesizer([w.unsqueeze(0) for w in ws])
        return [w.cpu().numpy() for w in ws], to_pil_image(y[0].cpu().numpy())

    def mix_styles_encoded(self, styles: list[ndarray]) -> tuple[list[Base64], Base64]:
        ws, image = self.mix_styles(styles)
        return [to_npy_base64(w) for w in ws], self.encode_image(image)

    def encode_image(self, image: Image) -> Base64:
        return to_jpeg_base64(image) if self.lossy else to_png_base64(image)

    def wrap_tensor(self, x: ndarray) -> torch.Tensor:
        return torch.as_tensor(x, device=self.device, dtype=next(self.generator.parameters()).dtype)

    @property
    def image_type(self) -> str:
        return jpeg_mime_type if self.lossy else png_mime_type

    @property
    def width(self) -> int:
        return self.generator.width

    @property
    def height(self) -> int:
        return self.generator.height

    @property
    def conditional(self) -> bool:
        return self.generator.conditional

    @property
    def labels(self) -> list[str] | None:
        return self.generator.labels if self.conditional else None

    @property
    def info(self) -> Model:
        return Model(
            id=self.id,
            name=self.name,
            description=self.description,
            conditional=self.conditional,
            labels=self.labels,
            width=self.width,
            height=self.height,
            lossy=self.lossy,
            mimeType=self.image_type,
            example=choice(self.examples),
        )

    @staticmethod
    def load(filepath: Path, id: str, name: str, description: str, *, gpu: bool | int | None = None, lossy: bool | None = None):
        generator = Generator.load(filepath)
        logger.info(f"Loaded '{filepath}' as '{name}'")
        device = get_device(gpu)
        model = GeneratorModel(generator, id, name, description, lossy=(config.lossy if lossy is None else lossy), device=device)
        logger.info(f"Model '{name}' is ready.")
        return model
