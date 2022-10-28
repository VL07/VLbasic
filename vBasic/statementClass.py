########################################
#	IMPORTS
########################################

from tokenclass import Token
from utils import StartEndPosition

########################################
#	PARSER
########################################

class StatementNode:
	def __init__(self) -> None:
		pass

class ExpressionNode(StatementNode):
	def __init__(self) -> None:
		self.position: StartEndPosition = None

class BinaryOperationNode:
	def __init__(self, left: ExpressionNode, operationToken: Token, right: ExpressionNode) -> None:
		self.left = left
		self.operationToken = operationToken
		self.right = right

		self.position = StartEndPosition(self.left.position.file.copy(), self.left.position.start.copy(), self.right.position.end.copy())

	def __repr__(self) -> str:
		return f"({str(self.left)} {str(self.operationToken.type.name)} {str(self.right)})"
	
class UnaryOperationNode:
	def __init__(self, operationToken: Token, expression: ExpressionNode) -> None:
		self.operationToken = operationToken
		self.expression = expression

		self.position = StartEndPosition(self.operationToken.position.file, self.operationToken.position.start.copy(), self.expression.position.end.copy())

	def __repr__(self) -> str:
		return f"({str(self.operationToken.type.name)} {str(self.expression)})"
	
class NumberNode:
	def __init__(self, token: Token) -> None:
		self.token = token

		self.position = token.position.copy()

	def __repr__(self) -> str:
		return f"{str(self.token.value)}"
