#!/usr/bin/env python3

from api import StyleGANFastAPI as API

if __name__ == "__main__":
	import uvicorn
	uvicorn.run("main:app", reload=True)
else:
	app = API(debug=False)
