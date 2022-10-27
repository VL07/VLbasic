########################################
#	IMPORTS
########################################

from tokenclass import TokenTypes, Token

########################################
#	PARSER
########################################

class StatementNode:
	def __init__(self) -> None:
		pass

class ExpressionNode(StatementNode):
	def __init__(self) -> None:
		pass

class BinaryOperationNode:
	def __init__(self, left: ExpressionNode, operationToken: Token, right: ExpressionNode) -> None:
		self.left = left
		self.operationToken = operationToken
		self.right = right

	def __repr__(self) -> str:
		return f"({str(self.left)} {str(self.operationToken.type.name)} {str(self.right)})"
	
class UnaryOperationNode:
	def __init__(self, operationToken: Token, expression: ExpressionNode) -> None:
		self.operationToken = operationToken
		self.expression = expression

	def __repr__(self) -> str:
		return f"({str(self.operationToken.type.name)} {str(self.expression)})"
	
class NumberNode:
	def __init__(self, token: Token) -> None:
		self.token = token

	def __repr__(self) -> str:
		return f"{str(self.token.value)}"
