#      _                               _           _
#   __| | ___ _ __  _ __ ___  ___ __ _| |_ ___  __| |
#  / _` |/ _ \ '_ \| '__/ _ \/ __/ _` | __/ _ \/ _` |
# | (_| |  __/ |_) | | |  __/ (_| (_| | ||  __/ (_| |
#  \__,_|\___| .__/|_|  \___|\___\__,_|\__\___|\__,_|
#            |_|

######## DEPRECATED ########
#    use vlb.py instead
############################

from vlbasic.vlbasic.tokenizer import Tokenizer
from vlbasic.vlbasic.parser import Parser
from vlbasic.vlbasic.interpreter import Interpreter
from vlbasic.vlbasic.contextclass import Context, VariableTable

v = VariableTable()

while True:
	inputText = input("] ").replace("\\n", "\n")
	if inputText.startswith("> "):
		with open(inputText[2:], "r") as f:
			inputText = f.read()
	print("TOKENIZING")
	t = Tokenizer("SHELL", inputText)
	tokens, error = t.tokenize()

	if error:
		print(repr(error))
		print("")
		continue
	
	print(tokens)

	# for token in tokens:
	# 	print(token.position, end=" ")

	print("PARSING")
	p = Parser("SHELL", tokens)

	statements, error = p.parse()

	if error:
		print(error)
		print(repr(error))
		print("")
		continue
	
	print(statements)

	context = Context("SHELL")
	context.setVariableTable(v)

	print("INTERPRETING")
	i = Interpreter(statements)
	i.addDefaultVariables(context)
	out, error = i.interpret(context)

	if error:
		print(repr(error))
		print("")
		continue

	print(out)
	print(out[0].value if out[0] else "NO OUTPUT")
		
