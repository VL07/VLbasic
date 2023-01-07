########################################
#	IMPORTS
########################################

from .statementclass import StatementNode, NumberNode, BinaryOperationNode, UnaryOperationNode, VariableAccessNode, VariableAssignNode, VariableDeclareNode, WhileNode, FunctionCallNode, StringNode, ListNode, GetItemNode, FunctionDefineNode, ReturnNode, IfContainerNode, SetItemNode, ImportNode, DictionaryNode, ContinueNode, BreakNode, ForNode, RangeNode, GetAttributeNode
from .contextclass import Context, VariableTable
from .runtimevaluesclass import RuntimeValue, Number, Boolean, Null, BuiltInFunction, String, List, Function, Dictionary, PythonFunction, Module
from .tokenclass import TokenTypes
from .error import RTError, CircularImportError, InvalidIteratorError, ArgumentError, ReturnOutsideFunctionError, ContinueOutsideLoopError, BreakOutsideLoopError, ValueError_
from .utils import StartEndPosition, Position, File, InterpretFile
from .builtins import builtins
from .tokenizer import Tokenizer
from .parser import Parser
import os
import importlib

########################################
#	INTERPRETER
########################################

class Interpreter:
	def __init__(self, statements: list[StatementNode], interpretFile: InterpretFile, isAFunction: bool = False) -> None:
		self.statements = statements
		self.interpretFile = interpretFile
		self.isAFunction = isAFunction
		self.returnValue = None
	
	def interpret(self, context: Context) -> tuple[list[RuntimeValue], RTError]:
		values: list[RuntimeValue] = []
		for statement in self.statements:
			value, error = self.visit(statement, context)
			if error:
				return None, error

			values.append(value)

			if self.returnValue:
				return values, None

		if self.isAFunction:
			file = File("<defaultVariable>", "")
			self.returnValue = Null(StartEndPosition(file, Position(-1, -1, -1, file)), context)

		return values, None

	def addDefaultVariables(self, context: Context) -> None:
		file = File("<defaultVariable>", "")
		position = StartEndPosition(file, Position(-1, -1, -1, file))

		for key, variable in builtins.items():
			variable.context = context
			context.variableTable.declareVariable(key, variable, True, position, True)

	def convertValue(self, value: any, position: StartEndPosition, context: Context, path: str, variableName: str = "", data: dict = {}) -> tuple[RuntimeValue, RuntimeError]:
		if isinstance(value, int) or isinstance(value, float):
			return Number(value, position.copy(), context), None
		elif isinstance(value, bool):
			return Boolean(value, position.copy(), context), None
		elif isinstance(value, str):
			return String(value, position.copy(), context), None
		elif value is None:
			return Null(position.copy(), context), None
		elif isinstance(value, list):
			convertedList = []
			for item in value:
				convertedItem, error = self.convertValue(item, position, context, path)
				if error:
					return None, error
				
				convertedList.append(convertedItem)

			return List(convertedList, position.copy(), context), None
		elif isinstance(value, dict):
			convertedDict = {}
			for key, value in value.items():
				convertedKey, error = self.convertValue(key, position, context, path)
				if error:
					return None, error
				
				convertedValue, error = self.convertValue(key, position, context, path)
				if error:
					return None, error

				convertedDict[convertedKey] = convertedValue

			return Dictionary(convertedDict, position.copy(), context), None
		elif callable(value):
			parameters = [0, 999]

			if not data:
				return None, RTError("Cannot nest functions inside of dicts in python modules", position.copy(), context)

			if "parameters" in data.keys():
				parameters = data["parameters"]

			return PythonFunction(variableName, value, position.copy(), context, path, parameters), None
		else:
			return None, RTError(f"Error while trying to import module {path}\nCannot convert {type(value)} to a runtime value", position.copy(), context)

	def importPythonModule(self, path: str, context: Context, position: StartEndPosition, importAs: str) -> tuple[Null, RTError]:
		try:
			pyModule = importlib.import_module(".".join(path.replace("/", ".").split(".")[:-1]))
		except Exception as error:
			print(error)
			return None, RTError(f"Error while trying to import module {path}", position.copy(), context)

		try:
			variables: dict[str, dict[str, any]] = pyModule.variables
		except AttributeError:
			return None, RTError(f"Module {path} dose not have a global variable variables", position.copy(), context)

		variableDictionary = Module({}, position.copy(), context)

		for variableName, variableData in variables.items():
			variable = variableData["value"]
			
			convertedValue, error = self.convertValue(variable, position, context, path, variableName, variableData)
			if error:
				return None, error

			variableDictionary.value[variableName] = convertedValue

			if importAs == "*":
				context.variableTable.declareVariable(variableName, convertedValue, variableData["constant"], position.copy(), False)

		if not importAs:
			importAs = path.split("/")[-1][:-3]

		if importAs != "*":
			context.variableTable.declareVariable(importAs, variableDictionary, True, position.copy(), False)

		return Null(position.copy(), context), None


	def importModule(self, moduleName: str, context: Context, position: StartEndPosition, importAs: str) -> tuple[Null, RTError]:
		circularImport = self.interpretFile.findCircularImport(moduleName)
		if circularImport:
			return None, CircularImportError(self.interpretFile.filepath, moduleName, position.copy(), context)

		path = None
		if os.path.exists(os.path.join(os.path.dirname(self.interpretFile.filepath), "vlbasic/modules/", moduleName + ".vlb")):
			path = os.path.join(os.path.dirname(self.interpretFile.filepath), "vlbasic/modules/", moduleName + ".vlb")
		elif os.path.exists(os.path.join("vlbasic/modules/", moduleName + ".vlb")):
			path = os.path.join("vlbasic/modules/", moduleName + ".vlb")
		elif os.path.exists(os.path.join(os.path.dirname(self.interpretFile.filepath), moduleName + ".vlb")):
			path = os.path.join(os.path.dirname(self.interpretFile.filepath), moduleName + ".vlb")
		elif os.path.exists(moduleName + ".vlb"):
			path = os.path.join(moduleName + ".vlb")
		elif os.path.exists(os.path.join(os.path.dirname(self.interpretFile.filepath), "vlbasic/modules/", moduleName + ".py")):
			_, error = self.importPythonModule(os.path.join(os.path.dirname(self.interpretFile.filepath), "vlbasic/modules/", moduleName + ".py"), context, position, importAs)
			if error:
				return None, error

			return Null(position.copy(), context), None
		elif os.path.exists(os.path.join("vlbasic/modules/", moduleName + ".py")):
			_, error = self.importPythonModule(os.path.join("vlbasic/modules/", moduleName + ".py"), context, position, importAs)
			if error:
				return None, error

			return Null(position.copy(), context), None


		if not path:
			return None, RTError(f"Module {moduleName} was not found ({os.path.join(os.path.dirname(self.interpretFile.filepath), moduleName + '.vlb')})", position.copy(), context)


		print(path)
		with open(path, "r") as f:
			inputText = f.read()

		tokenizer = Tokenizer(f"{self.interpretFile.filepath}", inputText)
		tokens, error = tokenizer.tokenize()

		if error:
			error.importStack.append(f"Error while trying to import module {moduleName}")
			return None, error

		parser = Parser(f"{self.interpretFile.filepath}", tokens)

		statements, error = parser.parse()

		if error:
			error.importStack.append(f"Error while trying to import module {moduleName}")
			return None, error

		importFileContext = Context(f"{self.interpretFile.filepath}")
		importFileContext.setVariableTable(VariableTable())
		
		interpreter = Interpreter(statements, InterpretFile(path, self.interpretFile))
		interpreter.addDefaultVariables(importFileContext)
		out, error = interpreter.interpret(importFileContext)

		if error:
			error.context.parent = context
			error.importStack.append(f"Error while trying to import module {moduleName}")
			return None, error

		variableDictionary = Module({}, position.copy(), context)

		for variableName in importFileContext.variableTable.variables.keys():
			variable = importFileContext.variableTable.variables[variableName]

			if variable.builtIn:
				continue

			variableDictionary.value[variableName] = variable.value

			if importAs == "*":
				context.variableTable.declareVariable(variableName, variable.value, variable.constant, position.copy(), False)

		if not importAs:
			importAs = moduleName.split("/")[-1]

		if importAs != "*":
			context.variableTable.declareVariable(importAs, variableDictionary, True, position.copy(), False)

		return Null(position.copy(), context), None

	def visit(self, statement: StatementNode, context: Context, insideLoop: bool = False) -> tuple[RuntimeValue | Number, RTError]:
		functionName = f"visit_{type(statement).__name__}"
		func = getattr(self, functionName, self.visitFunctionNotFound)
		return func(statement, context, insideLoop)

	def visitFunctionNotFound(self, statement: StatementNode, context: Context, insideLoop: bool) -> None:
		raise NotImplementedError(f"visit_{type(statement).__name__} is not implemented")

	def visit_NumberNode(self, node: NumberNode, context: Context, insideLoop: bool) -> tuple[Number, RTError]:
		return Number(node.token.value, node.position.copy(), context), None

	def visit_StringNode(self, node: StringNode, context: Context, insideLoop: bool) -> tuple[String, RTError]:
		return String(node.token.value, node.position.copy(), context), None

	def visit_BinaryOperationNode(self, node: BinaryOperationNode, context: Context, insideLoop: bool) -> tuple[Number, RTError]:
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
		elif node.operationToken.type == TokenTypes.POWER:
			result, error = left.power(right, position)
		elif node.operationToken.type == TokenTypes.MODULUS:
			result, error = left.modulus(right, position)
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
		elif node.operationToken.isKeyword("in"):
			result, error = right.hasValue(left, position)
		else:
			raise Exception(f"{node.operationToken.type} is not implemented!")

		if error:
			return None, error
		
		return result, None

	def visit_UnaryOperationNode(self, node: UnaryOperationNode, context: Context, insideLoop: bool) -> tuple[Number, RTError]:
		number, error = self.visit(node.expression, context)
		if error:
			return None, error

		position = node.operationToken.position.start.createStartEndPosition(node.expression.position.end)

		if node.operationToken.type == TokenTypes.MINUS:
			number, error = number.multiplied(Number(-1, number.position.copy(), context), position)
		elif node.operationToken.type == TokenTypes.PLUS:
			number, error = number.multiplied(Number(1, number.position.copy(), context), position)
		elif node.operationToken.isKeyword("not"):
			number, error = number.notted(position)
		else:
			raise f"{node.operationToken.type} is not implemented!"

		return number, None

	def visit_VariableAccessNode(self, node: VariableAccessNode, context: Context, insideLoop: bool) -> tuple[Number,  RTError]:
		value, error = context.variableTable.lookupVariable(node.token.value, node.position.copy())
		if error:
			return None, error

		value.position = node.position.copy()

		return value, None

	def visit_VariableAssignNode(self, node: VariableAssignNode, context: Context, insideLoop: bool) -> tuple[Number,  RTError]:
		result, error = self.visit(node.valueNode, context)
		if error:
			return None, error
			
		assignTo = result
		if node.type == "+=":
			variableValue, error = context.variableTable.lookupVariable(node.token.value, node.token.position.copy())
			if error:
				return None, error

			assignTo, error = variableValue.added(assignTo, node.position.copy())
			if error:
				return None, error
		elif node.type == "-=":
			variableValue, error = context.variableTable.lookupVariable(node.token.value, node.token.position.copy())
			if error:
				return None, error

			assignTo, error = variableValue.subtracted(assignTo, node.position.copy())
			if error:
				return None, error
		elif node.type == "*=":
			variableValue, error = context.variableTable.lookupVariable(node.token.value, node.token.position.copy())
			if error:
				return None, error

			assignTo, error = variableValue.multiplied(assignTo, node.position.copy())
			if error:
				return None, error
		elif node.type == "/=":
			variableValue, error = context.variableTable.lookupVariable(node.token.value, node.token.position.copy())
			if error:
				return None, error

			assignTo, error = variableValue.divided(assignTo, node.position.copy())
			if error:
				return None, error
			
		value, error = context.variableTable.assignVariable(node.token.value, assignTo, node.position.copy())
		if error:
			return None, error

		return value, None

	def visit_VariableDeclareNode(self, node: VariableDeclareNode, context: Context, insideLoop: bool) -> tuple[Number,  RTError]:
		isConstant = node.declareToken.isKeyword("const")

		result, error = self.visit(node.valueNode, context)
		if error:
			return None, error

		value, error = context.variableTable.declareVariable(node.token.value, result, isConstant, node.position.copy())
		if error:
			return None, error

		return value, None
	
	def visit_WhileNode(self, node: WhileNode, context: Context, insideLoop: bool) -> tuple[Number,  RTError]:
		condition, error = self.visit(node.condition, context)
		if error:
			return None, error

		conditionBoolean, error = condition.toBoolean(node.condition.position.copy())
		if error:
			return None, error

		while conditionBoolean.value:
			breakLoop = False
			continueLoop = False

			for statement in node.body:
				if isinstance(statement, ContinueNode):
					continue
				elif isinstance(statement, BreakNode):
					break

				statementVisited, error = self.visit(statement, context, True)
				if error: 
					return None, error

				if statementVisited.breakLoop:
					breakLoop = True
					break
				elif statementVisited.continueLoop:
					continueLoop = True
					break

			if breakLoop:
				break

			condition, error = self.visit(node.condition, context)
			if error:
				return None, error

			conditionBoolean, error = condition.toBoolean(node.condition.position.copy())
			if error:
				return None, error

		return Null(node.position.copy(), context), None

	def visit_ForNode(self, node: ForNode, context: Context, insideLoop: bool) -> tuple[Number,  RTError]:
		iteratorVisited, error = self.visit(node.iterator, context)
		if error:
			return None, error

		if not isinstance(iteratorVisited, List):
			return None, InvalidIteratorError(node.iterator.position.copy(), context)

		if node.item.value in context.variableTable.variables.keys():
			variableAssigned, error = context.variableTable.assignVariable(node.item.value, Null(node.item.position.copy(), context), node.item.position.copy())
			if error:
				return None, error
		else:
			variableDeclared, error = context.variableTable.declareVariable(node.item.value, Null(node.item.position.copy(), context), False, node.item.position.copy())
			if error:
				return None, error

		for item in iteratorVisited.value:
			variableAssigned, error = context.variableTable.assignVariable(node.item.value, item, node.item.position.copy())

			breakLoop = False
			continueLoop = False

			for statement in node.body:
				if isinstance(statement, ContinueNode):
					continue
				elif isinstance(statement, BreakNode):
					break

				statementVisited, error = self.visit(statement, context, True)
				if error: 
					return None, error

				if statementVisited.breakLoop:
					breakLoop = True
					break
				elif statementVisited.continueLoop:
					continueLoop = True
					break

			if breakLoop:
				break

		return Null(node.position.copy(), context), None


	def visit_FunctionCallNode(self, node: FunctionCallNode, context: Context, insideLoop: bool) -> tuple[Number,  RTError]:
		func, error = self.visit(node.func, context)
		if error:
			return None, error

		argumentsVisited = []
		for argument in node.arguments:
			argumentVisited, error = self.visit(argument, context)
			if error:
				return None, error

			argumentsVisited.append(argumentVisited)

		returnValue = None
		
		if isinstance(func, Function):
			if len(func.arguments) != len(node.arguments):
				return None, ArgumentError(len(func.arguments), len(node.arguments), func.name, node.position.copy(), context)

			executeContext = Context(f"<function {func.name}>", func.context)
			executeContext.setVariableTable(VariableTable())

			interpreter = Interpreter(func.body, True, True)
			interpreter.addDefaultVariables(executeContext)

			for argumentName, argument in zip(func.arguments, argumentsVisited):
				executeContext.variableTable.declareVariable(argumentName, argument, False, argument.position)

			_, error = interpreter.interpret(executeContext)
			if error:
				return None, error

			returnValue = interpreter.returnValue

			if not returnValue:
				returnValue = Null(node.position.copy(), context)

			returnValue.position = node.position.copy()

			return returnValue, None

		elif isinstance(func, BuiltInFunction):
			returnValue, error = func.execute(argumentsVisited, node.position.copy())
			if error:
				return None, error

		elif isinstance(func, PythonFunction):
			returnValue, error = func.execute(argumentsVisited, node.position.copy())
			if error:
				return None, error
			
			returnValueConverted, error = self.convertValue(returnValue, func.position.copy(), context, func.path)
			if error:
				return None, error

			return returnValueConverted, None

		else:
			returnValue, error = func.execute(argumentsVisited, node.position.copy())
			if error:
				return None, error
			return returnValue, None

		return returnValue, None

	def visit_ListNode(self, node: ListNode, context: Context, insideLoop: bool) -> tuple[Number,  RTError]:
		expressions = []

		for expression in node.expressions:
			expressionVisited, error = self.visit(expression, context)
			if error:
				return None, error

			expressions.append(expressionVisited)

		return List(expressions, node.position.copy(), context), None
		
	def visit_GetItemNode(self, node: GetItemNode, context: Context, insideLoop: bool) -> tuple[RuntimeValue,  RTError]:
		variable, error = self.visit(node.variable, context)
		if error:
			return None, error

		item, error = self.visit(node.item, context)

		value, error = variable.getItem(item, node.position.copy())
		if error:
			return None, error

		return value, None

	def visit_GetAttributeNode(self, node: GetAttributeNode, context: Context, insideLoop: bool) -> tuple[RuntimeValue,  RTError]:
		variable, error = self.visit(node.variable, context)
		if error:
			return None, error

		item, error = self.visit(node.item, context)

		value, error = variable.getAttribute(item, node.position.copy())
		if error:
			return None, error

		return value, None

	def visit_SetItemNode(self, node: SetItemNode, context: Context, insideLoop: bool) -> tuple[None,  RTError]:
		variable, error = self.visit(node.variable, context)
		if error:
			return None, error

		item, error = self.visit(node.item, context)

		value, error = self.visit(node.value, context)

		_, error = variable.setItem(item, value, node.position.copy())
		if error:
			return None, error

		return Null(node.position.copy(), context), None

	def visit_FunctionDefineNode(self, node: FunctionDefineNode, context: Context, insideLoop: bool) -> tuple[Function,  RTError]:
		func = Function(node.variable, node.arguments, node.body, node.position, node.anonymous, context)

		if not node.anonymous:
			value, error = context.variableTable.declareVariable(node.variable, func, True, node.position.copy())
			if error:
				return None, error
			return Null(node.position.copy(), context), None

		return func, None

	def visit_ReturnNode(self, node: ReturnNode, context: Context, insideLoop: bool) -> tuple[RuntimeValue,  RTError]:
		if not self.isAFunction:
			return None, ReturnOutsideFunctionError(node.position.copy(), context)

		if node.value:
			value, error = self.visit(node.value, context)
			if error:
				return None, error

			self.returnValue = value
			return value, None

		self.returnValue = Null(node.position.copy(), context)
		return self.returnValue, None

	def visit_IfContainerNode(self, node: IfContainerNode, context: Context, insideLoop: bool) -> tuple[Null,  RTError]:
		ifCondition, error = self.visit(node.ifNode.condition, context)
		if error:
			return None, error

		ifConditionAsBoolean, error = ifCondition.toBoolean(node.ifNode.condition.position.copy())
		if error:
			return None, error

		if ifConditionAsBoolean.value:
			for statement in node.ifNode.body:
				statementVisited, error = self.visit(statement, context, insideLoop)
				if error:
					return None, error

				if statementVisited.breakLoop:
					return Null(node.ifNode.position.copy(), context).setBreak(), None
				elif statementVisited.continueLoop:
					return Null(node.ifNode.position.copy(), context).setContinue(), None

			return Null(node.ifNode.position.copy(), context), None

		for elseIfNode in node.elseIfNodes:
			elseIfCondition, error = self.visit(elseIfNode.condition, context)
			if error:
				return None, error

			elseIfConditionAsBoolean, error = elseIfCondition.toBoolean(elseIfNode.condition.position.copy())
			if error:
				return None, error

			if not elseIfConditionAsBoolean.value:
				continue
			
			for statement in elseIfNode.body:
				statementVisited, error = self.visit(statement, context, insideLoop)
				if error:
					return None, error 

				if statementVisited.breakLoop:
					return Null(node.ifNode.position.copy(), context).setBreak(), None
				elif statementVisited.continueLoop:
					return Null(node.ifNode.position.copy(), context).setContinue(), None

			return Null(elseIfNode.position.copy(), context), None

		if node.elseNode:
			for statement in node.elseNode.body:
				statementVisited, error = self.visit(statement, context, insideLoop)
				if error:
					return None, error
				
				if statementVisited.breakLoop:
					return Null(node.ifNode.position.copy(), context).setBreak(), None
				elif statementVisited.continueLoop:
					return Null(node.ifNode.position.copy(), context).setContinue(), None

			return Null(node.elseNode.position.copy(), context), None
		return Null(node.position.copy(), context), None

	def visit_ImportNode(self, node: ImportNode, context: Context, insideLoop: bool) -> tuple[Null,  RTError]:
		moduleName, error = self.visit(node.moduleName, context)
		if error:
			return None, error

		if not isinstance(moduleName, String):
			return None, ValueError_(["string"], moduleName.__class__.__name__, moduleName.position.copy(), context)

		imported, error = self.importModule(moduleName.value, context, node.position.copy(), node.asName)
		if error:
			return None, error

		return Null(node.position.copy(), context), None
		
	def visit_DictionaryNode(self, node: DictionaryNode, context: Context, insideLoop: bool) -> tuple[Null,  RTError]:
		valuesVisited = {}

		for key, value in node.expressions.items():
			keyVisited, error = self.visit(key, context)
			if error:
				return None, error

			valueVisited, error = self.visit(value, context)
			if error:
				return None, error

			valuesVisited[keyVisited] = valueVisited

		return Dictionary(valuesVisited, node.position.copy(), context), None

	def visit_BreakNode(self, node: DictionaryNode, context: Context, insideLoop: bool) -> tuple[Null,  RTError]:
		if not insideLoop:
			return None, BreakOutsideLoopError(node.position.copy(), context)

		newNode = Null(node.position.copy(), context)
		newNode.breakLoop = True
		return newNode, None

	def visit_ContinueNode(self, node: DictionaryNode, context: Context, insideLoop: bool) -> tuple[Null,  RTError]:
		if not insideLoop:
			return None, ContinueOutsideLoopError(node.position.copy(), context)

		newNode = Null(node.position.copy(), context)
		newNode.continueLoop = True
		return newNode, None
			
	def visit_RangeNode(self, node: RangeNode, context: Context, insideLoop: bool) -> tuple[List,  RTError]:
		startValue, error = self.visit(node.start, context)
		if error:
			return None, error

		stopValue, error = self.visit(node.end, context)
		if error:
			return None, error

		stepValue, error = self.visit(node.step, context)
		if error:
			return None, error
		
		if not isinstance(startValue, Number) or "." in str(startValue.value):
			return None, ValueError_(["number(integer)"], startValue.__class__.__name__, startValue.position.copy(), context)
		elif not isinstance(stopValue, Number) or "." in str(stopValue.value):
			return None, ValueError_(["number(integer)"], stopValue.__class__.__name__, stopValue.position.copy(), context)
		elif not isinstance(stepValue, Number) or "." in str(stepValue.value):
			return None, ValueError_(["number(integer)"], stepValue.__class__.__name__, stepValue.position.copy(), context)

		rangeAsRange = range(startValue.value, stopValue.value, stepValue.value)
		
		def toNumber(n: int):
			return Number(n, node.position.copy(), context)

		return List(list(map(toNumber, rangeAsRange)), node.position.copy(), context), None