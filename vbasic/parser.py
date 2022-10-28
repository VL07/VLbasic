########################################
#	IMPORTS
########################################

from .tokenclass import Token, TokenTypes
from .error import Error, InvalidSyntaxError
from .statementclass import StatementNode, ExpressionNode, BinaryOperationNode, UnaryOperationNode, NumberNode, VariableAccessNode, VariableDeclareNode, VariableAssignNode

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

	def getNextToken(self) -> Token:
		if self.index + 1 >= len(self.tokens):
			return None
		return self.tokens[self.index + 1]

	def parse(self) -> tuple[list[StatementNode], Error]:
		statements: list[StatementNode] = []

		while self.currentToken.type != TokenTypes.EOF:
			statement, error = self.statement()
			if error:
				return None, error

			if statement:
				statements.append(statement)

		return statements, None

	def statement(self) -> tuple[StatementNode, Error]:
		expression, error = self.expression()

		if error:
			return None, error

		return expression, None

	def expression(self) -> tuple[ExpressionNode, Error]:
		if self.currentToken.isOneOfKeywords(["LET", "CONST"]):
			declareToken = self.currentToken

			self.advance()

			if self.currentToken.type != TokenTypes.IDENTIFIER:
				return None, InvalidSyntaxError(f"Expected identifier, not {str(self.currentToken.type)}", self.currentToken.position.copy())

			varName = self.currentToken
			self.advance()

			if self.currentToken.type != TokenTypes.EQUALS:
				return None, InvalidSyntaxError(f"Expected =, not {str(self.currentToken.type)}", self.currentToken.position.copy())

			self.advance()

			if self.currentToken.type == TokenTypes.EOF:
				return None, InvalidSyntaxError(f"Expected expression, not {str(self.currentToken.type)}", self.currentToken.position.copy())

			expression, error = self.expression()
			if error:
				return None, error

			return VariableDeclareNode(varName, expression, declareToken), None
		
		elif self.currentToken.type == TokenTypes.IDENTIFIER and self.getNextToken().type == TokenTypes.EQUALS:
			varName = self.currentToken

			self.advance()
			self.advance()

			expression, error = self.expression()
			if error:
				return None, error

			return VariableAssignNode(varName, expression), None

		term, error = self.binaryOperation(self.term, (TokenTypes.PLUS, TokenTypes.MINUS))
		if error:
			return None, error

		return term, None

	def term(self) -> tuple[BinaryOperationNode, Error]:
		factor, error = self.binaryOperation(self.factor, (TokenTypes.MULTIPLY, TokenTypes.DIVIDE))
		if error:
			return None, error

		return factor, None

	def factor(self) -> tuple[UnaryOperationNode, Error]:
		startToken = self.currentToken

		if startToken.type in (TokenTypes.PLUS, TokenTypes.MINUS) or startToken.isKeyword("NOT"):
			self.advance()
			factor, error = self.factor()
			if error: 
				return None, error

			return UnaryOperationNode(startToken, factor), None

		atom, error = self.atom()
		if error:
			return None, error
		
		return atom, None

	def atom(self) -> tuple[NumberNode | VariableAccessNode | VariableDeclareNode | VariableAssignNode, Error]:
		startToken = self.currentToken

		if startToken.type in (TokenTypes.INTEGER, TokenTypes.FLOAT):
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

		elif startToken.type == TokenTypes.IDENTIFIER:
			self.advance()
			
			return VariableAccessNode(startToken), None

		elif startToken.type == TokenTypes.NEW_LINE:
			self.advance()
			
			return None, None



		return None, InvalidSyntaxError(f"Expected number or identifier, not {str(self.currentToken.type)}", self.currentToken.position.copy())

	######################################

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