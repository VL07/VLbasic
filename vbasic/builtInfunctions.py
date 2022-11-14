########################################
#	IMPORTS
########################################

from .runtimevaluesclass import Null
from .utils import Position, File

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
		textConcatenated += str(argument.value) + ", "

	print(textConcatenated[:-2])

	return Null(placeholderPosition.copy(), executeContext), None