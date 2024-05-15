from typing import TypedDict, Any
from pydantic import BaseModel

class HTTPError(BaseModel):
	detail: Any = None


class NotFoundError(TypedDict):
	type: str
	name: str
	msg: str


class HTTPNotFoundError(HTTPError):
	detail: NotFoundError | None = None


class DeserializationError(HTTPError):
	detail: str | None = None


class EntityValidationError(HTTPError):
	pass


class RequestLimitError(HTTPError):
	detail: str | None = None
