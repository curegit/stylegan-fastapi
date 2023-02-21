from api.exceptions import HTTPException
from api.schemas.errors import HTTPError


class ProxyException(HTTPException):

	status_code = 502

	def __init__(self, msg: str = "") -> None:
		super().__init__(HTTPError(detail=msg))
