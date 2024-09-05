from api import StyleGANFastAPI as API

if __name__ == "__main__":
	import uvicorn
	uvicorn.run("main:app", reload=False)
else:
	app = API(debug=False)
