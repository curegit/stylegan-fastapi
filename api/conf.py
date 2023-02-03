import tomllib
from pathlib import Path
from pydantic import BaseModel

class ServerConfig(BaseModel):
	gpu: bool | int = False
	lossy: bool = False

class ModelConfig(BaseModel):
	file: str
	name: str
	description: str = ""
	gpu: bool | int | None = None
	lossy: bool | None = None

class APIConfig(BaseModel):
	title: str
	version: str
	description: str = ""
	server: ServerConfig
	models: dict[str, ModelConfig]

def load_config(filepath: str | Path) -> APIConfig:
	with open(filepath, "rb") as f:
		obj = tomllib.load(f)
		return APIConfig(**obj)
