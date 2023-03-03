from collections.abc import Awaitable, Callable
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from api import config, logger
from api.operations import routers

class StyleGANFastAPI(FastAPI):

	def __init__(self, *, debug: bool = False):
		super().__init__(
			debug=debug,
			title=config.title,
			description=config.description,
			version=config.version,
		)

		# Include sectioned subrouters
		for router in routers:
			self.include_router(router)

		# Don't let clients store caches
		@self.middleware("http")
		async def control_caches(request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
			response = await call_next(request)
			response.headers["Cache-Control"] = "no-store"
			return response

		# Configure cross-origin resource sharing
		if config.server.http.cors.enabled:
			self.add_middleware(CORSMiddleware,
				allow_origins=config.server.http.cors.origins,
				allow_credentials=False,
				allow_methods=["*"],
				allow_headers=["*"],
				expose_headers=["*"],
			)
			logger.info("Enabled cross-origin resource sharing")
