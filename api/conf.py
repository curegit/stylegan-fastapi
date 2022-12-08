import tomllib
from api.util import file_rel_path

filepath = file_rel_path("../conf.toml")

def load():
	with open(filepath, "rb") as f:
		return tomllib.load(f)
