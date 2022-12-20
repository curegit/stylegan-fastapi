import tomllib
from pathlib import Path
from pydantic import BaseModel
from api.util import file_rel_path

class ServerSection(BaseModel):
	gpu: bool | int = False

class ModelSection(BaseModel):
	file: str
	name: str
	description: str = ""
	gpu: bool | int | None = None

class APIConfig(BaseModel):
	title: str
	version: str
	description: str = ""
	server: ServerSection
	models: dict[str, ModelSection]

def load_config(filepath: str | Path = file_rel_path("../config.toml")):
	with open(filepath, "rb") as f:
		obj = tomllib.load(f)
		return APIConfig(**obj)
