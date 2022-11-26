########################################
#	IMPORTS
########################################

from __future__ import annotations
from .error import RTError, Error
from .utils import StartEndPosition

########################################
#	VARIABLE
########################################

class Variable:
	def __init__(self, value: any, constant: bool, builtIn: bool) -> None:
		self.constant = constant
		self.value = value
		self.builtIn = builtIn

########################################
#	VARIABLE TABLE
########################################

class VariableTable:
	def __init__(self) -> None:
		self.variables: dict[str, Variable] = {}
		self.parent: VariableTable = None
		self.context: Context = None
	
	def declareVariable(self, key: str, value: any, constant: bool, position: StartEndPosition, builtIn: bool = False) -> tuple[any, Error]:
		if key in self.variables.keys():
			return None, RTError(f"Variable {key} is already declared", position.copy(), self.context)

		self.variables[key] = Variable(value, constant, builtIn)

		self.test = "abc"

		return value, None

	def assignVariable(self, key: str, value: any, position: StartEndPosition) -> tuple[any, RTError]:
		environment, error = self.resolve(key, position)
		if error:
			return None, error

		variable = environment.variables[key]
		if variable.constant:
			return None, RTError(f"Variable {key} is a constant, and can therefor not be assigned to", position.copy(), self.context)

		variable.value = value

		return value, None

	def lookupVariable(self, key: str, position: StartEndPosition) -> tuple[any, RTError]:
		environment, error = self.resolve(key, position)
		if error:
			return None, error

		return environment.variables[key].value, None

	def resolve(self, key: str, position: StartEndPosition) -> tuple[VariableTable, RTError]:
		if key in self.variables.keys():
			return self, None

		if not self.parent:
			return None, RTError(f"Variable {key} is not defined", position.copy(), self.context)

		parentResolve, error = self.parent.resolve(key, position)
		if error:
			return None, error

		return parentResolve, None

########################################
#	CONTEXT
########################################

class Context:
	def __init__(self, displayName: str, parent: Context | None = None) -> None:
		self.displayName = displayName
		self.parent = parent
		self.variableTable: VariableTable = None

	def __repr__(self) -> str:
		return f"ENVIRONMENT(vars: {str(self.variableTable)}, parent: {str(self.parent)}, id: {str(self.id)})"

	def setVariableTable(self, variableTable: VariableTable) -> None:
		self.variableTable = variableTable
		self.variableTable.context = self
		self.variableTable.parent = self.parent.variableTable if self.parent else None
	