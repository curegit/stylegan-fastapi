import time
import asyncio
from fastapi import Request, Depends
from api import config
from api.http import get_client_id
from api.block import SignallingBlock


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

class RateLimiter:
	pass
