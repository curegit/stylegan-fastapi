from pydantic import BaseModel, Field
from api.types import Base64, base64_examples

class GenerateRequestBody(BaseModel):
	latent: Base64 | None = Field(None, examples=[next(base64_examples)])


class ReconstructionRequestBody(BaseModel):
	styles: list[Base64] = Field(min_length=1, examples=[[next(base64_examples), next(base64_examples), next(base64_examples)]])
