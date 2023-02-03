from api.exceptions import HTTPException
from api.schemas.error import NotFoundError

class NotFoundException(HTTPException[NotFoundError]):

	status_code = 404

	def __init__(self, msg: str):
		super().__init__(NotFoundError(detail=msg))

class ModelNotFoundException(NotFoundException):

	def __init__(self, name: str):
		super().__init__(f"No such model: {name}")
