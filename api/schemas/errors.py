from typing import Any
from pydantic import BaseModel

class HTTPError(BaseModel):
	detail: Any = None

class NotFoundError(HTTPError):
	detail = str

class RequestLimitError(HTTPError):
	detail = str
