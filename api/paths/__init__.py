from fastapi import APIRouter
from api.paths import info
from api.paths import generation
from api.paths import manipulation

# Export routers
routers: list[APIRouter] = [info.router, generation.router, manipulation.router]
