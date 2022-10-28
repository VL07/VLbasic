########################################
#	IMPORTS
########################################

from __future__ import annotations
from error import RTError, Error
from utils import StartEndPosition

########################################
#	CONTEXT
########################################

class Context:
	def __init__(self, displayName: str, parent: Context | None = None) -> None:
		self.displayName = displayName
		self.parent = parent
		self.variables = {}

	def __repr__(self) -> str:
		return f"ENVIRONMENT(vars: {' ,'.join(self.variables)}, parent: {str(self.parent)})"

	def declareVariable(self, key: str, value: any, position: StartEndPosition) -> tuple[any, Error]:
		if key in self.variables.keys():
			return None, RTError(f"Variable {key} is already declared", position.copy())

		self.variables[key] = value

		return value, None

	def assignVariable(self, key: str, value: any, position: StartEndPosition) -> tuple[any, RTError]:
		environment, error = self.resolve(key, position)
		if error:
			return None, error

		environment.variables[key] = value

		return value, None

	def lookupVariable(self, key: str, position: StartEndPosition) -> tuple[any, RTError]:
		environment, error = self.resolve(key, position)
		if error:
			return None, error

		return environment[key]

	def resolve(self, key: str, position: StartEndPosition) -> tuple[Context, RTError]:
		if key in self.variables.keys():
			return self

		if not self.parent:
			return RTError(f"Variable {key} is not defined", position.copy())

		return self.parent.resolve(key, position)
	