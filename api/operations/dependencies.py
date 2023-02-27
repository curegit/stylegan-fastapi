from fastapi import Request, Depends
from api import config
from api.http import get_client_id
from api.limit import SignallingBlock
from api.exceptions import raises
from api.exceptions.client import LimitException

async def client_id(request: Request) -> str:
	return get_client_id(request)

@raises(LimitException)
async def signalling_block(id: str = Depends(client_id, use_cache=True)):
	if config.server.limit.block.enabled:
		async with SignallingBlock(id):
			yield True
	else:
		yield False

@raises(id)
async def rate_limit(id: str = Depends(client_id, use_cache=True)):
	if config.server.limit.rate.enabled:
		yield
	else:
		yield

@raises(signalling_block.raises)
async def limit(block: bool = Depends(signalling_block), rate: bool = Depends(rate_limit)):
	return block or rate
