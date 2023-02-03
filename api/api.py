from fastapi import FastAPI
from api import config
from api.paths import routers

from api.schemas.error import NotFoundError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware



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

		origins = [
			"http://localhost:8000",
			"http://localhost:8080",
		]

		self.add_middleware(
			CORSMiddleware,
			allow_origins=origins,
			allow_credentials=True,
			allow_methods=["*"],
			allow_headers=["*"],)
