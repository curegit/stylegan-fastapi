import time
import asyncio
import filelock
from pathlib import Path
from api import config
from api.exceptions.client import LimitException
from api.util import resolve_path

# Context manager to block
class SignallingBlock:

	dir_path: Path = resolve_path(config.server.tmp_dir)

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
					raise LimitException()
				await asyncio.sleep(config.server.limit.block.poll)

	async def __aexit__(self, exc_type, exc_value, traceback) -> None:
		self.lock.release()
