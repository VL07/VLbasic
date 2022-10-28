########################################
#	IMPORTS
########################################

from .tokenclass import Token, TokenTypes
from .error import Error, InvalidSyntaxError
from .statementclass import StatementNode, ExpressionNode, BinaryOperationNode, UnaryOperationNode, NumberNode

########################################
#	PARSER
########################################

class Parser:
	def __init__(self, filename: str, tokens: list[Token]) -> None:
		self.tokens = tokens
		self.index = -1
		self.currentToken = None
		self.filename = filename

		self.advance()

	def advance(self) -> None:
		self.index += 1
		if self.index >= len(self.tokens):
			self.currentToken = None
			return
		
		self.currentToken = self.tokens[self.index]

	def parse(self) -> tuple[list[StatementNode], Error]:
		statements: list[StatementNode] = []

		while self.currentToken.type != TokenTypes.EOF:
			statement, error = self.statement()
			if error:
				return None, error

			statements.append(statement)

		return statements, None

	def statement(self) -> tuple[StatementNode, Error]:
		expression, error = self.expression()

		if error:
			return None, error

		return expression, None

	def expression(self) -> tuple[ExpressionNode, Error]:
		term, error = self.binaryOperation(self.term, (TokenTypes.PLUS, TokenTypes.MINUS))
		if error:
			return None, error

		return term, error

	def term(self) -> tuple[BinaryOperationNode, Error]:
		factor, error = self.binaryOperation(self.factor, (TokenTypes.MULTIPLY, TokenTypes.DIVIDE))
		if error:
			return None, error

		return factor, error

	def factor(self) -> tuple[UnaryOperationNode | NumberNode, Error]:
		startToken = self.currentToken

		if startToken.type in (TokenTypes.PLUS, TokenTypes.MINUS):
			self.advance()
			factor, error = self.factor()
			if error: 
				return None, error

			return UnaryOperationNode(startToken, factor), None

		elif startToken.type in (TokenTypes.INTEGER, TokenTypes.FLOAT):
			self.advance()
			return NumberNode(startToken), None
		
		elif startToken.type == TokenTypes.LEFT_PARENTHESES:
			self.advance()
			expression, error = self.expression()
			if error:
				return None, error

			if self.currentToken.type != TokenTypes.RIGHT_PARENTHESES:
				return None, InvalidSyntaxError(f"Expected ')', not {str(self.currentToken.type)}", self.currentToken.position.copy())

			self.advance()
			return expression, None

		return None, InvalidSyntaxError(f"Expected number, not {str(self.currentToken.type)}", self.currentToken.position.copy())

	def binaryOperation(self, function, operators) -> tuple[BinaryOperationNode, Error]:
		left, error = function()
		if error:
			return None, error
		
		while self.currentToken.type in operators:
			operationToken = self.currentToken
			self.advance()

			right, error = function()
			if error:
				return None, error

			left = BinaryOperationNode(left, operationToken, right)

		return left, None