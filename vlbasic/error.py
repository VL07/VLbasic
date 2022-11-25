########################################
#	IMPORTS
########################################

from __future__ import annotations
from .utils import StartEndPosition

########################################
#	ERROR CLASS
########################################

class Error:
	def __init__(self, name: str, details: str, position: StartEndPosition) -> None:
		self.name = name
		self.details = details
		self.position = position

	def __repr__(self) -> str:
		errorText = f"{self.name}: {self.details}\n"
		errorText += f"file: {self.position.file.name}, ln: {self.position.start.line}, col: {self.position.start.column}"
		return errorText

	def copy(self) -> Error:
		return Error(self.name, self.details, self.position.copy())

########################################
#	ERRORS
########################################

class IllegalCharacterError(Error):
	def __init__(self, details: str, position: StartEndPosition) -> None:
		super().__init__("IllegalCharacterError", details, position)

class ExpectedCharacterError(Error):
	def __init__(self, details: str, position: StartEndPosition) -> None:
		super().__init__("ExpectedCharacterError", details, position)

class InvalidSyntaxError(Error):
	def __init__(self, details: str, position: StartEndPosition) -> None:
		super().__init__("InvalidSyntaxError", details, position)

class RTError(Error):
	def __init__(self, details: str, position: StartEndPosition, context) -> None:
		self.name = "RuntimeError"
		self.details = details
		self.position = position
		self.context = context

	def __repr__(self) -> str:
		errorText = "stack:\n"

		hasStack = False

		parentContext = self.context.parent
		while parentContext:
			hasStack = True
			errorText += parentContext.displayName
			parentContext = parentContext.parent

		if not hasStack:
			errorText = ""
		else:
			errorText += "\n"

		errorText += f"file: {self.position.file.name}, ln: {self.position.start.line}, col: {self.position.start.column}\n"

		codeAtLine = self.position.file.text.split("\n")[self.position.start.line - 1]
		arrows = (" " * (self.position.start.column)) + ("^" * (self.position.end.column - self.position.start.column))

		errorText += codeAtLine + "\n"
		errorText += arrows + "\n"

		errorText += f"{self.name}: {self.details}\n"
		

		return errorText