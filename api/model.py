from typing import Self
from chainer.backend import CpuDevice, GpuDevice
from stylegan.networks import Generator
from utilities.image import to_pil_image
from api import config, logger
from api.schemas import Model

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
		case _:
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

	# Call the network
	def __call__(self, *args, **kwargs):
		return self.generator(*args, **kwargs)

	# Delegate to the network object
	def __getattr__(self, key: str):
		return getattr(self.generator, key)

	def generate(self, psi: float = 1.0):
		z = self.generator.generate_latents(1)
		c = self.generator.generate_conditions(1) if self.generator.conditional else None
		ws, y = self.generator(z, c, psi=psi)
		y.to_cpu()
		z.to_cpu()
		pil_img = to_pil_image(y[0].array)
		return z, ws, pil_img

	def blend_styles(self, ):
		pass

	def mix_styles():
		pass

	@property
	def info(self) -> Model:
		return Model(
			id=self.id,
			name=self.name,
			description=self.description,
			conditional=self.conditional,
			labels=(self.labels or None),
			width=self.width,
			height=self.height,
		)

	@staticmethod
	def load(filepath: str, id: str, name: str, description: str, *, gpu: bool | int | None = None, lossy: bool = False) -> Self:
		generator = Generator.load(filepath)
		logger.info(f"Loaded '{filepath}'")
		device = get_device(gpu)
		generator.to_device(device)
		return GeneratorModel(generator, id, name, description, lossy=lossy)
