########################################
#	IMPORTS
########################################

from .statementclass import StatementNode, NumberNode, BinaryOperationNode, UnaryOperationNode, VariableAccessNode, VariableAssignNode, VariableDeclareNode, ExpressionNode
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
	
	def interpret(self, context: Context) -> tuple[list[RuntimeValue], RTError]:
		values: list[RuntimeValue] = []
		for statement in self.statements:
			value, error = self.visit(statement, context)
			if error:
				return None, error

			values.append(value)

		return values, None

	def visit(self, statement: StatementNode, context: Context) -> tuple[RuntimeValue | Number, RTError]:

		functionName = f"visit_{type(statement).__name__}"
		func = getattr(self, functionName, self.visitFunctionNotFound)
		return func(statement, context)

	def visitFunctionNotFound(self, statement: StatementNode, context: Context) -> None:
		raise NotImplemented(f"visit_{type(statement).__name__} is not implemented")

	def visit_NumberNode(self, node: NumberNode, context: Context) -> tuple[Number, RTError]:
		return Number(node.token.value, node.position.copy(), context), None

	def visit_BinaryOperationNode(self, node: BinaryOperationNode, context: Context) -> tuple[Number, RTError]:
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

	def visit_UnaryOperationNode(self, node: UnaryOperationNode, context: Context) -> tuple[Number, RTError]:
		number, error = self.visit(node.expression, context)
		if error:
			return None, error

		if node.operationToken.type == TokenTypes.MINUS:
			number, error = number.multiplied(Number(-1, number.position.copy(), context))
		elif node.operationToken.type == TokenTypes.PLUS:
			number, error = number.multiplied(Number(1, number.position.copy(), context))
		elif node.operationToken.isKeyword("NOT"):
			number, error = number.notted(node.operationToken)
		else:
			return None, RTError(f"Expected operation token, not {node.operationToken}", number.position, context)

		return number, None

	def visit_VariableAccessNode(self, node: VariableAccessNode, context: Context) -> tuple[ExpressionNode,  RTError]:
		value, error = context.variableTable.lookupVariable(node.token.value, node.position.copy())
		if error:
			return None, error

		return value, None

	def visit_VariableAssignNode(self, node: VariableAssignNode, context: Context) -> tuple[ExpressionNode,  RTError]:
		result, error = self.visit(node.valueNode, context)
		if error:
			return None, error
			
		value, error = context.variableTable.assignVariable(node.token.value, result, node.position.copy())
		if error:
			return None, error

		return value, None

	def visit_VariableDeclareNode(self, node: VariableDeclareNode, context: Context) -> tuple[ExpressionNode,  RTError]:
		isConstant = node.declareToken.isKeyword("CONST")

		result, error = self.visit(node.valueNode, context)
		if error:
			return None, error

		value, error = context.variableTable.declareVariable(node.token.value, result, isConstant, node.position.copy())
		if error:
			return None, error

		return value, None
	