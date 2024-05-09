from pydantic import BaseModel, Field
from api.types import Base64, base64_examples

class RegenerateRequest(BaseModel):
	latent: Base64 = Field(examples=[next(base64_examples)])


class ReconstructionRequest(BaseModel):
	styles: list[Base64] = Field(min_length=1, examples=[[next(base64_examples), next(base64_examples), next(base64_examples)]])
