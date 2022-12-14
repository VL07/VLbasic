########################################
#	IMPORTS
########################################

import sys
import time
import os
import glob
from vlbasic.vlbasic.tokenizer import Tokenizer
from vlbasic.vlbasic.parser import Parser
from vlbasic.vlbasic.contextclass import Context, VariableTable
from vlbasic.vlbasic.interpreter import Interpreter
from vlbasic.vlbasic.utils import InterpretFile

########################################
#	COMMAND LINE TOOL
########################################

args = sys.argv[1:]

########################################
#	UTILS
########################################

helpText = """Commands:
	run
		[0]/--file: The file you want to run
		--debug: If you want to get debug messages from the interpreter, values: stages | all
		--time: If you want to time how long it takes to run the program

	--help
"""

def makeArguments(arguments: list[str]):
	argumentsParsed = {}

	if len(arguments) == 0:
		return {}, True, None

	argument = arguments[0]
	index = 0

	def noMoreArguments():
		return index > (len(arguments) - 1)

	lastKey = None
	keysStarted = False

	while argument:
		if argument.startswith("--"):
			keysStarted = True
			if argument in argumentsParsed.keys():
				return None, f"{argument} already declared"
			
			if lastKey:
				argumentsParsed[lastKey] = True

			lastKey = argument

		else:
			if not keysStarted:
				argumentsParsed[index] = argument
			else:
				if not lastKey:
					return None, f"Values, {argument}, without keys needs to be added first"
				
				argumentsParsed[lastKey] = argument
				lastKey = None

		index += 1

		if noMoreArguments():
			if lastKey:
				argumentsParsed[lastKey] = True
			break

		argument = arguments[index]

	return argumentsParsed, keysStarted, None

def run(file: str, debug = False):
	if debug == "stages":
		print("READING FILE")

	with open(file, "r") as f:
		inputText = f.read()

	if debug == "stages":
		print("TOKENIZING")

	tokenizer = Tokenizer(file, inputText)
	tokens, error = tokenizer.tokenize()

	if error:
		print(repr(error))
		return
	
	if debug == "all":
		print(tokens)

	if debug == "stages":
		print("PARSING")

	parser = Parser(file, tokens)

	statements, error = parser.parse()

	if error:
		print(repr(error))
		return
	
	if debug == "all":
		print(statements)

	context = Context(file)
	context.setVariableTable(VariableTable())

	if debug == "stages":
		print("INTERPRETING")
	
	interpreter = Interpreter(statements, InterpretFile(file, None))
	interpreter.addDefaultVariables(context)
	out, error = interpreter.interpret(context)

	if error:
		print(repr(error))
		return

	if debug == "all":
		print(out)

########################################
#	MAIN FUNCTION
########################################

def main():
	if len(args) == 0:
		print("No action argument was passed, use --help to get help")
		return

	action = args[0]

	if action == "run":
		arguments, onlyUnnamedArgs, error = makeArguments(args[1:])
		if error:
			print(error, "use --help to get help")
			return

		filename = None
		if "--file" in arguments.keys():
			filename = arguments["--file"]
		elif 0 in arguments.keys():
			filename = arguments[0]
		else:
			print("run missing required argument file, use --help to get help")
			return

		debug = None
		if "--debug" in arguments.keys():
			debug = arguments["--debug"]
			if debug not in ["stages", "all"]:
				print(f"run parameter --debug only accepts stages, all as its value, not {debug}, use --help to get help")
				return

		measureTime = None
		if "--time" in arguments.keys():
			measureTime = True

		if not os.path.exists(filename):
			print(f"file not found, {filename}, use --help to get help")
			return

		print(f"Running {filename}...")
		startTime = time.time()
		
		run(filename, debug)

		endTime = time.time()
		if measureTime:
			print(f"Finished in {str(endTime - startTime)}s")
		else:
			print("Finished")

	elif action == "modules":
		arguments, onlyUnnamedArgs, error = makeArguments(args[1:])
		if error:
			print(error, "use --help to get help")
			return

		modulesAction = None
		if "--action" in arguments.keys():
			modulesAction = arguments["--action"]
		elif 0 in arguments.keys():
			modulesAction = arguments[0]
		else:
			print("run missing required argument action, use --help to get help")
			return

		if modulesAction == "list":
			if not os.path.isdir("./vlbasic/modules"):
				print("modules folder not found(/vlbasic/modules)")
				return

			vlbFiles = glob.glob("./vlbasic/modules/*.vlb")
			pyFiles = glob.glob("./vlbasic/modules/*.py")

			outData = ""
			
			for file in vlbFiles:
				outData += ".".join(os.path.basename(file).split(".")[:-1]) + "\n"

			for file in pyFiles:
				outData += ".".join(os.path.basename(file).split(".")[:-1]) + "(py)\n"

			print("Currently installed modules: \n" + outData[:-1])

		else:
			print(f"argument action is invalid, expected list, not {modulesAction}")
			return

	elif action == "add":
		arguments, onlyUnnamedArgs, error = makeArguments(args[1:])
		if error:
			print(error, "use --help to get help")
			return

		template = "default"
		if "--template" in arguments.keys():
			template = arguments["--template"]
		elif 0 in arguments.keys():
			template = arguments[0]
		else:
			print("run missing required argument template, use --help to get help")
			return

		filename = None
		if "--file" in arguments.keys():
			filename = arguments["--file"]
		elif 1 in arguments.keys():
			filename = arguments[1]
		else:
			print("run missing required argument file, use --help to get help")
			return

		force = None
		if "--force" in arguments.keys():
			force = True

		if not os.path.isdir("./vlbasic/templates"):
			print("templates folder not found(/vlbasic/templates)")
			return

		templateFiles = glob.glob("./vlbasic/templates/*.vlb")
		templateFilesKeys = list(map(lambda file : ".".join(os.path.basename(file).split(".")[:-1]), templateFiles))

		templateFilesDict = {}

		for index, key in enumerate(templateFilesKeys):
			templateFilesDict[key] = templateFiles[index]

		if template not in templateFilesDict.keys():
			print("invalid template, use --help to get help")
			return

		if os.path.exists(filename) and not force:
			print("a file at specified path already exists, use --force to overwrite file, use --help to get help")
			return

		templateText = None

		with open(templateFilesDict[template], "r") as file:
			templateText = file.read()

		with open(filename, "w") as file:
			file.write(templateText)

		print(f"successfully created template {template} at {filename}")
			
	elif action == "--help":
		print(helpText)

	else:
		print(f"Invalid action argument {action}, use --help to get help")
		return

########################################
#	__MAIN__ CHECK
########################################

if __name__ == "__main__":
	main()