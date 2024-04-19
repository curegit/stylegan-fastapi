import types
from typing import TypeVar, Generic, Protocol, Self
from collections.abc import Callable, Iterable
from fastapi import HTTPException as FastAPIHTTPException
from reification import Reified
from api.schemas.errors import HTTPError


class HTTPException[T: HTTPError](Reified, FastAPIHTTPException):
	status_code: int = 400

	"""
	reified: dict[type, type] = {}

	def __class_getitem__(cls, key: type[T]) -> type[Self]:
		if key in cls.reified:
			return cls.reified[key]
		new_exception_class: type[Self] = types.new_class(
			name=cls.__name__,
			bases=(cls,),
			exec_body=(lambda ns: ns)
		)
		new_exception_class.error_model = key
		cls.reified[key] = new_exception_class
		return new_exception_class
	"""

	def __init__(self, error: T, headers: dict[str, str] | None = None) -> None:
		super().__init__(self.status_code, error.detail, headers)

	@classmethod
	def get_error_model(cls) -> type[HTTPError]:
		if issubclass(cls.targ, HTTPError):
			return cls.targ
		else:
			return HTTPError


class Raises[T: Callable](Protocol):
	@property
	def __call__(self) -> T:
		raise NotImplementedError()

	@property
	def raises(self) -> Iterable[type[HTTPException]]:
		raise NotImplementedError()


def raises[T: Callable](*exceptions: type[HTTPException]) -> Callable[[T], Raises[T]]:
	def decorator(function: T) -> Raises[T]:
		function.raises = list(exceptions)
		return function

	return decorator


def raises_from(*functions: Raises) -> Iterable[type[HTTPException]]:
	for function in functions:
		yield from function.raises


def responses(*exceptions: type[HTTPException]) -> dict[int, dict[str, str]]:
	response_dict: dict[int, dict[str, str]] = {}
	for exception in exceptions:
		if exception.status_code in response_dict:
			response = response_dict[exception.status_code]
			response["model"] = response["model"] | exception.get_error_model()
		else:
			response_dict[exception.status_code] = {"model": exception.get_error_model()}
	return response_dict
