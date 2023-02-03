from api import conf
from api import util

# Add the StyleGAN core to the Python module path
import sys
sys.path.insert(0, str(util.file_rel_path("../core")))
del sys

# Read configuration and define at top level
import os
config = conf.load_config(os.getenv("STYLEGAN_TOML", default=util.file_rel_path("../config.toml")))
del os

# Load all generator models in use
from api import model
models = {
	key: model.GeneratorModel.load(
		val.file,
		val.name,
		val.description,
		val.gpu
	) for key, val in config.models.items()
}

# Export main interfaces
from api import api
StyleGANFastAPI = api.StyleGANFastAPI
