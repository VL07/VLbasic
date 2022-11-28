########################################
#	IMPORTS
########################################

from __future__ import annotations
from .utils import StartEndPosition, NUMBERS
from .contextclass import Context, VariableTable
from .error import RTError
from typing import Callable
from .statementclass import ExpressionNode

########################################
#	INTERPRETER
########################################

class RuntimeValue:
	def __init__(self, value: int | float, position: StartEndPosition, context: Context) -> None:
		self.value = value
		self.position = position
		self.context = context
		self.continueLoop = False
		self.breakLoop = False

	def __repr__(self) -> str:
		return f"RUNTIME_VALUE({self.value})"
	
	def setContinue(self, value: bool = True) -> RuntimeValue:
		self.continueLoop = value
		return self

	def setBreak(self, value: bool = True) -> RuntimeValue:
		self.breakLoop = value
		return self

	def added(self, to: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return None, RTError(f"Unable to add {type(self).__name__} to {type(to).__name__}", position.copy(), self.context)

	def subtracted(self, by: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return None, RTError(f"Unable to subtract {type(self).__name__} by {type(by).__name__}", position.copy(), self.context)

	def multiplied(self, by: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return None, RTError(f"Unable to multiply {type(self).__name__} by {type(by).__name__}", position.copy(), self.context)

	def divided(self, by: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return None, RTError(f"Unable to divide {type(self).__name__} by {type(by).__name__}", position.copy(), self.context)

	def power(self, by: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return None, RTError(f"Unable to power {type(self).__name__} by {type(by).__name__}", position.copy(), self.context)

	def modulus(self, by: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return None, RTError(f"Unable to modulus {type(self).__name__} by {type(by).__name__}", position.copy(), self.context)

	def equals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return Boolean(False, position.copy(), self.context), None

	def notEquals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return Boolean(True, position.copy(), self.context), None

	def graterThan(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return None, RTError(f"Unable to compare size between {type(self).__name__} and {type(other).__name__}", position.copy(), self.context)

	def lessThan(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return None, RTError(f"Unable to compare size between {type(self).__name__} and {type(other).__name__}", position.copy(), self.context)

	def graterThanEquals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return None, RTError(f"Unable to compare size between {type(self).__name__} and {type(other).__name__}", position.copy(), self.context)

	def lessThanEquals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return None, RTError(f"Unable to compare size between {type(self).__name__} and {type(other).__name__}", position.copy(), self.context)

	def notted(self, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return None, RTError(f"Unable to invert {type(self).__name__}", position.copy(), self.context)

	def toBoolean(self, position: StartEndPosition) -> tuple[Boolean, RTError]:
		return None, RTError(f"Unable to convert a {type(self).__name__} by a Boolean", position.copy(), self.context)

	def toString(self, position: StartEndPosition) -> tuple[String, RTError]:
		return None, RTError(f"Unable to convert a {type(self).__name__} by a String", position.copy(), self.context)

	def toNumber(self, position: StartEndPosition) -> tuple[Number, RTError]:
		return None, RTError(f"Unable to convert a {type(self).__name__} by a Number", position.copy(), self.context)

	def execute(self, arguments: list[RuntimeValue], position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return None, RTError(f"Unable to call a {type(self).__name__}", position.copy(), self.context)

	def getItem(self, item: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return None, RTError(f"Unable to get item {str(item)} of {type(self).__name__}", position.copy(), self.context)

	def setItem(self, item: RuntimeValue, value: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return None, RTError(f"Unable to set item {str(item)} of {type(self).__name__} to {str(value)}", position.copy(), self.context)

	def getLength(self, position: StartEndPosition) -> tuple[Number, RTError]:
		return None, RTError(f"Unable to get length of a {type(self).__name__}", position.copy(), self.context)

class Number(RuntimeValue):
	def __init__(self, value: int | float, position: StartEndPosition, context: Context) -> None:
		self.value = value
		self.position = position
		self.context = context
		self.continueLoop = False
		self.breakLoop = False

	def __repr__(self) -> str:
		return f"NUMBER({self.value})"

	def added(self, to: Number | RuntimeValue, position: StartEndPosition) -> tuple[Number, RTError]:
		if isinstance(to, Number):
			return Number(self.value + to.value, position.copy(), self.context), None
		elif isinstance(to, Boolean):
			return Number(self.value + (1 if to.value else 0), position.copy(), self.context), None

		return super().added(to, position.copy())

	def subtracted(self, by: Number | RuntimeValue, position: StartEndPosition) -> tuple[Number, RTError]:
		if isinstance(by, Number):
			return Number(self.value - by.value, position.copy(), self.context), None
		elif isinstance(by, Boolean):
			return Number(self.value - (1 if by.value else 0), position.copy(), self.context), None

		return super().subtracted(by, position.copy())

	def multiplied(self, by: Number | RuntimeValue, position: StartEndPosition) -> tuple[Number, RTError]:
		if isinstance(by, Number):
			return Number(self.value * by.value, position.copy(), self.context), None
		elif isinstance(by, Boolean):
			return Number(self.value * (1 if by.value else 0), position.copy(), self.context), None
		elif isinstance(by, String):
			return String(by.value * self.value, position.copy(), self.context), None
		
		return super().multiplied(by, position)

	def divided(self, by: Number | RuntimeValue, position: StartEndPosition) -> tuple[Number, RTError]:
		if isinstance(by, Number):
			if by.value == 0:
				return None, RTError("Cannot divide by zero", position, self.context)

			return Number(self.value / by.value, position.copy(), self.context), None
		elif isinstance(bool, Boolean):
			if not by.value:
				return None, RTError("Cannot divide by zero", position.copy(), self.context)
			return Number(self.value - (1 if by.value else 0), position.copy(), self.context), None
		
		return super().divided(by, position)

	def power(self, by: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(by, Number):
			return Number(self.value ** by.value, position.copy(), self.context), None
		
		return super().divided(by, position)

	def modulus(self, by: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(by, Number):
			return Number(self.value % by.value, position.copy(), self.context), None
		
		return super().divided(by, position)

	def equals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(other, Number):
			return Boolean(self.value == other.value, position, self.context), None
		elif isinstance(other, Boolean):
			node, error = self.toBoolean(position.copy())
			if error:
				return None, error

			return Boolean(node.value == other.value, position.copy(), self.context), None
		
		return Boolean(False, position.copy(), self.context), None

	def notEquals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(other, Number):
			return Boolean(self.value != other.value, position, self.context), None
		elif isinstance(other, Boolean):
			node, error = self.toBoolean(position.copy())
			if error:
				return None, error

			return Boolean(node.value != other.value, position.copy(), self.context), None
		
		return Boolean(True, position.copy(), self.context), None

	def graterThan(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(other, Number):
			return Boolean(self.value > other.value, position, self.context), None
		
		return super().graterThan(other, position)

	def lessThan(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(other, Number):
			return Boolean(self.value < other.value, position, self.context), None
		
		return super().lessThan(other, position)

	def graterThanEquals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(other, Number):
			return Boolean(self.value >= other.value, position, self.context), None
		
		return super().graterThanEquals(other, position)
	
	def lessThanEquals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(other, Number):
			return Boolean(self.value <= other.value, position, self.context), None
		
		return super().lessThanEquals(other, position)

	def notted(self, position: StartEndPosition) -> tuple[Boolean, RTError]:
		asBoolean, error = self.toBoolean(position)
		if error:
			return None, error
		
		asNotBoolean, error = asBoolean.notted(position)
		if error:
			return None, error

		return asNotBoolean, None

	def toBoolean(self, position: StartEndPosition) -> tuple[Boolean, RTError]:
		return Boolean(False if self.value == 0 else True, position.copy(), self.context), None

	def toString(self, position: StartEndPosition) -> tuple[String, RTError]:
		return String(str(self.value), position.copy(), self.context), None

	def toNumber(self, position: StartEndPosition) -> tuple[Number, RTError]:
		return Number(self.value, position.copy(), self.context), None

class String(RuntimeValue):
	def __init__(self, value: str, position: StartEndPosition, context: Context) -> None:
		self.value = value
		self.position = position
		self.context = context
		self.continueLoop = False
		self.breakLoop = False

	def __repr__(self) -> str:
		return f"STRING({self.value})" 

	def added(self, to: Number | RuntimeValue, position: StartEndPosition) -> tuple[Number, RTError]:
		if isinstance(to, String):
			return String(self.value + to.value, position.copy(), self.context), None

		return super().added(to, position.copy())

	def multiplied(self, by: Number | RuntimeValue, position: StartEndPosition) -> tuple[Number, RTError]:
		if isinstance(by, Number):
			return String(self.value * by.value, position.copy(), self.context), None
		
		return super().multiplied(by, position)

	def equals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(other, String):
			return Boolean(self.value == other.value, position, self.context), None
		
		return Boolean(False, position.copy(), self.context), None

	def notEquals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(other, Number):
			return Boolean(self.value != other.value, position, self.context), None
		
		return Boolean(True, position.copy(), self.context), None

	def notted(self, position: StartEndPosition) -> tuple[Boolean, RTError]:
		asBoolean, error = self.toBoolean(position)
		if error:
			return None, error
		
		asNotBoolean, error = asBoolean.notted(position)
		if error:
			return None, error

		return asNotBoolean, None

	def toBoolean(self, position: StartEndPosition) -> tuple[Boolean, RTError]:
		return Boolean(False if len(self.value) == 0 else True, position.copy(), self.context), None

	def toString(self, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return String(str(self.value), position.copy(), self.context), None

	def getItem(self, item: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(item, Number):
			length, error = self.getLength(position)
			if error:
				return None, error

			if item.value + 1 > length.value:
				return None, RTError("String is out of range", position.copy(), self.context)

			return String(self.value[item.value], position.copy(), self.context), None

		return super().getItem(item, position)

	def getLength(self, position: StartEndPosition) -> tuple[Number, RTError]:
		return Number(len(self.value), position.copy(), self.context), None

	def toNumber(self, position: StartEndPosition) -> tuple[Number, RTError]:
		dots = 0

		for i, character in enumerate(self.value):
			if character in NUMBERS:
				continue
			elif character == "." and i > 0 and dots == 0:
				dots += 1
				continue

			return None, RTError("Unable to convert this String, to a number", position.copy(), self.context)

		if not dots:
			return Number(int(self.value), position.copy(), self.context), None
		return Number(float(self.value), position.copy(), self.context), None

class Boolean(RuntimeValue):
	def __init__(self, value: bool, position: StartEndPosition, context: Context) -> None:
		self.value = value
		self.position = position
		self.context = context
		self.continueLoop = False
		self.breakLoop = False

	def __repr__(self) -> str:
		return f"BOOLEAN({self.value})"

	def added(self, to: Boolean | RuntimeValue, position: StartEndPosition) -> tuple[Number, RTError]:
		if isinstance(to, Number):
			return Number((1 if self.value else 0) + to.value, position.copy(), self.context), None
		
		return super().added(to, position)

	def subtracted(self, by: Number | RuntimeValue, position: StartEndPosition) -> tuple[Number, RTError]:
		if isinstance(by, Number):
			return Number((1 if self.value else 0) - by.value, position.copy(), self.context), None
		
		return super().subtracted(by, position)

	def multiplied(self, by: Number | RuntimeValue, position: StartEndPosition) -> tuple[Number, RTError]:
		if isinstance(by, Number):
			return Number((1 if self.value else 0) * by.value, position.copy(), self.context), None
		
		return super().multiplied(by, position)

	def divided(self, by: Number | RuntimeValue, position: StartEndPosition) -> tuple[Number, RTError]:
		if isinstance(by, Number):
			if by.value == 0:
				return None, RTError("Cannot divide by zero", position.copy(), self.context)

			return Number((1 if self.value else 0) / by.value, position.copy(), self.context), None
		
		return super().divided(by, position)

	def equals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(other, Boolean):
			return Boolean(self.value == other.value, position.copy(), self.context), None

		return super().equals(other, position)

	def notEquals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(other, Boolean):
			return Boolean(self.value != other.value, position.copy(), self.context), None

		return super().notEquals(other, position)

	def notted(self, position: StartEndPosition) -> tuple[Boolean, RTError]:
		return Boolean(not self.value, position.copy(), self.context), None

	def toBoolean(self, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return Boolean(self.value, self.position.copy(), self.context), None

	def toString(self, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return String("TRUE" if self.value else "FALSE", position.copy(), self.context), None

	def toNumber(self, position: StartEndPosition) -> tuple[Number, RTError]:
		return Number(1 if self.value else 0, position.copy(), self.context), None

class Null(RuntimeValue):
	def __init__(self, position: StartEndPosition, context: Context) -> None:
		self.position = position
		self.context = context
		self.value = "NULL"
		self.continueLoop = False
		self.breakLoop = False

	def __repr__(self) -> str:
		return f"NULL()"

	def equals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(other, Null):
			return Boolean(True, position.copy(), self.context), None

		return super().equals(other, position)

	def notEquals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(other, Null):
			return Boolean(False, position.copy(), self.context), None

		return super().notEquals(other, position)

	def toString(self, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return String("NULL" if self.value else "FALSE", position.copy(), self.context), None

	def toBoolean(self, position: StartEndPosition) -> tuple[Boolean, RTError]:
		return Boolean(False, position.copy(), self.context), None

class List(RuntimeValue):
	def __init__(self, expressions: list[RuntimeValue], position: StartEndPosition, context: Context) -> None:
		self.position = position
		self.context = context
		self.value = expressions
		self.continueLoop = False
		self.breakLoop = False

	def __repr__(self) -> str:
		return f"LIST({self.value})"

	def toString(self, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		listAsString = "["

		for expression in self.value:
			expressionAsString, error = expression.toString(position.copy())
			if error:
				return None, error

			listAsString += expressionAsString.value + ", "

		if len(self.value):
			listAsString = listAsString[:-2] + "]"
		else:
			listAsString = "[]"

		return String(listAsString, position.copy(), self.context), None

	def equals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(other, List):
			if len(self.value) != len(other.value):
				return Boolean(False, position.copy(), self.context), None

			for item1, item2 in zip(self.value, other.value):
				if not item1.equals(item2, position.copy()):
					return Boolean(False, position.copy(), self.context), None

			return Boolean(True, position.copy(), self.context), None

		return super().equals(other, position)

	def notEquals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(other, List):
			if len(self.value) != len(other.value):
				return Boolean(True, position.copy(), self.context), None

			for item1, item2 in zip(self.value, other.value):
				if not item1.equals(item2, position.copy()):
					return Boolean(True, position.copy(), self.context), None

			return Boolean(False, position.copy(), self.context), None

		return super().notEquals(other, position)

	def getItem(self, item: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(item, Number):
			length, error = self.getLength(position)
			if error:
				return None, error

			if item.value + 1 > length.value or item.value < 0:
				return None, RTError("List is out of range", position.copy(), self.context)

			return self.value[item.value], None

		return super().getItem(item, position)

	def setItem(self, item: RuntimeValue, value: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(item, Number):
			length, error = self.getLength(position)
			if error:
				return None, error

			if item.value + 1 > length.value or item.value < 0:
				return None, RTError("List is out of range", position.copy(), self.context)

			self.value[item.value] = value

			return Null(position.copy(), self.context), None

		return super().getItem(item, position)

	def getLength(self, position: StartEndPosition) -> tuple[Number, RTError]:
		return Number(len(self.value), position.copy(), self.context), None

	def toBoolean(self, position: StartEndPosition) -> tuple[Boolean, RTError]:
		return Boolean(False if len(self.value) == 0 else True, position.copy(), self.context), None

class Dictionary(RuntimeValue):
	def __init__(self, expressions: dict[RuntimeValue, RuntimeValue], position: StartEndPosition, context: Context) -> None:
		self.position = position
		self.context = context
		self.value = expressions
		self.continueLoop = False
		self.breakLoop = False

	def __repr__(self) -> str:
		return f"DICTIONARY({self.value})"

	def toString(self, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		dictionaryAsString = "{"

		for key, value in self.value.items():
			keyAsString, error = key.toString(position.copy())
			if error:
				return None, error

			valueAsString, error = value.toString(position.copy())
			if error:
				return None, error

			dictionaryAsString += f"{keyAsString.value}: {valueAsString.value}, "

		if len(self.value):
			dictionaryAsString = dictionaryAsString[:-2] + "}"
		else:
			dictionaryAsString = "{}"

		return String(dictionaryAsString, position.copy(), self.context), None

	def equals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(other, Dictionary):
			if len(self.value) != len(other.value):
				return Boolean(False, position.copy(), self.context), None

			for item1, item2 in zip(self.value.keys(), other.value.keys()):
				if not item1.equals(item2, position.copy()):
					return Boolean(False, position.copy(), self.context), None

				if not self.value[item1].equals(other.value[item2], position.copy()):
					return Boolean(False, position.copy(), self.context), None

			return Boolean(True, position.copy(), self.context), None

		return super().equals(other, position)

	def notEquals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(other, Dictionary):
			if len(self.value) != len(other.value):
				return Boolean(True, position.copy(), self.context), None

			for item1, item2 in zip(self.value.keys(), other.value.keys()):
				if not item1.equals(item2, position.copy(), position.copy()):
					return Boolean(True, position.copy(), self.context), None

				if not self.value[item1].equals(other.value[item2], position.copy()):
					return Boolean(True, position.copy(), self.context), None

			return Boolean(False, position.copy(), self.context), None

		return super().equals(other, position)

	def getItem(self, item: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		for key in self.value.keys():
			equals, error = item.equals(key, position.copy())
			if error:
				return None, error

			if equals.value:
				return self.value[key], None

		return None, RTError(f"Invalid key {item}", position.copy(), self.context)

	def setItem(self, item: RuntimeValue, value: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		self.value[item] = value

		return Null(position.copy(), self.context), None

	def getLength(self, position: StartEndPosition) -> tuple[Number, RTError]:
		return Number(len(self.value), position.copy(), self.context), None

	def toBoolean(self, position: StartEndPosition) -> tuple[Boolean, RTError]:
		return Boolean(False if len(self.value) == 0 else True, position.copy(), self.context), None

class BuiltInFunction(RuntimeValue):
	def __init__(self, name: str, executeFunction: Callable[[list[RuntimeValue], Context], tuple[RuntimeValue, RTError]], position: StartEndPosition, context: Context) -> None:
		self.name = name
		self.position = position
		self.context = context
		self.executeFunction = executeFunction
		self.value = "BUILT_IN_FUNCTION"
		self.continueLoop = False
		self.breakLoop = False

	def execute(self, arguments: list[RuntimeValue], position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		executeContext = Context(self.name, self.context)

		returnValue, error = self.executeFunction(arguments, executeContext)
		if error:
			error.position = position.copy()
			error.context = self.context
			return None, error

		returnValue.context = self.context
		returnValue.position = position.copy()
		
		return returnValue, None

	def __repr__(self) -> str:
		return f"BUILT_IN_FUNCTION({self.name})"

	def equals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(other, BuiltInFunction):
			return Boolean(self == other, position.copy())

		return super().equals(other, position)

	def notEquals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(other, BuiltInFunction):
			return Boolean(self != other, position.copy())

		return super().notEquals(other, position)

	def toString(self, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return String(f"{self.name}()", position.copy(), self.context), None

class PythonFunction(RuntimeValue):
	def __init__(self, name: str, executeFunction: Callable[[list[RuntimeValue], Context, RTError], tuple[RuntimeValue, RTError]], position: StartEndPosition, context: Context, path: str, parameters: list[int, int]) -> None:
		self.name = name
		self.position = position
		self.context = context
		self.executeFunction = executeFunction
		self.value = "BUILT_IN_FUNCTION"
		self.continueLoop = False
		self.breakLoop = False
		self.path = path
		self.parameters = parameters

	def execute(self, arguments: list[RuntimeValue], position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		executeContext = Context(self.name, self.context)

		if len(arguments) < self.parameters[0] or len(arguments) > self.parameters[1]:
			return None, RTError(f"Function {self.name} expected {str(self.parameters[0])} to {str(self.parameters[1])} arguments, not {str(len(arguments))}", position.copy(), self.context)

		returnValue, error = self.executeFunction(arguments, executeContext, RTError)
		if error:
			error.position = position.copy()
			error.context = self.context
			return None, error
		
		return returnValue, None

	def __repr__(self) -> str:
		return f"PYTHON_FUNCTION({self.name})"

	def equals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(other, PythonFunction):
			return Boolean(self == other, position.copy())

		return super().equals(other, position)

	def notEquals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(other, PythonFunction):
			return Boolean(self != other, position.copy())

		return super().notEquals(other, position)

	def toString(self, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return String(f"{self.name}()", position.copy(), self.context), None

class Function(RuntimeValue):
	def __init__(self, name: str, arguments: list[str], body: list[ExpressionNode], position: StartEndPosition, anonymous: bool, context: Context) -> None:
		self.name = name
		self.arguments = arguments
		self.body = body
		self.position = position
		self.context = context
		self.value = "FUNCTION"
		self.anonymous = anonymous
		self.continueLoop = False
		self.breakLoop = False

	def __repr__(self) -> str:
		return f"FUNCTION({self.name})"

	def equals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(other, Function):
			return Boolean(self == other, position.copy())

		return super().equals(other, position)

	def notEquals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		if isinstance(other, Function):
			return Boolean(self != other, position.copy())

		return super().notEquals(other, position)

	def toString(self, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return String(f"{self.name}()", position.copy(), self.context), None