from vbasic.tokenizer import Tokenizer
from vbasic.parser import Parser
from vbasic.interpreter import Interpreter
from vbasic.contextclass import Context, VariableTable

v = VariableTable()

while True:
	inputText = input("] ").replace("\\n", "\n")
	print("TOKENIZING")
	t = Tokenizer("SHELL", inputText)
	tokens, error = t.tokenize()

	if error:
		print(repr(error))
		print("")
		continue
	
	print(tokens)

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
		
