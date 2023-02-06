from typing import Any
from pydantic import BaseModel

class HTTPError(BaseModel):
	detail: Any = None

class NotFoundError(HTTPError):
	detail = str

class RateLimitError(HTTPError):
	detail = str
