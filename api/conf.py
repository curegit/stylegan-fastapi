import tomllib
from pathlib import Path
from pydantic import BaseModel, Field


class CORSConfig(BaseModel):
	enabled: bool = False
	origins: list[str] = []


class HTTPConfig(BaseModel):
	forwarded: bool = False
	forwarded_headers: list[str] = ["", "", ""]
	cors: CORSConfig = CORSConfig()


class SignallingBlockConfig(BaseModel):
	enabled: bool = False
	timeout: float = 10
	poll: float = 0.2

class RateLimitConfig(BaseModel):
	enabled: bool = False



class LimitConfig(BaseModel):

	min_delay: float = Field(0, ge=0)



	block: SignallingBlockConfig
	rate: RateLimitConfig



class ServerConfig(BaseModel):
	gpu: bool | int = False
	lossy: bool = False
	logger: str | None = None
	tmp_dir: str = "./run"
	poll: float = 0.2
	timeout: float = 30
	http: HTTPConfig = HTTPConfig()
	limit: LimitConfig = LimitConfig()



	servers: list[dict[str, str]] | None = None
	terms_of_service: None = None
	contact: None = None
	license_info: None = None

class ModelConfig(BaseModel):
	file: str
	relative : bool = False
	name: str
	description: str = ""
	gpu: bool | int | None = None
	lossy: bool | None = None


class Config(BaseModel):
	title: str
	version: str
	description: str = ""
	docs: bool = True
	redoc: bool = True
	server: ServerConfig
	models: dict[str, ModelConfig]

def load_config(filepath: str | Path) -> Config:
	with open(filepath, "rb") as f:
		obj = tomllib.load(f)
		return Config(**obj)
