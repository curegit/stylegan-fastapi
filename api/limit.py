import os
import os.path
import math
import time
import glob
import asyncio
import sqlite3
import aiosqlite
import filelock
from pathlib import Path
from itertools import chain
from api import config, logger
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

	mkdirp(dir_path, recreate=True)

	def __init__(self, id: str, timeout: float = config.server.limit.block.timeout) -> None:
		self.id = id
		self.timeout = timeout
		self.lock_path = self.dir_path.joinpath(f"{id}.lock")

	async def __aenter__(self) -> None:
		start = time.monotonic()
		self.lock = filelock.UnixFileLock(self.lock_path)
		while True:
			try:
				self.lock.acquire(blocking=False)
				return
			except filelock.Timeout:
				t = time.monotonic() - start
				if t >= self.timeout:
					raise BlockTimeoutException()
				await asyncio.sleep(config.server.limit.block.poll)

	async def __aexit__(self, exc_type, exc_value, traceback) -> None:
		self.lock.release()


# Crude concurrency control to limit computing power usage
class ConcurrencyLimiter:

	lock_dir_path: Path = resolve_path(config.server.tmp_dir).joinpath("lock")

	queue_dir_path: Path = resolve_path(config.server.tmp_dir).joinpath("queue")

	mkdirp(lock_dir_path, recreate=True)
	mkdirp(queue_dir_path, recreate=True)

	def __init__(self, timeout: float = config.server.limit.concurrency.timeout) -> None:
		self.timeout = timeout

	async def __aenter__(self) -> None:
		start = time.monotonic()
		start_ns = time.monotonic_ns()
		self.lock = filelock.SoftFileLock(self.lock_dir_path.joinpath(f"{start_ns}.lock"))
		self.queue_lock = None
		self.clean_flag = False

		# When it has spare power, just go
		runnings = glob.glob("*.lock", root_dir=self.lock_dir_path)
		semaphore = config.server.limit.concurrency.max_concurrency - len(runnings)
		if semaphore > 0:
			try:
				self.lock.acquire(blocking=False)
			except filelock.Timeout:
				pass
			return

		# If it is busy unluckily, join the queue and wait
		self.clean_flag = True
		join_time = start_ns
		try:
			# Quit when the queue is too long
			waitings = glob.glob("*.lock", root_dir=self.queue_dir_path)
			queue_length = len(waitings)
			if queue_length >= config.server.limit.concurrency.max_queue:
				raise OverloadedException()
			# Join the queue
			while time.monotonic() - start < self.timeout:
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
				if t >= self.timeout:
					raise OverloadedException()
		finally:
			if self.queue_lock is not None:
				self.queue_lock.release()

	async def __aexit__(self, exc_type, exc_value, traceback) -> None:
		self.lock.release()
		# Failsafe to avoid deadlocks due to process crashes
		if self.clean_flag:
			self.clean()

	@classmethod
	def clean(cls) -> None:
		now = time.monotonic()
		for f in chain(glob.glob("*.lock", root_dir=cls.lock_dir_path), glob.glob("*.lock", root_dir=cls.queue_dir_path)):
			try:
				time_ns = int(Path(f).stem)
				# This threshold is heuristic
				dt = now - (time_ns / 10 ** 9)
				if dt > 30 * config.server.limit.concurrency.timeout:
					logger.warning("Deadlock detected")
					os.remove(f)
			except:
				pass


# Fixed window-based rate limiter
class RateLimiter:

	dir_path: Path = resolve_path(config.server.tmp_dir)

	db_path: Path = dir_path.joinpath("client.sqlite3")

	mkdirp(dir_path)

	# Initialize the client database
	if os.path.lexists(db_path):
		os.remove(db_path)
	with sqlite3.connect(db_path, isolation_level="EXCLUSIVE") as connection:
		connection.execute("CREATE TABLE request(id TEXT NOT NULL PRIMARY KEY, time REAL NOT NULL, count INTEGER NOT NULL DEFAULT 0, CHECK(time >= 0.0 AND count >= 0))")
		connection.commit()
	del connection

	def __init__(self, id: str) -> None:
		self.id = id

	async def check(self, timeout=3.0) -> None:
		now = time.time()
		async with aiosqlite.connect(self.db_path, isolation_level="EXCLUSIVE", timeout=timeout) as connection:
			connection.row_factory = aiosqlite.Row
			try:
				hit = False
				async with connection.execute("SELECT * FROM request WHERE id = ?", (self.id,)) as cursor:
					async for row in cursor:
						hit = True
						count = int(row["count"])
						window_start = float(row["time"])
				if hit:
					elapsed = now - window_start
					if elapsed >= config.server.limit.rate.window:
						await connection.execute("UPDATE request SET time = ?, count = 1 WHERE id = ?", (now, self.id))
					else:
						if count >= config.server.limit.rate.max_request:
							retry_after = max(1, math.ceil(config.server.limit.rate.window - elapsed))
							raise RateLimitException(retry_after)
						else:
							await connection.execute("UPDATE request SET count = ? WHERE id = ?", (count + 1, self.id))
				else:
					await connection.execute("INSERT INTO request(id, time, count) VALUES(?, ?, ?)", (self.id, now, 1))
			except RateLimitException:
				await connection.commit()
				raise
			except:
				await connection.rollback()
				raise
			else:
				await connection.commit()
