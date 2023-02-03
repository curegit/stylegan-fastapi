from typing import Self
from chainer.backend import CpuDevice, GpuDevice
from stylegan.networks import Generator
from utilities.image import to_pil_image
from api import config
from api.schemas import Model

def get_device(gpu: bool | int = config.server.gpu) -> CpuDevice | GpuDevice:
	if gpu is True:
		return GpuDevice.from_device_id(0)
	if gpu is False:
		return CpuDevice()
	if gpu >= 0:
		return GpuDevice.from_device_id(gpu)
	if gpu == -1:
		return CpuDevice()
	raise ValueError()

class GeneratorModel():

	def __init__(
		self,
		generator: Generator,
		id: str,
		name: str,
		description: str,
		#gpu: bool | int | None = False
	) -> None:
		self.generator = generator
		self.id = id
		self.name = name
		self.description = description
		#self.gpu = config.server.gpu if gpu is None else gpu


	def __call__(self, *args, **kwargs):
		return self.generator(*args, **kwargs)

	def __getattr__(self, key):
		return getattr(self.generator, key)

	def generate_image(self, psi: float = 1.0):
		z = self.generator.generate_latents(1)
		c = self.generator.generate_conditions(1) if self.generator.conditional else None
		ws, y = self.generator(z, c, psi=psi)
		y.to_cpu()
		pil_img = to_pil_image(y[0].array)
		return z, ws, pil_img

	@property
	def spec(self) -> Model:
		return Model(
			id=self.id,
			name=self.name,
			description=self.description,
			conditional=self.conditional,
			labels=(self.labels or None),
			width=self.width,
			height=self.height
		)

	@staticmethod
	def load(filepath: str, id: str, name: str, description: str, gpu: bool | int | None = None) -> Self:
		generator = Generator.load(filepath)
		device = get_device() if gpu is None else get_device(gpu)
		generator.to_device(device)
		return GeneratorModel(generator, id, name, description)
