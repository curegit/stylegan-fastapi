import os
from pathlib import Path
from api import util

# Configuration file location
toml_path: Path = util.resolve_path(os.getenv("STYLEGAN_TOML", default=util.file_rel_path("../config.toml")))
