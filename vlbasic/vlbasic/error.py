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

# RTError

class RTError(Error):
	def __init__(self, details: str, position: StartEndPosition, context, name: str = "RuntimeError") -> None:
		self.name = name
		self.details = details
		self.position = position
		self.context = context
		self.importStack: list[str] = []

	def __repr__(self) -> str:
		errorText = "Stack:\n"

		hasStack = False

		parentContext = self.context.parent
		while parentContext:
			hasStack = True
			errorText += parentContext.displayName
			parentContext = parentContext.parent

		if not hasStack:
			errorText = ""
		else:
			errorText += "\n" + self.context.displayName
			errorText += "\n\n"

		codeAtLine = self.position.file.text.split("\n")[self.position.start.line - 1]
		arrows = (" " * (self.position.start.column)) + ("^" * (self.position.end.column - self.position.start.column))

		errorText += codeAtLine + "\n"
		errorText += arrows + "\n"

		if len(self.importStack):
			errorText += self.importStack[0] + "\n"

		errorText += f"{self.name}: {self.details}\n"

		errorText += f"\nfile: {self.position.file.name}, ln: {self.position.start.line}, col: {self.position.start.column}"
		

		return errorText

class ArgumentError(RTError):
	def __init__(self, expectedArguments: int, gotArguments: int, functionName: str, position: StartEndPosition, context) -> None:
		super().__init__(f"Expected {expectedArguments} argument{'s' if expectedArguments > 1 or expectedArguments == 0 else ''}, but got {gotArguments} argument{'s' if gotArguments > 1 or gotArguments == 0 else ''} when calling function {functionName}", position, context, "ArgumentError")

class VariableDeclarationError(RTError):
	def __init__(self, variableName: str, position: StartEndPosition, context) -> None:
		super().__init__(f"Variable '{variableName}' is already declared", position, context, "VariableDeclarationError")

class VariableConstantAssignmentError(RTError):
	def __init__(self, variableName: str, position: StartEndPosition, context, name: str = "RuntimeError") -> None:
		super().__init__(f"Variable '{variableName}' is a constant and can therefor not be assigned to", position, context, "VariableConstantAssignmentError")

class VariableNotDefinedError(RTError):
	def __init__(self, variableName: str, position: StartEndPosition, context) -> None:
		super().__init__(f"Variable '{variableName}' is not defined", position, context, "VariableNotDefinedError")

class CircularImportError(RTError):
	def __init__(self, file: str, fileToImport: str, position: StartEndPosition, context) -> None:
		super().__init__(f"Circular import ocurred while trying to import file {fileToImport}, from file {file}", position, context, "CircularImportError")

class InvalidIteratorError(RTError):
	def __init__(self, position: StartEndPosition, context) -> None:
		super().__init__("Iterator inside of for loops can only be of type list", position, context, "InvalidIteratorError")

class ReturnOutsideFunctionError(RTError):
	def __init__(self, position: StartEndPosition, context) -> None:
		super().__init__("Returning values can only be done inside of functions", position, context, "ReturnOutsideFunctionError")

class BreakOutsideLoopError(RTError):
	def __init__(self, position: StartEndPosition, context) -> None:
		super().__init__("Break can only be done inside of loops", position, context, "BreakOutsideLoopError")

class ContinueOutsideLoopError(RTError):
	def __init__(self, position: StartEndPosition, context) -> None:
		super().__init__("Continue can only be done inside of loops", position, context, "ContinueOutsideLoopError")

class ValueError_(RTError):
	def __init__(self, types: list[str], gotType: str, position: StartEndPosition, context) -> None:
		super().__init__(f"Expected value of type {', '.join(types)}, not {gotType}", position, context, "ValueError")

class DivisionByZeroError(RTError):
	def __init__(self, position: StartEndPosition, context) -> None:
		super().__init__("Unable to divide by zero", position, context, "DivisionByZeroError")

class RangeError(RTError):
	def __init__(self, valueType: str, position: StartEndPosition, context) -> None:
		super().__init__(f"Object of type {valueType} is out of range", position, context, "RangeError")

class InvalidStringError(RTError):
	def __init__(self, position: StartEndPosition, context) -> None:
		super().__init__("Unable to convert this string to a number", position, context, "InvalidStringError")

class KeyError_(RTError):
	def __init__(self, key: str, position: StartEndPosition, context) -> None:
		super().__init__(f"Invalid key with value '{key}'", position, context, "KeyError")