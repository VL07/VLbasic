########################################
#	IMPORTS
########################################

from .runtimevaluesclass import Null
from .utils import Position, File
from .error import RTError
from .runtimevaluesclass import String, Number

########################################
#	VARS
########################################

placeholderPosition = Position(0, 0, 0, File("<FUNC_RETURN>", ""))

########################################
#	FUNCTIONS
########################################

def funcPrint(arguments, executeContext):
	textConcatenated = ""

	for argument in arguments:
		string, error = argument.toString(placeholderPosition.copy())
		if error:
			return None, error

		textConcatenated += str(string.value) + ", "

	print(textConcatenated[:-2])

	return Null(placeholderPosition.copy(), executeContext), None

def funcToString(arguments, executeContext):
	if len(arguments) > 1:
		return None, RTError(f"STRING function only accepts 1 argument, not {str(len(arguments))}", placeholderPosition.copy(), executeContext)

	argument = arguments[0]

	asString, error = argument.toString(placeholderPosition.copy())
	if error:
		return None, error

	return String(asString.value, placeholderPosition.copy(), executeContext), None