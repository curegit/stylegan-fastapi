import os
from pathlib import Path
from api import utils

# Configuration file location
toml_path: Path = utils.resolve_path(os.getenv("STYLEGAN_TOML", default=utils.file_rel_path("../default/config.toml")))
