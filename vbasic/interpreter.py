########################################
#	IMPORTS
########################################

from .statementclass import StatementNode, NumberNode, BinaryOperationNode, UnaryOperationNode, VariableAccessNode, VariableAssignNode, VariableDeclareNode, WhileNode, FunctionCallNode, StringNode, ListNode, GetItemNode
from .contextclass import Context
from .runtimevaluesclass import RuntimeValue, Number, Boolean, Null, BuiltInFunction, String, List
from .tokenclass import TokenTypes
from .error import RTError
from .utils import StartEndPosition, Position, File
from .builtInfunctions import funcPrint, funcToString, funcToNumber

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

	def addDefaultVariables(self, context: Context) -> None:
		file = File("<DEFAULT_VARIABLE>", "")
		position = StartEndPosition(file, Position(-1, -1, -1, file))

		context.variableTable.declareVariable("TRUE", Boolean(True, position, context), True, position)
		context.variableTable.declareVariable("FALSE", Boolean(False, position, context), True, position)
		context.variableTable.declareVariable("NULL", Null(position, context), True, position)
		context.variableTable.declareVariable("PRINT", BuiltInFunction("PRINT", funcPrint, position, context), True, position)
		context.variableTable.declareVariable("STRING", BuiltInFunction("STRING", funcToString, position, context), True, position)
		context.variableTable.declareVariable("NUMBER", BuiltInFunction("NUMBER", funcToNumber, position, context), True, position)

	def visit(self, statement: StatementNode, context: Context) -> tuple[RuntimeValue | Number, RTError]:

		functionName = f"visit_{type(statement).__name__}"
		func = getattr(self, functionName, self.visitFunctionNotFound)
		return func(statement, context)

	def visitFunctionNotFound(self, statement: StatementNode, context: Context) -> None:
		raise NotImplementedError(f"visit_{type(statement).__name__} is not implemented")

	def visit_NumberNode(self, node: NumberNode, context: Context) -> tuple[Number, RTError]:
		return Number(node.token.value, node.position.copy(), context), None

	def visit_StringNode(self, node: StringNode, context: Context) -> tuple[String, RTError]:
		return String(node.token.value, node.position.copy(), context), None

	def visit_BinaryOperationNode(self, node: BinaryOperationNode, context: Context) -> tuple[Number, RTError]:
		left, error = self.visit(node.left, context)
		if error:
			return None, error

		right, error = self.visit(node.right, context)
		if error:
			return None, error

		position = left.position.start.createStartEndPosition(right.position.end)

		if node.operationToken.type == TokenTypes.PLUS:
			result, error = left.added(right, position)
		elif node.operationToken.type == TokenTypes.MINUS:
			result, error = left.subtracted(right, position)
		elif node.operationToken.type == TokenTypes.MULTIPLY:
			result, error = left.multiplied(right, position)
		elif node.operationToken.type == TokenTypes.DIVIDE:
			result, error = left.divided(right, position)
		elif node.operationToken.type == TokenTypes.DOUBLE_EQUALS:
			result, error = left.equals(right, position)
		elif node.operationToken.type == TokenTypes.NOT_EQUALS:
			result, error = left.notEquals(right, position)
		elif node.operationToken.type == TokenTypes.GRATER_THAN:
			result, error = left.graterThan(right, position)
		elif node.operationToken.type == TokenTypes.LESS_THAN:
			result, error = left.lessThan(right, position)
		elif node.operationToken.type == TokenTypes.GREATER_EQUALS:
			result, error = left.graterThanEquals(right, position)
		elif node.operationToken.type == TokenTypes.LESS_EQUALS:
			result, error = left.lessThanEquals(right, position)
		else:
			return None, RTError(f"Expected operation token, not {node.operationToken}", node.operationToken.position.copy(), context)

		if error:
			return None, error
		
		return result, None

	def visit_UnaryOperationNode(self, node: UnaryOperationNode, context: Context) -> tuple[Number, RTError]:
		number, error = self.visit(node.expression, context)
		if error:
			return None, error

		position = node.operationToken.position.start.createStartEndPosition(node.expression.position.end)

		if node.operationToken.type == TokenTypes.MINUS:
			number, error = number.multiplied(Number(-1, number.position.copy(), context), position)
		elif node.operationToken.type == TokenTypes.PLUS:
			number, error = number.multiplied(Number(1, number.position.copy(), context), position)
		elif node.operationToken.isKeyword("NOT"):
			number, error = number.notted(position)
		else:
			return None, RTError(f"Expected operation token, not {node.operationToken}", number.position, context)

		return number, None

	def visit_VariableAccessNode(self, node: VariableAccessNode, context: Context) -> tuple[Number,  RTError]:
		value, error = context.variableTable.lookupVariable(node.token.value, node.position.copy())
		if error:
			return None, error

		value.position = node.position.copy()

		return value, None

	def visit_VariableAssignNode(self, node: VariableAssignNode, context: Context) -> tuple[Number,  RTError]:
		result, error = self.visit(node.valueNode, context)
		if error:
			return None, error
			
		value, error = context.variableTable.assignVariable(node.token.value, result, node.position.copy())
		if error:
			return None, error

		return value, None

	def visit_VariableDeclareNode(self, node: VariableDeclareNode, context: Context) -> tuple[Number,  RTError]:
		isConstant = node.declareToken.isKeyword("CONST")

		result, error = self.visit(node.valueNode, context)
		if error:
			return None, error

		value, error = context.variableTable.declareVariable(node.token.value, result, isConstant, node.position.copy())
		if error:
			return None, error

		return value, None
	
	def visit_WhileNode(self, node: WhileNode, context: Context) -> tuple[Number,  RTError]:
		condition, error = self.visit(node.condition, context)
		if error:
			return None, error

		conditionBoolean, error = condition.toBoolean(node.condition.position.copy())
		if error:
			return None, error

		while conditionBoolean.value:
			for statement in node.body:
				statementVisited, error = self.visit(statement, context)
				if error: 
					return None, error

			condition, error = self.visit(node.condition, context)
			if error:
				return None, error

			conditionBoolean, error = condition.toBoolean(node.condition.position.copy())
			if error:
				return None, error

		return None, None

	def visit_FunctionCallNode(self, node: FunctionCallNode, context: Context) -> tuple[Number,  RTError]:
		func, error = self.visit(node.func, context)
		if error:
			return None, error

		argumentsVisited = []
		for argument in node.arguments:
			argumentVisited, error = self.visit(argument, context)
			if error:
				return None, error

			argumentsVisited.append(argumentVisited)

		returnValue, error = func.execute(argumentsVisited, node.position.copy())
		if error:
			return None, error

		return returnValue, None

	def visit_ListNode(self, node: ListNode, context: Context) -> tuple[Number,  RTError]:
		expressions = []

		for expression in node.expressions:
			expressionVisited, error = self.visit(expression, context)
			if error:
				return None, error

			expressions.append(expressionVisited)

		return List(expressions, node.position.copy(), context), None
		
	def visit_GetItemNode(self, node: GetItemNode, context: Context) -> tuple[Number,  RTError]:
		variable, error = self.visit(node.variable, context)
		if error:
			return None, error

		item, error = self.visit(node.item, context)

		value, error = variable.getItem(item, node.position.copy())
		if error:
			return None, error

		return value, None