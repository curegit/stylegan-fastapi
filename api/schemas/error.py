from api.exceptions import HTTPError

class NotFoundError(HTTPError):
	detail = str

class RateLimitError(HTTPError):
	detail = str
