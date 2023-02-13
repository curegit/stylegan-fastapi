import base64
from io import BytesIO
from PIL.Image import Image
from api.types import Base64

png_mime_type: str = "image/png"

def to_png_base64(pil_image: Image) -> Base64:
	io = BytesIO()
	pil_image.save(io, "PNG")
	seq = io.getvalue()
	string = base64.b64encode(seq).decode("ascii")
	return string

jpeg_mime_type: str = "image/jpeg"

def to_jpeg_base64(pil_image: Image) -> Base64:
	io = BytesIO()
	pil_image.save(io, "JPEG")
	seq = io.getvalue()
	string = base64.b64encode(seq).decode("ascii")
	return string
