########################################
#	IMPORTS
########################################

from typing import Optional
from .utils import File, Position, NUMBERS, LETTERS, StartEndPosition
from .tokenclass import Token, TokenTypes
from .error import Error, IllegalCharacterError, ExpectedCharacterError
from .keywords import KEYWORDS

########################################
#	TOKENIZER
########################################

class Tokenizer:
	def __init__(self, filename: str, fileText: str) -> None:
		self.file = File(filename, fileText.replace("\t", "    "))
		self.position = Position(-1, 1, -1, self.file)
		self.currentCharacter = None

		if not fileText:
			self.file.text = " "

		self.advance()

	def getCharacterAtIndex(self, index: Optional[str] = None) -> str:
		if self.file.length - 1 < self.position.index:
			return None
		
		if index is not None:
			return self.file.text[index]
		return self.file.text[self.position.index]

	def updateCurrentCharacter(self) -> None:
		if self.file.length > self.position.index:
			self.currentCharacter = self.getCharacterAtIndex()
		else:
			self.currentCharacter = None

	def advance(self) -> None:
		nextCharacter = self.currentCharacter

		if not nextCharacter:
			nextCharacter = self.getCharacterAtIndex(self.position.index)

		self.position.advance(nextCharacter == "\n")

		self.updateCurrentCharacter()

	#########################################
	# TOKENIZE
	#########################################

	def tokenize(self) -> tuple[list[Token], Error]:
		tokens: list[Token] = []
		error: Error | None = None

		while self.currentCharacter is not None:
			if self.currentCharacter in ["\n", ";"]:
				tokens.append(Token(TokenTypes.NEW_LINE, self.position.asStartEndPosition()))
				self.advance()
			elif self.currentCharacter == "#":
				while self.currentCharacter and self.currentCharacter != "\n":
					self.advance()
			elif self.currentCharacter in [" ", "\t"]:
				self.advance()
			elif self.currentCharacter in NUMBERS:
				token, error = self.makeNumber()
				tokens.extend(token)
			elif self.currentCharacter in LETTERS:
				token, error = self.makeKeywordOrIdentifier()
				tokens.append(token)
			elif self.currentCharacter in ["'", '"']:
				token, error = self.makeString()
				tokens.append(token)
			elif self.currentCharacter == "+":
				token, error = self.makePlusEquals()
				tokens.append(token)
			elif self.currentCharacter == "-":
				token, error = self.makeMinusEqualsArrow()
				tokens.append(token)
			elif self.currentCharacter == "*":
				token, error = self.makeMultiplyEquals()
				tokens.append(token)
			elif self.currentCharacter == "/":
				token, error = self.makeDivideEquals()
				tokens.append(token)
			elif self.currentCharacter == "^":
				tokens.append(Token(TokenTypes.POWER, self.position.asStartEndPosition()))
				self.advance()
			elif self.currentCharacter == "%":
				tokens.append(Token(TokenTypes.MODULUS, self.position.asStartEndPosition()))
				self.advance()
			elif self.currentCharacter == "(":
				tokens.append(Token(TokenTypes.LEFT_PARENTHESES, self.position.asStartEndPosition()))
				self.advance()
			elif self.currentCharacter == ")":
				tokens.append(Token(TokenTypes.RIGHT_PARENTHESES, self.position.asStartEndPosition()))
				self.advance()
			elif self.currentCharacter == "[":
				tokens.append(Token(TokenTypes.LEFT_SQUARE, self.position.asStartEndPosition()))
				self.advance()
			elif self.currentCharacter == "]":
				tokens.append(Token(TokenTypes.RIGHT_SQUARE, self.position.asStartEndPosition()))
				self.advance()
			elif self.currentCharacter == "{":
				tokens.append(Token(TokenTypes.LEFT_CURLY, self.position.asStartEndPosition()))
				self.advance()
			elif self.currentCharacter == "}":
				tokens.append(Token(TokenTypes.RIGHT_CURLY, self.position.asStartEndPosition()))
				self.advance()
			elif self.currentCharacter == ",":
				tokens.append(Token(TokenTypes.COMMA, self.position.asStartEndPosition()))
				self.advance()
			elif self.currentCharacter == ".":
				token, error = self.makeDot()
				tokens.append(token)
			elif self.currentCharacter == ":":
				tokens.append(Token(TokenTypes.COLON, self.position.asStartEndPosition()))
				self.advance()
			elif self.currentCharacter == "=":
				token, error = self.makeEquals()
				tokens.append(token)
			elif self.currentCharacter == "!":
				token, error = self.makeNotEquals()
				tokens.append(token)
			elif self.currentCharacter == ">":
				token, error = self.makeGraterThanEquals()
				tokens.append(token)
			elif self.currentCharacter == "<":
				token, error = self.makeLessThanEquals()
				tokens.append(token)
			elif self.currentCharacter is not None:
				startPosition = self.position.copy()
				character = self.currentCharacter
				self.advance()
				error = IllegalCharacterError(f"'{character}' is not a valid character", startPosition.asStartEndPosition())
				break

			if error:
				break

		if error is not None:
			return None, error

		position = self.position.copy()
		position.advance()
		tokens.append(Token(TokenTypes.EOF, position.asStartEndPosition()))

		return tokens, None

	def makeDot(self) -> tuple[Token | None, Error | None]:
		startPosition = self.position.copy()

		# self.advance()

		# if self.currentCharacter == ".":
		# 	endPosition = self.position.copy()

		# 	self.advance()

		# 	return Token(TokenTypes.DOUBLE_DOT, startPosition.createStartEndPosition(endPosition)), None
		
		self.advance()

		return Token(TokenTypes.DOT, startPosition.asStartEndPosition()), None

	def makePlusEquals(self) -> tuple[Token | None, Error | None]:
		startPosition = self.position.copy()

		self.advance()

		if self.currentCharacter == "=":
			endPosition = self.position.copy()

			self.advance()

			return Token(TokenTypes.PLUS_EQUALS, startPosition.createStartEndPosition(endPosition)), None
		return Token(TokenTypes.PLUS, startPosition.asStartEndPosition()), None

	def makeMinusEqualsArrow(self) -> tuple[Token | None, Error | None]:
		startPosition = self.position.copy()

		self.advance()

		if self.currentCharacter == "=":
			endPosition = self.position.copy()

			self.advance()

			return Token(TokenTypes.MINUS_EQUALS, startPosition.createStartEndPosition(endPosition)), None
		elif self.currentCharacter == ">":
			endPosition = self.position.copy()

			self.advance()

			return Token(TokenTypes.RIGHT_ARROW, startPosition.createStartEndPosition(endPosition)), None
		return Token(TokenTypes.MINUS, startPosition.asStartEndPosition()), None

	def makeMultiplyEquals(self) -> tuple[Token | None, Error | None]:
		startPosition = self.position.copy()

		self.advance()

		if self.currentCharacter == "=":
			endPosition = self.position.copy()

			self.advance()

			return Token(TokenTypes.MULTIPLY_EQUALS, startPosition.createStartEndPosition(endPosition)), None
		return Token(TokenTypes.MULTIPLY, startPosition.asStartEndPosition()), None

	def makeDivideEquals(self) -> tuple[Token | None, Error | None]:
		startPosition = self.position.copy()

		self.advance()

		if self.currentCharacter == "=":
			endPosition = self.position.copy()

			self.advance()

			return Token(TokenTypes.DIVIDE_EQUALS, startPosition.createStartEndPosition(endPosition)), None
		return Token(TokenTypes.DIVIDE, startPosition.asStartEndPosition()), None

	def makeEquals(self) -> tuple[Token | None, Error | None]:
		startPosition = self.position.copy()

		self.advance()

		if self.currentCharacter == "=":
			token = Token(TokenTypes.DOUBLE_EQUALS, startPosition.createStartEndPosition(self.position))
			self.advance()
		else:
			token = Token(TokenTypes.EQUALS, startPosition.asStartEndPosition())

		return token, None

	def makeNotEquals(self) -> tuple[Token | None, Error | None]:
		startPosition = self.position.copy()

		self.advance()

		if self.currentCharacter != "=":
			return None, IllegalCharacterError(f"'{self.currentCharacter}' is not a valid character", startPosition.asStartEndPosition())

		token = Token(TokenTypes.NOT_EQUALS, startPosition.createStartEndPosition(self.position))

		self.advance()

		return token, None

	def makeGraterThanEquals(self) -> tuple[Token | None, Error | None]:
		startPosition = self.position.copy()

		self.advance()

		if self.currentCharacter == "=":
			token = Token(TokenTypes.GREATER_EQUALS, startPosition.createStartEndPosition(self.position))
			self.advance()
		else:
			token = Token(TokenTypes.GRATER_THAN, startPosition.asStartEndPosition())

		return token, None

	def makeLessThanEquals(self) -> tuple[Token | None, Error | None]:
		startPosition = self.position.copy()

		self.advance()

		if self.currentCharacter == "=":
			token = Token(TokenTypes.LESS_EQUALS, startPosition.createStartEndPosition(self.position))
			self.advance()
		else:
			token = Token(TokenTypes.LESS_THAN, startPosition.asStartEndPosition())

		return token, None

	def makeNumber(self) -> tuple[Token | None, Error | None]:
		number = self.currentCharacter
		startPosition = self.position.copy()
		dots = 0
		dotLast = False
		dotLastPos = None

		self.advance()

		while self.currentCharacter and self.currentCharacter in NUMBERS + ".":
			number += self.currentCharacter
			dotLast = False

			if self.currentCharacter == ".":
				dotLast = True
				dotLastPos = self.position.copy()

				if dots == 1:
					position = StartEndPosition(self.file, startPosition, self.position.copy())

					return [Token(TokenTypes.FLOAT, position, float(number[:-1])), Token(TokenTypes.DOT, dotLastPos.asStartEndPosition())], None

				dots += 1

			self.advance()

		position = StartEndPosition(self.file, startPosition, self.position.copy())

		if dotLast:
			return [Token(TokenTypes.INTEGER, position, int(number[:-1])), Token(TokenTypes.DOT, dotLastPos.asStartEndPosition())], None

		if dots == 0:
			return [Token(TokenTypes.INTEGER, position, int(number))], None
		return [Token(TokenTypes.FLOAT, position, float(number))], None

	def makeKeywordOrIdentifier(self) -> tuple[Token | None, Error | None]:
		startPosition = self.position.copy()
		text = self.currentCharacter

		self.advance()

		while self.currentCharacter and self.currentCharacter in LETTERS + "_":
			text += self.currentCharacter
			self.advance()

		if text in KEYWORDS:
			return Token(TokenTypes.KEYWORD, startPosition.createStartEndPosition(self.position), text), None
		return Token(TokenTypes.IDENTIFIER, startPosition.createStartEndPosition(self.position), text), None

	def makeEscapeCharacter(self, startingQuote: str) -> tuple[str | None, Error | None]:
		if not self.currentCharacter == "\\":
			return None, ExpectedCharacterError(f"Expected character \\, not {self.currentCharacter}", self.position.copy())

		self.advance()

		escapeCharacter = None

		if self.currentCharacter == "\\":
			escapeCharacter = "\\"
		elif self.currentCharacter == "n":
			escapeCharacter = "\n"
		elif self.currentCharacter == "r":
			escapeCharacter = "\r"
		elif self.currentCharacter == "t":
			escapeCharacter = "\t"
		elif self.currentCharacter == "b":
			escapeCharacter = "\b"
		elif self.currentCharacter == startingQuote:
			escapeCharacter = startingQuote
		else:
			return None, ExpectedCharacterError(f"Expected escape a valid escape character, not {self.currentCharacter}", self.position.copy())

		self.advance()
		
		return escapeCharacter, None
	
	def makeString(self) -> tuple[Token | None, Error | None]:
		startPosition = self.position.copy()
		startStringChar = self.currentCharacter
		text = ""

		self.advance()

		while self.currentCharacter and self.currentCharacter not in [startStringChar, "\n"]:
			escapeCharacter = None

			if self.currentCharacter == "\\":
				escapeCharacter, error = self.makeEscapeCharacter(startStringChar)
				if error:
					return None, error


			text += escapeCharacter if escapeCharacter else self.currentCharacter

			if not escapeCharacter:
				self.advance()

		if self.currentCharacter == startStringChar:
			self.advance()
			return Token(TokenTypes.STRING, startPosition.createStartEndPosition(self.position), text), None

		self.advance()
		return None, ExpectedCharacterError(f"Expected string closing character, not '{self.currentCharacter or 'EOF'}'", self.position.asStartEndPosition())
	
	

	