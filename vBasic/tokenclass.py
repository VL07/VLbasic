########################################
#	IMPORTS
########################################

from .utils import StartEndPosition
from enum import Enum, auto

########################################
#	ENUM
########################################

class TokenTypes(Enum):
	NEW_LINE = 			auto()
	EOF =				auto()

	KEYWORD = 			auto()
	IDENTIFIER = 		auto()

	PLUS = 				auto()
	MINUS = 			auto()
	MULTIPLY = 			auto()
	DIVIDE =			auto()

	LEFT_PARENTHESES = 	auto()
	RIGHT_PARENTHESES = auto()

	COMMA = 			auto()

	INTEGER =			auto()
	FLOAT = 			auto()
	STRING =			auto()

########################################
#	TOKEN CLASS
########################################

class Token:
	def __init__(self, type_: TokenTypes, position: StartEndPosition, value = None) -> None:
		self.type = type_
		self.value = value
		self.position = position
		
	def __repr__(self) -> str:
		return f"{self.type.name}({str(self.value or '')})"