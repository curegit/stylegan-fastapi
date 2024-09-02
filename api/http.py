from hashlib import blake2b
from starlette.requests import Request
from api import config, logger
from api.exceptions.server import BadGatewayException

def get_client_id(request: Request) -> str:
	if config.server.http.forwarded:
		for name in config.server.http.forwarded_headers:
			match request.headers.get(name):
				case str() as value if value:
					logger.debug(f"{name}: {value}")
					return hash_client(value)
		logger.warning("Encountered a client whose IP address is not set in the header as expected")
		raise BadGatewayException("client IP address is not set in the header as expected")
	else:
		return hash_client(client_ip_address(request))

def client_ip_address(request: Request) -> str:
	match request.client:
		case (host, port) if host:
			return host
	logger.warning("Encountered a client whose IP address is not set")
	raise BadGatewayException("client IP address is not set")

def hash_client(client: str) -> str:
	blake2 = blake2b(digest_size=16)
	blake2.update(client.encode("ascii", errors="ignore"))
	return blake2.hexdigest()
