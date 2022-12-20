from api.paths import info
from api.paths import generation
from api.paths import manipulation

routers = [info.router, generation.router, manipulation.router]
