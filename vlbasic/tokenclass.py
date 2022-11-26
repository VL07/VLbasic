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
	POWER =				auto()
	MODULUS =			auto()

	LEFT_PARENTHESES = 	auto()
	RIGHT_PARENTHESES = auto()

	LEFT_SQUARE =		auto()
	RIGHT_SQUARE =		auto()

	LEFT_CURLY =		auto()
	RIGHT_CURLY =		auto()

	COMMA = 			auto()
	DOT = 				auto()
	COLON = 			auto()

	INTEGER =			auto()
	FLOAT = 			auto()
	STRING =			auto()

	EQUALS =			auto()

	DOUBLE_EQUALS = 	auto()
	NOT_EQUALS =		auto()
	GRATER_THAN = 		auto()
	LESS_THAN = 		auto()
	GREATER_EQUALS =	auto()
	LESS_EQUALS = 		auto()

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

	def isKeyword(self, keywordName: str) -> bool:
		return self.type == TokenTypes.KEYWORD and self.value == keywordName

	def isOneOfKeywords(self, keywordNames: list[str]) -> bool:
		return self.type == TokenTypes.KEYWORD and self.value in keywordNames