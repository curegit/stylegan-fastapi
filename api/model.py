from stylegan.networks import Generator
from utilities.image import to_pil_image

class GeneratorModel():

	def __init__(self, generator, name, description):
		self.generator = generator
		self.name = name
		self.description = description

	def __call__(self, *args, **kwargs):
		return self.generator(*args, **kwargs)

	def __getattr__(self, key):
		return getattr(self.generator, key)

	def generate_image(self, psi):
		z = self.generator.generate_latents(1)
		c = self.generator.generate_conditions(1) if self.generator.conditional else None
		ws, y = self.generator(z, c, psi=psi)
		y.to_cpu()
		pil_img = to_pil_image(y[0].array)
		return z, ws, pil_img

	@property
	def spec_dict(self):
		return {
			"size": self.size,
			"depth": self.depth,
			"levels": self.levels,
			"channels": (self.first_channels, self.last_channels),
			"conditional": self.conditional,
			"categories": self.categories,
			"labels": self.labels,
			"width": self.resolution[1],
			"height": self.resolution[0],
		}

	@staticmethod
	def load(file, name, description):
		generator = Generator.load(file)
		return GeneratorModel(generator, name, description)
