import tomllib
from pydantic import BaseModel
from api.util import file_rel_path

def load_config(filepath=file_rel_path("../config.toml")):
	with open(filepath, "rb") as f:
		obj = tomllib.load(f)
		return APIConfig(**obj)

class ModelSection(BaseModel):
	file: str
	name: str
	description: str | None = None

class APIConfig(BaseModel):
	title: str
	version: str
	description: str
	models: dict[str, ModelSection]
