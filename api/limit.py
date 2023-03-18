import time
import glob
import asyncio
import sqlite3
import aiosqlite
import filelock
from pathlib import Path
from api import config
from api.exceptions.client import BlockTimeoutException
from api.exceptions.client import RateLimitException
from api.exceptions.server import OverloadedException
from api.utils import mkdirp, resolve_path

# Delay the execution of a block for at least some seconds
class SpeedLimit:

	def __init__(self, delay: float = config.server.limit.min_delay) -> None:
		self.delay = delay

	async def __aenter__(self) -> None:
		self.entry_time = time.monotonic()

	async def __aexit__(self, exc_type, exc_value, traceback) -> None:
		exit_time = time.monotonic()
		wait = self.delay - (exit_time - self.entry_time)
		if wait > 0:
			await asyncio.sleep(wait)


# Locking mechanisms to prevent simultaneous requests from the same client
class SignallingBlock:

	dir_path: Path = resolve_path(config.server.tmp_dir).joinpath("block")

	mkdirp(dir_path)

	def __init__(self, id: str) -> None:
		self.id = id
		self.lock_path = self.dir_path.joinpath(f"{id}.lock")

	async def __aenter__(self) -> None:
		start = time.monotonic()
		self.lock = filelock.SoftFileLock(self.lock_path)
		while True:
			try:
				self.lock.acquire(blocking=False)
				return
			except filelock.Timeout:
				t = time.monotonic() - start
				if t >= config.server.limit.block.timeout:
					raise BlockTimeoutException()
				await asyncio.sleep(config.server.limit.block.poll)

	async def __aexit__(self, exc_type, exc_value, traceback) -> None:
		self.lock.release()


# Crude concurrency control to limit computing power usage
class ConcurrencyLimiter:

	lock_dir_path: Path = resolve_path(config.server.tmp_dir).joinpath("lock")

	queue_dir_path: Path = resolve_path(config.server.tmp_dir).joinpath("queue")

	mkdirp(lock_dir_path)
	mkdirp(queue_dir_path)

	async def __aenter__(self):
		start = time.monotonic()
		start_ns = time.monotonic_ns()
		self.lock = filelock.SoftFileLock(self.lock_dir_path.joinpath(f"{start_ns}.lock"))
		self.queue_lock = None

		#
		runnings = glob.glob("*.lock", root_dir=self.lock_dir_path)
		semaphore = config.server.limit.concurrency.max_concurrency - len(runnings)
		if semaphore > 0:
			try:
				self.lock.acquire(blocking=False)
			except filelock.Timeout:
				pass
			return

		# If it is busy unluckily, join the queue and wait
		join_time = start_ns
		try:
			# Quit when the queue is too long
			waitings = glob.glob("*.lock", root_dir=self.queue_dir_path)
			queue_length = len(waitings)
			if queue_length >= config.server.limit.concurrency.max_queue:
				raise OverloadedException()
			# Join the queue
			while time.monotonic() - start < config.server.limit.concurrency.timeout:
				self.queue_lock = filelock.SoftFileLock(self.queue_dir_path.joinpath(f"{join_time}.lock"))
				try:
					self.queue_lock.acquire(blocking=False)
					break
				except filelock.Timeout:
					join_time = time.monotonic_ns()
			else:
				raise OverloadedException()
			# Wait for your turn
			while True:
				await asyncio.sleep(config.server.limit.concurrency.poll)
				runnings = glob.glob("*.lock", root_dir=self.lock_dir_path)
				semaphore = config.server.limit.concurrency.max_concurrency - len(runnings)
				waitings = glob.glob("*.lock", root_dir=self.queue_dir_path)
				rivals = [p for p in (int(Path(w).stem) for w in waitings) if p < join_time]
				if semaphore - len(rivals) > 0:
					try:
						self.lock.acquire(blocking=False)
					except filelock.Timeout:
						pass
					return
				t = time.monotonic() - start
				if t >= config.server.limit.concurrency.timeout:
					raise OverloadedException()
		finally:
			if self.queue_lock is not None:
				self.queue_lock.release()

	async def __aexit__(self, exc_type, exc_value, traceback) -> None:
		self.lock.release()


#
class RateLimiter:

	db_path: Path = resolve_path(config.server.tmp_dir).joinpath("client.sqlite3")

	mkdirp(db_path.parent)
	with sqlite3.connect(db_path, isolation_level=None) as conn:
		conn.row_factory = sqlite3.Row
		u = conn.cursor()
		u.execute("CREATE TABLE IF NOT EXISTS request(id TEXT NOT NULL PRIMARY KEY, time REAL NOT NULL, count INTEGER NOT NULL DEFAULT 0, CHECK(time >= 0.0 AND count >= 0))")


	def __init__(self, id: str) -> None:
		self.id = id

	async def __aenter__(self) -> None:
		# TODO: unsafe
		async with aiosqlite.connect(self.db_path, isolation_level=None) as db:
			db.row_factory = aiosqlite.Row
			e = 0
			async with db.execute("SELECT * FROM request WHERE id = ?", (self.id,)) as cursor:
				async for row in cursor:
					e += 1
					count = int(row["count"])
					st = float(row["time"])
			t = time.time()
			if e > 0:
				w = config.server.limit.rate.window
				m = config.server.limit.rate.max_request
				if t - st >= w:
					await db.execute("UPDATE request SET time = ?, count = 1 WHERE id = ?", (t, self.id))
				else:
					if count >= m:
						raise RateLimitException()
					else:
						await db.execute("UPDATE request SET count = ? WHERE id = ?", (count + 1, self.id))
			else:
				await db.execute("INSERT INTO request(id, time, count) VALUES(?, ?, ?)", (self.id, t, 1))

	async def __aexit__(self, exc_type, exc_value, traceback) -> None:
		pass
