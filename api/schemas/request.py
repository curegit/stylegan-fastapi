from pydantic import BaseModel, Field
from api.array import MAX_NPY_BASE64_LENGTH
from api.types import Base64, base64_examples

class GenerateRequestBody(BaseModel):
	latent: Base64 | None = Field(None, max_length=MAX_NPY_BASE64_LENGTH, examples=[next(base64_examples)])


class ReconstructionRequestBody(BaseModel):
	styles: list[Base64] = Field(min_length=1, max_length=20, examples=[[next(base64_examples), next(base64_examples), next(base64_examples)]])
