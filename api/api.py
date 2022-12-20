from fastapi import FastAPI
from api import config
from api.paths import routers

class StyleGANFastAPI(FastAPI):

	def __init__(self, *,
		debug: bool = False,
		title: str = config.title,
		description: str = config.description,
		version: str = config.version
	):
		super().__init__(
			debug=debug,
			title=title,
			description=description,
			version=version,
		)

		for router in routers:
			self.include_router(router)


