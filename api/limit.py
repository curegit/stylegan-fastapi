import time
import glob
import asyncio
import sqlite3
import aiosqlite
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


# おおむねのチェック
class CLimit:

	dir_path: Path = resolve_path(config.server.tmp_dir).joinpath("con")
	mkdirp(dir_path)

	def __init__(self) -> None:
		pass

	async def __aenter__(self):
		runs = glob.glob(glob.escape(self.dir_path) + "/*.id")
		# ロック再取得の順序が問題になる
		# pending フォルダに time を書く
		#with PendingLock():
			# time ->
			# sleep poll
			# check empty?
			# go thru

	async def __aexit__(self):
		pass


class RateLimiter:

	db_path: Path = resolve_path(config.server.tmp_dir).joinpath("client.sqlite3")
	mkdirp(db_path.parent)
	with sqlite3.connect(db_path, isolation_level=None) as c:
		c.row_factory = sqlite3.Row
		u = c.cursor()
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
						raise
					else:
						await db.execute("UPDATE request SET count = ? WHERE id = ?", (count + 1, self.id))
			else:
				await db.execute("INSERT INTO request(id, time, count) VALUES(?, ?, ?)", (self.id, t, 1))

	async def __aexit__(self, exc_type, exc_value, traceback) -> None:
		pass
