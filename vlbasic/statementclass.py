########################################
#	IMPORTS
########################################

from .tokenclass import Token
from .utils import StartEndPosition

########################################
#	PARSER
########################################

class StatementNode:
	def __init__(self) -> None:
		pass

class ExpressionNode(StatementNode):
	def __init__(self) -> None:
		self.position: StartEndPosition = None
		self.token: Token = None

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

class StringNode:
	def __init__(self, token: Token) -> None:
		self.token = token

		self.position = token.position.copy()

	def __repr__(self) -> str:
		return f"{str(self.token.value)}"

class VariableAccessNode:
	def __init__(self, token: Token) -> None:
		self.token = token

		self.position = token.position.copy()

	def __repr__(self) -> str:
		return f"VARIABLE_ACCESS_NODE({str(self.token.value)})"
		
class VariableAssignNode:
	def __init__(self, token: Token, valueNode: ExpressionNode) -> None:
		self.token = token
		self.valueNode = valueNode

		self.position = self.token.position.start.createStartEndPosition(valueNode.position.end)

	def __repr__(self) -> str:
		return f"VARIABLE_ASSIGN_NODE({str(self.token.value)})"

class VariableDeclareNode:
	def __init__(self, token: Token, valueNode: ExpressionNode, declareToken: Token) -> None:
		self.token = token
		self.valueNode = valueNode
		self.declareToken = declareToken

		self.position = self.declareToken.position.start.createStartEndPosition(valueNode.position.end)

	def __repr__(self) -> str:
		return f"VARIABLE_DECLARE_NODE({str(self.token.value)})"

class WhileNode:
	def __init__(self, position: StartEndPosition, condition: ExpressionNode, body: list[ExpressionNode]) -> None:
		self.position = position
		self.condition = condition
		self.body = body

	def __repr__(self) -> str:
		return "WHILE_NODE()"

class FunctionCallNode:
	def __init__(self, position: StartEndPosition, func: VariableAccessNode, arguments: list[ExpressionNode]) -> None:
		self.position = position
		self.func = func
		self.arguments = arguments

	def __repr__(self) -> str:
		return f"FUNCTION_CALL_NODE({str(self.func)}, {str(self.arguments)})"

class ListNode:
	def __init__(self, position: StartEndPosition, expressions: list[ExpressionNode]) -> None:
		self.position = position
		self.expressions = expressions

	def __repr__(self) -> str:
		return f"LIST_NODE({str(self.expressions)})"

class GetItemNode:
	def __init__(self, position: StartEndPosition, variable: ExpressionNode, item: VariableAccessNode) -> None:
		self.position = position
		self.variable = variable
		self.item = item

	def __repr__(self) -> str:
		return f"GET_ITEM_NODE({str(self.variable)}, {str(self.item)})"

class FunctionDefineNode:
	def __init__(self, position: StartEndPosition, variable: str, arguments: list[ExpressionNode], body: list[ExpressionNode]) -> None:
		self.position = position
		self.variable = variable
		self.arguments = arguments
		self.body = body

	def __repr__(self) -> str:
		return f"FUNCTION_DEFINE_NODE({str(self.variable)}, {str(self.arguments)})"
		
class ReturnNode:
	def __init__(self, position: StartEndPosition, value: ExpressionNode) -> None:
		self.position = position
		self.value = value

	def __repr__(self) -> str:
		return f"RETURN({str(self.value)})"