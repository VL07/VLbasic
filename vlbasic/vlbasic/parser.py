########################################
#	IMPORTS
########################################

from .tokenclass import Token, TokenTypes
from .error import Error, InvalidSyntaxError
from .statementclass import StatementNode, ExpressionNode, BinaryOperationNode, UnaryOperationNode, NumberNode, VariableAccessNode, VariableDeclareNode, VariableAssignNode, WhileNode, FunctionCallNode, StringNode, ListNode, GetItemNode, FunctionDefineNode, ReturnNode, IfNode, IfContainerNode, SetItemNode, ImportNode, DictionaryNode, ContinueNode, BreakNode, ForNode, RangeNode, GetAttributeNode

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

	def parseIf(self) -> tuple[list[ExpressionNode], Error]:
		statements: list[StatementNode] = []

		while self.currentToken.type != TokenTypes.EOF and not self.currentToken.isOneOfKeywords(["END", "ELSE", "ELSEIF"]):
			statement, error = self.statement()
			if error:
				return None, error

			if statement:
				statements.append(statement)

		if self.currentToken.type == TokenTypes.EOF:
			return None, InvalidSyntaxError(f"Expected keyword END, ELSE or ELSEIF, not {str(self.currentToken.type)}", self.currentToken.position.copy())
		
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

			if self.currentToken.type in [TokenTypes.EOF, TokenTypes.NEW_LINE]:
				return None, InvalidSyntaxError(f"Expected expression, not {str(self.currentToken.type)}", self.currentToken.position.copy())

			expression, error = self.expression()
			if error:
				return None, error

			return VariableDeclareNode(varName, expression, declareToken), None
		
		elif self.currentToken.type == TokenTypes.IDENTIFIER and self.getNextToken().type in [TokenTypes.EQUALS, TokenTypes.PLUS_EQUALS, TokenTypes.MINUS_EQUALS, TokenTypes.MULTIPLY_EQUALS, TokenTypes.DIVIDE_EQUALS]:
			varName = self.currentToken

			self.advance()

			assignType = "="
			if self.currentToken.type == TokenTypes.PLUS_EQUALS:
				assignType = "+="
			elif self.currentToken.type == TokenTypes.MINUS_EQUALS:
				assignType = "-="
			elif self.currentToken.type == TokenTypes.MULTIPLY_EQUALS:
				assignType = "*="
			elif self.currentToken.type == TokenTypes.DIVIDE_EQUALS:
				assignType = "/="

			self.advance()

			expression, error = self.expression()
			if error:
				return None, error

			return VariableAssignNode(varName, expression, assignType), None

		elif self.currentToken.isKeyword("RETURN"):
			returnToken = self.currentToken

			self.advance()

			if self.currentToken.type in [TokenTypes.EOF, TokenTypes.NEW_LINE]:
				return ReturnNode(returnToken.position.copy(), None), None

			value, error = self.binaryOperation(self.compExpression, (TokenTypes.PLUS, TokenTypes.MINUS))
			if error:
				return None, error

			return ReturnNode(returnToken.position.start.createStartEndPosition(value.position.end), value), None


		elif self.currentToken.isKeyword("CONTINUE"):
			token = self.currentToken

			self.advance()

			return ContinueNode(token.position.copy()), None

		elif self.currentToken.isKeyword("BREAK"):
			token = self.currentToken

			self.advance()

			return BreakNode(token.position.copy()), None

		elif self.currentToken.isKeyword("IMPORT"):
			startPosition = self.currentToken.position.start.copy()

			self.advance()

			importName, error = self.compExpression()
			if error:
				return None, error

			if not self.currentToken.isKeyword("AS"):
				return ImportNode(startPosition.createStartEndPosition(importName.position.end), importName, None), None

			self.advance()

			if self.currentToken.type not in [TokenTypes.IDENTIFIER, TokenTypes.MULTIPLY]:
				return None, InvalidSyntaxError(f"Expected IDENTIFIER, not {str(self.currentToken.type)}", self.currentToken.position.copy())

			asName = self.currentToken

			if self.currentToken.type == TokenTypes.MULTIPLY:
				self.currentToken.value = "*"

			self.advance()

			return ImportNode(startPosition.createStartEndPosition(asName.position.end), importName, asName.value), None

		compExpression, error = self.binaryOperation(self.compExpression, (TokenTypes.PLUS, TokenTypes.MINUS))
		if error:
			return None, error

		return compExpression, None

	def compExpression(self) -> tuple[BinaryOperationNode, Error]:
		startToken = self.currentToken

		if startToken.isKeyword("NOT"):
			self.advance()
			factor, error = self.compExpression()
			if error:
				return None, error

			return UnaryOperationNode(startToken, factor), None

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
		factor, error = self.binaryOperation(self.power, (TokenTypes.MULTIPLY, TokenTypes.DIVIDE, TokenTypes.MODULUS))
		if error:
			return None, error

		return factor, None

	def power(self) -> tuple[BinaryOperationNode, Error]:
		factor, error = self.binaryOperation(self.factor, [TokenTypes.POWER])
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

		callGetItem, error = self.callGetItem()
		if error:
			return None, error
		
		return callGetItem, None

	def callGetItem(self) -> tuple[FunctionCallNode, Error]:
		atom, error = self.atom()
		if error:
			return None, error

		while self.currentToken.type in [TokenTypes.LEFT_PARENTHESES, TokenTypes.LEFT_SQUARE, TokenTypes.DOT]:
			atom, error = self.makeSubGetItemCall(atom)
			if error:
				return None, error
			
		return atom, None

	def atom(self) -> tuple[NumberNode | VariableAccessNode | VariableDeclareNode | VariableAssignNode, Error]:
		startToken = self.currentToken

		if startToken.type in (TokenTypes.INTEGER, TokenTypes.FLOAT):
			self.advance()
			return NumberNode(startToken), None

		elif startToken.type == TokenTypes.STRING:
			self.advance()
			return StringNode(startToken), None
		
		elif startToken.type == TokenTypes.LEFT_PARENTHESES:
			self.advance()
			expression, error = self.expression()
			if error:
				return None, error

			if self.currentToken.type != TokenTypes.RIGHT_PARENTHESES:
				return None, InvalidSyntaxError(f"Expected ')', not {str(self.currentToken.type)}", self.currentToken.position.copy())

			self.advance()
			return expression, None

		elif startToken.type == TokenTypes.LEFT_SQUARE:
			expression, error = self.listExpression()
			if error:
				return None, error

			self.advance()
			
			return expression, None

		elif startToken.type == TokenTypes.LEFT_CURLY:
			expression, error = self.dictionaryExpression()
			if error:
				return None, error

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

		elif startToken.isKeyword("FOR"):
			expression, error = self.forExpression()
			if error:
				return None, error
			return expression, None

		elif startToken.isKeyword("FUNCTION"):
			expression, error = self.functionDefinition()
			if error:
				return None, error
			return expression, None

		elif startToken.isKeyword("IF"):
			expression, error = self.ifExpression()
			if error:
				return None, error
			return expression, None

		return None, InvalidSyntaxError(f"Expected number or identifier, not {str(self.currentToken.type)}", self.currentToken.position.copy())

	######################################

	def ifExpression(self) -> tuple[ListNode, Error]:
		startPosition = self.currentToken.position.start.copy()

		self.advance()

		condition, error = self.compExpression()
		if error:
			return None, error

		if not self.currentToken.isKeyword("THEN"):
			return None, InvalidSyntaxError(f"Expected THEN, not {str(self.currentToken.type)}", self.currentToken.position.copy())

		self.advance()

		body, error = self.parseIf()
		if error:
			return None, error

		mainIf = IfNode(startPosition.createStartEndPosition(self.currentToken.position.end), condition, body)

		elseifNodes = []

		while self.currentToken.isKeyword("ELSEIF"):
			elifStart = self.currentToken.position.start.copy()

			self.advance()

			condition, error = self.compExpression()
			if error:
				return None, error

			if not self.currentToken.isKeyword("THEN"):
				return None, InvalidSyntaxError(f"Expected THEN, not {str(self.currentToken.type)}", self.currentToken.position.copy())

			self.advance()

			body, error = self.parseIf()
			if error:
				return None, error

			elseifNodes.append(IfNode(elifStart.createStartEndPosition(self.currentToken.position.end), condition, body))

		elseNode = None
		if self.currentToken.isKeyword("ELSE"):
			elseStartPosition = self.currentToken.position.start.copy()

			self.advance()

			body, error = self.parseEnd()
			if error:
				return None, error

			elseNode = IfNode(elseStartPosition.createStartEndPosition(self.currentToken.position.end), None, body)

		endPosition = startPosition.createStartEndPosition(self.currentToken.position.end)

		self.advance()
		
		return IfContainerNode(endPosition, mainIf, elseifNodes, elseNode), None

	def functionDefinition(self) -> tuple[ListNode, Error]:
		startPosition = self.currentToken.position.start.copy()

		self.advance()

		anonymous = True
		functionName = None

		if self.currentToken.type == TokenTypes.IDENTIFIER:
			anonymous = False
			functionName = self.currentToken.value

			self.advance()

		if self.currentToken.type != TokenTypes.LEFT_PARENTHESES:
			return None, InvalidSyntaxError(f"Expected (, not {str(self.currentToken.type)}", self.currentToken.position.copy())

		self.advance()

		arguments = []

		if self.currentToken.type != TokenTypes.RIGHT_PARENTHESES:
			if self.currentToken.type != TokenTypes.IDENTIFIER:
				return None, InvalidSyntaxError(f"Expected IDENTIFIER, not {str(self.currentToken.type)}", self.currentToken.position.copy())

			firstArgument = self.currentToken.value

			arguments.append(firstArgument)

			self.advance()

			while self.currentToken.type == TokenTypes.COMMA:
				self.advance()
				
				if self.currentToken.type != TokenTypes.IDENTIFIER:
					return None, InvalidSyntaxError(f"Expected IDENTIFIER, not {str(self.currentToken.type)}", self.currentToken.position.copy())

				argument = self.currentToken.value

				arguments.append(argument)

				self.advance()

		if self.currentToken.type != TokenTypes.RIGHT_PARENTHESES:
			return None, InvalidSyntaxError(f"Expected ), not {str(self.currentToken.type)}", self.currentToken.position.copy())

		self.advance()

		if self.currentToken.type != TokenTypes.NEW_LINE:
			return None, InvalidSyntaxError(f"Expected , or new line, not {str(self.currentToken.type)}", self.currentToken.position.copy())

		body, error = self.parseEnd()
		if error:
			return None, error
		
		endPosition = self.currentToken.position.end.copy()

		self.advance()

		return FunctionDefineNode(startPosition.createStartEndPosition(endPosition), functionName, arguments, body, anonymous), None

	def makeSubGetItemCall(self, base: GetItemNode | FunctionCallNode) -> tuple[GetItemNode | FunctionCallNode, Error]:
		startPosition = self.currentToken.position.start.copy()

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
				return None, InvalidSyntaxError(f"Expected , or ), not {str(self.currentToken.type)}", self.currentToken.position.copy())

			endPosition = self.currentToken.position.end.copy()
			endPosition.column += 1

			self.advance()

			return FunctionCallNode(base.position.start.createStartEndPosition(endPosition), base, arguments), None
		elif self.currentToken.type == TokenTypes.LEFT_SQUARE:
			self.advance()

			if self.currentToken.type == TokenTypes.RIGHT_SQUARE:
				return None, InvalidSyntaxError(f"Expected expression, not {str(self.currentToken.type)}", self.currentToken.position.copy())
			
			indexNode, error = self.expression()
			if error:
				return None, error

			if self.currentToken.type != TokenTypes.RIGHT_SQUARE:
				return None, InvalidSyntaxError(f"Expected ], not {str(self.currentToken.type)}", self.currentToken.position.copy())
			
			endPosition = self.currentToken.position.end.copy()
			endPosition.column += 1

			self.advance()

			if self.currentToken.type != TokenTypes.EQUALS:
				return GetItemNode(startPosition.createStartEndPosition(endPosition), base, indexNode), None

			self.advance()

			value, error = self.compExpression()
			if error:
				return None, error

			return SetItemNode(startPosition.createStartEndPosition(value.position.end), base, indexNode, value), None

		elif self.currentToken.type == TokenTypes.DOT:
			self.advance()

			if self.currentToken.type != TokenTypes.IDENTIFIER:
				return None, InvalidSyntaxError(f"Expected IDENTIFIER, not {str(self.currentToken.type)}", self.currentToken.position.copy())

			index = StringNode(self.currentToken)

			self.advance()

			return GetAttributeNode(startPosition.createStartEndPosition(index.position.end), base, index), None

	def listExpression(self) -> tuple[ListNode, Error]:
		startPosition = self.currentToken.position.start.copy()

		self.advance()

		expressions = []

		if self.currentToken.type == TokenTypes.RIGHT_SQUARE:
			return ListNode(startPosition.createStartEndPosition(self.currentToken.position.end.copy()), expressions), None

		firstExpression, error = self.compExpression()
		if error:
			return None, error

		expressions.append(firstExpression)

		if self.currentToken.type == TokenTypes.RIGHT_ARROW:
			self.advance()

			endExpression, error = self.compExpression()
			if error:
				return None, error

			if self.currentToken.type != TokenTypes.RIGHT_ARROW:
				if self.currentToken.type != TokenTypes.RIGHT_SQUARE:
					return None, InvalidSyntaxError(f"Expected ], not {str(self.currentToken.type)}", self.currentToken.position.copy())

				return RangeNode(startPosition.createStartEndPosition(self.currentToken.position.end), firstExpression, endExpression, NumberNode(Token(TokenTypes.INTEGER, self.currentToken.position.copy(), 1))), None

			self.advance()

			stepExpression, error = self.compExpression()
			if error:
				return None, error
			
			if self.currentToken.type != TokenTypes.RIGHT_SQUARE:
				return None, InvalidSyntaxError(f"Expected ], not {str(self.currentToken.type)}", self.currentToken.position.copy())

			return RangeNode(startPosition.createStartEndPosition(self.currentToken.position.end), firstExpression, endExpression, stepExpression), None
		
		while self.currentToken.type == TokenTypes.COMMA:
			self.advance()

			expression, error = self.compExpression()
			if error:
				return None, error

			expressions.append(expression)

		if self.currentToken.type != TokenTypes.RIGHT_SQUARE:
			return None, InvalidSyntaxError(f"Expected , or ], not {str(self.currentToken.type)}", self.currentToken.position.copy())

		return ListNode(startPosition.createStartEndPosition(self.currentToken.position.end.copy()), expressions), None

	def dictionaryExpression(self) -> tuple[WhileNode, Error]:
		startPosition = self.currentToken.position.start.copy()

		self.advance()

		expressions = {}

		if self.currentToken.type == TokenTypes.RIGHT_CURLY:
			return DictionaryNode(startPosition.createStartEndPosition(self.currentToken.position.end), expressions), None

		first = True
		while self.currentToken.type == TokenTypes.COMMA or first:
			if not first:
				self.advance()

			first = False

			key, error = self.compExpression()
			if error:
				return None, error

			if self.currentToken.type != TokenTypes.COLON:
				return None, InvalidSyntaxError(f"Expected :, not {str(self.currentToken.type)}", self.currentToken.position.copy())

			self.advance()

			value, error = self.compExpression()
			if error:
				return None, error

			expressions[key] = value

		if self.currentToken.type != TokenTypes.RIGHT_CURLY:
			return None, InvalidSyntaxError(f"Expected }}, not {str(self.currentToken.type)}", self.currentToken.position.copy())
		
		endPosition = self.currentToken.position.end.copy()

		self.advance()

		return DictionaryNode(startPosition.createStartEndPosition(endPosition), expressions), None

	def forExpression(self) -> tuple[ForNode, Error]:
		startPosition = self.currentToken.position.start.copy()

		self.advance()

		if self.currentToken.type != TokenTypes.IDENTIFIER:
			return None, InvalidSyntaxError(f"Expected identifier, not {str(self.currentToken.type)}", self.currentToken.position.copy())

		item = self.currentToken

		self.advance()

		if not self.currentToken.isKeyword("IN"):
			return None, InvalidSyntaxError(f"Expected keyword IN, not {str(self.currentToken.type)}", self.currentToken.position.copy())

		self.advance()

		iterator, error = self.compExpression()
		if error:
			return None, error

		if not self.currentToken.isKeyword("THEN"):
			return None, InvalidSyntaxError(f"Expected keyword THEN, not {str(self.currentToken.type)}", self.currentToken.position.copy())

		self.advance()

		if not self.currentToken.type == TokenTypes.NEW_LINE:
			return None, InvalidSyntaxError(f"Expected new line, not {str(self.currentToken.type)}", self.currentToken.position.copy())

		self.advance()

		body, error = self.parseEnd()
		if error:
			return None, error

		endPosition = self.currentToken.position.end.copy()

		self.advance()

		return ForNode(startPosition.createStartEndPosition(endPosition), item, iterator, body), None

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