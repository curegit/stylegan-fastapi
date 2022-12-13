#from fastapi import FastAPI
#from fastapi.staticfiles import StaticFiles
#from fastapi.openapi.utils import get_openapi
from api import config, models
from api import StyleGANFastAPI as API
from api.image import to_png_base64

app = API()
#app = FastAPI(**conf.fastapi_params)

"""
def openapi():
	if app.openapi_schema:
		return app.openapi_schema
	app.openapi_schema = get_openapi(
		title=conf.title,
		version=conf.version,
		description=conf.description,
		routes=app.routes,
	)
	return app.openapi_schema
app.openapi = openapi
app.mount("/pages", StaticFiles(directory="pages", html=True), name="pages")
"""

@app.get("/")
def welcome():
	return {"": ""}

@app.get("/list")
def model_list():
	return {key: model.name for key, model in models.items()}

@app.get("/models")
def model_list():
	return {key: model.spec_dict for key, model in models.items()}

@app.get("/{model}/generate")
def generate(model: str, psi: float=1.0):
	m = models[model]
	z, w, y = m.generate_image(psi=psi)
	return {
		"hash": 0,
		"time": 1,
		"label": "",
		"width": m.width,
		"height": m.height,
		"data": to_png_base64(y)
	}
