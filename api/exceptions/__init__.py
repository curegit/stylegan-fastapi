import types
from typing import TypeVar, Generic, Protocol, Self, Any
from collections.abc import Callable, Iterable
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
		new_exception_class: type[Self] = types.new_class(
			name=cls.__name__,
			bases=(cls,),
			exec_body=(lambda ns: ns)
		)
		new_exception_class.error_model = key
		cls.reified[key] = new_exception_class
		return new_exception_class

	def __init__(self, error: T, headers: dict[str, Any] | None = None) -> None:
			super().__init__(self.status_code, error.detail, headers)


C = TypeVar("C", bound=Callable, covariant=True)

class Raises(Protocol[C]):

	@property
	def __call__(self) -> C:
		raise NotImplementedError()

	@property
	def raises(self) -> Iterable[type[HTTPException]]:
		raise NotImplementedError()


F = TypeVar("F", bound=Callable)

def raises(*exceptions: type[HTTPException]) -> Callable[[F], Raises[F]]:
	def decorator(function: F) -> Raises[F]:
		function.raises = list(exceptions)
		return function
	return decorator

def raises_from(*functions: Raises[F]) -> Iterable[type[HTTPException]]:
	for function in functions:
		yield from function.raises

def responses(*exceptions: type[HTTPException]) -> dict[int, dict[str, Any]]:
	response_dict: dict[int, dict[str, Any]] = {}
	for exception in exceptions:
		if exception.status_code in response_dict:
			response = response_dict[exception.status_code]
			response["model"] = response["model"] | exception.error_model
		else:
			response_dict[exception.status_code] = {"model": exception.error_model}
	return response_dict
