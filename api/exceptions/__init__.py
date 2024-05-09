from typing import Protocol, Any
from collections.abc import Callable, Iterable
from fastapi import HTTPException as FastAPIHTTPException
from reification import Reified
from api.schemas.errors import HTTPError

class HTTPException[T: HTTPError](Reified, FastAPIHTTPException):

	status_code: int = 400

	def __init__(self, error: T, headers: dict[str, str] | None = None) -> None:
		super().__init__(self.status_code, error.detail, headers)

	@classmethod
	def get_error_model(cls) -> type[HTTPError]:
		if isinstance(cls.targ, type) and issubclass(cls.targ, HTTPError):
			return cls.targ
		else:
			return HTTPError


class Raises[T, **P](Protocol):

	@property
	def __call__(self) -> Callable[P, T]:
		...

	@property
	def raises(self) -> Iterable[type[HTTPException]]:
		...


def raises[T, **P](*exceptions: type[HTTPException]):
	def decorator(function: Callable[P, T]) -> Raises[T, P]:
		function.raises = list(exceptions)
		return function
	return decorator

def raises_from(*functions: Raises) -> Iterable[type[HTTPException]]:
	for function in functions:
		yield from function.raises

def responses(*exceptions: type[HTTPException]) -> dict[int, dict[str, Any]]:
	response_dict: dict[int, dict[str, Any]] = dict()
	for exception in exceptions:
		if exception.status_code in response_dict:
			response = response_dict[exception.status_code]
			response["model"] = response["model"] | exception.get_error_model()
		else:
			response_dict[exception.status_code] = {"model": exception.get_error_model()}
	return response_dict
