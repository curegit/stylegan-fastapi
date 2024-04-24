from api.exceptions import HTTPException
from api.schemas.errors import HTTPError

class BadGatewayException(HTTPException):

	status_code = 502

	def __init__(self, msg: str | None = None) -> None:
		super().__init__(HTTPError(detail=msg))


class OverloadedException(HTTPException):

	status_code = 503

	def __init__(self) -> None:
		super().__init__(HTTPError(detail="the server is too busy and temporarily unavailable"))
