########################################
#	IMPORTS
########################################

from .tokenclass import Token, TokenTypes
from .error import Error, InvalidSyntaxError
from .statementclass import StatementNode, ExpressionNode, BinaryOperationNode, UnaryOperationNode, NumberNode, VariableAccessNode, VariableDeclareNode, VariableAssignNode, WhileNode, FunctionCallNode

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

	def parse(self) -> tuple[list[ExpressionNode], Error]:
		statements: list[StatementNode] = []

		while self.currentToken.type != TokenTypes.EOF:
			statement, error = self.statement()
			if error:
				return None, error

			if statement:
				statements.append(statement)

		return statements, None

	def parseEnd(self) -> tuple[list[ExpressionNode], Error]:
		statements: list[StatementNode] = []

		while self.currentToken.type != TokenTypes.EOF and not self.currentToken.isKeyword("END"):
			statement, error = self.statement()
			if error:
				return None, error

			if statement:
				statements.append(statement)

		if self.currentToken.type == TokenTypes.EOF:
			return None, InvalidSyntaxError(f"Expected keyword END, not {str(self.currentToken.type)}", self.currentToken.position.copy())
		
		return statements, None

	def statement(self) -> tuple[ExpressionNode, Error]:
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

		term, error = self.binaryOperation(self.compExpression, (TokenTypes.PLUS, TokenTypes.MINUS))
		if error:
			return None, error

		return term, None

	def compExpression(self) -> tuple[BinaryOperationNode, Error]:
		if self.currentToken.isKeyword("NOT"):
			self.advance()
			factor, error = self.factor()
			if error:
				return None, error

			return UnaryOperationNode(self.currentToken, factor), None

		node, error = self.binaryOperation(self.term, (
			TokenTypes.DOUBLE_EQUALS,
			TokenTypes.NOT_EQUALS,
			TokenTypes.GRATER_THAN,
			TokenTypes.LESS_THAN,
			TokenTypes.GREATER_EQUALS,
			TokenTypes.LESS_EQUALS
		))
		
		if error:
			return None, error

		return node, None

	def term(self) -> tuple[BinaryOperationNode, Error]:
		factor, error = self.binaryOperation(self.factor, (TokenTypes.MULTIPLY, TokenTypes.DIVIDE))
		if error:
			return None, error

		return factor, None

	def factor(self) -> tuple[UnaryOperationNode, Error]:
		startToken = self.currentToken

		if startToken.type in (TokenTypes.PLUS, TokenTypes.MINUS):
			self.advance()
			factor, error = self.factor()
			if error: 
				return None, error

			return UnaryOperationNode(startToken, factor), None

		call, error = self.call()
		if error:
			return None, error
		
		return call, None

	def call(self) -> tuple[FunctionCallNode, Error]:
		print("t", self.currentToken.type)

		atom, error = self.atom()
		if error:
			return None, error

		print("t2", self.currentToken.type)

		if self.currentToken.type == TokenTypes.LEFT_PARENTHESES:
			self.advance()

			arguments = []

			if self.currentToken.type != TokenTypes.RIGHT_PARENTHESES:
				firstArgument, error = self.expression()
				if error:
					return None, error

				arguments.append(firstArgument)

				while self.currentToken.type == TokenTypes.COMMA:
					self.advance()

					argument, error = self.expression()
					if error:
						return None, error

					arguments.append(argument)

			if self.currentToken.type != TokenTypes.RIGHT_PARENTHESES:
				print(self.currentToken)
				return None, InvalidSyntaxError(f"Expected , or ), not {str(self.currentToken.type)}", self.currentToken.position.copy())

			endPosition = self.currentToken.position.end.copy()

			self.advance()

			return FunctionCallNode(atom.position.start.copy().createStartEndPosition(endPosition), atom, arguments), None
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

		elif startToken.isKeyword("WHILE"):
			expression, error = self.whileExpression()
			if error:
				return None, error
			return expression, None

		return None, InvalidSyntaxError(f"Expected number or identifier, not {str(self.currentToken.type)}", self.currentToken.position.copy())

	######################################

	def whileExpression(self) -> tuple[WhileNode, Error]:
		startPosition = self.currentToken.position.start.copy()

		self.advance()

		condition, error = self.compExpression()
		if error:
			return None, error

		previousPosition = self.currentToken.position.copy()

		if not self.currentToken:
			return None, InvalidSyntaxError(f"Expected keyword THEN, not EOF", previousPosition)

		if not self.currentToken.isKeyword("THEN"):
			return None, InvalidSyntaxError(f"Expected keyword THEN, not {str(self.currentToken.type)}", self.currentToken.position.copy())

		self.advance()

		if not self.currentToken.type == TokenTypes.NEW_LINE:
			return None, InvalidSyntaxError(f"Expected new line, not {str(self.currentToken.type)}", self.currentToken.position.copy())

		self.advance()

		body, error = self.parseEnd()
		if error:
			return None, error

		print("WHILE BODY:", body)

		endPosition = self.currentToken.position.end.copy()

		self.advance()

		return WhileNode(startPosition.createStartEndPosition(endPosition), condition, body), None

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