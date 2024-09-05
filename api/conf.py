import tomllib
from sys import float_info
from pathlib import Path
from pydantic import BaseModel, Field

class CORSConfig(BaseModel, extra="forbid"):
	enabled: bool = False
	origins: list[str] = []


class HTTPConfig(BaseModel, extra="forbid"):
	forwarded: bool = False
	forwarded_headers: list[str] = ["X-Forwarded-For", "Forwarded"]
	cors: CORSConfig = CORSConfig()


class SignallingBlockConfig(BaseModel, extra="forbid"):
	enabled: bool = False
	timeout: float = Field(10.0, gt=0)
	poll: float = Field(0.25, gt=float_info.min)


class ConcurrencyLimitConfig(BaseModel, extra="forbid"):
	enabled: bool = False
	max_concurrency: int = Field(8, gt=0)
	max_queue: int = Field(24, ge=0)
	timeout: float = Field(20, gt=0)
	poll: float = Field(0.1, gt=float_info.min)


class RateLimitConfig(BaseModel, extra="forbid"):
	enabled: bool = False
	window: float = Field(3600.0, gt=float_info.min)
	max_request: int = Field(200, gt=0)


class LimitConfig(BaseModel, extra="forbid"):
	min_delay: float = Field(0.0, ge=0)
	block: SignallingBlockConfig = SignallingBlockConfig()
	concurrency: ConcurrencyLimitConfig = ConcurrencyLimitConfig()
	rate: RateLimitConfig = RateLimitConfig()


class ServerConfig(BaseModel, extra="forbid"):
	gpu: bool | int = False
	logger: str | None = None
	tmp_dir: str = Field("./run", min_length=1)
	http: HTTPConfig = HTTPConfig()
	limit: LimitConfig = LimitConfig()


class ModelConfig(BaseModel, extra="forbid"):
	file: str
	relative: bool = False
	name: str | None = None
	description: str = ""
	gpu: bool | int | None = None
	lossy: bool | None = None


class Config(BaseModel, extra="forbid"):
	title: str = "StyleGAN FastAPI"
	version: str = "1.0.0"
	description: str = ""
	docs: bool = True
	redoc: bool = True
	lossy: bool = False
	server: ServerConfig = ServerConfig()
	models: dict[str, ModelConfig]


def load_config(filepath: str | Path) -> Config:
	with open(filepath, "rb") as f:
		obj = tomllib.load(f)
		return Config(**obj)
