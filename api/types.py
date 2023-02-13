from typing import TypeAlias, Iterator
from itertools import cycle

Base64: TypeAlias = str

base64_examples: Iterator[Base64] = cycle([
	"TWVybWFpZCBNZWxvZHkg8J+OtiBQaWNoaSBQaWNoaSBQaXRjaA==",
	"U2FpbG9yIE1vb24g8J+MmQ==",
	"8J+QiOKAjeKsm1Rva3lvIE1ldyBNZXc=",
	"UHJlY3VyZSDwn6m18J+pt/Cfkps=",
	"QWlrYXRzdSEg8J+pt/CfjJ/wn46k",
])
