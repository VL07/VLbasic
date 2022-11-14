########################################
#	IMPORTS
########################################

from __future__ import annotations
from .utils import StartEndPosition
from .contextclass import Context
from .error import RTError
from typing import Callable

########################################
#	INTERPRETER
########################################

class RuntimeValue:
	def __init__(self, value: int | float, position: StartEndPosition, context: Context) -> None:
		self.value = value
		self.position = position
		self.context = context

	def __repr__(self) -> str:
		return f"RUNTIME_VALUE({self.value})"

	def added(self, to: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return None, RTError(f"Unable to add {type(self).__name__} to {type(to).__name__}", position.copy(), self.context)

	def subtracted(self, by: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return None, RTError(f"Unable to subtract {type(self).__name__} by {type(by).__name__}", position.copy(), self.context)

	def multiplied(self, by: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return None, RTError(f"Unable to multiply {type(self).__name__} by {type(by).__name__}", position.copy(), self.context)

	def divided(self, by: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return None, RTError(f"Unable to divide {type(self).__name__} by {type(by).__name__}", position.copy(), self.context)

	def equals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return None, RTError(f"Unable to check equality between {type(self).__name__} and {type(other).__name__}", position.copy(), self.context)

	def notEquals(self, other: RuntimeValue, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return None, RTError(f"Unable to check inequality between {type(self).__name__} and {type(other).__name__}", position.copy(), self.context)

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

	def toBoolean(self, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return None, RTError(f"Unable to convert a {type(self).__name__} by a Boolean", position.copy(), self.context)

	def execute(self, arguments: list[RuntimeValue], position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return None, RTError(f"Unable to call a {type(self).__name__}", position.copy(), self.context)

class Number(RuntimeValue):
	def __init__(self, value: int | float, position: StartEndPosition, context: Context) -> None:
		self.value = value
		self.position = position
		self.context = context

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
		
		return super().divided()

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

class Boolean(RuntimeValue):
	def __init__(self, value: bool, position: StartEndPosition, context: Context) -> None:
		self.value = value
		self.position = position
		self.context = context

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

	def notted(self, position: StartEndPosition) -> tuple[Boolean, RTError]:
		return Boolean(not self.value, position.copy(), self.context), None

	def toBoolean(self, position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		return Boolean(self.value, self.position.copy(), self.context), None

class Null(RuntimeValue):
	def __init__(self, position: StartEndPosition, context: Context) -> None:
		self.position = position
		self.context = context
		self.value = "NULL"

	def __repr__(self) -> str:
		return f"NULL()"

class BuiltInFunction(RuntimeValue):
	def __init__(self, name: str, executeFunction: Callable[[list[RuntimeValue], Context], tuple[RuntimeValue, RuntimeError]], position: StartEndPosition, context: Context) -> None:
		self.name = name
		self.position = position
		self.context = context
		self.executeFunction = executeFunction

	def execute(self, arguments: list[RuntimeValue], position: StartEndPosition) -> tuple[RuntimeValue, RTError]:
		executeContext = Context(self.name, self.context)

		returnValue, error = self.executeFunction(arguments, executeContext)
		if error:
			return None, error

		returnValue.context = self.context
		returnValue.position = position.copy()
		
		return returnValue, None

	def __repr__(self) -> str:
		return f"BUILT_IN_FUNCTION({self.name}"