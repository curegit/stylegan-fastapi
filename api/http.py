from hashlib import blake2b
from starlette.requests import Request
from api import config
from api.exceptions import ProxyException

def get_client_id(request: Request) -> str:
	if config.server.http.forwarded:
		for name in config.server.http.forwarded_headers:
			match request.headers.get(name):
				case str() as value if value:
					return hash_client(value)
		raise ProxyException
	else:
		return hash_client(client_ip_address(request))

def client_ip_address(request: Request) -> str:
	match request.client:
		case (host, port):
			return host
	raise ProxyException

def hash_client(client: str) -> str:
	blake2 = blake2b(digest_size=16)
	blake2.update(client.encode("ascii", errors="ignore"))
	return blake2.hexdigest()
