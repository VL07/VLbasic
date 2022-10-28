########################################
#	IMPORTS
########################################

from .statementclass import StatementNode, NumberNode, BinaryOperationNode, UnaryOperationNode
from .contextclass import Context
from .runtimevaluesclass import RuntimeValue, Number
from .tokenclass import TokenTypes
from .error import RTError

########################################
#	INTERPRETER
########################################

class Interpreter:
	def __init__(self, statements: list[StatementNode]) -> None:
		self.statements = statements
	
	def interpret(self, context: Context) -> tuple[list[RuntimeValue], RuntimeError]:
		values: list[RuntimeValue] = []
		for statement in self.statements:
			value, error = self.visit(statement, context)
			if error:
				return None, error

			values.append(value)

		return values, None

	def visit(self, statement: StatementNode, context: Context) -> tuple[RuntimeValue | Number, RuntimeError]:
		functionName = f"visit_{type(statement).__name__}"
		func = getattr(self, functionName, self.visitFunctionNotFound)
		return func(statement, context)

	def visitFunctionNotFound(self, statement: StatementNode, context: Context) -> None:
		raise NotImplemented(f"visit_{type(statement).__name__} is not implemented")

	def visit_NumberNode(self, node: NumberNode, context: Context) -> tuple[Number, RuntimeError]:
		return Number(node.token.value, node.position.copy(), context), None

	def visit_BinaryOperationNode(self, node: BinaryOperationNode, context: Context) -> tuple[Number, RuntimeError]:
		left, error = self.visit(node.left, context)
		if error:
			return None, error

		right, error = self.visit(node.right, context)
		if error:
			return None, error

		if node.operationToken.type == TokenTypes.PLUS:
			result, error = left.added(right)
		elif node.operationToken.type == TokenTypes.MINUS:
			result, error = left.subtracted(right)
		elif node.operationToken.type == TokenTypes.MULTIPLY:
			result, error = left.multiplied(right)
		elif node.operationToken.type == TokenTypes.DIVIDE:
			result, error = left.divided(right)
		else:
			return None, RTError(f"Expected operation token, not {node.operationToken}", node.operationToken.position.copy(), context)

		if error:
			return None, error
		
		return result, None

	def visit_UnaryOperationNode(self, node: UnaryOperationNode, context: Context) -> tuple[Number, RuntimeError]:
		number, error = self.visit(node.expression, context)
		if error:
			return None, error

		if node.operationToken.type == TokenTypes.MINUS:
			number, error = number.multiplied(Number(-1, number.position.copy(), context))
		else:
			return None, RTError(f"Expected operation token, not {node.operationToken}", number.position, context)

		return number, None


	