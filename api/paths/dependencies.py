
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
