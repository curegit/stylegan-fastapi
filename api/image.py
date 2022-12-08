import base64
from io import BytesIO

def to_png_base64(pil_image):
	io = BytesIO()
	pil_image.save(io, "PNG")
	seq = io.getvalue()
	string = base64.b64encode(seq).decode("ascii")
	return string
