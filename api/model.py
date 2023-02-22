from typing import Self
from pathlib import Path
from PIL.Image import Image
from numpy import ndarray
from chainer.backend import CpuDevice, GpuDevice
from stylegan.networks import Generator
from utilities.image import to_pil_image
from api import config, logger
from api.image import to_png_base64, to_jpeg_base64, png_mime_type, jpeg_mime_type
from api.schemas import Model
from api.types import Base64

def get_device(gpu: bool | int | None = config.server.gpu) -> CpuDevice | GpuDevice:
	match gpu:
		case None:
			return get_device()
		case True:
			return GpuDevice.from_device_id(0)
		case False:
			return CpuDevice()
		case int() if gpu == -1:
			return CpuDevice()
		case int() if gpu >= 0:
			return GpuDevice.from_device_id(gpu)
	raise ValueError()


class GeneratorModel:

	def __init__(self, generator: Generator, id: str, name: str, description: str, *, lossy: bool = False) -> None:
		self.generator = generator
		self.id = id
		self.name = name
		self.description = description
		self.lossy = lossy
		self.xp = generator.xp
		self.mean_ws = [generator.calculate_mean_w(categories=[c]) for c in range(self.generator.categories)]

	def generate(self, psi: float = 1.0) -> tuple[ndarray, ndarray, Image, set | None]:
		z = self.generator.generate_latents(1)
		c = self.generator.generate_conditions(1) if self.generator.conditional else None
		(w, *ws), y = self.generator(z, c, psi=psi)
		z.to_cpu()
		w.to_cpu()
		y.to_cpu()
		return z.array[0], w.array[0], to_pil_image(y.array[0])

	def generate_encoded(self) -> tuple[Base64, Base64, Base64, str | None]:
		pass

	def blend_styles(self):
		pass

	def mix_styles(self):
		pass

	def encode_image(self, image: Image) -> tuple[str, Base64]:
		if self.lossy:
			return to_jpeg_base64(image)
		else:
			return to_png_base64(image)

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
		return self.generator.labels or None if self.conditional else None

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
			mime_type=self.image_type,
		)

	@staticmethod
	def load(filepath: Path, id: str, name: str, description: str, *, gpu: bool | int | None = None, lossy: bool = False) -> Self:
		generator = Generator.load(filepath)
		logger.info(f"Loaded '{filepath}'")
		device = get_device(gpu)
		generator.to_device(device)
		return GeneratorModel(generator, id, name, description, lossy=lossy)
