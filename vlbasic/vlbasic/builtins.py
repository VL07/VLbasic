########################################
#	IMPORTS
########################################

from .runtimevaluesclass import Null
from .utils import Position, File
from .error import RTError, ArgumentError
from .runtimevaluesclass import String, Number, BuiltInFunction, Boolean, RuntimeValue
from .contextclass import Context

########################################
#	VARS
########################################

placeholderPosition = Position(0, 0, 0, File("<funcReturn>", ""))
position = placeholderPosition.asStartEndPosition()
context = Context("builtins")

########################################
#	BUILTINS
########################################

builtins: dict[str, RuntimeValue] = {}

builtins["true"] = Boolean(True, position, context)
builtins["false"] = Boolean(False, position, context)
builtins["null"] = Null(position, context)

########################################
#	FUNCTIONS
########################################

def funcPrint(arguments: list[RuntimeValue], executeContext: Context):
	textConcatenated = ""

	for argument in arguments:
		string, error = argument.toString(position.copy())
		if error:
			return None, error

		textConcatenated += str(string.value) + ", "

	print(textConcatenated[:-2])

	return Null(position.copy(), executeContext), None

builtins["print"] = BuiltInFunction("print", funcPrint, position, context)

def funcToString(arguments: list[RuntimeValue], executeContext: Context):
	if len(arguments) > 1:
		return None, ArgumentError(1, len(arguments), "string", position.copy(), executeContext)

	argument = arguments[0]

	asString, error = argument.toString(position.copy())
	if error:
		return None, error

	return String(asString.value, position.copy(), executeContext), None

builtins["string"] = BuiltInFunction("string", funcToString, position, context)

def funcToNumber(arguments: list[RuntimeValue], executeContext: Context):
	if len(arguments) > 1:
		return None, ArgumentError(1, len(arguments), "number", position.copy(), executeContext)

	argument = arguments[0]

	asNumber, error = argument.toNumber(position.copy())
	if error:
		return None, error

	return Number(asNumber.value, position.copy(), executeContext), None

builtins["number"] = BuiltInFunction("number", funcToNumber, position, context)