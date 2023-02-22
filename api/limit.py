import time
import asyncio
from fastapi import Request, Depends
from api import config
from api.http import get_client_id
from api.block import SignallingBlock

async def client_id(request: Request) -> str:
	return get_client_id(request)

async def signalling_block(id: str = Depends(client_id, use_cache=True)):
	if config.server.limit.block.enabled:
		async with SignallingBlock(id):
			return True
	else:
		return False

async def rate_limit(id: str = Depends(client_id, use_cache=True)):
	if config.server.limit.rate.enabled:
		yield
	else:
		yield

async def limit(block: bool = Depends(signalling_block), rate: bool = Depends(rate_limit)):
	return block or rate

#
class SpeedLimit:

	def __init__(self, min_delay_sec: float = config.server.limit.min_delay) -> None:
		self.delay = min_delay_sec

	async def __aenter__(self) -> None:
		self.entry_time = time.time()

	async def __aexit__(self, exc_type, exc_value, traceback) -> None:
		exit_time = time.time()
		wait = self.delay - (exit_time - self.entry_time)
		if wait > 0:
			await asyncio.sleep(wait)
