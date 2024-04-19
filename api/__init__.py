from api import env
from api import conf
from api import utils

# Add the StyleGAN core to the Python module path
import sys

sys.path.insert(0, str(utils.file_rel_path("../core")))
del sys

# Read configuration and define at top level
config: conf.Config = conf.load_config(env.toml_path)

# Create a logger
import logging

logger: logging.Logger = logging.getLogger(__name__ if config.server.logger is None else config.server.logger)
del logging

# Create the runtime directory
utils.mkdirp(config.server.tmp_dir)

# Optimize Chainer
import utilities.chainer

utilities.chainer.config_valid(faster=True)
del utilities

# Load all generator models in use
from api import model

models: dict[str, model.GeneratorModel] = {
	key:
	model.GeneratorModel.load(
		filepath=utils.resolve_path(env.toml_path.parent.joinpath(val.file) if val.relative else val.file),
		id=key,
		name=val.name,
		description=val.description,
		gpu=val.gpu,
		lossy=val.lossy,
	)
	for key, val in config.models.items()
}

# Export main interface
from api import app

StyleGANFastAPI = app.StyleGANFastAPI
