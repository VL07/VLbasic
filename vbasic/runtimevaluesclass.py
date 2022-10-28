########################################
#	IMPORTS
########################################

from __future__ import annotations
from .utils import StartEndPosition
from .contextclass import Context
from .error import RTError
from .tokenclass import Token

########################################
#	INTERPRETER
########################################

class RuntimeValue:
	def __init__(self, position: StartEndPosition) -> None:
		self.position = position
		self.value = None

class Number(RuntimeValue):
	def __init__(self, value: int | float, position: StartEndPosition, context: Context) -> None:
		self.value = value
		self.position = position
		self.context = context

	def __repr__(self) -> str:
		return f"NUMBER({self.value})"

	def added(self, to: Number | RuntimeValue) -> tuple[Number, RTError]:
		if isinstance(to, Number):
			return Number(self.value + to.value, self.position.start.createStartEndPosition(to.position.end), self.context), None
		elif isinstance(to, Boolean):
			return Number(self.value + (1 if to.value else 0), self.position.start.createStartEndPosition(to.position.end), self.context), None
		else:
			return None, RTError(f"Unable to add Number to {type(to).__name__}", self.position.start.createStartEndPosition(to.position.end), self.context)

	def subtracted(self, by: Number | RuntimeValue) -> tuple[Number, RTError]:
		if isinstance(by, Number):
			return Number(self.value - by.value, self.position.start.createStartEndPosition(by.position.end), self.context), None
		elif isinstance(by, Boolean):
			return Number(self.value - (1 if by.value else 0), self.position.start.createStartEndPosition(by.position.end), self.context), None
		else:
			return None, RTError(f"Unable to subtract Number by {type(by).__name__}", self.position.start.createStartEndPosition(by.position.end), self.context)

	def multiplied(self, by: Number | RuntimeValue) -> tuple[Number, RTError]:
		if isinstance(by, Number):
			return Number(self.value * by.value, self.position.start.createStartEndPosition(by.position.end), self.context), None
		elif isinstance(by, Boolean):
			return Number(self.value * (1 if by.value else 0), self.position.start.createStartEndPosition(by.position.end), self.context), None
		else:
			return None, RTError(f"Unable to multiply Number by {type(by).__name__}", self.position.start.createStartEndPosition(by.position.end), self.context)

	def divided(self, by: Number | RuntimeValue) -> tuple[Number, RTError]:
		if isinstance(by, Number):
			position = self.position.start.createStartEndPosition(by.position.end)
			if by.value == 0:
				return None, RTError("Cannot divide by zero", position, self.context)

			return Number(self.value / by.value, position, self.context), None
		elif isinstance(bool, Boolean):
			if not by.value:
				return None, RTError("Cannot divide by zero", position, self.context)
			return Number(self.value - (1 if by.value else 0), position, self.context), None
		else:
			return None, RTError(f"Unable to divide Number by {type(by).__name__}", position, self.context)

	def notted(self, by: Token) -> tuple[Boolean, RTError]:
		asBoolean, error = self.toBoolean()
		if error:
			return None, error
		
		asNotBoolean, error = asBoolean.notted(by)
		if error:
			return None, error

		return asNotBoolean, None

	def toBoolean(self) -> tuple[Boolean, RTError]:
		return Boolean(False if self.value == 0 else True, self.position.copy(), self.context), None

class Boolean(RuntimeValue):
	def __init__(self, value: bool, position: StartEndPosition, context: Context) -> None:
		self.value = value
		self.position = position
		self.context = context

	def __repr__(self) -> str:
		return f"BOOLEAN({self.value})"

	def notted(self, by: Token) -> tuple[Boolean, RTError]:
		return Boolean(not self.value, self.position.start.createStartEndPosition(by.position.end), self.context), None