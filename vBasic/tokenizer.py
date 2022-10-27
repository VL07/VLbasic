########################################
#	IMPORTS
########################################

from typing import Optional
import utils
from tokenclass import Token, TokenTypes
from error import Error, IllegalCharacterError, ExpectedCharacterError

########################################
#	TOKENIZER
########################################

class Tokenizer:
	def __init__(self, filename: str, fileText: str) -> None:
		self.file = utils.File(filename, fileText)
		self.position = utils.Position(-1, 1, 0, self.file)
		self.currentCharacter = None

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
			if self.currentCharacter in ["\n", ":"]:
				tokens.append(Token(TokenTypes.NEW_LINE, self.position.asStartEndPosition()))
				self.advance()
			elif self.currentCharacter in [" ", "\t"]:
				self.advance()
			elif self.currentCharacter in utils.NUMBERS:
				token, error = self.makeNumber()
				tokens.append(token)
			elif self.currentCharacter in utils.LETTERS_UPPERCASE:
				token, error = self.makeKeywordOrIdentifier()
				tokens.append(token)
			elif self.currentCharacter in ["'", '"']:
				token, error = self.makeString()
				tokens.append(token)
			elif self.currentCharacter == "+":
				tokens.append(Token(TokenTypes.PLUS, self.position.asStartEndPosition()))
				self.advance()
			elif self.currentCharacter == "-":
				tokens.append(Token(TokenTypes.MINUS, self.position.asStartEndPosition()))
				self.advance()
			elif self.currentCharacter == "*":
				tokens.append(Token(TokenTypes.MULTIPLY, self.position.asStartEndPosition()))
				self.advance()
			elif self.currentCharacter == "/":
				tokens.append(Token(TokenTypes.DIVIDE, self.position.asStartEndPosition()))
				self.advance()
			elif self.currentCharacter == "(":
				tokens.append(Token(TokenTypes.LEFT_PARENTHESES, self.position.asStartEndPosition()))
				self.advance()
			elif self.currentCharacter == ")":
				tokens.append(Token(TokenTypes.RIGHT_PARENTHESES, self.position.asStartEndPosition()))
				self.advance()
			elif self.currentCharacter == ",":
				tokens.append(Token(TokenTypes.COMMA, self.position.asStartEndPosition()))
				self.advance()
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

	def makeNumber(self) -> tuple[Token | None, Error | None]:
		number = self.currentCharacter
		startPosition = self.position.copy()
		dots = 0

		self.advance()

		while self.currentCharacter and self.currentCharacter in utils.NUMBERS + ".":
			number += self.currentCharacter

			if self.currentCharacter == ".":
				if dots == 1:
					return

				dots += 1

			self.advance()

		position = utils.StartEndPosition(self.file, startPosition, self.position.copy())

		if dots == 0:
			return Token(TokenTypes.INTEGER, position, int(number)), None
		return Token(TokenTypes.FLOAT, position, float(number)), None

	def makeKeywordOrIdentifier(self) -> tuple[Token | None, Error | None]:
		startPosition = self.position.copy()
		text = self.currentCharacter

		self.advance()

		while self.currentCharacter and self.currentCharacter in utils.LETTERS_UPPERCASE + "_":
			text += self.currentCharacter
			self.advance()

		if text in utils.KEYWORDS:
			return Token(TokenTypes.KEYWORD, startPosition.createStartEndPosition(self.position), text), None
		return Token(TokenTypes.IDENTIFIER, startPosition.createStartEndPosition(self.position), text), None
	
	def makeString(self) -> tuple[Token | None, Error | None]:
		startPosition = self.position.copy()
		startStringChar = self.currentCharacter
		text = ""

		self.advance()

		while self.currentCharacter and self.currentCharacter not in [startStringChar, "\n"]:
			text += self.currentCharacter
			self.advance()

		if self.currentCharacter == startStringChar:
			print(self.currentCharacter)
			self.advance()
			return Token(TokenTypes.STRING, startPosition.createStartEndPosition(self.position), text), None

		self.advance()
		return None, ExpectedCharacterError(f"Expected string closing character, not '{self.currentCharacter or 'EOF'}'", self.position.asStartEndPosition())
	
	

	