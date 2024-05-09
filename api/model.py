from pathlib import Path
from PIL.Image import Image
from numpy import ndarray
from chainer import Variable
from chainer.backend import CpuDevice, GpuDevice
from chainer.functions import stack
from mix import justify, slide_ellipsis
from stylegan.networks import Generator
from utilities.image import to_pil_image
from api import config, logger
from api.array import to_npy_base64
from api.image import to_png_base64, to_jpeg_base64, png_mime_type, jpeg_mime_type
from api.schemas import Model
from api.types import Base64

type Device = CpuDevice | GpuDevice

def get_device(gpu: bool | int | None = config.server.gpu) -> Device:
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

	def __init__(self, generator: Generator, id: str, name: str, description: str, *, lossy: bool = False, device: Device = CpuDevice()) -> None:
		self.generator = generator
		self.id = id
		self.name = name
		self.description = description
		self.lossy = lossy
		logger.info(f"Transfer '{name}' model to '{device}' backend ...")
		generator.to_device(device)
		self.device = device
		self.xp = generator.xp
		logger.info(f"Calculating the mean W for '{name}' ...")
		self.mean_ws = [generator.calculate_mean_w(categories=[c]) for c in range(self.generator.categories)]

	def generate_latent(self, *, mean: ndarray | None = None, sd: float = 1.0) -> Variable:
		return self.generator.generate_latents(1, center=mean, sd=sd)

	def generate_condition(self, *, category: int | None) -> tuple[Variable, str] | tuple[None, None]:
		if self.generator.conditional:
			k, c = self.generator.generate_conditions(1, categories=(None if category is None else [category]))
			return c, self.generator.labels[k[0]]
		return None, None

	def generate(self, *, category: int | None = None, psi: float = 1.0, mean: ndarray | None = None, sd: float = 1.0) -> tuple[ndarray, ndarray, Image, str | None]:
		z = self.generate_latent(mean=mean, sd=sd)
		c, label = self.generate_condition(category=category)
		(w, *ws), y = self.generator(z, c, psi=psi)
		z.to_cpu()
		w.to_cpu()
		y.to_cpu()
		return z.array[0], w.array[0], to_pil_image(y.array[0]), label

	def generate_encoded(self, *, category: int | None = None, psi: float = 1.0, mean: ndarray | None = None, sd: float = 1.0) -> tuple[Base64, Base64, Base64, str | None]:
		z, w, image, label = self.generate(category=category, psi=psi, mean=mean, sd=sd)
		return to_npy_base64(z), to_npy_base64(w), self.encode_image(image), label

	def combine_styles(self, styles: list[ndarray]) -> tuple[ndarray, Image]:
		n = len(styles)
		if n == 0:
			raise ValueError()
		w = sum(self.wrap_variable(s) for s in styles) / n
		y = self.generator.synthesizer([stack([w])] * self.generator.levels)
		y.to_cpu()
		w.to_cpu()
		return w.array, to_pil_image(y.array[0])

	def combine_styles_encoded(self, styles: list[ndarray]) -> tuple[Base64, Base64]:
		w, image = self.combine_styles(styles)
		return to_npy_base64(w), self.encode_image(image)

	def mix_styles(self, styles: list[ndarray]) -> tuple[list[ndarray], Image]:
		ws = [self.wrap_variable(w) for w in styles]
		ws = justify(ws, self.generator.levels, align_end=False)
		ws = slide_ellipsis(ws)
		y = self.generator.synthesizer([stack([w]) for w in ws])
		y.to_cpu()
		for w in ws:
			w.to_cpu()
		return [w.array for w in ws], to_pil_image(y.array[0])

	def mix_styles_encoded(self, styles: list[ndarray]) -> tuple[list[Base64], Base64]:
		ws, image = self.mix_styles(styles)
		return [to_npy_base64(w) for w in ws], self.encode_image(image)

	def encode_image(self, image: Image) -> Base64:
		return to_jpeg_base64(image) if self.lossy else to_png_base64(image)

	def wrap_variable(self, x: ndarray) -> Variable:
		v = Variable(x)
		v.to_device(self.device)
		return v

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
			mime_type=self.image_type,
		)

	@staticmethod
	def load(filepath: Path, id: str, name: str, description: str, *, gpu: bool | int | None = None, lossy: bool | None = None):
		generator = Generator.load(filepath)
		logger.info(f"Loaded '{filepath}'")
		device = get_device(gpu)
		return GeneratorModel(generator, id, name, description, lossy=(config.lossy if lossy is None else lossy), device=device)
