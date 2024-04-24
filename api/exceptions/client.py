from api.exceptions import HTTPException
from api.schemas.errors import HTTPNotFoundError, NotFoundError, DeserializationError, EntityValidationError, RequestLimitError

class NotFoundException(HTTPException[HTTPNotFoundError]):

	status_code = 404

	def __init__(self, type: str, name: str, msg: str) -> None:
		super().__init__(HTTPNotFoundError(detail=NotFoundError(type=type, name=name, msg=msg)))


class ModelNotFoundException(NotFoundException):

	def __init__(self, name: str, msg: str | None = None) -> None:
		super().__init__(type="model", name=name, msg=(msg or "no such model"))


class LabelNotFoundException(NotFoundException):

	def __init__(self, name: str, msg: str | None = None) -> None:
		super().__init__(type="label", name=name, msg=(msg or "no such label"))


class DeserializationException(HTTPException[DeserializationError]):

	status_code = 415

	def __init__(self) -> None:
		super().__init__(DeserializationError())


class ArrayValidationException(HTTPException[EntityValidationError]):

	status_code = 422


class RequestLimitException(HTTPException[RequestLimitError]):

	status_code = 429

	def __init__(self, msg: str, retry_after: int | None = None) -> None:
		if retry_after is None:
			super().__init__(RequestLimitError(detail=msg))
		else:
			super().__init__(RequestLimitError(detail=msg), headers={"Retry-After": str(retry_after)})


class BlockTimeoutException(RequestLimitException):

	def __init__(self) -> None:
		super().__init__("too many requests simultaneously")


class RateLimitException(RequestLimitException):

	def __init__(self, retry_after: int) -> None:
		super().__init__("hit the rate limit", retry_after=retry_after)
