from pydantic import BaseModel, Field
from api.types import Base64, base64_examples

class RegenerateRequest(BaseModel):
	latent: Base64 = Field(example=next(base64_examples))
