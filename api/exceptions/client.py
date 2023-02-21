from api.exceptions import HTTPException
from api.schemas.errors import NotFoundError, RequestLimitError

class NotFoundException(HTTPException[NotFoundError]):

	status_code = 404

	def __init__(self, msg: str):
		super().__init__(NotFoundError(detail=msg))

class ModelNotFoundException(NotFoundException):

	def __init__(self, name: str):
		super().__init__(f"No such model: {name}")

class ArrayValidationException(HTTPException):
	pass

class LimitException(HTTPException[RequestLimitError]):
	status_code = 429
	def __init__(self) -> None:
		super().__init__(RequestLimitError())
