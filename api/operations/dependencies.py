from fastapi import Request, Depends
from api import config
from api.http import get_client_id
from api.limit import SignallingBlock, ConcurrencyLimiter, RateLimiter
from api.exceptions import raises, raises_from
from api.exceptions.client import BlockTimeoutException, RateLimitException
from api.exceptions.server import OverloadedException

async def client_id(request: Request) -> str:
	return get_client_id(request)

@raises(BlockTimeoutException)
async def signalling_block(id: str = Depends(client_id, use_cache=True)) -> bool:
	if config.server.limit.block.enabled:
		async with SignallingBlock(id):
			yield True
	else:
		yield False

@raises(RateLimitException)
async def rate_limit(id: str = Depends(client_id, use_cache=True)) -> bool:
	if config.server.limit.rate.enabled:
		async with RateLimiter(id):
			yield True
	else:
		yield False

@raises(OverloadedException)
async def concurrency_limit() -> bool:
	if config.server.limit.concurrency.enabled:
		async with ConcurrencyLimiter():
			yield True
	else:
		yield False

@raises(*raises_from(signalling_block, rate_limit, concurrency_limit))
async def limit(block: bool = Depends(signalling_block), rate: bool = Depends(rate_limit), concurrency: bool = Depends(concurrency_limit)):
	return block or rate or concurrency
