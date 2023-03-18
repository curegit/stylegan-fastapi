import tomllib
from pathlib import Path
from pydantic import BaseModel, Field


class CORSConfig(BaseModel, extra="forbid"):
	enabled: bool = False
	origins: list[str] = []


class HTTPConfig(BaseModel, extra="forbid"):
	forwarded: bool = False
	forwarded_headers: list[str] = ["", "", ""]
	cors: CORSConfig = CORSConfig()


class SignallingBlockConfig(BaseModel, extra="forbid"):
	enabled: bool = False
	timeout: float = 10
	poll: float = 0.2

class ConcurrencyLimitConfig(BaseModel, extra="forbid"):
	enabled: bool = False
	max_concurrency: int = Field(8, gt=0)
	max_queue: int = Field(24, ge=0)
	timeout: float = 20
	poll: float = 0.1

class RateLimitConfig(BaseModel, extra="forbid"):
	enabled: bool = False
	window: float = 3600
	max_request: int = Field(100, gt=0)



class LimitConfig(BaseModel, extra="forbid"):

	min_delay: float = Field(0, ge=0)

	block: SignallingBlockConfig
	concurrency: ConcurrencyLimitConfig
	rate: RateLimitConfig



class ServerConfig(BaseModel, extra="forbid"):
	gpu: bool | int = False
	logger: str | None = None
	tmp_dir: str = "./run"
	poll: float = 0.2
	timeout: float = 30
	http: HTTPConfig = HTTPConfig()
	limit: LimitConfig



	servers: list[dict[str, str]] | None = None
	terms_of_service: None = None
	contact: None = None
	license_info: None = None

class ModelConfig(BaseModel, extra="forbid"):
	file: str
	relative : bool = False
	name: str
	description: str = ""
	gpu: bool | int | None = None
	lossy: bool | None = None
	labels: dict[str, str] | None = None


class Config(BaseModel, extra="forbid"):
	title: str
	version: str
	description: str = ""
	lossy: bool = False
	docs: bool = True
	redoc: bool = True
	server: ServerConfig
	models: dict[str, ModelConfig]

def load_config(filepath: str | Path) -> Config:
	with open(filepath, "rb") as f:
		obj = tomllib.load(f)
		return Config(**obj)
