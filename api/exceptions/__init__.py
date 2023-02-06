import types
from typing import TypeVar, Generic, Self, Any
from fastapi import HTTPException as FastAPIHTTPException
from api.schemas.errors import HTTPError

T = TypeVar("T", bound=HTTPError)

class HTTPException(FastAPIHTTPException, Generic[T]):

	status_code: int = 400

	error_model: type[HTTPError] = HTTPError

	reified: dict[type, type] = {}

	def __class_getitem__(cls, key: type[T]) -> type[Self]:
		if key in cls.reified:
			return cls.reified[key]
		new_exception_class: type[HTTPException] = types.new_class(
			name=cls.__name__,
			bases=(cls,),
			exec_body=(lambda ns: ns)
		)
		new_exception_class.error_model = key
		cls.reified[key] = new_exception_class
		return new_exception_class

	def __init__(self, error: T, headers: dict[str, Any] | None = None) -> None:
			super().__init__(self.status_code, error.detail, headers)

def raises(*exceptions: type[HTTPException]) -> dict[int, dict[str, Any]]:
	return {e.status_code: {"model": e.error_model} for e in exceptions}

# Export concrete exceptions
from api.exceptions.client import NotFoundException
