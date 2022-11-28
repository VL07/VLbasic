# MADE BY VL07 2022

import os

variables = {}

BLACK = 			"\e[0;30m"
BLUE = 				"\e[0;34m"
GREEN = 			"\e[0;32m"
CYAN = 				"\e[0;36m"
RED = 				"\e[0;31m"
PURPLE = 			"\e[0;35m"
BROWN = 			"\e[0;33m"
GRAY = 				"\e[0;37m"
DARKGRAY = 			"\e[1;30m"
LIGHTBLUE = 		"\e[1;34m"
LIGHTGREEN = 		"\e[1;32m"
LIGHTCYAN = 		"\e[1;36m"
LIGHTRED = 			"\e[1;31m"
LIGHTPURPLE = 		"\e[1;35m"
YELLOW = 			"\e[1;33m"
WHITE = 			"\e[1;37m"
END = 				"\033[0m"

def clear(parameters, context, error):
	os.system('cls' if os.name == 'nt' else 'clear')
	return None, None

variables["clear"] = {
	"value": clear,
	"constant": True,
	"parameters": [0, 0]
}

def printFunc(parameters, context, error):
	textConcatenated = ""

	for argument in parameters:
		string, error = argument.toString(argument.position.copy())
		if error:
			return None, error

		textConcatenated += str(string.value) + ", "

	print(textConcatenated[:-2], end="")

	return None, None

variables["print"] = {
	"value": printFunc,
	"constant": True,
	"parameters": [1, 999]
}

def printLine(parameters, context, error):
	textConcatenated = ""

	for argument in parameters:
		string, error = argument.toString(argument.position.copy())
		if error:
			return None, error

		textConcatenated += str(string.value) + ", "

	print(textConcatenated[:-2])

	return None, None

variables["printLine"] = {
	"value": printLine,
	"constant": True,
	"parameters": [1, 999]
}

def inputFunc(parameters, context, error):
	inputText = ""

	if len(parameters):
		asText, error = parameters[0].toString(parameters[0].position.copy())
		if error:
			return None, error

		inputText = asText.value

	output = input(inputText)

	return output, None

variables["input"] = {
	"value": inputFunc,
	"constant": True,
	"parameters": [0, 1]
}

# def black(parameters, context, error):
# 	return f"{BLACK}{parameters[0].toString(parameters[0].position.copy())}{END}", None

# variables["black"] = {
# 	"value": black,
# 	"constant": True,
# 	"parameters": [1, 1]
# }

# def blue(parameters, context, error):
# 	return f"{BLUE}{parameters[0].toString(parameters[0].position.copy())}{END}", None

# variables["blue"] = {
# 	"value": blue,
# 	"constant": True,
# 	"parameters": [1, 1]
# }

# def green(parameters, context, error):
# 	return f"{GREEN}{parameters[0].toString(parameters[0].position.copy())}{END}", None

# variables["green"] = {
# 	"value": green,
# 	"constant": True,
# 	"parameters": [1, 1]
# }

# def cyan(parameters, context, error):
# 	return f"{CYAN}{parameters[0].toString(parameters[0].position.copy())}{END}", None

# variables["CYAN"] = {
# 	"value": cyan,
# 	"constant": True,
# 	"parameters": [1, 1]
# }

# def red(parameters, context, error):
# 	return f"{RED}{parameters[0].toString(parameters[0].position.copy())}{END}", None

# variables["red"] = {
# 	"value": red,
# 	"constant": True,
# 	"parameters": [1, 1]
# }

# def purple(parameters, context, error):
# 	return f"{PURPLE}{parameters[0].toString(parameters[0].position.copy())}{END}", None

# variables["purple"] = {
# 	"value": purple,
# 	"constant": True,
# 	"parameters": [1, 1]
# }

# def brown(parameters, context, error):
# 	return f"{BROWN}{parameters[0].toString(parameters[0].position.copy())}{END}", None

# variables["brown"] = {
# 	"value": brown,
# 	"constant": True,
# 	"parameters": [1, 1]
# }

# def gray(parameters, context, error):
# 	return f"{GRAY}{parameters[0].toString(parameters[0].position.copy())}{END}", None

# variables["gray"] = {
# 	"value": gray,
# 	"constant": True,
# 	"parameters": [1, 1]
# }

# def darkGray(parameters, context, error):
# 	return f"{DARKGRAY}{parameters[0].toString(parameters[0].position.copy())}{END}", None

# variables["darkGray"] = {
# 	"value": darkGray,
# 	"constant": True,
# 	"parameters": [1, 1]
# }

# def lightblue(parameters, context, error):
# 	return f"{LIGHTBLUE}{parameters[0].toString(parameters[0].position.copy())}{END}", None

# variables["lightblue"] = {
# 	"value": lightblue,
# 	"constant": True,
# 	"parameters": [1, 1]
# }

# def lightGreen(parameters, context, error):
# 	return f"{LIGHTGREEN}{parameters[0].toString(parameters[0].position.copy())}{END}", None

# variables["lightGreen"] = {
# 	"value": lightGreen,
# 	"constant": True,
# 	"parameters": [1, 1]
# }

# def lightCyan(parameters, context, error):
# 	return f"{LIGHTCYAN}{parameters[0].toString(parameters[0].position.copy())}{END}", None

# variables["lightCyan"] = {
# 	"value": lightCyan,
# 	"constant": True,
# 	"parameters": [1, 1]
# }

# def lightRed(parameters, context, error):
# 	return f"{LIGHTRED}{parameters[0].toString(parameters[0].position.copy())}{END}", None

# variables["lightRed"] = {
# 	"value": lightRed,
# 	"constant": True,
# 	"parameters": [1, 1]
# }

# def lightPurple(parameters, context, error):
# 	return f"{LIGHTPURPLE}{parameters[0].toString(parameters[0].position.copy())}{END}", None

# variables["lightPurple"] = {
# 	"value": lightPurple,
# 	"constant": True,
# 	"parameters": [1, 1]
# }

# def yellow(parameters, context, error):
# 	return f"{YELLOW}{parameters[0].toString(parameters[0].position.copy())}{END}", None

# variables["yellow"] = {
# 	"value": yellow,
# 	"constant": True,
# 	"parameters": [1, 1]
# }

# def white(parameters, context, error):
# 	return f"{WHITE}{parameters[0].toString(parameters[0].position.copy())}{END}", None

# variables["white"] = {
# 	"value": white,
# 	"constant": True,
# 	"parameters": [1, 1]
# }