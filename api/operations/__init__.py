from fastapi import APIRouter
from api.operations.paths import info
from api.operations.paths import generation
from api.operations.paths import manipulation

# Export subrouters
routers: list[APIRouter] = [info.router, generation.router, manipulation.router]
