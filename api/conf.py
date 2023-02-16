import tomllib
from pathlib import Path
from pydantic import BaseModel

class CORSConfig(BaseModel):
	enabled: bool = False
	origins: list[str] = []

class HTTPConfig(BaseModel):
	cors: CORSConfig = CORSConfig()

class ServerConfig(BaseModel):
	gpu: bool | int = False
	lossy: bool = False
	logger: str | None = None
	http: HTTPConfig = HTTPConfig()

class ModelConfig(BaseModel):
	file: str
	name: str
	description: str = ""
	gpu: bool | int | None = None
	lossy: bool | None = None

class Config(BaseModel):
	title: str
	version: str
	description: str = ""
	server: ServerConfig
	models: dict[str, ModelConfig]

def load_config(filepath: str | Path) -> Config:
	with open(filepath, "rb") as f:
		obj = tomllib.load(f)
		return Config(**obj)
