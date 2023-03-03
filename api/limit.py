import time
import asyncio
from api import config
from api.http import get_client_id

import time
import asyncio
import filelock
from pathlib import Path
from api import config
from api.exceptions.client import BlockTimeoutException
from api.utils import mkdirp, resolve_path

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



# Context manager to block
class SignallingBlock:

	dir_path: Path = resolve_path(config.server.tmp_dir).joinpath("lock")
	mkdirp(dir_path)

	def __init__(self, id: str, timeout: float = config.server.limit.block.timeout) -> None:
		self.id = id
		self.timeout = timeout
		self.lock_path = self.dir_path.joinpath(id + ".lock")

	async def __aenter__(self) -> None:
		start = time.time()
		self.lock = filelock.SoftFileLock(self.lock_path)
		while True:
			try:
				self.lock.acquire(blocking=False)
				return
			except filelock.Timeout:
				t = time.time() - start
				if t >= self.timeout:
					raise BlockTimeoutException()
				await asyncio.sleep(config.server.limit.block.poll)

	async def __aexit__(self, exc_type, exc_value, traceback) -> None:
		self.lock.release()


class RateLimiter:

	def __init__(self, id: str) -> None:
		pass

	async def __aenter__(self) -> None:
		pass

	async def __aexit__(self, exc_type, exc_value, traceback) -> None:
		pass
