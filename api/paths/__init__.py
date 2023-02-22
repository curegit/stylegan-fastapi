from fastapi import APIRouter
from api.paths.ops import info
from api.paths.ops import generation
from api.paths.ops import manipulation

# Export subrouters
routers: list[APIRouter] = [info.router, generation.router, manipulation.router]
