########################################
#	IMPORTS
########################################

from __future__ import annotations
import utils

########################################
#	ERROR CLASS
########################################

class Error:
	def __init__(self, name: str, details: str, position: utils.StartEndPosition) -> None:
		self.name = name
		self.details = details
		self.position = position

	def __repr__(self) -> str:
		print(self.position.start)
		errorText = f"{self.name}: {self.details}\n"
		errorText += f"file: {self.position.file.name}, ln: {self.position.start.line}, col: {self.position.start.column}"
		return errorText

	def copy(self) -> Error:
		return Error(self.name, self.details, self.position.copy())

########################################
#	ERRORS
########################################

class IllegalCharacterError(Error):
	def __init__(self, details: str, position: utils.StartEndPosition) -> None:
		super().__init__("IllegalCharacterError", details, position)

class ExpectedCharacterError(Error):
	def __init__(self, details: str, position: utils.StartEndPosition) -> None:
		super().__init__("ExpectedCharacterError", details, position)

class InvalidSyntaxError(Error):
	def __init__(self, details: str, position: utils.StartEndPosition) -> None:
		super().__init__("InvalidSyntaxError", details, position)